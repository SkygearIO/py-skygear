import contextlib
import re

from ..container import SkygearContainer
from ..transmitter.common import _get_engine

_app_name_pattern = re.compile('[.:]')


def quotedIdentifier(s):
    return '"%s"' % s.replace('"', '""')


def _search_path_sql():
    app_name = SkygearContainer.get_default_app_name()
    app_name = _app_name_pattern.sub('_', app_name)
    app_name = quotedIdentifier("app_" + app_name)
    return "SET search_path TO {0}, public;".format(app_name)


def _set_search_path(db):
    sql = _search_path_sql()
    db.execute(sql)


@contextlib.contextmanager
def conn():
    sql = _search_path_sql()
    with _get_engine().begin() as conn:
        conn.execute(sql)
        yield conn
