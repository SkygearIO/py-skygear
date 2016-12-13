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

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from configargparse import Namespace
from strict_rfc3339 import timestamp_to_rfc3339_utcoffset

from .cloud import CloudAssetSigner, CloudAssetSignerToken


class TestCloudAssetSignerToken(unittest.TestCase):
    def test_create(self):
        info = {'value': 'mock-token-value',
                'expired_at': '2016-12-08T08:38:33Z',
                'extra': 'mock-token-extra'}
        token = CloudAssetSignerToken.create(info)
        assert token.value == 'mock-token-value'
        assert token.extra == 'mock-token-extra'
        assert token.expired_at == datetime.fromtimestamp(1481186313)

    def test_create_fail(self):
        with self.assertRaises(Exception):
            CloudAssetSignerToken.create({
                'expired_at': '2016-12-08T08:38:33Z',
                'extra': 'mock-token-extra'})

        with self.assertRaises(Exception):
            CloudAssetSignerToken.create({
                'value': 'mock-token-value',
                'extra': 'mock-token-extra'})

        with self.assertRaises(Exception):
            CloudAssetSignerToken.create({
                'value': 'mock-token-value',
                'expired_at': 'invalid-format',
                'extra': 'mock-token-extra'})

    def test_init(self):
        token = CloudAssetSignerToken('mock-token-value',
                                      datetime.fromtimestamp(1481186313),
                                      'mock-token-extra')
        assert token.value == 'mock-token-value'
        assert token.extra == 'mock-token-extra'
        assert token.expired_at == datetime.fromtimestamp(1481186313)

    def test_expiration(self):
        token1 = CloudAssetSignerToken('mock-token-value',
                                       datetime.now() + timedelta(minutes=10),
                                       'mock-token-extra')
        assert token1.expired() is False

        token2 = CloudAssetSignerToken('mock-token-value',
                                       datetime.now() - timedelta(minutes=10),
                                       'mock-token-extra')
        assert token2.expired() is True


