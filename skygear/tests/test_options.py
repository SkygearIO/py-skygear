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

from ..options import _parse_load_modules_envvar


class TestParseLoadModules(unittest.TestCase):
    def test_colon(self):
        self.assertEqual(_parse_load_modules_envvar('a:b'), ['a', 'b'])

    def test_comma(self):
        self.assertEqual(_parse_load_modules_envvar('a,b'), ['a', 'b'])

    def test_space(self):
        self.assertEqual(_parse_load_modules_envvar('a b'), ['a', 'b'])

    def test_empty(self):
        self.assertEqual(_parse_load_modules_envvar(''), [])

    def test_ignore(self):
        self.assertEqual(_parse_load_modules_envvar('a~js,b,c~py'), ['b', 'c'])
