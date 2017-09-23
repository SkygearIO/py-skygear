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
import logging

import requests
import strict_rfc3339

from .__version__ import __version__
from .database import Database

log = logging.getLogger(__name__)


class PayloadEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            ts = obj.timestamp()
            return strict_rfc3339.timestamp_to_rfc3339_utcoffset(ts)


def send_action(url, payload, timeout=60):
    log.error("skygear.container.send_action is deprecated.\n"
              "Please use SkygearContainer().send_action instead.")
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'X-Skygear-SDK-Version': 'py-skygear/' + __version__}
    _data = json.dumps(payload, cls=PayloadEncoder)
    return requests.post(url, data=_data, headers=headers, timeout=timeout) \
        .json()


class SkygearContainer(object):
    endpoint = 'http://localhost:3000'
    """Skygear Server Location"""
    api_key = None
    access_token = None
    user_id = None
    app_name = ''
    transport = None

    def __init__(self, endpoint=None, api_key=None, access_token=None,
                 user_id=None, transport=None):
        """
        `public_database` Public Database
        `private_database` Private Database
        """
        if endpoint:
            self.endpoint = endpoint
        if api_key:
            self.api_key = api_key
        if user_id:
            self.user_id = user_id
        self.access_token = access_token
        if transport is None:
            self.transport = SkygearContainer.transport
        else:
            self.transport = transport
        self.public_database = Database(self, '_public')
        self.private_database = Database(self, '_private')

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

    @classmethod
    def set_default_transport(cls, transport):
        cls.transport = transport

    def send_action(self, action_name, params, plugin_request=False,
                    timeout=60):
        url = self._request_url(action_name)
        payload = self._payload(action_name, params, plugin_request)
        resp = self.transport.send_action(action_name, payload, url, timeout)
        return resp
