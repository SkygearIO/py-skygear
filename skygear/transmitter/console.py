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
import json
import logging
import sys

from ..registry import get_registry
from .common import _get_engine
from .encoding import _serialize_exc, deserialize_or_none, serialize_record

log = logging.getLogger(__name__)


# a decorator intended to be used in ConsoleTransport's member method.
# it encapsulates return value or exception thrown into a response,
# then write it to the console
def _serialize(func):
    def serialize_with_exc(self, *args, **kwargs):
        d = {}
        try:
            d['result'] = func(self, *args, **kwargs)
        except Exception as e:
            d['error'] = _serialize_exc(e)
        self.write(json.dumps(d))

    return serialize_with_exc


class ConsoleTransport:

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, registry=None):
        if registry is None:
            registry = get_registry()
        self._registry = registry

        self.input = stdin
        self.output = stdout

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)

    @_serialize
    def handle_call(self, kind, name, *args):
        param = json.loads(self.read())

        # derive args and kwargs
        if kind == 'op':
            param = param.get('args', {})
            if isinstance(param, list):
                args = param
                kwargs = {}
            elif isinstance(param, dict):
                args = []
                kwargs = param
            else:
                msg = "Unsupported args type '{0}'".format(type(param))
                raise ValueError(msg)

            obj = self._registry.get_obj(kind, name)
            return self.op(obj, *args, **kwargs)
        elif kind == 'handler':
            obj = self._registry.get_obj(kind, name)
            return self.handler(obj)
        elif kind == 'hook':
            record_type = param['record']['_id'].split('/')[0]
            obj = self._registry.get_obj(kind, name, record_type)
            return self.hook(obj, param)
        elif kind == 'timer':
            obj = self._registry.get_obj(kind, name)
            return self.timer(obj)
        elif kind == 'provider':
            obj = self._registry.get_obj(kind, name)
            return self.provider(obj, args[0], param)

        return obj, args, kwargs

    def op(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def handler(self, func):
        return func()

    def hook(self, func, param):
        original_record = deserialize_or_none(param.get('original', None))
        record = deserialize_or_none(param.get('record', None))
        with _get_engine().begin() as conn:
            func(record, original_record, conn)
        return serialize_record(record)

    def timer(self, func):
        return func()

    def provider(self, provider, action, data):
        return provider.handle_action(action, data)
