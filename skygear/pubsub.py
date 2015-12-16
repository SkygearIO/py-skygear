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
import json
import os

from websocket import create_connection

encoder = json.dumps


def get_hub():
    return _hub


def publish(channel, data):
    get_hub().publish(channel, data)


class Hub:

    def __init__(self):
        self.transport = 'websocket'
        self.end_point = 'ws://localhost:3000/pubsub'

    def publish(self, channel, data):
        conn = create_connection(self.end_point)
        _data = encoder({
            'action': 'pub',
            'channel': channel,
            'data': data,
        })
        conn.send(_data)
        conn.close()


_hub = Hub()
_hub.end_point = os.getenv('PUBSUB_URL', None)
if not _hub.end_point:
    raise ValueError('empty environment variable "PUBSUB_URL"')
