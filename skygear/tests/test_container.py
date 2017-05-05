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
import unittest
from unittest.mock import patch

from ..container import SkygearContainer
from ..transmitter.http import send_action


class TestSendAction(unittest.TestCase):
    @patch('skygear.transmitter.http.requests', autospec=True)
    def test_send_str(self, mock_requests):
        send_action('http://skygear.dev/', {
            'key': 'string'
        })
        self.assertEqual(len(mock_requests.method_calls), 1)
        call = mock_requests.method_calls[0]
        self.assertEqual(call[0], 'post')
        self.assertEqual(call[1][0], 'http://skygear.dev/')
        self.assertEqual(call[2]['data'], '{"key": "string"}')

    @patch('skygear.transmitter.http.requests', autospec=True)
    def test_send_date(self, mock_requests):
        dt = datetime.datetime(2014, 9, 27, 17, 40, 0,
                               tzinfo=datetime.timezone.utc)
        send_action('http://skygear.dev/', {
            'print_at': dt
        })
        self.assertEqual(len(mock_requests.method_calls), 1)
        call = mock_requests.method_calls[0]
        self.assertEqual(call[0], 'post')
        self.assertEqual(call[1][0], 'http://skygear.dev/')
        self.assertEqual(
            call[2]['data'],
            '{"print_at": "2014-09-27T17:40:00Z"}')


class TestContainer():
    def test_payload_include_action(self):
        c = SkygearContainer(endpoint='endpoint', access_token='access-token')
        payload = c._payload('action:work', {'data': 'hello world'}, False)
        assert payload['action'] == 'action:work'
        assert payload['data'] == 'hello world'

    def test_payload_include_api_key(self):
        c = SkygearContainer(endpoint='endpoint', api_key='api-key')
        payload = c._payload('action:work', {}, False)
        assert payload['api_key'] == 'api-key'

    def test_payload_include_user_id(self):
        c = SkygearContainer(endpoint='endpoint', api_key='api-key',
                             user_id='user-id')
        payload = c._payload('action:work', {}, False)
        assert payload['_user_id'] == 'user-id'

    def test_payload_include_access_token(self):
        c = SkygearContainer(endpoint='endpoint', access_token='access-token')
        payload = c._payload('action:work', {}, False)
        assert payload['access_token'] == 'access-token'

    def test_payload_include_all_credentials(self):
        c = SkygearContainer(endpoint='endpoint',
                             access_token='access-token',
                             api_key='api-key',
                             user_id='user-id')
        payload = c._payload('action:work', {}, False)
        assert payload['access_token'] == 'access-token'
        assert payload['api_key'] == 'api-key'
        assert payload['_user_id'] == 'user-id'

    def test_plugin_request_payload(self):
        c = SkygearContainer(endpoint='endpoint',
                             access_token='access-token',
                             api_key='master-key')
        payload = c._payload('action:work', {}, True)
        assert payload['access_token'] == 'access-token'
        assert payload['api_key'] == 'master-key'
        assert payload['_from_plugin']
