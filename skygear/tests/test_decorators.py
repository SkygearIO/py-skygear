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
from unittest.mock import ANY, patch

from .. import decorators as d
from ..registry import Registry  # noqa


class TestHookDecorators(unittest.TestCase):
    @patch('skygear.registry.Registry.register')
    def test_before_save(self, mocker):
        @d.before_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')

    @patch('skygear.registry.Registry.register')
    def test_after_save(self, mocker):
        @d.after_save('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterSave')

    @patch('skygear.registry.Registry.register')
    def test_before_delete(self, mocker):
        @d.before_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeDelete')

    @patch('skygear.registry.Registry.register')
    def test_after_delete(self, mocker):
        @d.after_delete('note')
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='afterDelete')

    @patch('skygear.registry.Registry.register')
    def test_hook(self, mocker):
        @d.hook('beforeSave', type="note")
        def fn():
            pass
        mocker.assert_called_with(
            'hook',
            'skygear.tests.test_decorators.fn', ANY,
            type='note', trigger='beforeSave')
