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
from datetime import datetime

from ..models import Record, RecordID


class TestRecord():
    def test_create(eslf):
        now = datetime.now()
        rid = RecordID("note", "hello_world")
        r = Record(rid, "OWNER_ID", None,
                   created_at=now, created_by="CREATOR_ID",
                   updated_at=now, updated_by="UPDATER_ID",
                   data={"content": "Hello!", "noteOrder": 1})

        assert r is not None
        assert r.id == rid
        assert r.owner_id == 'OWNER_ID'
        assert r.created_at == now
        assert r.created_by == 'CREATOR_ID'
        assert r.updated_at == now
        assert r.updated_by == 'UPDATER_ID'
        assert r.data == {"content": "Hello!", "noteOrder": 1}

    def test_create_empty_data(eslf):
        rid = RecordID("note", "hello_world")
        r = Record(rid, "OWNER_ID", None)

        assert r is not None
        assert r.id == rid
        assert r.owner_id == 'OWNER_ID'
        assert r.data == {}
