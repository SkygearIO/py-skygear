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
import os
import unittest
from unittest.mock import MagicMock, patch

from .. import common
from ...error import SkygearException
from ...models import Record, RecordID
from ...registry import Registry
from ...utils.context import current_context
from ...utils.http import Response
from ..common import CommonTransport
from ..encoding import deserialize_or_none, serialize_record


class TestCommonTransport(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()
        self.transport = CommonTransport(self.registry)
        self.ctx = {'state': 'happy'}

    def tearDown(self):
        self.registry = None
        self.transport = None

    @patch('skygear.registry.Registry.func_list')
    def testInitInfo(self, mocker):
        mocker.return_value = {'op': []}
        assert self.transport.init_info() == mocker.return_value

    @patch('skygear.registry.Registry.get_obj')
    def testCallFuncGetCorrectObject(self, mocker):
        mocker.return_value = MagicMock()
        self.transport.call_func(self.ctx, 'timer', 'name', {})
        mocker.assert_called_once_with('timer', 'name')
        mocker.return_value.assert_called_once_with()

    @patch('skygear.registry.Registry.get_obj')
    def testCallFuncContext(self, mocker):
        def assertState(expectedState):
            def func():
                assert current_context().get('state') == expectedState
            return func

        mocker.return_value = MagicMock(side_effect=assertState("happy"))
        self.transport.call_func(self.ctx, 'timer', 'name', {})
        mocker.return_value.assert_called_once_with()
        assert 'state' not in current_context()

    @patch('skygear.registry.Registry.get_obj')
    def testCallFuncResult(self, mocker):
        mocker.return_value = MagicMock(return_value={'data': 'hello'})
        result = self.transport.call_func(self.ctx, 'timer', 'name', {})
        assert result['result'] == {'data': 'hello'}

    @patch('skygear.registry.Registry.get_obj')
    def testCallProviderGetCorrectObject(self, mocker):
        mocker.return_value = MagicMock()
        self.transport.call_provider(self.ctx, 'name', 'action', {})
        mocker.assert_called_once_with('provider', 'name')
        mocker.return_value.handle_action.assert_called_once_with('action', {})

    @patch('skygear.registry.Registry.get_obj')
    def testCallProviderContext(self, mocker):
        def assertState(expectedState):
            def func():
                assert current_context().get('state') == expectedState
            return func

        mocker.return_value = MagicMock(side_effect=assertState("happy"))
        self.transport.call_provider(self.ctx, 'name', 'action', {})
        mocker.return_value.handle_action.assert_called_once_with('action', {})
        assert 'state' not in current_context()

    @patch('skygear.registry.Registry.get_obj')
    def testCallProviderResult(self, mocker):
        provider_mock = MagicMock()
        provider_mock.handle_action.return_value = {'data': 'hello'}
        mocker.return_value = provider_mock
        result = self.transport.call_provider(self.ctx, 'name', 'action', {})
        assert result['result'] == {'data': 'hello'}

    @patch('skygear.registry.Registry.get_obj')
    def testCallFuncGenericException(self, mocker):
        exc = Exception('Error occurred')
        mocker.return_value = MagicMock(side_effect=exc)
        result = self.transport.call_func(self.ctx, 'timer', 'name', {})
        assert result['error']['message'] == 'Error occurred'

    @patch('skygear.registry.Registry.get_obj')
    def testCallFuncSkygearException(self, mocker):
        exc = SkygearException('Error occurred', 1, {'data': 'hello'})
        mocker.return_value = MagicMock(side_effect=exc)
        result = self.transport.call_func(self.ctx, 'timer', 'name', {})
        assert result['error']['message'] == 'Error occurred'
        assert result['error']['code'] == 1

    def testOpDictArg(self):
        mock = MagicMock(return_value={'result': 'OK'})
        self.transport.op(mock, dict(named='value'))
        mock.assert_called_with(named='value')

    def testOpArrayArg(self):
        mock = MagicMock(return_value={'result': 'OK'})
        self.transport.op(mock, [1, 2])
        mock.assert_called_with(1, 2)

    def testHandlerWithStrReturn(self):
        mock = MagicMock(return_value='Hello')
        response = self.transport.handler(mock, {
            'path': '/',
            'method': 'POST',
            'header': {'Content-Type': ['text/plain; charset=utf-8']},
            'body': base64.b64encode(b'rawstream')
        })
        assert response['header']['Content-Type'] == \
            ['text/plain; charset=utf-8']
        assert response['status'] == 200
        assert base64.b64decode(response['body']) == b'Hello'

    def testHandlerWithDictReturn(self):
        mock = MagicMock(return_value={
            'hello': 'world'
        })
        response = self.transport.handler(mock, {
            'path': '/',
            'method': 'POST',
            'header': {'Content-Type': ['text/plain; charset=utf-8']},
            'body': base64.b64encode(b'rawstream')
        })
        assert response['header']['Content-Type'] == ['application/json']
        assert response['status'] == 200
        assert base64.b64decode(response['body']) == b'{"hello": "world"}'

    def testHandlerWithResponseReturn(self):
        mock = MagicMock(return_value=Response(
            headers={},
            status=405,
            response='Method NOT Allowed'
        ))
        response = self.transport.handler(mock, {
            'path': '/',
            'method': 'POST',
            'header': {'Content-Type': ['text/plain; charset=utf-8']},
            'body': base64.b64encode(b'rawstream')
        })
        assert response['header']['Content-Type'] == \
            ['text/plain; charset=utf-8']
        assert response['status'] == 405
        assert base64.b64decode(response['body']) == b'Method NOT Allowed'

    def testHook(self):
        record_id = RecordID('note', 'note1')
        updated_record = Record(record_id, 'owner', None,
                                data={'data': 'updated'})
        old_record = Record(record_id, 'owner', None, data={'data': 'old'})
        new_record = Record(record_id, 'owner', None, data={'data': 'new'})
        param = {
            'original': serialize_record(old_record),
            'record': serialize_record(new_record),
            }
        mock = MagicMock(return_value=updated_record)
        returned_record = self.transport.hook(mock, param)
        assert mock.call_count == 1
        args, kwargs = mock.call_args
        assert args[0].data == new_record.data
        assert args[1].data == old_record.data
        assert deserialize_or_none(returned_record).data == updated_record.data

    def testTimer(self):
        mock = MagicMock()
        self.transport.timer(mock)
        mock.assert_called_once_with()

    def testProvider(self):
        mock = MagicMock()
        self.transport.provider(mock, 'action', {'data': 'hello'})
        mock.handle_action.assert_called_with('action', {'data': 'hello'})


class TestBase64Encoding(unittest.TestCase):
    @patch.dict(os.environ, {'SKYGEAR_CONTEXT': 'e30='})
    def testFromEnviron(self):
        d = common.dict_from_base64_environ('SKYGEAR_CONTEXT')
        assert d == {}

    def testEncoding(self):
        assert common.encode_base64_json({}) == b'e30='

    def testDecoding(self):
        assert common.decode_base64_json('e30=') == {}
