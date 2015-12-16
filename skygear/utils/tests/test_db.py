import unittest

from sqlalchemy.sql import text

from skygear.container import SkygearContainer
from skygear.transmitter.common import _get_engine
from skygear.utils import db


class TestResetPassword(unittest.TestCase):
    app_name = 'app+db'

    def setUp(self):
        SkygearContainer.set_default_app_name(self.app_name)
        with _get_engine().begin() as conn:
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
        with _get_engine().begin() as conn:
            conn.execute("DROP TABLE \"app_{0}\".note;".format(self.app_name))

    def test_correct_db_context(self):
        with db.conn() as conn:
            result = conn.execute("""
                SELECT id, content FROM note
            """)
            r = result.fetchone()
            assert r['id'] == 'first'
            assert r['content'] == 'Hello World!'
