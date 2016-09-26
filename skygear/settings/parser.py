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
import os
from collections import namedtuple

from . import Namespace

SettingItem = namedtuple('SettingItem',
                         'name default atype env_var resolve required')


class SettingsParser:
    """
    SettingsParser allows cloudcode and plugins to define the settings to
    parse. It reads from os.environ and parse the values into an object.

    By default, if a setting called `SOME_VAR` is defined, it will
    first check for `PREFIX_SOME_VAR` and then `SOME_VAR`, stopping at
    the first available variable.
    """
    def __init__(self, prefix):
        """
        Create a new SettingsParser.

        Specify a prefix for environment variable.
        """
        self.prefix = prefix
        self.settings = {}

    def add_setting(self,
                    name,
                    default=None,
                    atype=str,
                    env_var=None,
                    resolve=True,
                    required=True):
        """
        Add a setting to the parser.

        * name - The name of the setting, the value of the setting
          will be stored in the object with attribute of the same name.
        * default - If no environment variable is defined during paring,
          the default value will be used instead. Default is `None`.
        * atype - The type of the value. Specify a type or a function
          that accepts a single argument of the input and return the converted
          value. Default is `str`.
        * env_var - Alternatively name of the environment variable. If not
          specified, the default is the uppercase of the setting name.
        * resolve - In addition to the prefixed environment variable,
          also check the unprefixed variant. Default is `true`.
        * required - Whether the setting is required. The parser will
          raise an exception during parsing if the corresponding environment
          variables are not set. (Empty value is considered "set").
        """
        if not name:
            raise Exception("Setting name must be specified.")

        if name in self.settings:
            raise Exception("Setting named '{}' already defined.".format(name))

        if not env_var:
            env_var = name.upper()

        setting = SettingItem(name, default, atype, env_var, resolve, required)
        self.settings[name] = setting

    def parse_settings(self, namespace=None):
        """
        Parse the settings from environment variables. The settings
        are returned as an object.

        * namespace - Optionally specify a namespace where the settings
          are saved. This object is returned if specified. A new object
          is created if none is specified.
        """
        if not namespace:
            namespace = Namespace()

        for name, setting in self.settings.items():
            setattr(namespace, name, self._parse_setting(setting))
        return namespace

    def _parse_setting(self, setting):
        order = self._resolve_order(setting)
        for var_name in order:
            if var_name in os.environ:
                val = os.environ[var_name]
                break
        else:
            val = setting.default

        if val is None and setting.required:
            raise Exception("Setting named \"{}\" is defined "
                            "but it is not set.".format(setting.name))

        if val is not None:
            val = setting.atype(val)

        return val

    def _resolve_order(self, setting):
        order = ["{}_{}".format(self.prefix, setting.env_var)]
        if setting.resolve:
            order.append(setting.env_var)
        return order
