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
from ..container import SkygearContainer


class TestContainer():
    def test_payload_include_action(self):
        c = SkygearContainer(endpoint='endpoint', access_token='access-token')
        payload = c._payload('action:work', {'data': 'hello world'})
        assert payload['action'] == 'action:work'
        assert payload['data'] == 'hello world'

    def test_payload_include_api_key(self):
        c = SkygearContainer(endpoint='endpoint', api_key='api-key')
        payload = c._payload('action:work', {})
        assert payload['api_key'] == 'api-key'

    def test_payload_include_user_id(self):
        c = SkygearContainer(endpoint='endpoint', api_key='api-key',
                             user_id='user-id')
        payload = c._payload('action:work', {})
        assert payload['_user_id'] == 'user-id'

    def test_payload_include_access_token(self):
        c = SkygearContainer(endpoint='endpoint', access_token='access-token')
        payload = c._payload('action:work', {})
        assert payload['access_token'] == 'access-token'
