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
import inspect
import logging
import os.path
import shutil

log = logging.getLogger(__name__)


def _trim_abs_path(path):
    if path.startswith('/'):
        path = path[1:]
    if path.startswith('./'):
        path = path[2:]
    return path


class StaticAssetsLoader:
    """
    This loader is a generic class for loading static assets.
    """
    def get_asset(self, name):
        """
        Get content of a static assets by name.
        """
        return None

    def copy_into(self, path):
        """
        Copy the content of all static assets into a directory.
        """
        pass

    def exists_asset(self, name):
        return False


class DictStaticAssetsLoader(StaticAssetsLoader):
    """
    This class loads static asset from a provided dictionary.
    """
    def __init__(self, _dict):
        super().__init__()
        self._dict = _dict

    def get_asset(self, name):
        return self._dict.get(name, None)

    def copy_into(self, path):
        for filename, content in self._dict.items():
            filepath = os.path.abspath(
                    os.path.join(path, _trim_abs_path(filename)))
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(content)

    def exists_asset(self, name):
        return name in self._dict


class DirectoryStaticAssetsLoader(StaticAssetsLoader):
    """
    This class loads static asset from a provided file system directory.
    """
    def __init__(self, dirpath):
        super().__init__()
        self._dirpath = os.path.abspath(dirpath)

    @property
    def dirpath(self):
        return self._dirpath

    def get_asset(self, path):
        filename = os.path.join(self.dirpath, path)
        with open(filename, 'rb') as f:
            return f.read()

    def copy_into(self, dest):
        shutil.copytree(self.dirpath, dest, symlinks=True)

    def exists_asset(self, name):
        full_path = os.path.join(self.dirpath, name)
        log.debug('Checking asset exist {}'.format(full_path))
        return os.path.exists(full_path)


class PackageStaticAssetsLoader(StaticAssetsLoader):
    """
    This class loads static asset from the provided python package.
    """
    def __init__(self, package_name, package_path):
        super().__init__()
        from pkg_resources import ResourceManager, get_provider
        self.provider = get_provider(package_name)
        self.manager = ResourceManager()
        self.package_path = package_path

    def resource_name(self, name):
        return os.path.join(self.package_path, _trim_abs_path(name))

    def get_asset(self, name):
        return self.provider.get_resource_string(self.manager,
                                                 self.resource_name(name))

    def copy_into(self, dest):
        def _walk(subpath=None):
            """
            `_walk` copies files in a subdirectory to the destination. If
            file is a directory, recursively call `_walk` for the directory.

            If subpath evaluates to False, copy from the `package_path`.
            """
            if subpath:
                resource_dir = self.resource_name(subpath)
            else:
                resource_dir = self.package_path

            for filename in self.provider.resource_listdir(resource_dir):
                childpath = subpath + '/' + filename if subpath else filename
                dest_name = os.path.abspath(os.path.join(dest, childpath))
                if self.provider.resource_isdir(self.resource_name(childpath)):
                    os.mkdir(dest_name)
                    _walk(childpath)
                else:
                    print('writing to {}'.format(dest_name))
                    with open(dest_name, 'wb') as f:
                        f.write(self.get_asset(childpath))

        os.makedirs(dest, exist_ok=True)
        _walk()

    def exists_asset(self, name):
        return self.provider.has_resource(self.resource_name(name))


def directory_assets(path='static'):
    """
    This helper function returns the absolute path of the static assets
    directory by specifying a path relative to the current directory,
    or by specifying a absolute path.
    """
    return DirectoryStaticAssetsLoader(path)


def relative_assets(path='static', current_file=None):
    """
    This helper function returns the absolute path of the static assets
    directory by specifying a path relative to the file of a python module.

    If the file of a python module is not specified, the `__file__` of the
    caller module is used. This is effectively the same as calling
    this function with `relative_assets(path, __file__)`.
    """
    if not current_file:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        current_file = module.__file__
    rel_dir = os.path.dirname(current_file)
    return directory_assets(os.path.join(rel_dir, path))


def package_assets(package_name, path='static'):
    """
    This helper function returns the absolute path of the static assets
    directory by specifying a path relative to a specified package name.
    """
    return PackageStaticAssetsLoader(package_name, path)
