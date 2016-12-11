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

import unittest

from .common import BaseAssetSigner


class TestBaseAssetSigner(unittest.TestCase):
    def test_init(self):
        assert BaseAssetSigner().public is False
        assert BaseAssetSigner(public=True).public is True

    def test_available(self):
        assert BaseAssetSigner().available() is True
        assert BaseAssetSigner(public=True).available() is True

    def test_signature_required(self):
        assert BaseAssetSigner().signature_required is True
        assert BaseAssetSigner(public=True).signature_required is False
