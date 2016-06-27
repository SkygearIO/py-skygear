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


class StaticAssetsHelperFunction(unittest.TestCase):
    def test_directory_assets(self):
        loader = assetsutils.directory_assets('hello-world')
        assert isinstance(loader, assetsutils.StaticAssetsLoader)
        assert loader.dirpath == os.path.abspath('hello-world')

    def test_relative_assets(self):
        loader = assetsutils.relative_assets('hello-world')
        assert isinstance(loader, assetsutils.StaticAssetsLoader)
        expected = os.path.join(os.path.dirname(__file__), 'hello-world')
        assert loader.dirpath == os.path.abspath(expected)

    def test_package_assets(self):
        loader = assetsutils.package_assets(__name__, 'assets')
        assert isinstance(loader, assetsutils.PackageStaticAssetsLoader)


class TestPackageStaticAssetsLoader(unittest.TestCase):
    def setUp(self):
        self.loader = assetsutils.PackageStaticAssetsLoader(__name__, 'assets')
        self.dist = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.dist):
            shutil.rmtree(self.dist)

    def test_get_asset(self):
        content = self.loader.get_asset('content/index.txt')
        assert content.startswith(b'Hello World!')

    def test_copy_into(self):
        self.loader.copy_into(self.dist)
        with open(os.path.join(self.dist, 'content/index.txt'), 'rb') as f:
            assert f.read().startswith(b'Hello World!')

    def test_exists_asset(self):
        assert self.loader.exists_asset('content/index.txt') is True

    def test_exists_asset_nonexistent(self):
        assert self.loader.exists_asset('non-existent') is False
