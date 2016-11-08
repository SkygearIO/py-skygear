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
import threading
import time
from random import randint

import zmq

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

PREFIX = randint(0, 0x10000)


def worker_socket(addr, context, poller):
    worker = context.socket(zmq.DEALER)
    identity = "%04X-%04X" % (PREFIX, randint(0, 0x10000))
    worker.setsockopt_string(zmq.IDENTITY, identity)
    poller.register(worker, zmq.POLLIN)
    worker.connect(addr)
    worker.send(PPP_READY)
    return worker


class Worker(threading.Thread, CommonTransport):
    """
    Worker is a Paranoid-Pirate worker described in the zguide:
    Related RFC: https://rfc.zeromq.org/spec:6/PPP
    refs:
    http://zguide.zeromq.org/py:all#Robust-Reliable-Queuing-Paranoid-Pirate-Pattern
    """
    def __init__(self, z_context, addr, stopper, registry=None):
        threading.Thread.__init__(self)
        CommonTransport.__init__(self, registry)
        self.addr = addr
        self.z_context = z_context
        self.stopper = stopper

    def run(self):
        """
        The majority of this function is taken from:
        http://zguide.zeromq.org/py:ppworker
        """
        poller = zmq.Poller()

        liveness = HEARTBEAT_LIVENESS
        interval = INTERVAL_INIT

        heartbeat_at = time.time() + HEARTBEAT_INTERVAL

        worker = worker_socket(self.addr, self.z_context, poller)

        while True:
            socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

            # Handle worker activity on backend
            if socks.get(worker) == zmq.POLLIN:
                #  Get message
                #  - 3-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = worker.recv_multipart()
                if not frames:
                    log.warn(
                        'Invalid message: %s, assuming socket dead', frames)
                    return

                if len(frames) == 3:
                    client, empty, message = frames
                    assert empty == b''

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
                    worker = worker_socket(self.addr, self.z_context, poller)
                    liveness = HEARTBEAT_LIVENESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + HEARTBEAT_INTERVAL
                worker.send(PPP_HEARTBEAT)
            if self.stopper.is_set():
                worker.send(PPP_SHUTDOWN)
                poller.unregister(worker)
                worker.setsockopt(zmq.LINGER, 0)
                worker.close()
                return

    @_encoded
    def handle_message(self, req):
        kind = req.get('kind')
        if kind == 'init':
            raise Exception('Init trigger is deprecated, '
                            'use init event instead')

        name = req.get('name')
        param = req.get('param', {})
        ctx = req.get('context', {})

        if kind == 'provider':
            action = param.pop('action')
            return self.call_provider(ctx, name, action, param)
        elif kind == 'handler':
            return self.call_handler(ctx, name, param)
        elif kind == 'event':
            return self.call_event_func(name, param)
        else:
            return self.call_func(ctx, kind, name, param)


class ZmqTransport(CommonTransport):
    """
    ZmqTransport will start the working thread which run it own zmq socket.
    Since the zmq socket is not thread safe, the worker will be responabile for
    doing their own heartbeat to the keep alive. To skygear-server it just
    like multiple worker process.
    """

    def __init__(self, addr, context=None, registry=None, threading=4):
        super().__init__(registry)
        if context is None:
            context = zmq.Context()

        self._addr = addr
        self._context = context
        self._threading = threading
        self.threads = []
        self.threads_opened = 0

    def run(self):
        self.start()
        try:
            self.maintain_workers_count()
        except KeyboardInterrupt:
            log.info('Shutting down all worker')
            self.stop()

    def start(self):
        self.stopper = threading.Event()
        for i in range(self._threading):
            t = Worker(self._context, self._addr, self.stopper)
            self.threads.append(t)
            t.start()
            self.threads_opened = self.threads_opened + 1

    def maintain_workers_count(self):
        i = 0
        while True:
            t = self.threads[i]
            t.join(HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS)
            if self.stopper.is_set():
                log.info(
                    'Workers are shutting down, stop maintain workers loop')
                return
            if not t.is_alive():
                log.warn(
                    'Worker Thread dead, starting a new one')
                new_t = Worker(self._context, self._addr, self.stopper)
                self.threads[i] = new_t
                new_t.start()
                self.threads_opened = self.threads_opened + 1
            i = i + 1
            if i >= self._threading:
                i = 0

    def stop(self):
        self.stopper.set()
        for t in self.threads:
            t.join()
