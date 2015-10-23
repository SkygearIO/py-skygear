from datetime import datetime
from ..models import RecordID, Record


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
