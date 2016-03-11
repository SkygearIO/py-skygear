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
        registry.register('handler', 'plugin:handler', handler, **kwargs)

        assert len(registry.handler) == 1
        assert registry.get_handler('plugin:handler', 'GET') == handler
        assert registry.get_handler('plugin:handler', 'POST') == handler
        assert registry.get_handler('plugin:handler', 'PUT') is None

        param_map = registry.param_map['handler']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'plugin:handler'
        assert 'POST' in param_map[0]['methods']
        assert param_map[0]['key_required'] is True
        assert param_map[0]['user_required'] is True

    def test_register_handler_with_one_str_method(self):
        def handler():
            pass

        kwargs = {
            'method': 'PUT',
        }
        registry = Registry()
        registry.register('handler', 'plugin:handler', handler, **kwargs)

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
        registry.register('op', 'plugin:action', fn, **kwargs)

        func_map = registry.func_map['op']
        assert len(func_map) == 1
        assert func_map['plugin:action'] == fn

        param_map = registry.param_map['op']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'plugin:action'
        assert param_map[0]['auth_required'] is True
        assert param_map[0]['user_required'] is True

    def test_register_hook(self):
        def fn():
            pass

        kwargs = {
                'type': 'note',
                'trigger': 'beforeSave',
                }
        registry = Registry()
        registry.register('hook', 'hook_name', fn, **kwargs)

        func_map = registry.func_map['hook']
        assert len(func_map) == 1
        assert func_map['hook_name'] == fn

        param_map = registry.param_map['hook']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'hook_name'
        assert param_map[0]['type'] == 'note'
        assert param_map[0]['trigger'] == 'beforeSave'

    def test_register_timer(self):
        def fn():
            pass

        registry = Registry()
        registry.register('timer', 'timer_name', fn)

        func_map = registry.func_map['timer']
        assert len(func_map) == 1
        assert func_map['timer_name'] == fn

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
