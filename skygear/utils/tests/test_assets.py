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
import shutil
import tempfile
import unittest

from .. import assets as assetsutils


class TestStaticAssetsCollector(unittest.TestCase):
    def setUp(self):
        self.dist = tempfile.mkdtemp()
        self.collector = assetsutils.StaticAssetsCollector(self.dist)

    def tearDown(self):
        if os.path.exists(self.dist):
            shutil.rmtree(self.dist)

    def test_clean(self):
        self.collector.clean()
        assert os.path.exists(self.dist) is False

    def test_collect(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp_dir, 'index.txt'), 'w') as f:
                f.write('Hello World!')

            self.collector.collect('hello-world', tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)

        collected_path = os.path.join(self.collector.base_path,
                                      'hello-world',
                                      'index.txt')
        with open(collected_path, 'r') as f:
            assert f.read() == 'Hello World!'

    def test_collect_incorrect_prefix(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp_dir, 'index.txt'), 'w') as f:
                f.write('Hello World!')

            with self.assertRaises(assetsutils.CollectorException):
                self.collector.collect('../hello-world', tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)


class StaticAssetsHelperFunction(unittest.TestCase):
    def test_directory_assets(self):
        assert assetsutils.directory_assets('hello-world') == \
            os.path.abspath('hello-world')

    def test_relative_assets(self):
        expected = os.path.join(os.path.dirname(__file__), 'hello-world')
        assert assetsutils.relative_assets('hello-world') == \
            os.path.abspath(expected)
