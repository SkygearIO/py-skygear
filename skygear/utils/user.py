import bcrypt
from sqlalchemy.sql import text

from .db import _set_search_path


def hash_password(password):
    """
    Return a hased password of a plaintext password.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode("utf-8")


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
