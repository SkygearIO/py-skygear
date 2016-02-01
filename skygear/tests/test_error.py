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

from ..error import SkygearException


class TestSkygearException(unittest.TestCase):
    def test_from_dict(self):
        e = SkygearException.from_dict({
            'message': 'This is an error.',
            'code': 24601,
            'info': {'reason': 'unknown'},
            })
        assert e.message == 'This is an error.'
        assert e.code == 24601
        assert e.info == {'reason': 'unknown'}

    def test_as_dict(self):
        e = SkygearException('This is an error.', 24601, {'reason': 'unknown'})
        d = e.as_dict()
        assert d == {
            'message': 'This is an error.',
            'code': 24601,
            'info': {'reason': 'unknown'},
            }
