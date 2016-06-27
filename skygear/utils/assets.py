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
import os.path
import shutil


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
                    os.path.join(dest, _trim_abs_path(filename)))
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
        return os.path.exists(os.path.join(self.dirpath, name))


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

    This helper function is not implemented yet. Calling it will
    raise the NotImplemented exception.
    """
    # TODO(cheungpat): This is currently not implemented because a python
    # package can be installed as a python egg, which is a zip archive. The
    # static assets are in the zip archive rather than an actual directory in
    # the file system.
    raise NotImplemented('package_assets are not implemented yet')
