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
from unittest.mock import patch

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from .. import assets
from ..utils.assets import DictStaticAssetsLoader, DirectoryStaticAssetsLoader


class TestStaticAssetsCollector(unittest.TestCase):
    def setUp(self):
        self.dist = tempfile.mkdtemp()
        self.collector = assets.StaticAssetsCollector(self.dist)

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

            self.collector.collect('hello-world',
                                   DirectoryStaticAssetsLoader(tmp_dir))
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

            with self.assertRaises(assets.CollectorException):
                self.collector.collect('../hello-world',
                                       DirectoryStaticAssetsLoader(tmp_dir))
        finally:
            shutil.rmtree(tmp_dir)


class TestServeStaticAssets(unittest.TestCase):
    def setUp(self):
        assets = {
                'content/index.html': 'Hello World!'
                }
        self.loader = DictStaticAssetsLoader(assets)

    @patch('skygear.registry.Registry.get_static_assets')
    def test_response(self, mocker):
        mocker.return_value = (self.loader, 'content/index.html')
        builder = EnvironBuilder(method='GET',
                                 path='/static/myloader/content/index.html')
        request = Request(builder.get_environ())
        response = assets.serve_static_assets(request, '/static/')
        assert response.data == b'Hello World!'
        mocker.assert_called_once_with('myloader/content/index.html')
