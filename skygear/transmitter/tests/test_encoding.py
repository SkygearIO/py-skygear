from ..encoding import deserialize_record


class TestsDeserializeRecord():
    def test_normal(self):
        rdata = {
            "_access": None,
            "_id": "note/99D92DBA-74D5-477F-B35E-F735E21B2DD5",
            "_ownerID": "OWNER_ID",
            "content": "Hello World!",
            "noteOrder": 1,
            }
        r = deserialize_record(rdata)
        assert r.id.type == "note"
        assert r.id.key == "99D92DBA-74D5-477F-B35E-F735E21B2DD5"
        print(r.data)
        assert r['content'] == "Hello World!"
        assert r['noteOrder'] == 1
        assert r.owner_id == "OWNER_ID"
