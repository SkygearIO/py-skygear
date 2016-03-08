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
import logging
import time
from random import randint

import zmq

from ..config import parse_config
from .common import CommonTransport

log = logging.getLogger(__name__)


def _encoded(func):
    def encoded(self, input):
        decoded = input.decode('utf-8')
        deserialized = json.loads(decoded)

        retval = func(self, deserialized)

        serialized = json.dumps(retval)
        out = serialized.encode('utf-8')
        return out
    return encoded

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 32

PPP_READY = b'\x01'
PPP_HEARTBEAT = b'\x02'
PPP_SHUTDOWN = b'\x03'


def worker_socket(addr, context, poller):
    worker = context.socket(zmq.DEALER)
    identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
    worker.setsockopt_string(zmq.IDENTITY, identity)
    poller.register(worker, zmq.POLLIN)
    worker.connect(addr)
    worker.send(PPP_READY)
    return worker


class ZmqTransport(CommonTransport):
    """ZmqTransport implements the Paranoid-Pirate worker described in the zguide:
    http://zguide.zeromq.org/py:all#Robust-Reliable-Queuing-Paranoid-Pirate-Pattern
    """

    def __init__(self, addr, context=None, registry=None):
        super().__init__(registry)
        if context is None:
            context = zmq.Context()

        self._addr = addr
        self._context = context

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            if self._worker:
                self._worker.send(PPP_SHUTDOWN)

    # the majority of this function is taken from:
    # http://zguide.zeromq.org/py:ppworker
    def _run(self):
        context = self._context
        poller = zmq.Poller()

        liveness = HEARTBEAT_LIVENESS
        interval = INTERVAL_INIT

        heartbeat_at = time.time() + HEARTBEAT_INTERVAL

        worker = worker_socket(self._addr, context, poller)
        self._worker = worker
        while True:
            socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

            # Handle worker activity on backend
            if socks.get(worker) == zmq.POLLIN:
                #  Get message
                #  - 3-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = worker.recv_multipart()
                if not frames:
                    break

                if len(frames) == 3:
                    client, empty, message = frames
                    assert empty == b''

                    log.debug('Recv message')
                    log.debug(message)
                    response = self.handle_message(message)
                    worker.send_multipart([
                        client,
                        b'',
                        response,
                    ])

                    liveness = HEARTBEAT_LIVENESS
                elif len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
                    liveness = HEARTBEAT_LIVENESS
                else:
                    log.warn('Invalid message: %s', frames)
                interval = INTERVAL_INIT
            else:
                liveness -= 1
                if liveness == 0:
                    log.warn('Heartbeat failure, can\'t reach queue')
                    log.warn('Reconnecting in %0.2fs...' % interval)
                    time.sleep(interval)

                    if interval < INTERVAL_MAX:
                        interval *= 2
                    poller.unregister(worker)
                    worker.setsockopt(zmq.LINGER, 0)
                    worker.close()
                    worker = worker_socket(self._addr, context, poller)
                    self._worker = worker
                    liveness = HEARTBEAT_LIVENESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + HEARTBEAT_INTERVAL
                worker.send(PPP_HEARTBEAT)

    @_encoded
    def handle_message(self, req):
        kind = req['kind']
        param = req.get('param')
        if kind == 'init':
            parse_config(param.get('config') or {})
            return self.init_info()

        name = req['name']

        ctx = req.get('context') or {}

        if kind == 'provider':
            action = param.pop('action')
            return self.call_provider(ctx, name, action, param)
        elif kind == 'handler':
            return self.call_handler(ctx, name, param)
        else:
            return self.call_func(ctx, kind, name, param)
