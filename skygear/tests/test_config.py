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
from unittest.mock import patch

from .. import config


class TestParseConfig():
    def test_simple_dict(self):
        ns = config.Configuration()
        assert config._parse_config({'hello': 'world'}, ns) == ns
        assert ns.hello == 'world'

    def test_complex_dict(self):
        ns = config.Configuration()
        data = {
                'hello': 'world',
                'bye': {
                    'apple': {'fruit': True},
                    'pie': {'fruit': False},
                    }
                }
        assert config._parse_config(data, ns) == ns
        assert ns.hello == 'world'
        assert isinstance(ns.bye, config.Configuration)
        assert isinstance(ns.bye.apple, config.Configuration)
        assert isinstance(ns.bye.pie, config.Configuration)
        assert ns.bye.apple.fruit is True
        assert ns.bye.pie.fruit is False

    @patch('skygear.config.config', config.Configuration())
    def test_parse_config(self):
        assert config.parse_config({'hello': 'world'}) == config.config
        assert config.config.hello == 'world'
