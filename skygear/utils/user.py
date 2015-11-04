import re

import bcrypt
from sqlalchemy.sql import text

from ..container import SkygearContainer

_app_name_pattern = re.compile('[.:]')


def hash_password(password):
    """
    Return a hased password of a plaintext password.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode("utf-8")


def _set_search_path(db):
    app_name = SkygearContainer.get_default_app_name()
    app_name = _app_name_pattern.sub('_', app_name)
    db.execute("set search_path to app_{0};".format(app_name))


def reset_password_by_username(db, username, new_password):
    """
    Reset the user password with a new password.
    """
    if not (isinstance(username, str) and isinstance(new_password, str)):
        raise ValueError("username and new_password must be string")

    _set_search_path(db)
    sql = text('''
        UPDATE \"_user\"
        SET password = :new_password
        WHERE username = :username
        ''')

    result = db.execute(sql,
                        new_password=hash_password(new_password),
                        username=username)
    return result.rowcount > 0
