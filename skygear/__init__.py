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
from .__version__ import (
  __title__,
  __description__,
  __url__,
  __version__,
  __author__,
  __author_email__,
  __license__,
)

from .decorators import (
    hook,
    handler,
    op,
    event,
    every,
    provides,
    before_save,
    after_save,
    before_delete,
    after_delete,
    rest,
    static_assets,
    exception_handler,
)

from .restful import RestfulRecord, RestfulResource
from .utils.db import conn as db_conn
from .utils.http import Response
from .settings import config_module as config

"""
Testing
"""
__all__ = [hook, handler, op, event, every, provides,
           before_save, after_save, before_delete, after_delete,
           rest, RestfulRecord, RestfulResource,
           static_assets, exception_handler,
           config,
           db_conn,
           Response,
           __title__,
           __description__,
           __url__,
           __version__,
           __author__,
           __author_email__,
           __license__]
