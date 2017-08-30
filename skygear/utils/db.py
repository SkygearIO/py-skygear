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
import logging
import os
import re

import sqlalchemy as sa
from sqlalchemy import schema
from sqlalchemy.dialects.postgresql.base import ischema_names

from ..container import SkygearContainer

_app_name_pattern = re.compile('[.:]')
_engine = None
_metadata = None
_logger = logging.getLogger(__name__)

# Register CIText to SQLAlchemy's Postgres reflection subsystem.
ischema_names['citext'] = sa.types.TEXT


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


def _get_schema_name():
    app_name = SkygearContainer.get_default_app_name()
    return 'app_' + _app_name_pattern.sub('_', app_name)


def _get_metadata():
    global _metadata
    if _metadata:
        return _metadata

    _metadata = _reflect_tables()
    return _metadata


def _reflect_tables():
    meta = schema.MetaData()

    schema_name = _get_schema_name()
    _logger.info("Reflecting database schema from postgres schema '{}'."
                 .format(schema_name))
    meta.reflect(bind=_get_engine(), schema=schema_name, views=True)
    return meta


def _search_path_sql():
    app_name = quotedIdentifier(_get_schema_name())
    return "SET search_path TO {0}, public;".format(app_name)


def _set_search_path(db):
    sql = _search_path_sql()
    db.execute(sql)


def _full_table_name(schema_name, name):
    """
    Return the full name of a table, which includes the schema name.
    """
    return "{}.{}".format(schema_name, name)


def get_table(name):
    """
    Returns the table object with the specified name from the reflected
    database.

    An exception is raised if the table does not exist.
    """
    schema_name = _get_schema_name()
    try:
        return _get_metadata().tables[_full_table_name(schema_name, name)]
    except KeyError:
        raise Exception("No table of name '{}' exists in schema '{}'.".format(
                        name, schema_name))


def has_table(name):
    """
    Returns whether a table with the specified name exists in the reflected
    database schema.
    """
    schema_name = _get_schema_name()
    return _full_table_name(schema_name, name) in _get_metadata().tables


@contextlib.contextmanager
def conn():
    sql = _search_path_sql()
    with _get_engine().begin() as conn:
        conn.execute(sql)
        yield conn
