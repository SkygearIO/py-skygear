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

from ..error import SkygearException, InvalidArgument
from ..options import options as skygear_options
from .fs import FileSystemAssetSigner
from .s3 import S3AssetSigner
from .cloud import CloudAssetSigner

signer = None


def get_signer():
    global signer

    if signer and signer.available():
        return signer

    store_type = skygear_options.asset_store
    if store_type == 'fs':
        signer = FileSystemAssetSigner.create(skygear_options)
    elif store_type == 's3':
        signer = S3AssetSigner.create(skygear_options)
    elif store_type == 'cloud':
        signer = CloudAssetSigner.create(skygear_options)
    else:
        raise SkygearException(
            'Unknown asset store type: {}'.format(store_type),
            code=InvalidArgument
        )

    return signer
