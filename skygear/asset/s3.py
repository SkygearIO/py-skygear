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

from datetime import timedelta

import configargparse as argparse
from boto3 import client as aws_client

from ..error import InvalidArgument, SkygearException
from .common import CommonAssetSigner


class S3AssetSigner(CommonAssetSigner):
    @classmethod
    def create(cls, options: argparse.Namespace) -> CommonAssetSigner:
        access_key = options.asset_store_access_key
        if not access_key:
            raise SkygearException('Missing access key for s3 asset store',
                                   code=InvalidArgument)

        access_secret = options.asset_store_secret_key
        if not access_secret:
            raise SkygearException('Missing access secret for s3 asset store',
                                   code=InvalidArgument)

        region = options.asset_store_region
        if not region:
            raise SkygearException('Missing region for s3 asset store',
                                   code=InvalidArgument)

        bucket = options.asset_store_bucket
        if not bucket:
            raise SkygearException('Missing bucket name for s3 asset store',
                                   code=InvalidArgument)

        return cls(access_key, access_secret, region, bucket,
                   options.asset_store_public)

    def __init__(self, access_key: str, access_secret: str,
                 region: str, bucket: str, public: bool = False):
        super().__init__(public)
        self.bucket = bucket
        self.region = region
        self.client = aws_client('s3',
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=access_secret,
                                 region_name=region)

    def sign(self, name: str) -> str:
        if not self.signature_required():
            return 'https://s3-{}.amazonaws.com/{}/{}'.format(self.region,
                                                              self.bucket,
                                                              name)
        params = {'Bucket': self.bucket, 'Key': name}
        expire_duration = int(timedelta(minutes=15).total_seconds())
        return self.client.generate_presigned_url('get_object',
                                                  Params=params,
                                                  ExpiresIn=expire_duration)
