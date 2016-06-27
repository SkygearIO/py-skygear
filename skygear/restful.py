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
import uuid

from skygear.container import SkygearContainer
from skygear.error import BadRequest, SkygearException, UnexpectedError

log = logging.getLogger(__name__)


def get_ident(base_name, request):
    if not request.path.startswith(base_name):
        raise Exception('path "{}" not matching "{}"'
                        .format(request.path, base_name))
    path = request.path[len(base_name):]
    if path.startswith('/'):
        path = path[1:]
    return path.split('/')[0] or None


def has_func(obj, name):
    return callable(getattr(obj, name, None))


class RestfulResource:
    @classmethod
    def get_allowed_methods(cls):
        methods = []
        for r in cls._routes():
            if has_func(cls, r['func']):
                methods.append(r['method'])
        return list(set(methods))

    def get_payload(self):
        data = self.request.get_data(as_text=True)
        if data == '':
            return {}
        try:
            payload = json.loads(data)
            return payload
        except ValueError:
            raise SkygearException('unable to decode json', BadRequest)

    @classmethod
    def _routes(cls):
        return [
                {'ident': True, 'method': 'PUT', 'func': 'update'},
                {'ident': True, 'method': 'GET', 'func': 'get'},
                {'ident': True, 'method': 'DELETE', 'func': 'delete'},
                {'ident': False, 'method': 'POST', 'func': 'create'},
                {'ident': False, 'method': 'GET', 'func': 'index'},
                ]

    def handle_request(self, base_name, request):
        self.request = request
        ident = get_ident(base_name, request)

        for r in self._routes():
            if r['ident'] != bool(ident):
                continue
            if r['method'] != request.method:
                continue
            if not has_func(self, r['func']):
                continue

            if ident:
                return getattr(self, r['func'])(ident)
            else:
                return getattr(self, r['func'])()
        else:
            raise SkygearException('invalid request method', BadRequest)


class RestfulRecord(RestfulResource):
    record_type = None
    database_id = '_public'

    @property
    def container(self):
        token = self._access_token()
        container = SkygearContainer(access_token=token)
        return container

    def _send_multi(self, action, **payload):
        result = self.container.send_action(action, payload)
        if 'error' in result:
            raise SkygearException.from_dict(result['error'])
        elif 'result' in result and isinstance(result['result'], list):
            return result
        else:
            raise SkygearException('unexpected result', UnexpectedError)

    def _send_single(self, action, **payload):
        result = self.container.send_action(action, payload)
        if 'error' in result:
            raise SkygearException.from_dict(result['error'])
        elif 'result' in result and isinstance(result['result'], list) \
                and len(result['result']) > 0:
            first_result = result['result'][0]
            if first_result.get('_type', None) == 'error':
                raise SkygearException.from_dict(first_result)
            return first_result
        else:
            raise SkygearException('unexpected result', UnexpectedError)

    def _record_id(self, ident):
        return self.record_type + '/' + ident

    def _access_token(self):
        token = self.request.headers.get('X-Skygear-Access-Token', None)
        if token:
            return token

        try:
            data = json.loads(self.request.get_data(as_text=True))
            return data.get('access_token', None)
        except ValueError:
            return None

    def predicate(self):
        return None

    def query_options(self):
        return {}

    def index(self):
        """
        List records by querying the database.
        """
        options = self.query_options() or {}
        predicate = self.predicate()
        if predicate is not None:
            options['predicate'] = predicate

        return self._send_multi('record:query',
                                database_id=self.database_id,
                                record_type=self.record_type,
                                **options
                                )

    def create(self):
        payload = self.get_payload()
        if not payload.get('_id', '').startswith(self.record_type + '/'):
            payload['_id'] = self.record_type + '/' + str(uuid.uuid4())
        return self._send_single('record:save',
                                 database_id=self.database_id,
                                 records=[payload])

    def delete(self, ident):
        record_id = self._record_id(ident)
        return self._send_single('record:delete',
                                 database_id=self.database_id,
                                 ids=[record_id])

    def update(self, ident):
        payload = self.get_payload()
        payload['_id'] = self._record_id(ident)
        return self._send_single('record:save',
                                 database_id=self.database_id,
                                 records=[payload])

    def get(self, ident):
        record_id = self._record_id(ident)
        return self._send_single('record:fetch',
                                 database_id=self.database_id,
                                 ids=[record_id])
