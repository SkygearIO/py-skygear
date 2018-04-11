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
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from configargparse import Namespace

from .fs import FileSystemAssetSigner


class TestFileSystemAssetSigner(unittest.TestCase):
    @property
    def mock_options(self):
        return Namespace(asset_store_url_prefix='http://skygear.dev/files',
                         asset_store_secret='asset_secret',
                         asset_store_public=False,
                         asset_store_presign_expiry=120*60,
                         asset_store_presign_interval=60*60)

    def test_create(self):
        signer = FileSystemAssetSigner.create(self.mock_options)
        assert signer.url_prefix == 'http://skygear.dev/files'
        assert signer.secret == 'asset_secret'
        assert signer.signature_required is True
        assert signer.presign_expiry == timedelta(seconds=120*60)
        assert signer.presign_interval == timedelta(seconds=60*60)

    def test_create_fail(self):
        with self.assertRaises(Exception):
            FileSystemAssetSigner.create(
                Namespace(asset_store_url_prefix=None,
                          asset_store_secret='asset_secret',
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))
        with self.assertRaises(Exception):
            FileSystemAssetSigner.create(
                Namespace(asset_store_url_prefix='http://skygear.dev/files',
                          asset_store_secret=None,
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))

    def test_init(self):
        signer = FileSystemAssetSigner(url_prefix='http://skygear.dev/files',
                                       secret='asset_secret',
                                       presign_expiry=120*60,
                                       presign_interval=60*60)
        assert signer.url_prefix == 'http://skygear.dev/files'
        assert signer.secret == 'asset_secret'
        assert signer.signature_required is True
        assert signer.presign_expiry == timedelta(seconds=120*60)
        assert signer.presign_interval == timedelta(seconds=60*60)

    @patch('skygear.asset.common.time.time',
           Mock(return_value=1481095934.0))
    def test_signing(self):
        signer = FileSystemAssetSigner.create(self.mock_options)
        assert signer.sign('index.html') == (
            'http://skygear.dev/files/index.html'
            '?expiredAt=1481072400'
            '&signature=gHLJXBvAu0bljii8xsfctqaFvuTH0v7snQrAyBTTAxA=')

    def test_signing_public(self):
        options = self.mock_options
        options.asset_store_public = True
        signer = FileSystemAssetSigner.create(options)
        assert signer.sign('index.html') \
            == 'http://skygear.dev/files/index.html'
