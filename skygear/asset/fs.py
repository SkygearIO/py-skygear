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
from datetime import datetime

import configargparse as argparse

from .common import BaseAssetSigner


class FileSystemAssetSigner(BaseAssetSigner):
    def __init__(self, url_prefix: str, secret: str, public: bool = False):
        super().__init__(public)
        self.url_prefix = url_prefix
        self.secret = secret

    def sign(self, name: str) -> str:
        if not self.signature_required:
            return '{}/{}'.format(self.url_prefix, name)

        expired_at = datetime.now() + self.signature_expiry_duration
        expired_at_str = str(int(expired_at.timestamp()))

        hasher = hmac.new(self.secret.encode('utf-8'),
                          digestmod=hashlib.sha256)
        hasher.update(name.encode('utf-8'))
        hasher.update(expired_at_str.encode('utf-8'))

        signature = base64\
            .urlsafe_b64encode(hasher.digest())\
            .decode('utf-8')

        return '{}/{}?expiredAt={}&signature={}'.format(self.url_prefix,
                                                        name,
                                                        expired_at_str,
                                                        signature)

    @classmethod
    def create(cls, options: argparse.Namespace) -> BaseAssetSigner:
        url_prefix = options.asset_store_url_prefix
        if not url_prefix:
            raise Exception('Missing URL prefix of fs asset store')

        secret = options.asset_store_secret
        if not secret:
            raise Exception('Missing signing secret for fs asset store')

        return cls(url_prefix, secret, options.asset_store_public)