class TestCloudAssetSigner(unittest.TestCase):
    def mock_options(self, public=False):
        return Namespace(
            appname='skygear-test',
            cloud_asset_host='http://mock-cloud-asset.dev',
            cloud_asset_token='mock-cloud-asset-token',
            cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
            cloud_asset_private_prefix='http://mock-cloud-asset.dev/private',
            asset_store_public=public)

    def setUp(self):
        self.request_patcher = patch('skygear.asset.cloud.request')
        self.mock_request = self.request_patcher.start()
        self.mock_request.return_value = MagicMock()
        self.mock_request.return_value.text = json.dumps({
            'value': 'mock-token-value',
            'expired_at': '2016-12-08T08:38:33Z',
            'extra': 'mock-token-extra'})

    def tearDown(self):
        self.request_patcher.stop()
        self.mock_request = None

    def test_create(self):
        signer1 = CloudAssetSigner.create(self.mock_options())
        assert signer1.app_name == 'skygear-test'
        assert signer1.host == 'http://mock-cloud-asset.dev'
        assert signer1.token == 'mock-cloud-asset-token'
        assert signer1.url_prefix == 'http://mock-cloud-asset.dev/private'
        assert signer1.signer_token.value == 'mock-token-value'
        assert signer1.signer_token.extra == 'mock-token-extra'
        assert signer1.signer_token.expired_at == \
            datetime.fromtimestamp(1481186313)

        signer2 = CloudAssetSigner.create(self.mock_options(public=True))
        assert signer2.app_name == 'skygear-test'
        assert signer2.host == 'http://mock-cloud-asset.dev'
        assert signer2.token == 'mock-cloud-asset-token'
        assert signer2.url_prefix == 'http://mock-cloud-asset.dev/public'
        assert signer2.signer_token.value == 'mock-token-value'
        assert signer2.signer_token.extra == 'mock-token-extra'
        assert signer2.signer_token.expired_at == \
            datetime.fromtimestamp(1481186313)

    def test_create_fail(self):
        with self.assertRaises(Exception):
            CloudAssetSigner.create(Namespace(
                appname=None,
                cloud_asset_host='http://mock-cloud-asset.dev',
                cloud_asset_token='mock-cloud-asset-token',
                cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
                cloud_asset_private_prefix=(
                    'http://mock-cloud-asset.dev/private'),
                asset_store_public=False))

        with self.assertRaises(Exception):
            CloudAssetSigner.create(Namespace(
                appname='skygear-test',
                cloud_asset_host=None,
                cloud_asset_token='mock-cloud-asset-token',
                cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
                cloud_asset_private_prefix=(
                    'http://mock-cloud-asset.dev/private'),
                asset_store_public=False))

        with self.assertRaises(Exception):
            CloudAssetSigner.create(Namespace(
                appname='skygear-test',
                cloud_asset_host='http://mock-cloud-asset.dev',
                cloud_asset_token=None,
                cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
                cloud_asset_private_prefix=(
                    'http://mock-cloud-asset.dev/private'),
                asset_store_public=False))

        with self.assertRaises(Exception):
            CloudAssetSigner.create(Namespace(
                appname='skygear-test',
                cloud_asset_host='http://mock-cloud-asset.dev',
                cloud_asset_token='mock-cloud-asset-token',
                cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
                cloud_asset_private_prefix=None,
                asset_store_public=False))

        with self.assertRaises(Exception):
            CloudAssetSigner.create(Namespace(
                appname='skygear-test',
                cloud_asset_host='http://mock-cloud-asset.dev',
                cloud_asset_token='mock-cloud-asset-token',
                cloud_asset_public_prefix=None,
                cloud_asset_private_prefix=(
                    'http://mock-cloud-asset.dev/private'),
                asset_store_public=True))

    def test_init(self):
        signer = CloudAssetSigner('skygear-test',
                                  'http://mock-cloud-asset.dev',
                                  'mock-cloud-asset-token',
                                  'http://mock-cloud-asset.dev/private')
        assert signer.app_name == 'skygear-test'
        assert signer.host == 'http://mock-cloud-asset.dev'
        assert signer.token == 'mock-cloud-asset-token'
        assert signer.url_prefix == 'http://mock-cloud-asset.dev/private'
        assert signer.signer_token.value == 'mock-token-value'
        assert signer.signer_token.extra == 'mock-token-extra'
        assert signer.signer_token.expired_at == \
            datetime.fromtimestamp(1481186313)

    def test_signer_availability(self):
        self.mock_request.return_value.text = json.dumps({
            'value': 'mock-token-value',
            'expired_at': timestamp_to_rfc3339_utcoffset(
                (datetime.now() + timedelta(minutes=10)).timestamp()),
            'extra': 'mock-token-extra'
            })
        signer1 = CloudAssetSigner.create(self.mock_options())
        assert signer1.available() is True

        self.mock_request.return_value.text = json.dumps({
            'value': 'mock-token-value',
            'expired_at': timestamp_to_rfc3339_utcoffset(
                (datetime.now() - timedelta(minutes=10)).timestamp()),
            'extra': 'mock-token-extra'
            })
        signer2 = CloudAssetSigner.create(self.mock_options())
        assert signer2.available() is False

    @patch('skygear.asset.cloud.datetime')
    def test_refresh_signer_token(self, mock_datetime):
        fixed_now = datetime.now()
        mock_datetime.now.return_value = fixed_now
        CloudAssetSigner.create(self.mock_options())
        self.mock_request.assert_called_once_with(
            'GET', 'http://mock-cloud-asset.dev/token/skygear-test',
            headers={'Authorization': 'Bearer mock-cloud-asset-token'},
            params={
                'expired_at':
                    str(int((fixed_now + timedelta(hours=2)).timestamp()))
            })

    def test_refresh_signer_token_fail(self):
        self.mock_request.return_value.text = json.dumps({
                'Error': 'Testing Error'
            })
        with self.assertRaises(Exception):
            CloudAssetSigner.create(self.mock_options())

    @patch('skygear.asset.cloud.datetime')
    @patch('skygear.asset.cloud.CloudAssetSignerToken.expired',
           Mock(return_value=True))
    def test_sign(self, mock_datetime):
        mock_datetime.now.return_value = datetime.fromtimestamp(1481095934)
        signer = CloudAssetSigner.create(self.mock_options())
        assert signer.sign('index.html') == (
            'http://mock-cloud-asset.dev/private/skygear-test/index.html'
            '?expired_at=1481096834'
            '&signature=peQtnmSFdoQWtFAk3cwLkM3lUspBkIhl5SPlR5hjFm4%3D'
            '.mock-token-extra')

    def test_sign_public(self):
        signer = CloudAssetSigner.create(Namespace(
            appname='skygear-test',
            cloud_asset_host='http://mock-cloud-asset.dev',
            cloud_asset_token='mock-cloud-asset-token',
            cloud_asset_public_prefix='http://mock-cloud-asset.dev/public',
            cloud_asset_private_prefix='http://mock-cloud-asset.dev/private',
            asset_store_public=True))
        assert signer.sign('index.html') == \
            'http://mock-cloud-asset.dev/public/skygear-test/index.html'
