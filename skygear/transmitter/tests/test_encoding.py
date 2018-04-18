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

from skygear.models import (Asset, Location, PublicAccessControlEntry, Record,
                            RecordID, Reference, RoleAccessControlEntry,
                            UnknownValue)

from ...encoding import (deserialize_record, deserialize_value,
                         serialize_record, serialize_value)


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


class TestsDeserializeValue():
    def test_integer(self):
        assert deserialize_value(42) == 42

    def test_null(self):
        assert deserialize_value(None) is None

    def test_boolean(self):
        assert deserialize_value(True) is True

    def test_date(self):
        value = {"$type": "date", "$date": "2016-12-08T08:38:33Z"}
        assert deserialize_value(value) == datetime.fromtimestamp(1481186313)

    def test_asset(self):
        value = {
            "$type": "asset",
            "$name": "c1d0e8d4-648c-4c88-86c6-22feb1a6e734",
            "$content_type": "text/html"
        }
        assert deserialize_value(value) == \
            Asset("c1d0e8d4-648c-4c88-86c6-22feb1a6e734", "text/html")

    def test_location(self):
        value = {"$type": "geo", "$lng": 1, "$lat": 2}
        assert deserialize_value(value) == Location(1, 2)

    def test_reference(self):
        value = {
            "$type": "ref",
            "$id": "note/c1d0e8d4-648c-4c88-86c6-22feb1a6e734"
        }
        assert deserialize_value(value) == \
            Reference(RecordID("note", "c1d0e8d4-648c-4c88-86c6-22feb1a6e734"))

    def test_unknown_value(self):
        value = {"$type": "unknown", "$underlying_type": "unknown_type"}
        assert deserialize_value(value) == UnknownValue("unknown_type")

    def test_record(self):
        value = {
            "$type": "record",
            "$record": {
                "_access": None,
                "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
                "_ownerID": "OWNER_ID",
                "content": "Hello World!",
            }
        }
        r = deserialize_value(value)
        assert r.id.type == "note"
        assert r.id.key == "99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        assert r.owner_id == "OWNER_ID"
        assert r["content"] == "Hello World!"

    def test_list(self):
        value = [42, {"$type": "geo", "$lng": 1, "$lat": 2}]
        assert deserialize_value(value) == [42, Location(1, 2)]

    def test_dict(self):
        value = {
            "distance": 42,
            "location": {"$type": "geo", "$lng": 1, "$lat": 2}
        }
        assert deserialize_value(value) == {
            "distance": 42,
            "location": Location(1, 2)
        }


class TestsSerializeValue():
    def test_integer(self):
        assert serialize_value(42) == 42

    def test_null(self):
        assert serialize_value(None) is None

    def test_boolean(self):
        assert serialize_value(True) is True

    def test_date(self):
        value = datetime.fromtimestamp(1481186313)
        assert serialize_value(value) == \
            {"$type": "date", "$date": "2016-12-08T08:38:33Z"}

    def test_asset(self):
        value = Asset("c1d0e8d4-648c-4c88-86c6-22feb1a6e734", "text/html")
        assert serialize_value(value) == \
            {
                "$type": "asset",
                "$name": "c1d0e8d4-648c-4c88-86c6-22feb1a6e734",
                "$content_type": "text/html"
            }

    def test_location(self):
        value = Location(1, 2)
        assert serialize_value(value) == \
            {"$type": "geo", "$lng": 1, "$lat": 2}

    def test_reference(self):
        value = Reference(
            RecordID("note", "c1d0e8d4-648c-4c88-86c6-22feb1a6e734"))
        assert serialize_value(value) == \
            {
                "$type": "ref",
                "$id": "note/c1d0e8d4-648c-4c88-86c6-22feb1a6e734"
            }

    def test_unknown_value(self):
        value = UnknownValue("unknown_type")
        assert serialize_value(value) == \
            {"$type": "unknown", "$underlying_type": "unknown_type"}

    def test_record(self):
        value = Record(
                id=RecordID("note", "99D92DBA-74D5-477F-B35E-F735E21B2DD5"),
                owner_id="OWNER_ID",
                acl=None,
                data={
                      "content": "Hello World!",
                      })
        assert serialize_value(value) == \
            {
                "$type": "record",
                "$record": {
                    "_access": None,
                    "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
                    "_ownerID": "OWNER_ID",
                    "content": "Hello World!",
                }
            }

    def test_list(self):
        value = [42, Location(1, 2)]
        assert serialize_value(value) == \
            [42, {"$type": "geo", "$lng": 1, "$lat": 2}]

    def test_dict(self):
        value = {
            "distance": 42,
            "location": Location(1, 2)
        }
        assert serialize_value(value) == \
            {
                "distance": 42,
                "location": {"$type": "geo", "$lng": 1, "$lat": 2}
            }
