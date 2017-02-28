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

MESSAGE_TYPE_REQUEST = 'REQ'
MESSAGE_TYPE_RESPONSE = 'RES'

PREFIX = randint(0, 0x10000)


def worker_socket(addr, context, poller):
    socket = context.socket(zmq.DEALER)
    identity = "%04X-%04X" % (PREFIX, randint(0, 0x10000))
    socket.setsockopt_string(zmq.IDENTITY, identity)
    poller.register(socket, zmq.POLLIN)
    socket.connect(addr)
    socket.send(PPP_READY)
    return socket


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
        self.bounce_count = 0
        self.request_id = None

    def run(self):
        """
        The majority of this function is taken from:
        http://zguide.zeromq.org/py:ppworker
        """
        self.poller = zmq.Poller()
        self.socket = worker_socket(self.addr, self.z_context, self.poller)
        self.socket_name = self.socket.getsockopt_string(zmq.IDENTITY)
        self.run_message_loop()

    # This method handle messages from sockets:
    # 1. It performs heartbeat
    # 2. It takes request and handle them
    # 3. It returns value when there is a response from server to plugin
    #
    # (3) should only occurs when this method is called recursively
    # Return values:
    # None - The socket is closing
    # Otherwise - response from server
    #
    # Btw, I cannot think of a better name for this method,
    # please update this if you have a better name
    def run_message_loop(self):
        liveness = HEARTBEAT_LIVENESS
        interval = INTERVAL_INIT
        poller = self.poller

        heartbeat_at = time.time() + HEARTBEAT_INTERVAL

        while True:
            socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

            # Handle worker activity on backend
            if socks.get(self.socket) == zmq.POLLIN:
                #  Get message
                #  - 7-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = self.socket.recv_multipart()
                if not frames:
                    log.warn(
                        'Invalid message: %s, assuming socket dead', frames)
                    return None

                if len(frames) == 7:
                    client = frames[0]
                    assert frames[1] == b''
                    message_type = frames[2].decode('utf8')
                    bounce_count = int(frames[3].decode('utf8'))
                    request_id = frames[4]
                    assert frames[5] == b''
                    message = frames[6]

                    self.request_id = request_id
                    self.bounce_count = bounce_count

                    if message_type == MESSAGE_TYPE_REQUEST:
                        response = self.handle_message(message)
                        self.socket.send_multipart([
                            client,
                            b'',
                            MESSAGE_TYPE_RESPONSE.encode('utf8'),
                            str(bounce_count).encode('utf8'),
                            request_id,
                            b'',
                            response,
                        ])
                    elif message_type == MESSAGE_TYPE_RESPONSE:
                        self.bounce_count -= 1
                        return message.decode('utf8')
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
                    poller.unregister(self.socket)
                    self.socket.setsockopt(zmq.LINGER, 0)
                    self.socket.close()
                    self.socket = worker_socket(self.addr, self.z_context, poller)
                    self.socket_name = self.socket.getsockopt_string(zmq.IDENTITY)
                    liveness = HEARTBEAT_LIVENESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + HEARTBEAT_INTERVAL
                self.socket.send(PPP_HEARTBEAT)
            if self.stopper.is_set():
                self.socket.send(PPP_SHUTDOWN)
                poller.unregister(self.socket)
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.close()
                return None

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

    def send_action(self, action, payload):
        self.bounce_count += 1
        message = {
            'action': action,
            'payload': payload
        }
        self.socket.send_multipart([
            self.socket_name.encode('utf8'),
            b'',
            MESSAGE_TYPE_REQUEST.encode('utf8'),
            str(self.bounce_count).encode('utf8'),
            self.request_id,
            b'',
            json.dumps(message).encode('utf8')
        ])
        return self.run_message_loop()

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

    def send_action(self, action_name, payload):
        worker = threading.current_thread()
        assert isinstance(worker, Worker)
        return worker.send_action(action_name, payload)
