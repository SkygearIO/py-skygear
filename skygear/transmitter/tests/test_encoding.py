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

from skygear.models import (PublicAccessControlEntry, Record, RecordID,
                            RoleAccessControlEntry, UnknownValue)

from ...encoding import deserialize_record, serialize_record


class TestsDeserializeRecord():
    def test_normal(self):
        rdata = {
            "_access": None,
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER_ID",
            "content": "Hello World!",
            "noteOrder": 1,
            "money": {"$type": "unknown", "$underlying_type": "money"},
            }
        r = deserialize_record(rdata)
        assert r.id.type == "note"
        assert r.id.key == "99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        print(r.data)
        assert r['content'] == "Hello World!"
        assert r['noteOrder'] == 1
        assert r.owner_id == "OWNER_ID"
        assert r['money'].underlyingType == "money"

    def test_model_with_acl(self):
        rdata = {
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER _ID",
            "_access": [{
                "role": "admin",
                "level": "write"
            }]
        }
        r = deserialize_record(rdata)
        assert r.id.type == "note"
        assert r.id.key == "99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        assert isinstance(r.acl, list)
        assert isinstance(r.acl[0], RoleAccessControlEntry)

    def test_model_with_public_read_acl(self):
        rdata = {
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER _ID",
            "_access": [{
                "public": True,
                "level": "read"
            }]
        }
        r = deserialize_record(rdata)
        assert r.id.type == "note"
        assert r.id.key == "99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        assert isinstance(r.acl, list)
        assert isinstance(r.acl[0], PublicAccessControlEntry)
        assert r.acl[0].level == "read"

    def test_serialize_record_back(self):
        rdata = {
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER_ID",
            "_access": [{
                "public": True,
                "level": "read"
            }],
            "_created_at": "2014-09-27T17:40:00Z"
        }
        r = deserialize_record(rdata)
        result = serialize_record(r)
        assert result['_id'] == "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        assert result['_ownerID'] == "OWNER_ID"
        assert result['_access'] == [{
            "public": True,
            "level": "read"
        }]
        assert result['_created_at'] == "2014-09-27T17:40:00Z"


class TestsSerializeRecord():
    def test_normal(self):
        r = Record(
            id=RecordID('note', '99D92DBA-74D5-477F-B35E-F735E21B2DD5'),
            owner_id='OWNER_ID',
            acl=None,
            data={
                  "content": "Hello World!",
                  "noteOrder": 1,
                  "money": UnknownValue("money"),
                  })
        rdata = serialize_record(r)
        assert rdata == {
            "_access": None,
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER_ID",
            "content": "Hello World!",
            "noteOrder": 1,
            "money": {'$type': 'unknown', '$underlying_type': 'money'},
        }
