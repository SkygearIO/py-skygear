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
import warnings

from skygear.encoding import (_RecordDecoder, _RecordEncoder,
                              deserialize_or_none, deserialize_record,
                              serialize_record)

# This file is to re-export the original package to maintain backward
# compability
warnings.warn("""Please import skygear.encoding instead,
skygear.transmitter.encoding is deperated""", DeprecationWarning)

__all__ = [
    'deserialize_record',
    'deserialize_or_none',
    'serialize_record',
    '_RecordDecoder',
    '_RecordEncoder',
]
