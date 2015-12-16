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
import os

import sqlalchemy as sa

# engine-related code should belong to the runner of plugin. Ccurrently
# transport runs the func themselves, so we have no choice but put this func
# here
#
# TODO(limouren): refactor plugin-running logic to a separate func/class

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError('empty environment variable "DATABASE_URL"')

        _engine = sa.create_engine(db_url)

    return _engine
