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


loaded_modules = {}


def _config_module(module, settings, *args, **kwargs):
    try:
        module.includeme(settings, *args, **kwargs)
    except AttributeError as e:
        msg = "Module {} does not implement function includeme"\
            .format(module.__name__)
        raise NotImplementedError(msg)


def add_module(name, module):
    loaded_modules[name] = module


def get_module(name):
    try:
        return loaded_modules[name]
    except KeyError as ex:
        raise NameError("name '{}' is not defined".format(name))
