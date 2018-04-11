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
from unittest.mock import MagicMock, Mock, patch

from configargparse import Namespace

from .s3 import S3AssetSigner


class TestS3AssetSigner(unittest.TestCase):
    @property
    def mock_options(self):
        return Namespace(asset_store_access_key='mock_s3_access_key',
                         asset_store_secret_key='mock_s3_secret_key',
                         asset_store_region='ap-southeast-1',
                         asset_store_bucket='mock-s3-bucket',
                         asset_store_s3_url_prefix=None,
                         asset_store_public=False,
                         asset_store_presign_expiry=120*60,
                         asset_store_presign_interval=60*60)

    @patch('skygear.asset.s3.Minio')
    def test_create(self, mock_client):
        signer = S3AssetSigner.create(self.mock_options)
        assert signer.bucket == 'mock-s3-bucket'
        assert signer.region == 'ap-southeast-1'
        assert signer.signature_required is True
        assert signer.url_prefix is None
        assert signer.presign_expiry == timedelta(seconds=120*60)
        assert signer.presign_interval == timedelta(seconds=60*60)
        mock_client.assert_called_once_with(
            's3.amazonaws.com',
            region='ap-southeast-1',
            access_key='mock_s3_access_key',
            secret_key='mock_s3_secret_key')

    def test_create_fail(self):
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key=None,
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region='ap-southeast-1',
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key=None,
                          asset_store_region='ap-southeast-1',
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region=None,
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region='ap-southeast-1',
                          asset_store_bucket=None,
                          asset_store_public=False,
                          asset_store_presign_expiry=120*60,
                          asset_store_presign_interval=60*60))

    @patch('skygear.asset.s3.Minio')
    def test_init(self, mock_client):
        signer = S3AssetSigner(access_key='mock_s3_access_key',
                               access_secret='mock_s3_secret_key',
                               region='ap-southeast-1',
                               bucket='mock-s3-bucket',
                               presign_expiry=120*60,
                               presign_interval=60*60)
        assert signer.bucket == 'mock-s3-bucket'
        assert signer.region == 'ap-southeast-1'
        assert signer.signature_required is True
        assert signer.presign_expiry == timedelta(seconds=120*60)
        assert signer.presign_interval == timedelta(seconds=60*60)
        mock_client.assert_called_once_with(
            's3.amazonaws.com',
            region='ap-southeast-1',
            access_key='mock_s3_access_key',
            secret_key='mock_s3_secret_key')

    @patch('skygear.asset.common.time.time',
           Mock(return_value=1481095934.0))
    @patch('skygear.asset.s3.Minio')
    def test_signing(self, mock_client):
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.presigned_get_object.return_value = \
            'http://skygear.dev/signed_url'

        signer = S3AssetSigner.create(self.mock_options)
        assert signer.sign('index.html') == \
            mock_client_instance.presigned_get_object.return_value

        response_headers = {
            'X-Amz-Date': '20161207T070000Z'
        }
        mock_client_instance.presigned_get_object.\
            assert_called_once_with('mock-s3-bucket',
                                    'index.html',
                                    expires=timedelta(seconds=120*60),
                                    response_headers=response_headers)

    def test_signing_public(self):
        options = self.mock_options
        options.asset_store_public = True
        signer = S3AssetSigner.create(options)
        assert signer.sign('index.html') == (
            'https://s3-mock-s3-region.amazonaws.com/'
            'mock-s3-bucket/index.html')

    def test_signing_public_with_url_prefix(self):
        options = self.mock_options
        options.asset_store_public = True
        options.asset_store_s3_url_prefix = 'http://skygear.dev'
        signer = S3AssetSigner.create(options)
        assert signer.sign('index.html') == 'http://skygear.dev/index.html'
