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
from datetime import datetime
from unittest.mock import patch

from configargparse import Namespace

from .fs import FileSystemAssetSigner


class TestFileSystemAssetSigner(unittest.TestCase):
    @property
    def mock_options(self):
        return Namespace(asset_store_url_prefix='http://skygear.dev/files',
                         asset_store_secret='asset_secret',
                         asset_store_public=False)

    def test_create(self):
        signer = FileSystemAssetSigner.create(self.mock_options)
        assert signer.url_prefix == 'http://skygear.dev/files'
        assert signer.secret == 'asset_secret'
        assert signer.signature_required is True

    def test_create_fail(self):
        with self.assertRaises(Exception):
            FileSystemAssetSigner.create(
                Namespace(asset_store_url_prefix=None,
                          asset_store_secret='asset_secret',
                          asset_store_public=False))
        with self.assertRaises(Exception):
            FileSystemAssetSigner.create(
                Namespace(asset_store_url_prefix='http://skygear.dev/files',
                          asset_store_secret=None,
                          asset_store_public=False))

    def test_init(self):
        signer = FileSystemAssetSigner(url_prefix='http://skygear.dev/files',
                                       secret='asset_secret')
        assert signer.url_prefix == 'http://skygear.dev/files'
        assert signer.secret == 'asset_secret'
        assert signer.signature_required is True

    @patch('skygear.asset.fs.datetime')
    def test_signing(self, mock_datetime):
        mock_datetime.now.return_value = datetime.fromtimestamp(1481095934)
        signer = FileSystemAssetSigner.create(self.mock_options)
        assert signer.sign('index.html') == (
            'http://skygear.dev/files/index.html'
            '?expiredAt=1481096834'
            '&signature=R5kMq2neUkCGBjQD6zSv99PajRvI0EqMesuRHQS4hNA=')

    def test_signing_public(self):
        options = self.mock_options
        options.asset_store_public = True
        signer = FileSystemAssetSigner.create(options)
        assert signer.sign('index.html') \
            == 'http://skygear.dev/files/index.html'
