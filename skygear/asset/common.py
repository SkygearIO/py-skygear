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

import time
from datetime import datetime, timedelta


class BaseAssetSigner:
    def __init__(self, public=False,
                 presign_expiry=15*60, presign_interval=5*60):
        self.public = public
        self.presign_expiry = timedelta(seconds=presign_expiry)
        self.presign_interval = timedelta(seconds=presign_interval)

    @property
    def signature_expiry_duration(self) -> timedelta:
        return timedelta(minutes=15)

    @property
    def signature_required(self) -> bool:
        return not self.public

    # espect subclass may have some costly checking in this method
    def available(self) -> bool:
        return True

    @property
    def presign_interval_start_time(self):
        if not self.presign_interval:
            return datetime.utcnow()

        interval = self.presign_interval.total_seconds()
        start_time = time.time()//interval*interval
        return datetime.utcfromtimestamp(start_time)

    @property
    def presign_expire_time(self):
        return self.presign_interval_start_time + self.presign_expiry
