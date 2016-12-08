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

from ..error import InvalidArgument, ResourceNotFound, SkygearException
from .common import CommonAssetSigner


class CloudAssetSignerToken:
    @classmethod
    def create(cls, info: dict) -> object:
        value = info.get('value')
        if not value:
            raise SkygearException(
                'Missing signer token value for cloud asset',
                code=ResourceNotFound)

        expired_at_str = info.get('expired_at')
        if not expired_at_str:
            raise SkygearException(
                'Missing expiry time for cloud asset signer token',
                code=ResourceNotFound)

        expire_timestamp = None
        try:
            expire_timestamp = rfc3339_to_timestamp(expired_at_str)
        except InvalidRFC3339Error as ex:
            raise SkygearException(
                'Invalid format of expiry time for cloud asset signer token',
                code=ResourceNotFound,
                info={'error': str(ex), 'value': expired_at_str})

        return cls(value,
                   datetime.fromtimestamp(expire_timestamp),
                   info.get('extra'))

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


class CloudAssetSigner(CommonAssetSigner):
    @classmethod
    def create(cls, options: argparse.Namespace) -> CommonAssetSigner:
        app_name = options.appname
        if not app_name:
            raise SkygearException('Missing app name', code=InvalidArgument)

        host = options.cloud_asset_host
        if not host:
            raise SkygearException('Missing host for cloud asset store',
                                   code=InvalidArgument)

        token = options.cloud_asset_token
        if not token:
            raise SkygearException('Missing token for cloud asset store',
                                   code=InvalidArgument)

        public = options.asset_store_public
        url_prefix = options.cloud_asset_public_prefix if public else \
            options.cloud_asset_private_prefix

        if not url_prefix:
            raise SkygearException('Missing url prefix for cloud asset',
                                   code=InvalidArgument)

        return cls(app_name, host, token, url_prefix, public)

    def __init__(self, app_name: str, host: str, token: str,
                 url_prefix: str, public: bool = False):
        super().__init__(public)
        self.app_name = app_name
        self.host = host
        self.token = token
        self.url_prefix = url_prefix
        self.signer_token = None
        self.request_signer_token()

    @property
    def signer_token_expiry_duration(self):
        return timedelta(hours=2)

    def available(self) -> bool:
        return self.signer_token and not self.signer_token.expired()

    def request_signer_token(self):
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
            raise SkygearException(
                'Fail to decode the response from cloud asset')

        resp_err = resp_dict.get('Error')
        if resp_err:
            raise SkygearException('Fail to get the signer token',
                                   code=ResourceNotFound,
                                   info={'error': resp_err})

        self.signer_token = CloudAssetSignerToken.create(resp_dict)

    def sign(self, name: str) -> str:
        url = '/'.join([self.url_prefix, self.app_name, name])
        if not self.signature_required():
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
