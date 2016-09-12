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

from .. import importutil


class TestGuessPackageName(unittest.TestCase):
    def test_bare_init(self):
        assert importutil.guess_package_name('__init__.py') == 'plugin'

    def test_outside_relpath(self):
        with self.assertRaises(importutil.LoadException):
            importutil.guess_package_name('../__init__.py')

    def test_current_directory(self):
        assert importutil.guess_package_name('.') == 'plugin'

    @patch('os.path.isfile')
    def test_file_path_init(self, mocker):
        mocker.return_value = True
        assert importutil.guess_package_name('./abc/__init__.py') \
            == 'abc'

    @patch('os.path.isfile')
    def test_file_path_other(self, mocker):
        mocker.return_value = True
        assert importutil.guess_package_name('./abc/def.py') \
            == 'abc.def'

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    def test_dir_path(self, dirmocker, filemocker):
        filemocker.return_value = False
        dirmocker.return_value = True
        assert importutil.guess_package_name('./abc/def') \
            == 'abc.def'

    def test_non_existent_file(self):
        with self.assertRaises(importutil.LoadException):
            importutil.guess_package_name('./abc/non_existent.py')


class TestLoadModule(unittest.TestCase):
    def setUp(self):
        self.guess = patch('skygear.importutil.guess_package_name',
                           lambda p: 'guess_package_name')
        self.guess.start()

    def tearDown(self):
        self.guess.stop()

    @patch('skygear.importutil.SourceFileLoader')
    def test_load_module_file(self, mocker):
        with patch('os.path.isfile', lambda p: True):
            importutil.load_module('abc/__init__.py')
        mocker.assert_called_once_with('guess_package_name',
                                       'abc/__init__.py')

    @patch('skygear.importutil.SourceFileLoader')
    def test_load_module_dir(self, mocker):
        with patch('os.path.isdir', lambda p: True):
            importutil.load_module('abc/def')
        mocker.assert_called_once_with('guess_package_name',
                                       'abc/def/__init__.py')

    @patch('importlib.import_module')
    def test_load_module_package(self, mocker):
        importutil.load_module('abc.def')
        mocker.assert_called_once_with('abc.def')


class TestLoadDefaultModule(unittest.TestCase):
    @patch('skygear.importutil.SourceFileLoader')
    def test_load_success(self, mocker):
        importutil.load_default_module()
        mocker.assert_called_once_with('plugin', '__init__.py')

    @patch('skygear.importutil.SourceFileLoader')
    def test_load_not_found(self, mocker):
        mocker.side_effect = FileNotFoundError
        with self.assertRaises(importutil.LoadException):
            importutil.load_default_module()
        mocker.assert_has_calls([
            call('plugin', '__init__.py'),
            call('plugin', 'plugin.py'),
            ])


class TestLoadModules(unittest.TestCase):
    @patch('skygear.importutil.load_default_module')
    def test_empty(self, mocker):
        importutil.load_modules([])
        mocker.assert_called_once_with()

    @patch('skygear.importutil.load_module')
    def test_multiple(self, mocker):
        importutil.load_modules(['abc', 'def'])
        mocker.assert_has_calls([
            call('abc'),
            call('def'),
            ])
