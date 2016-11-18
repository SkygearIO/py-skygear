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
from ..utils.assets import DirectoryStaticAssetsLoader


class TestOpDecorators(unittest.TestCase):
    @patch('skygear.registry.Registry.register_op')
    def test_register(self, mocker):
        @d.op('do:something')
        def fn():
            pass
        mocker.assert_called_with(
            'do:something', ANY)


class TestTimerDecorators(unittest.TestCase):
    @patch('skygear.registry.Registry.register_timer')
    def test_register(self, mocker):
        @d.every('* * * * * *')
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            spec='* * * * * *')


class TestHookDecorators(unittest.TestCase):
    @patch('skygear.registry.Registry.register_hook')
    def test_before_save(self, mocker):
        @d.before_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')

    @patch('skygear.registry.Registry.register_hook')
    def test_after_save(self, mocker):
        @d.after_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterSave')

    @patch('skygear.registry.Registry.register_hook')
    def test_before_delete(self, mocker):
        @d.before_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeDelete')

    @patch('skygear.registry.Registry.register_hook')
    def test_after_delete(self, mocker):
        @d.after_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterDelete')

    @patch('skygear.registry.Registry.register_hook')
    def test_hook(self, mocker):
        @d.hook('beforeSave', type="note")
        def fn():
            pass
        mocker.assert_called_with(
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')


def test_fix_handler_path():
    assert d._fix_handler_path('hello:world') == 'hello/world'
    assert d._fix_handler_path('hello/world') == 'hello/world'
    assert d._fix_handler_path('/hello/world/') == 'hello/world'


class TestRestDecorator(unittest.TestCase):
    @patch('skygear.registry.Registry.register_handler')
    def test_register(self, mock):
        @d.rest('/hello/world', user_required=True)
        class HelloWorld:
            def handle_request(self, base_name, request):
                pass

        mock.assert_has_calls([
            call('hello/world/', ANY, method=ANY,
                 user_required=True),
            call('hello/world', ANY, method=ANY,
                 user_required=True),
            ])

        registered_func = mock.call_args[0][1]
        with patch.object(HelloWorld, 'handle_request') as handle_request:
            req = Request({})
            registered_func(req)
            handle_request.assert_called_with('/hello/world', req)


class TestStaticAssetsDecorator(unittest.TestCase):
    @patch('skygear.registry.Registry.register_static_assets')
    def test_register(self, mock):
        @d.static_assets('admin')
        def fn():
            return '/tmp/public'

        mock.assert_called_with('admin', ANY)
        loader = fn()
        assert isinstance(loader, DirectoryStaticAssetsLoader)
        assert loader.dirpath == '/tmp/public'

    @patch('skygear.registry.Registry.register_static_assets')
    def test_register_with_slash(self, mock):
        @d.static_assets('/admin')
        def fn():
            return '/tmp/public'

        mock.assert_called_with('admin', ANY)


class TestExceptionHandlerDecorator(unittest.TestCase):
    @patch('skygear.registry.Registry.register_exception_handler')
    def test_register(self, mock):
        class SomeException(Exception):
            pass

        @d.exception_handler(SomeException)
        def fn(exc):
            return exc

        mock.assert_called_with(SomeException, ANY)
        exc = fn(SomeException())
        assert isinstance(exc, SomeException)
