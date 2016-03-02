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
from unittest.mock import call, patch

from ..bin import load_source_or_exit


class TestLoadSource(unittest.TestCase):
    @patch('skygear.bin.SourceFileLoader')
    def test_load_specified_success(self, mocker):
        load_source_or_exit('something.py')
        mocker.assert_called_once_with('plugin', 'something.py')

    @patch('skygear.bin.SourceFileLoader')
    def test_load_specified_not_found(self, mocker):
        mocker.side_effect = FileNotFoundError
        with self.assertRaises(SystemExit):
            load_source_or_exit('something.py')
        mocker.assert_called_once_with('plugin', 'something.py')

    @patch('skygear.bin.SourceFileLoader')
    def test_load_unspecified_success(self, mocker):
        load_source_or_exit(None)
        mocker.assert_called_once_with('plugin', '__init__.py')

    @patch('skygear.bin.SourceFileLoader')
    def test_load_unspecified_not_found(self, mocker):
        mocker.side_effect = FileNotFoundError
        with self.assertRaises(SystemExit):
            load_source_or_exit(None)
        mocker.assert_has_calls([
            call('plugin', '__init__.py'),
            call('plugin', 'plugin.py'),
            ])
