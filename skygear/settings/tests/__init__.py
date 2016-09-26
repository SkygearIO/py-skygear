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

from .. import add_parser, parse_all, settings, _parsers
from ..parser import SettingsParser


class TestHelper(unittest.TestCase):
    @patch.dict(_parsers)
    def test_add(self):
        parser = SettingsParser("PARSER_PREFIX")
        add_parser('example', parser, parse_now=False)
        assert _parsers['example'] is parser

    @patch.dict(_parsers)
    @patch.dict(settings)
    @patch.dict(os.environ, {'TEST_VAR': 'yes'})
    def test_add_parse_now(self):
        parser = SettingsParser("PARSER_PREFIX")
        parser.add_setting('test_var')
        add_parser('example', parser)
        assert settings.example.test_var == 'yes'

    @patch.dict(_parsers)
    @patch.dict(settings)
    @patch.dict(os.environ, {'TEST_VAR': 'yes'})
    def test_add_parse_all(self):
        parser = SettingsParser("PARSER_PREFIX")
        add_parser('example', parser, parse_now=False)
        parse_all()
        assert settings.example.test_var == 'yes'
