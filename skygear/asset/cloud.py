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

import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from json.decoder import JSONDecoder
from urllib.parse import quote as percent_encode

import configargparse as argparse
from requests import request
from strict_rfc3339 import InvalidRFC3339Error, rfc3339_to_timestamp

from .common import BaseAssetSigner


class CloudAssetSignerToken:
    def __init__(self, value: str, expired_at: datetime, extra: str = ''):
        self._value = value
        self._expired_at = expired_at
        self._extra = extra

    @property
    def value(self) -> str:
        return self._value

    @property
    def expired_at(self) -> datetime:
        return self._expired_at

    @property
    def extra(self) -> str:
        return self._extra

    def expired(self) -> bool:
        expiry_duration = datetime.now() - self.expired_at
        return expiry_duration.total_seconds() > 0

    @classmethod
    def create(cls, info: dict) -> object:
        value = info.get('value')
        if not value:
            raise Exception('Missing signer token value for cloud asset')

        expired_at_str = info.get('expired_at')
        if not expired_at_str:
            raise Exception('Missing expiry time for cloud asset signer token')

        expire_timestamp = None
        try:
            expire_timestamp = rfc3339_to_timestamp(expired_at_str)
        except InvalidRFC3339Error as ex:
            raise Exception(
                'Invalid format of expiry time for cloud asset signer token')

        return cls(value,
                   datetime.fromtimestamp(expire_timestamp),
                   info.get('extra'))


class CloudAssetSigner(BaseAssetSigner):
    def __init__(self, app_name: str, host: str, token: str,
                 url_prefix: str, public: bool = False):
        super().__init__(public)
        self.app_name = app_name
        self.host = host
        self.token = token
        self.url_prefix = url_prefix
        self.signer_token = None
        self.refresh_signer_token()

    @property
    def signer_token_expiry_duration(self):
        return timedelta(hours=2)

    def available(self) -> bool:
        return self.signer_token and not self.signer_token.expired()

    def refresh_signer_token(self):
        url = "{}/token/{}".format(self.host, self.app_name)
        authorization_token = 'Bearer {}'.format(self.token)
        expired_at = datetime.now() + self.signer_token_expiry_duration
        expired_at_str = str(int(expired_at.timestamp()))
        resp = request('GET', url,
                       headers={'Authorization': authorization_token},
                       params={'expired_at': expired_at_str})

        resp_dict = None
        try:
            resp_dict = JSONDecoder().decode(resp.text)
        except Exception as ex:
            raise Exception(
                'Fail to decode the response from cloud asset')

        resp_err = resp_dict.get('Error')
        if resp_err:
            raise Exception('Fail to get the signer token')

        self.signer_token = CloudAssetSignerToken.create(resp_dict)

    def sign(self, name: str) -> str:
        if not self.available():
            self.refresh_signer_token()

        url = '/'.join([self.url_prefix, self.app_name, name])
        if not self.signature_required:
            return url

        expired_at = datetime.now() + self.signature_expiry_duration
        expired_at_str = str(int(expired_at.timestamp()))

        hasher = hmac.new(self.signer_token.value.encode('utf-8'),
                          digestmod=hashlib.sha256)
        for each_info in [self.app_name, name, expired_at_str,
                          self.signer_token.extra]:
            hasher.update(each_info.encode('utf-8'))

        # use standard_b64encode instead of urlsafe_b64encode following
        # the implementation of cloud asset
        signature = base64\
            .standard_b64encode(hasher.digest())\
            .decode('utf-8')
        signature_and_extra = percent_encode(
            '{}.{}'.format(signature, self.signer_token.extra))

        return '{}?expired_at={}&signature={}'.format(url, expired_at_str,
                                                      signature_and_extra)

    @classmethod
    def create(cls, options: argparse.Namespace) -> BaseAssetSigner:
        app_name = options.appname
        if not app_name:
            raise Exception('Missing app name')

        host = options.cloud_asset_host
        if not host:
            raise Exception('Missing host for cloud asset store')

        token = options.cloud_asset_token
        if not token:
            raise Exception('Missing token for cloud asset store')

        public = options.asset_store_public
        url_prefix = options.cloud_asset_public_prefix if public else \
            options.cloud_asset_private_prefix

        if not url_prefix:
            raise Exception('Missing url prefix for cloud asset')

        return cls(app_name, host, token, url_prefix, public)
