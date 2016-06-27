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
import os



def directory_assets(path='static'):
    """
    This helper function returns the absolute path of the static assets
    directory by specifying a path relative to the current directory,
    or by specifying a absolute path.
    """
    return os.path.abspath(path)


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
