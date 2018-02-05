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

import bcrypt
import pytest
from sqlalchemy.sql import text

from skygear.container import SkygearContainer
from skygear.utils import db
from skygear.utils import user as u

PLAINTEXT = 'helloworld!'


def assert_correct_pw(password, salt):
    decoded_salt = salt.encode('utf-8')
    new_hash = bcrypt.hashpw(password.encode('utf-8'), decoded_salt)
    assert new_hash == decoded_salt


class TestHashPassword():
    def test_hash_password(self):
        hashed = u.hash_password(PLAINTEXT)
        assert isinstance(hashed, str)
        assert_correct_pw(PLAINTEXT, hashed)


class TestResetPassword(unittest.TestCase):
    app_name = '_'

    def setUp(self):
        SkygearContainer.set_default_app_name(self.app_name)
        with db.conn() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS app_{0}"
                         .format(self.app_name))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _user (
                    id text PRIMARY KEY,
                    username text,
                    email text,
                    password text,
                    auth jsonb
                );""")
            sql = text("""
                INSERT INTO _user (id, username, password)
                VALUES (:id, :username, :password);
                """)
            conn.execute(sql,
                         id='1',
                         username='USER_1',
                         password=u.hash_password('supersecret1'))

    def tearDown(self):
        with db.conn() as conn:
            conn.execute("DROP TABLE app_{0}._user;".format(self.app_name))

    def test_reset_password(self):
        done = u.reset_password_by_username("USER_1", PLAINTEXT)
        assert done

        with db.conn() as conn:
            result = conn.execute(text("""
                SELECT password
                FROM app_{0}._user
                WHERE username=:username
                """.format(self.app_name)),
                username='USER_1')
            r = result.fetchone()
            assert_correct_pw(PLAINTEXT, r[0])

    def test_no_such_user(self):
        done = u.reset_password_by_username("USER_2", PLAINTEXT)
        assert not done

    def test_bad_parameter(self):
        with pytest.raises(ValueError):
            u.reset_password_by_username(1, '')

        with pytest.raises(ValueError):
            u.reset_password_by_username('', 1)
