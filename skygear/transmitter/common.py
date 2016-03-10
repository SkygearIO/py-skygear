# Copyright 2015 Oursky Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import base64
import json
import logging
import os
from functools import wraps

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from ..error import SkygearException
from ..registry import get_registry
from ..utils import db
from ..utils.context import start_context
from ..utils.http import Response
from .encoding import _serialize_exc, deserialize_or_none, serialize_record


def _get_engine():
    return db._get_engine()


def _wrap_result(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return dict(result=f(self, *args, **kwargs))
        except SkygearException as e:
            return dict(error=e.as_dict())
        except Exception as e:
            self.logger.exception("Error occurred processing request")
            return dict(error=_serialize_exc(e).as_dict())
    return wrapper


def encode_base64_json(data):
    """
    Encode dict-like data into a base64 encoded JSON string.

    This can be used to get dict-like data into HTTP headers / envvar.
    """
    return base64.b64encode(bytes(json.dumps(data), 'utf-8'))


def decode_base64_json(data):
    """
    Decode dict-like data from a base64 encoded JSON string.

    This can be used to get dict-like data into HTTP headers / envvar.
    """
    return json.loads(base64.b64decode(data).decode('utf-8'))


def dict_from_base64_environ(name):
    data = os.environ.get(name)
    return decode_base64_json(data) if data else {}


class CommonTransport:
    def __init__(self, registry=None, logger=None):
        self._registry = registry or get_registry()
        self.logger = logger or logging.getLogger(__name__)

    def init_info(self):
        return self._registry.func_list()

    @_wrap_result
    def call_func(self, ctx, kind, name, param):
        obj = self._registry.get_obj(kind, name)
        with start_context(ctx):
            if kind == 'op':
                return self.op(obj, param.get('args', {}))
            elif kind == 'hook':
                return self.hook(obj, param)
            elif kind == 'timer':
                return self.timer(obj)
            else:
                raise SkygearException("unknown plugin extension point")

    @_wrap_result
    def call_provider(self, ctx, name, action, param):
        obj = self._registry.get_obj('provider', name)

        with start_context(ctx):
            return self.provider(obj, action, param)

    @_wrap_result
    def call_handler(self, ctx, name, param):
        func = self._registry.get_handler(name, param['method'])
        with start_context(ctx):
            return self.handler(func, param)

    def handler(self, func, param):
        builder = EnvironBuilder(
            method=param['method'],
            path=param['path'],
            query_string=param.get('query_string'),
            headers=param['header'],
            data=base64.b64decode(param['body'])
        )
        environ = builder.get_environ()
        request = Request(environ, populate_request=False, shallow=False)
        response = func(request)
        status = 200
        if isinstance(response, Response):
            headers = {}
            for k, v in response.headers:
                headers[k] = [v]
            body_byte = response.get_data()
            body = base64.b64encode(body_byte).decode('utf-8')
            status = response.status_code
        elif isinstance(response, str):
            headers = {'Content-Type': ['text/plain; charset=utf-8']}
            body = base64.b64encode(
                bytes(response, 'utf-8')
            ).decode('utf-8')
        else:
            headers = {
                'Content-Type': ['application/json']
             }
            body = encode_base64_json(response).decode('utf-8')
        return {
            'status': status,
            'header': headers,
            'body': body
        }

    def op(self, func, param):
        if isinstance(param, list):
            args = param
            kwargs = {}
        elif isinstance(param, dict):
            args = []
            kwargs = param
        else:
            msg = "Unsupported args type '{0}'".format(type(param))
            raise ValueError(msg)
        return func(*args, **kwargs)

    def hook(self, func, param):
        original_record = deserialize_or_none(param.get('original', None))
        record = deserialize_or_none(param.get('record', None))
        with db.conn() as conn:
            returned = func(record, original_record, conn)

            # If the hook function does not return a value, assume that
            # the record in the first argument is to be returned.
            if returned is None:
                returned = record
        return serialize_record(returned)

    def timer(self, func):
        return func()

    def provider(self, provider, action, data):
        return provider.handle_action(action, data)

    def run(self):
        raise NotImplemented()
