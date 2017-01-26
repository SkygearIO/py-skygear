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
import datetime
import json

import requests
import strict_rfc3339

from . import error


class PayloadEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            ts = obj.timestamp()
            return strict_rfc3339.timestamp_to_rfc3339_utcoffset(ts)


def send_action(url, payload, timeout=60):
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}

    _data = json.dumps(payload, cls=PayloadEncoder)
    return requests.post(url, data=_data, headers=headers, timeout=timeout) \
        .json()


class SkygearContainer(object):
    endpoint = 'http://localhost:3000'
    api_key = None
    access_token = None
    user_id = None
    app_name = ''

    def __init__(self, endpoint=None, api_key=None, access_token=None,
                 user_id=None):
        if endpoint:
            self.endpoint = endpoint
        if api_key:
            self.api_key = api_key
        if user_id:
            self.user_id = user_id
        self.access_token = access_token

    def _request_url(self, action_name):
        endpoint = self.endpoint
        endpoint = endpoint[:-1] if endpoint[-1] == '/' else endpoint
        return endpoint + '/' + action_name.replace(':', '/')

    def _payload(self, action_name, params, plugin_request):
        payload = params.copy() if isinstance(params, dict) else {}
        payload['action'] = action_name
        if self.access_token:
            payload['access_token'] = self.access_token
        if self.api_key:
            payload['api_key'] = self.api_key
        if self.user_id:
            payload['_user_id'] = self.user_id
        if plugin_request:
            payload['_from_plugin'] = True
        return payload

    @classmethod
    def set_default_app_name(cls, app_name):
        cls.app_name = app_name

    @classmethod
    def get_default_app_name(cls):
        return cls.app_name

    @classmethod
    def set_default_endpoint(cls, endpoint):
        cls.endpoint = endpoint

    @classmethod
    def set_default_apikey(cls, api_key):
        cls.api_key = api_key

    def send_action(self, action_name, params, plugin_request=False,
                    timeout=60):
        resp = send_action(self._request_url(action_name),
                           self._payload(action_name, params, plugin_request),
                           timeout=timeout)
        if 'error' in resp:
            raise error.SkygearException.from_dict(resp['error'])

        return resp
