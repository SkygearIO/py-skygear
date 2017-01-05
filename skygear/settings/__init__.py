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
from argparse import Namespace

from .parser import SettingsParser
from .module import _config_module, get_module


_parsers = {}
"""
`settings` is namespaced settings for plugins. Following is an example of how
a plugin developer can register settings and query back the value.


Declaring the required settings:
```
from skygear.settings import SettingsParser, add_parser

parser = SettingsParser('SKYGEAR_CMS')
parser.add_setting('prefix', default='cms')
parser.add_setting('static_assets_prefix', default='/static/:prefix/')

add_parser('cms', parser)
```

The settings module will read the environment and set the value. For example,
os.environ `SKYGEAR_CMS_PREFIX` will be available as follows:

```
from skygear.settings import settings

settings.cms.prefix
```
"""
settings = Namespace()


def add_parser(name, parser, parse_now=True):
    """
    Add the specified SettingsParser. If parse_now is True (the default),
    the parser is run immediately.
    """
    global _parsers
    if name in _parsers:
        raise Exception("Parser \"{}\" already defined.", name)
    _parsers[name] = parser
    if parse_now:
        _parse(name, parser)


def _parse(name, parser):
    global settings

    ns = getattr(settings, name, Namespace())
    ns = parser.parse_settings(ns)
    setattr(settings, name, ns)


def parse_all():
    """
    Parse all settings.
    """
    global _parsers
    global settings

    for name, parser in _parsers.items():
        _parse(name, parser)
    return settings


def config_module(name, *args, **kwargs):
    """
    Try to config the already imported module on boot time. If the package is
    not already imported in boot time, will try to import as normal package
    and config it.

    config_module will not import another copy of the module if it was already
    loaded at boot time.

    To config a module, the `includeme` function will be called and all
    skygear lambda functions, database hooks, etc. are expected to be declared
    in the `includeme` function as follows:

    ```
    import skygear

    def includeme(settings, *args, **kwargs):
        @skygear.op('some:lambda')
        def some_lambda_func():
            return {
                'success': True,
                'message': 'Some message being returned'
            }

        @skygear.after_save('some_record', async=True)
        def some_record_after_save(record, original_record, db):
            return {
                'success': True
            }

        # other lambda functions

    ```

    The `includeme` function will be called in the following cases:

    1. The module is declared on Skygear Plugin Runner, i.e. execute
       `py-skygear some_module`.

    2. The module is configured in cloud code, i.e. user calls
       `skygear.config('some_module')` in his cloud code.

    When the `includeme` function is called, settings will be passed as an
    argument.

    """
    global settings
    try:
        module = get_module(name)
    except NameError:
        module = importlib.import_module(name)
    _config_module(module, settings, *args, **kwargs)


__all__ = [
    Namespace,
    SettingsParser, settings,
    config_module,
    add_parser, parse_all
]
