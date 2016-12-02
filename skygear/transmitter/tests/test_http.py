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
import unittest
from unittest.mock import ANY, patch

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from ...registry import Registry
from ..common import encode_base64_json
from ..http import HttpTransport


def headers_with_context(data):
    return {'X-Skygear-Plugin-Context': encode_base64_json(data)}


class TestHttpTransport(unittest.TestCase):
    def get_app(self):
        return self.transport.dispatch

    def get_client(self, dispatcher=None):
        return Client(dispatcher or self.get_app(), BaseResponse)

    def setUp(self):
        self.transport = HttpTransport('127.0.0.1:8888', Registry())

    def tearDown(self):
        self.transport = None

    @patch('skygear.transmitter.http.run_simple')
    def testRun(self, mocker):
        self.transport.run()
        mocker.assert_called_once_with('127.0.0.1', 8888,
                                       self.transport.dispatch,
                                       threaded=True,
                                       use_reloader=False)

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testCallFuncWithData(self, mocker):
        mocker.return_value = {'data': 'hello'}
        data = {
            'context': {'context': 'happy'},
            'kind': 'timer',
            'name': 'name',
            'param': {
                'data': 'bye'
            }
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with({'context': 'happy'}, 'timer', 'name',
                                       {'data': 'bye'})
        assert json.loads(resp.get_data(as_text=True)) == mocker.return_value

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testOp(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'op',
            'name': 'john'
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'op', 'john', ANY)

    @patch('skygear.transmitter.http.HttpTransport.call_event_func')
    def testEvent(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'event',
            'name': 'funny'
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with('funny', ANY)

    @patch('skygear.transmitter.http.HttpTransport.init_event_handler')
    def testInitEvent(self, mocker):
        mocker.return_value = {'data': 'hello'}
        data = {
            'kind': 'event',
            'name': 'init',
            'param': {
                'config': {'hello': 'world'}
            }
        }
        transport = HttpTransport('127.0.0.1:8888', Registry())
        client = self.get_client(transport.dispatch)
        resp = client.post('/', data=json.dumps(data))

        assert resp.status_code == 200
        mocker.assert_called_once_with(config={'hello': 'world'})

        resp_data = json.loads(resp.get_data(as_text=True))
        assert resp_data.get('result') == mocker.return_value

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testHook(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'hook',
            'name': 'john'
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'hook', 'john', ANY)

    @patch('skygear.transmitter.http.HttpTransport.call_provider')
    def testProvider(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'provider',
            'name': 'john',
            'param': {
                'action': 'work'
            }
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'john', 'work', ANY)
        args, kwargs = mocker.call_args

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testTimer(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'timer',
            'name': 'john'
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'timer', 'john', ANY)

    @patch('skygear.transmitter.http.HttpTransport.call_handler')
    def testHandler(self, mocker):
        mocker.return_value = {}
        data = {
            'kind': 'handler',
            'name': 'apple/pie'
        }
        resp = self.get_client().post('/', data=json.dumps(data))
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'apple/pie', ANY)
