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
import logging
import mimetypes
import os
import shutil

from werkzeug.exceptions import NotFound

from . import Response
from .registry import get_registry
from .utils.assets import StaticAssetsLoader

log = logging.getLogger(__name__)
_registry = get_registry()


class CollectorException(Exception):
    pass


class StaticAssetsCollector:
    def __init__(self, dist):
        self.dist = os.path.abspath(dist)

    @property
    def base_path(self):
        return os.path.join(self.dist, 'static')

    def _prefix_path(self, prefix):
        prefix_path = os.path.abspath(os.path.join(self.base_path, prefix))
        if not prefix_path.startswith(self.base_path):
            raise CollectorException(
                'Prefix {} (absolute path {}) does not reside in'
                ' base path {}.'.format(prefix, prefix_path, self.base_path))
        return prefix_path

    def collect(self, prefix, loader):
        if not isinstance(loader, StaticAssetsLoader):
            raise ValueError('The second argument must be an instance '
                             'of StaticAssetsLoader.')
        prefix_path = self._prefix_path(prefix)
        log.debug('Prefix path is %s', prefix_path)
        loader.copy_into(prefix_path)

    def clean(self):
        shutil.rmtree(self.dist)


def serve_static_assets(request, basepath):
    """
    Serve static assets with the given request object.
    """
    if not request.path.startswith(basepath):
        raise ValueError('Request path does not start with basepath ""'
                         .format(basepath))

    path = request.path[len(basepath):]
    try:
        loader, subpath = _registry.get_static_assets(path)
    except KeyError:
        raise NotFound()

    if subpath and subpath[0] == '/':
        subpath = subpath[1:]

    if not loader.exists_asset(subpath):
        log.debug('Asset not found: {}'.format(subpath))
        raise NotFound()

    content_type, _ = mimetypes.guess_type(subpath)
    return Response(loader.get_asset(subpath), content_type=content_type)
