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
import argparse


class Configuration(argparse.Namespace):
    pass


config = Configuration()


def _parse_config(data, ns):
    for k, v in data.items():
        if isinstance(v, dict):
            setattr(ns, k, _parse_config(v, Configuration()))
        else:
            setattr(ns, k, v)
    return ns


def parse_config(data, namespace=None):
    """
    Parse the Skygear config from a dict to a Configuration object.

    When namespace is not specified, the global config is updated instead.
    """
    global config
    return _parse_config(data, namespace or config)
