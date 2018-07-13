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
from urllib.parse import quote


class BaseAssetSigner:
    def __init__(self, public=False):
        self.public = public

    @property
    def signature_expiry_duration(self) -> timedelta:
        return timedelta(minutes=15)

    @property
    def signature_required(self) -> bool:
        return not self.public

    # espect subclass may have some costly checking in this method
    def available(self) -> bool:
        return True

    def percent_escape_asset_name(self, name: str) -> str:
        # We do not quote '/' in name.
        # The first reason is that most file system
        # does not allow '/' be part of the filename.
        # Another reason is that AWS S3 allows object
        # key to contain '/'.
        return quote(name, safe='/')
