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
import contextlib
import os
import re

import sqlalchemy as sa

from ..container import SkygearContainer

_app_name_pattern = re.compile('[.:]')
_engine = None


def quotedIdentifier(s):
    return '"%s"' % s.replace('"', '""')


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError('empty environment variable "DATABASE_URL"')

        _engine = sa.create_engine(db_url)

    return _engine


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
