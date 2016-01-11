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

from skygear.utils import context as ctx


class TestContextFunctions(unittest.TestCase):
    def tearDown(self):
        ctx.clear_contexts()

    def test_start_context(self):
        with ctx.start_context({'hello': 'world'}):
            assert ctx.current_context()['hello'] == 'world'
        assert ctx.current_context().get('hello', None) is None

    def test_push_context(self):
        ctx.push_context({'hello': 'world'})
        assert ctx.current_context()['hello'] == 'world'

    def test_pop_context(self):
        ctx.push_context({'hello': 'world'})
        ctx.pop_context()
        assert ctx.current_context().get('hello', None) is None

    def test_pop_context_top(self):
        with self.assertRaises(Exception):
            ctx.pop_context()

    def test_current_user_id(self):
        ctx.push_context({'user_id': '42'})
        assert ctx.current_user_id()
