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
import bcrypt
from sqlalchemy.sql import text

from .db import conn


def hash_password(password):
    """
    Return a hased password of a plaintext password.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode("utf-8")


def reset_password_by_username(username, new_password):
    """
    Reset the user password with a new password.
    """
    if not (isinstance(username, str) and isinstance(new_password, str)):
        raise ValueError("username and new_password must be string")

    sql = text('''
        UPDATE \"_user\"
        SET password = :new_password
        WHERE username = :username
        ''')
    with conn() as db:
        result = db.execute(sql,
                            new_password=hash_password(new_password),
                            username=username)
    return result.rowcount > 0
