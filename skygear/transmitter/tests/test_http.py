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

from ... import config as skyconfig
from ...registry import Registry
from ..common import encode_base64_json
from ..http import HttpTransport


def headers_with_context(data):
    return {'X-Skygear-Plugin-Context': encode_base64_json(data)}


@patch('skygear.config.config', skyconfig.Configuration())
class TestHttpTransport(unittest.TestCase):
    def get_app(self):
        return self.transport.dispatch

    def get_client(self):
        return Client(self.get_app(), BaseResponse)

    def setUp(self):
        self.transport = HttpTransport('127.0.0.1:8888', Registry())

    def tearDown(self):
        self.transport = None

    @patch('skygear.transmitter.http.run_simple')
    def testRun(self, mocker):
        self.transport.run()
        mocker.assert_called_once_with('127.0.0.1', 8888,
                                       self.transport.dispatch,
                                       use_reloader=False)

    @patch('skygear.transmitter.http.HttpTransport.init_info')
    def testInitInfo(self, mocker):
        mocker.return_value = {'data': 'hello'}
        request_data = json.dumps({'config': {'hello': 'world'}})
        resp = self.get_client().post('/init', data=request_data)
        assert resp.status_code == 200
        mocker.assert_called_once_with()
        assert json.loads(resp.get_data(as_text=True)) == mocker.return_value
        assert skyconfig.config.hello == 'world'

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testCallFuncWithData(self, mocker):
        mocker.return_value = {'data': 'hello'}
        request_data = json.dumps({'data': 'bye'})
        headers = headers_with_context({'context': 'happy'})
        resp = self.get_client().post('/timer/name', data=request_data,
                                      headers=headers)
        assert resp.status_code == 200
        mocker.assert_called_once_with({'context': 'happy'}, 'timer', 'name',
                                       {'data': 'bye'})
        assert json.loads(resp.get_data(as_text=True)) == mocker.return_value

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testOp(self, mocker):
        mocker.return_value = {}
        resp = self.get_client().post('/op/john')
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'op', 'john', ANY)

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testHook(self, mocker):
        mocker.return_value = {}
        resp = self.get_client().post('/hook/john')
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'hook', 'john', ANY)

    @patch('skygear.transmitter.http.HttpTransport.call_provider')
    def testProvider(self, mocker):
        mocker.return_value = {}
        resp = self.get_client().post('/provider/john/work')
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'john', 'work', ANY)
        args, kwargs = mocker.call_args

    @patch('skygear.transmitter.http.HttpTransport.call_func')
    def testTimer(self, mocker):
        mocker.return_value = {}
        resp = self.get_client().post('/timer/john')
        assert resp.status_code == 200
        mocker.assert_called_once_with(ANY, 'timer', 'john', ANY)
