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
from unittest.mock import MagicMock, patch

from configargparse import Namespace

from .s3 import S3AssetSigner


class TestS3AssetSigner(unittest.TestCase):
    @property
    def mock_options(self):
        return Namespace(asset_store_access_key='mock_s3_access_key',
                         asset_store_secret_key='mock_s3_secret_key',
                         asset_store_region='mock-s3-region',
                         asset_store_bucket='mock-s3-bucket',
                         asset_store_s3_url_prefix=None,
                         asset_store_public=False)

    @patch('skygear.asset.s3.aws_client')
    def test_create(self, mock_aws_client):
        signer = S3AssetSigner.create(self.mock_options)
        assert signer.bucket == 'mock-s3-bucket'
        assert signer.region == 'mock-s3-region'
        assert signer.signature_required is True
        assert signer.url_prefix is None
        mock_aws_client.assert_called_once_with(
            's3',
            aws_access_key_id='mock_s3_access_key',
            aws_secret_access_key='mock_s3_secret_key',
            region_name='mock-s3-region')

    def test_create_fail(self):
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key=None,
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region='mock-s3-region',
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key=None,
                          asset_store_region='mock-s3-region',
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region=None,
                          asset_store_bucket='mock-s3-bucket',
                          asset_store_public=False))
        with self.assertRaises(Exception):
            S3AssetSigner.create(
                Namespace(asset_store_access_key='mock_s3_access_key',
                          asset_store_secret_key='mock_s3_secret_key',
                          asset_store_region='mock-s3-region',
                          asset_store_bucket=None,
                          asset_store_public=False))

    @patch('skygear.asset.s3.aws_client')
    def test_init(self, mock_aws_client):
        signer = S3AssetSigner(access_key='mock_s3_access_key',
                               access_secret='mock_s3_secret_key',
                               region='mock-s3-region',
                               bucket='mock-s3-bucket')
        assert signer.bucket == 'mock-s3-bucket'
        assert signer.region == 'mock-s3-region'
        assert signer.signature_required is True
        mock_aws_client.assert_called_once_with(
            's3',
            aws_access_key_id='mock_s3_access_key',
            aws_secret_access_key='mock_s3_secret_key',
            region_name='mock-s3-region')

    @patch('skygear.asset.s3.aws_client')
    def test_signing(self, mock_aws_client):
        mock_aws_client_instance = MagicMock()
        mock_aws_client.return_value = mock_aws_client_instance
        mock_aws_client_instance.generate_presigned_url.return_value = \
            'http://skygear.dev/signed_url'

        signer = S3AssetSigner.create(self.mock_options)
        assert signer.sign('index.html') == \
            mock_aws_client_instance.generate_presigned_url.return_value
        mock_aws_client_instance.generate_presigned_url.\
            assert_called_once_with('get_object',
                                    Params={
                                        'Bucket': 'mock-s3-bucket',
                                        'Key': 'index.html'
                                    },
                                    ExpiresIn=900)

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
