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
import io
import json
import os
import unittest
from unittest.mock import ANY, patch

from ...registry import Registry
from ..common import encode_base64_json
from ..console import ConsoleTransport


def environ_dict(context):
    return {'SKYGEAR_CONTEXT': encode_base64_json(context).decode('utf-8')}


class TestConsoleTransport(unittest.TestCase):
    def exec(self, args, data, registry=None):
        out = io.StringIO()
        data = data if isinstance(data, str) else json.dumps(data)
        transport = ConsoleTransport(args,
                                     stdin=io.StringIO(data),
                                     stdout=out,
                                     registry=registry or Registry())
        transport.run()
        out.seek(0)
        return json.loads(out.read())

    @patch.dict(os.environ, environ_dict({'context': 'happy'}))
    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testCallFuncWithData(self, mocker):
        mocker.return_value = {'data': 'hello'}
        output = self.exec(['timer', 'name'], {'data': 'bye'})
        mocker.assert_called_once_with({'context': 'happy'}, 'timer', 'name',
                                       {'data': 'bye'})
        assert output == mocker.return_value

    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testOpInvalidJSON(self, mocker):
        mocker.return_value = {}
        output = self.exec(['op', 'john'], "not-valid")
        assert not mocker.called
        expected_output = {'code': 10000, 'info': {},
                           'message': 'unable to parse JSON string'}
        assert output == expected_output

    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testOpEmpty(self, mocker):
        mocker.return_value = {"data": "hi"}
        output = self.exec(['op', 'john'], "")
        mocker.assert_called_once_with(ANY, 'op', 'john', {})
        assert output == mocker.return_value

    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testOp(self, mocker):
        mocker.return_value = {"data": "hi"}
        output = self.exec(['op', 'john'], {'data': 'bye'})
        mocker.assert_called_once_with(ANY, 'op', 'john', {'data': 'bye'})
        assert output == mocker.return_value

    @patch('skygear.transmitter.console.ConsoleTransport.call_event_func')
    def testEvent(self, mocker):
        mocker.return_value = {"data": "okay-event"}
        output = self.exec(['event', 'okay'], {'data': 'haha'})
        mocker.assert_called_once_with('okay', {'data': 'haha'})
        assert output == mocker.return_value

    @patch('skygear.transmitter.console.ConsoleTransport.init_event_handler')
    def testInitEvent(self, mocker):
        mocker.return_value = {'data': 'hello'}
        output = self.exec(['event', 'init'], {'config': {'hello': 'world'}})
        mocker.assert_called_once_with(config={'hello': 'world'})
        assert output.get('result') == mocker.return_value

    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testHook(self, mocker):
        mocker.return_value = {}
        self.exec(['hook', 'john'], {'data': 'bye'})
        mocker.assert_called_once_with(ANY, 'hook', 'john', {'data': 'bye'})

    @patch('skygear.transmitter.console.ConsoleTransport.call_provider')
    def testProvider(self, mocker):
        mocker.return_value = {}
        self.exec(['provider', 'john', 'work'], {'data': 'bye'})
        mocker.assert_called_once_with(ANY, 'john', 'work', {'data': 'bye'})

    @patch('skygear.transmitter.console.ConsoleTransport.call_func')
    def testTimer(self, mocker):
        mocker.return_value = {}
        self.exec(['timer', 'john'], "")
        mocker.assert_called_once_with(ANY, 'timer', 'john', {})
