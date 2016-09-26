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
import os
import unittest
from unittest.mock import patch

from .. import Namespace, SettingsParser


class TestSettingsParser(unittest.TestCase):
    def setUp(self):
        self.parser = SettingsParser('PARSER_PREFIX')

    def tearDown(self):
        self.parser = None

    @patch.dict(os.environ, {'TEST_VAR': 'yes'})
    def test_var(self):
        self.parser.add_setting('test_var')
        assert self.parser.parse_settings().test_var == 'yes'

    def test_var_with_default(self):
        self.parser.add_setting('test_var', default='yes')
        assert self.parser.parse_settings().test_var == 'yes'

    def test_var_unspecified(self):
        self.parser.add_setting('test_var')
        with self.assertRaises(Exception):
            self.parser.parse_settings().test_var

    def test_var_unspecified_ignored(self):
        self.parser.add_setting('test_var', required=False)
        assert self.parser.parse_settings().test_var is None

    @patch.dict(os.environ, {'ANOTHER_VAR': 'yes'})
    def test_var_explicit(self):
        self.parser.add_setting('test_var', env_var='ANOTHER_VAR')
        assert self.parser.parse_settings().test_var == 'yes'

    @patch.dict(os.environ, {'PARSER_PREFIX_TEST_VAR': 'no',
                             'TEST_VAR': 'yes'})
    def test_var_correct_resolve(self):
        self.parser.add_setting('test_var')
        assert self.parser.parse_settings().test_var == 'no'

    @patch.dict(os.environ, {'TEST_VAR': 'yes'})
    def test_var_unresolved(self):
        self.parser.add_setting('test_var', resolve=False)
        with self.assertRaises(Exception):
            self.parser.parse_settings().test_var

    @patch.dict(os.environ, {'TEST_VAR': '42'})
    def test_var_int(self):
        self.parser.add_setting('test_var', atype=int)
        assert self.parser.parse_settings().test_var == 42

    def test_var_existing_namespace(self):
        self.parser.add_setting('test_var', default='yes')
        ns = Namespace()
        setattr(ns, 'existing', 'no')
        assert self.parser.parse_settings(ns) is ns
        assert ns.existing == 'no'
        assert ns.test_var == 'yes'
