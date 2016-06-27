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
import os.path
import unittest

from .. import assets as assetsutils


class StaticAssetsHelperFunction(unittest.TestCase):
    def test_directory_assets(self):
        assert assetsutils.directory_assets('hello-world') == \
            os.path.abspath('hello-world')

    def test_relative_assets(self):
        expected = os.path.join(os.path.dirname(__file__), 'hello-world')
        assert assetsutils.relative_assets('hello-world') == \
            os.path.abspath(expected)
