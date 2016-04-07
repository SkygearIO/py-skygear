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
import unittest
from unittest.mock import ANY, call, patch

from werkzeug.wrappers import Request

from .. import decorators as d
from ..registry import Registry  # noqa


class TestHookDecorators(unittest.TestCase):
    @patch('skygear.registry.Registry.register')
    def test_before_save(self, mocker):
        @d.before_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')

    @patch('skygear.registry.Registry.register')
    def test_after_save(self, mocker):
        @d.after_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterSave')

    @patch('skygear.registry.Registry.register')
    def test_before_delete(self, mocker):
        @d.before_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeDelete')

    @patch('skygear.registry.Registry.register')
    def test_after_delete(self, mocker):
        @d.after_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterDelete')

    @patch('skygear.registry.Registry.register')
    def test_hook(self, mocker):
        @d.hook('beforeSave', type="note")
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')


def test_fix_handler_path():
    assert d._fix_handler_path('hello:world') == 'hello/world'
    assert d._fix_handler_path('hello/world') == 'hello/world'
    assert d._fix_handler_path('/hello/world/') == 'hello/world'


class TestRestDecorator(unittest.TestCase):
    @patch('skygear.registry.Registry.register')
    def test_register(self, mock):
        @d.rest('/hello/world', user_required=True)
        class HelloWorld:
            def handle_request(self, base_name, request):
                pass

        mock.assert_has_calls([
            call('handler', 'hello/world/', ANY, method=ANY,
                 user_required=True),
            call('handler', 'hello/world', ANY, method=ANY,
                 user_required=True),
            ])

        registered_func = mock.call_args[0][2]
        with patch.object(HelloWorld, 'handle_request') as handle_request:
            req = Request({})
            registered_func(req)
            handle_request.assert_called_with('/hello/world', req)
