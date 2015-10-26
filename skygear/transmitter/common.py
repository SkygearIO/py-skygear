import os

import sqlalchemy as sa

# engine-related code should belong to the runner of plugin. Ccurrently
# transport runs the func themselves, so we have no choice but put this func
# here
#
# TODO(limouren): refactor plugin-running logic to a separate func/class

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError('empty environment variable "DATABASE_URL"')

        _engine = sa.create_engine(db_url)

    return _engine
