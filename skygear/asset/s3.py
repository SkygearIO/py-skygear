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

import configargparse as argparse
from boto3 import client as aws_client

from .common import BaseAssetSigner


class S3AssetSigner(BaseAssetSigner):
    def __init__(self, access_key: str, access_secret: str,
                 region: str, bucket: str,
                 url_prefix: str = None, public: bool = False):
        super().__init__(public)
        self.bucket = bucket
        self.region = region
        self.url_prefix = url_prefix
        self.client = aws_client('s3',
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=access_secret,
                                 region_name=region)

    def public_url(self, name: str) -> str:
        if self.url_prefix:
            return '/'.join([self.url_prefix, name])
        return 'https://s3-{}.amazonaws.com/{}/{}'.format(self.region,
                                                          self.bucket,
                                                          name)

    def sign(self, name: str) -> str:
        if not self.signature_required:
            return self.public_url(name)

        params = {'Bucket': self.bucket, 'Key': name}
        expire_duration = int(self.signature_expiry_duration.total_seconds())
        return self.client.generate_presigned_url('get_object',
                                                  Params=params,
                                                  ExpiresIn=expire_duration)

    @classmethod
    def create(cls, options: argparse.Namespace) -> BaseAssetSigner:
        access_key = options.asset_store_access_key
        if not access_key:
            raise Exception('Missing access key for s3 asset store')

        access_secret = options.asset_store_secret_key
        if not access_secret:
            raise Exception('Missing access secret for s3 asset store')

        region = options.asset_store_region
        if not region:
            raise Exception('Missing region for s3 asset store')

        bucket = options.asset_store_bucket
        if not bucket:
            raise Exception('Missing bucket name for s3 asset store')

        return cls(access_key, access_secret, region, bucket,
                   options.asset_store_s3_url_prefix,
                   options.asset_store_public)
