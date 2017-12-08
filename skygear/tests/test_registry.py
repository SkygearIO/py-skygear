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

from ..registry import Registry


class TestRegistry(unittest.TestCase):
    def test_register_handler(self):
        def handler():
            pass

        kwargs = {
            'method': ['GET', 'POST'],
            'key_required': True,
            'user_required': True,
        }
        registry = Registry()
        registry.register_handler('plugin:handler', handler, **kwargs)

        assert len(registry.handler) == 1
        assert registry.get_handler('plugin:handler', 'GET') == handler
        assert registry.get_handler('plugin:handler', 'POST') == handler
        assert registry.get_handler('plugin:handler', 'PUT') is None

        param_map = registry.param_map['handler']
        assert len(param_map) == 2
        assert param_map[0]['name'] == 'plugin:handler'
        assert 'GET' in param_map[0]['methods']
        assert param_map[0]['key_required'] is True
        assert param_map[0]['user_required'] is True
        assert param_map[1]['name'] == 'plugin:handler'
        assert 'POST' in param_map[1]['methods']
        assert param_map[1]['key_required'] is True
        assert param_map[1]['user_required'] is True

    def test_register_handler_with_different_method(self):
        def handler1():
            pass

        def handler2():
            pass

        def handler3():
            pass

        registry = Registry()
        registry.register_handler('plugin:handler', handler1,
                                  method=['GET', 'POST'])
        registry.register_handler('plugin:handler', handler2, method='POST')
        registry.register_handler('plugin:handler3', handler3, method='POST')

        assert len(registry.handler) == 2
        assert registry.get_handler('plugin:handler', 'GET') == handler1
        assert registry.get_handler('plugin:handler', 'POST') == handler2
        assert registry.get_handler('plugin:handler', 'PUT') is None
        assert registry.get_handler('plugin:handler3', 'POST') == handler3

        param_map = registry.param_map['handler']
        assert len(param_map) == 3
        assert param_map[0]['name'] == 'plugin:handler'
        assert param_map[0]['methods'] == ['GET']
        assert param_map[1]['name'] == 'plugin:handler'
        assert param_map[1]['methods'] == ['POST']
        assert param_map[2]['name'] == 'plugin:handler3'
        assert param_map[2]['methods'] == ['POST']

    def test_register_handler_twice(self):
        def handler1():
            pass

        def handler2():
            pass

        kwargs = {
            'method': ['GET', 'POST'],
            'key_required': True,
            'user_required': True,
        }
        registry = Registry()
        registry.register_handler('plugin:handler', handler1, **kwargs)
        registry.register_handler('plugin:handler', handler2, **kwargs)

        assert len(registry.handler) == 1
        assert registry.get_handler('plugin:handler', 'GET') == handler2
        assert registry.get_handler('plugin:handler', 'POST') == handler2
        assert registry.get_handler('plugin:handler', 'PUT') is None

        param_map = registry.param_map['handler']
        assert len(param_map) == 2
        assert param_map[0]['name'] == 'plugin:handler'
        assert 'GET' in param_map[0]['methods']
        assert param_map[0]['key_required'] is True
        assert param_map[0]['user_required'] is True

    def test_register_handler_with_one_str_method(self):
        def handler():
            pass

        kwargs = {
            'method': 'PUT',
        }
        registry = Registry()
        registry.register_handler('plugin:handler', handler, **kwargs)

        assert len(registry.handler) == 1
        assert registry.get_handler('plugin:handler', 'GET') is None
        assert registry.get_handler('plugin:handler', 'POST') is None
        assert registry.get_handler('plugin:handler', 'PUT') == handler

        param_map = registry.param_map['handler']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'plugin:handler'
        assert 'PUT' in param_map[0]['methods']
        assert param_map[0]['key_required'] is False
        assert param_map[0]['user_required'] is False

    def test_register_op(self):
        def fn():
            pass

        kwargs = {
                'key_required': True,
                'user_required': True,
                }
        registry = Registry()
        registry.register_op('plugin:action', fn, **kwargs)

        func_map = registry.func_map['op']
        assert len(func_map) == 1
        assert func_map['plugin:action'] == fn

        param_map = registry.param_map['op']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'plugin:action'
        assert param_map[0]['key_required'] is True
        assert param_map[0]['user_required'] is True

    def test_register_event(self):
        def fn():
            pass

        registry = Registry()
        registry.register_event('plugin:event:foo', fn)

        func_map = registry.func_map['event']
        assert len(func_map) == 1
        assert func_map['plugin:event:foo'] == fn

        param_map = registry.param_map['event']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'plugin:event:foo'

    def test_register_hook(self):
        def fn():
            pass

        kwargs = {
                'type': 'note',
                'trigger': 'beforeSave',
                }
        registry = Registry()
        registry.register_hook('hook_name', fn, **kwargs)

        func_map = registry.func_map['hook']
        assert len(func_map) == 1
        assert func_map['hook_name'] == fn

        param_map = registry.param_map['hook']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'hook_name'
        assert param_map[0]['type'] == 'note'
        assert param_map[0]['trigger'] == 'beforeSave'

    def test_register_hook_twice(self):
        def fn1():
            pass

        def fn2():
            pass

        kwargs = {
                'type': 'note',
                'trigger': 'beforeSave',
                }
        registry = Registry()
        registry.register_hook('hook_name', fn1, **kwargs)
        registry.register_hook('hook_name', fn2, **kwargs)

        func_map = registry.func_map['hook']
        assert len(func_map) == 1
        assert func_map['hook_name'] == fn2

        param_map = registry.param_map['hook']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'hook_name'
        assert param_map[0]['type'] == 'note'
        assert param_map[0]['trigger'] == 'beforeSave'

    def test_register_timer(self):
        def fn():
            pass

        registry = Registry()
        registry.register_timer('timer_name', fn)

        func_map = registry.func_map['timer']
        assert len(func_map) == 1
        assert func_map['timer_name'] == fn

        param_map = registry.param_map['timer']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'timer_name'

    def test_register_timer_twice(self):
        def fn1():
            pass

        def fn2():
            pass

        registry = Registry()
        registry.register_timer('timer_name', fn1)
        registry.register_timer('timer_name', fn2)

        func_map = registry.func_map['timer']
        assert len(func_map) == 1
        assert func_map['timer_name'] == fn2

        param_map = registry.param_map['timer']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'timer_name'

    def test_register_provider(self):
        def fn():
            pass

        class Provider():
            pass

        the_provider = Provider()
        registry = Registry()
        registry.register_provider('example', 'com.example', the_provider)

        assert len(registry.providers) == 1
        assert registry.providers['com.example'] == the_provider

        param_map = registry.param_map['provider']
        assert len(param_map) == 1
        assert param_map[0]['type'] == 'example'
        assert param_map[0]['id'] == 'com.example'

    def test_register_static_assets(self):
        def fn():
            pass

        registry = Registry()
        registry.register_static_assets('admin', fn)

        assert len(registry.static_assets) == 1
        assert registry.static_assets['admin'] == fn

    def test_get_static_assets(self):
        class Loader:
            pass

        loader = Loader()

        def fn():
            return loader

        registry = Registry()
        registry.static_assets['admin'] = fn
        got_loader, subpath = registry.get_static_assets('admin/apple/pie')

        assert got_loader is loader
        assert subpath == '/apple/pie'

    def test_get_static_assets_with_traling(self):
        class Loader:
            pass

        loader = Loader()

        def fn():
            return loader

        registry = Registry()
        registry.static_assets['admin/'] = fn
        got_loader, subpath = registry.get_static_assets('admin/apple/pie')

        assert got_loader is loader
        assert subpath == 'apple/pie'

    def test_register_exception_handler(self):
        def fn(exc):
            pass

        registry = Registry()
        registry.register_exception_handler(Exception, fn)

        assert len(registry.exception_handlers) == 1
        assert registry.exception_handlers[Exception] == fn

    def test_get_exception_handler(self):
        class SomeException(Exception):
            pass

        def fn(exc):
            return exc

        registry = Registry()
        registry.exception_handlers[Exception] = fn
        handler = registry.get_exception_handler(SomeException)

        assert handler is fn

    def test_register_lambda(self):
        def fn():
            return True

        registry = Registry()
        registry.register_op('plugin:action', fn, key_required=True)
        assert registry.func_map['op']['plugin:action'] == fn
        assert registry.param_map['op'][0]['key_required'] is True

    def test_register_lambda_twice(self):
        def fn1():
            return True

        def fn2():
            return False

        registry = Registry()
        registry.register_op('plugin:action', fn1, key_required=True)
        registry.register_op('plugin:action', fn2, key_required=False)

        assert len(registry.func_map['op']) == 1
        assert registry.func_map['op']['plugin:action'] == fn2
        assert len(registry.param_map['op']) == 1
        assert registry.param_map['op'][0]['key_required'] is False
