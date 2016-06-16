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
import unittest

from sqlalchemy.schema import Table
from sqlalchemy.sql import text

from skygear.container import SkygearContainer
from skygear.utils import db


class BaseTestCase(unittest.TestCase):
    app_name = 'app+db'

    def setUp(self):
        SkygearContainer.set_default_app_name(self.app_name)
        with db.conn() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS \"app_{0}\""
                         .format(self.app_name))
            conn.execute(
                "set search_path to \"app_{0}\", public;".format(
                    self.app_name
                )
            )
            conn.execute("""
                CREATE TABLE IF NOT EXISTS note (
                    id text PRIMARY KEY,
                    content text
                );""")
            sql = text("""
                INSERT INTO note (id, content)
                VALUES (:id, :content);
                """)
            conn.execute(sql,
                         id='first',
                         content='Hello World!')

    def tearDown(self):
        with db.conn() as conn:
            conn.execute("DROP TABLE \"app_{0}\".note;".format(self.app_name))


class TestResetPassword(BaseTestCase):
    def test_correct_db_context(self):
        with db.conn() as conn:
            result = conn.execute("""
                SELECT id, content FROM note
            """)
            r = result.fetchone()
            assert r['id'] == 'first'
            assert r['content'] == 'Hello World!'


class TestReflectTable(BaseTestCase):
    def test_get_metadata(self):
        metadata = db._get_metadata()
        assert db._get_metadata() == metadata
        assert metadata is not None

    def test_get_table(self):
        table = db.get_table('note')
        assert isinstance(table, Table)
        assert table.c.content is not None

    def test_get_table_nonexistent(self):
        with self.assertRaises(Exception):
            db.get_table('something')

    def test_has_table(self):
        assert db.has_table('note') is True

    def test_has_table_nonexistent(self):
        assert db.has_table('something') is False
