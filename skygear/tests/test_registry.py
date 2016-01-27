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
    def test_register_hook(eslf):
        def hook_func():
            pass

        registry = Registry()
        kwargs = {
                'type': 'note',
                'trigger': 'beforeSave',
                }
        registry.register('hook', 'hook_name', hook_func, **kwargs)

        func_map = registry.func_map['hook']
        assert len(func_map) == 1
        assert func_map['hook_name'] == hook_func

        param_map = registry.param_map['hook']
        assert len(param_map) == 1
        assert param_map[0]['name'] == 'hook_name'
        assert param_map[0]['type'] == 'note'
        assert param_map[0]['trigger'] == 'beforeSave'
