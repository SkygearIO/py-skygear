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
        conn = create_connection('ws://localhost:3000/pubsub')
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
