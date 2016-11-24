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
import importlib
import os
from importlib.machinery import SourceFileLoader

from .settings import settings as module_settings
from .settings.module import _config_module, add_module


class LoadException(Exception):
    pass


def guess_package_name(path):
    """
    Guess the package name for the specified file path.
    """
    relpath = os.path.relpath(os.path.expanduser(path))
    if relpath.startswith('..'):
        msg = "Path {0} must reside in current working directory".format(path)
        raise LoadException(msg)

    if relpath == '.' or relpath == '__init__.py':
        return 'plugin'

    if os.path.basename(relpath) == '__init__.py':
        # abc/def/__init__.py -> abc.def
        return os.path.dirname(relpath).replace(os.sep, '.')

    if os.path.isfile(relpath):
        # abc/def/plugin.py -> abc.def.plugin
        return os.path.dirname(relpath).replace(os.sep, '.') + '.' + \
            os.path.splitext(os.path.basename(relpath))[0]

    if os.path.isdir(relpath):
        # abc/def/plugin -> abc.def.plugin
        return relpath.replace(os.sep, '.')

    msg = "Unable to load {0}.".format(path)
    raise LoadException(msg)


def load_module(path):
    """
    Load the module specified by path.

    Path can be one of the followings:
    - If path is a file, load the file as a python module.
    - If path is a directory, load the file as a python package. The directory
      must contains `__init__.py`
    - Else, treat path as the name of the package to load.

    For file, we assume it is cloud code and have no `includeme` function.

    For directory or package, we regards it is explicit imported module, so we
    will config the module once loaded. i.e. calling the `includeme` function
    of the module.
    """
    if os.path.isfile(path):
        package_name = guess_package_name(path)
        loaded = SourceFileLoader(package_name, path).load_module()
        add_module(package_name, loaded)
    elif os.path.isdir(path):
        package_name = guess_package_name(path)
        loadpath = os.path.join(path, '__init__.py')
        loaded = SourceFileLoader(package_name, loadpath).load_module()
        add_module(package_name, loaded)
        _config_module(loaded, module_settings)
    else:
        imported = importlib.import_module(path)
        _config_module(imported, module_settings)


def load_default_module():
    """
    Load default module.
    """
    for module in ['__init__.py', 'plugin.py']:
        try:
            SourceFileLoader('plugin', module).load_module()
            break
        except FileNotFoundError:
            pass
    else:
        raise LoadException("Unable to find __init__.py or plugin.py.")


def load_modules(modules):
    """
    Load the specified modules.

    If no modules are specified, this function will attempt
    to load __init__.py. If unable to load, it will attempt to load plugin.py.
    If both files cannot be loaded, this function will exit the program.

    If modules are specified, this function will attempt to load all modules
    in the order they are specified. Failure to load a module will exit
    the program.
    """
    if not modules:
        load_default_module()
        return

    for module in modules:
        try:
            load_module(module)
        except FileNotFoundError:
            raise LoadException("File not found: {0}".format(module))
