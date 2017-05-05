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
    def encoded(self, input, *args):
        decoded = input.decode('utf-8')
        deserialized = json.loads(decoded)

        try:
            retval = func(self, deserialized, *args)
            response_string = json.dumps(retval)
        except ValueError as e:
            response_string = str(e)
            log.error(str(e))
        out = response_string.encode('utf-8')
        return out
    return encoded


HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 32

PPP_READY = b'\x01'
PPP_HEARTBEAT = b'\x02'
PPP_SHUTDOWN = b'\x03'
PPP_REQUEST = b'\x04'
PPP_RESPONSE = b'\x05'

PREFIX = randint(0, 0x10000)


LISTEN_MESSAGE_RESULT_TIMEOUT = 0
LISTEN_MESSAGE_RESULT_INVALID = 1
LISTEN_MESSAGE_RESULT_HEARTBEAT = 2
LISTEN_MESSAGE_RESULT_HANDLED_REQUEST = 3


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
        self.bounce_count = -1
        self.request_id = None
        self.busy_lock = threading.Lock()

    def generate_request_id(self):
        prefix = self.socket_name[5:]
        request_id = "%s-%04X" % (prefix, randint(0, 0x10000))
        return request_id.encode('utf8')

    def setup_zmq_sockets(self):
        self.poller = zmq.Poller()
        self.socket = worker_socket(self.addr, self.z_context, self.poller)
        self.socket_name = self.socket.getsockopt_string(zmq.IDENTITY)
        self.liveness = HEARTBEAT_LIVENESS
        self.interval = INTERVAL_INIT
        self.heartbeat_at = time.time() + HEARTBEAT_INTERVAL

    def run(self):
        self.setup_zmq_sockets()
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
    def run_message_loop(self, send_heartbeat=True):
        timeout = (HEARTBEAT_INTERVAL * 1000) if send_heartbeat else None
        while True:
            result = self.listen_to_message_once(timeout)
            if result == LISTEN_MESSAGE_RESULT_INVALID:
                return None
            elif result == LISTEN_MESSAGE_RESULT_HEARTBEAT:
                self.liveness = HEARTBEAT_LIVENESS
            elif result == LISTEN_MESSAGE_RESULT_TIMEOUT:
                self.handle_heartbeat_timeout()

            if send_heartbeat and time.time() > self.heartbeat_at:
                self.send_heartbeat()

            if result not in [LISTEN_MESSAGE_RESULT_HEARTBEAT,
                              LISTEN_MESSAGE_RESULT_TIMEOUT,
                              LISTEN_MESSAGE_RESULT_HANDLED_REQUEST]:
                # We have a response
                return result

            if self.stopper.is_set():
                self.shutdown_socket()
                return None

    def listen_to_message_once(self, timeout=None):
        poller = self.poller
        socks = dict(poller.poll(timeout))
        if socks.get(self.socket) != zmq.POLLIN:
            return LISTEN_MESSAGE_RESULT_TIMEOUT

        #  Get message
        #  - 7-part envelope + content -> request
        #  - 1-part HEARTBEAT -> heartbeat
        frames = self.socket.recv_multipart()
        if len(frames) == 7:
            client = frames[0]
            assert frames[1] == b''
            message_type = frames[2]
            bounce_count = int(frames[3].decode('utf8'))
            request_id = frames[4]
            assert frames[5] == b''
            message = frames[6]

            self.request_id = request_id
            self.bounce_count = bounce_count
            self.liveness = HEARTBEAT_LIVENESS

            if message_type == PPP_REQUEST:
                self.mark_as_busy_if_needed()
                ctx = {
                    'bounce_count': bounce_count,
                    'request_id': request_id.decode('utf8'),
                }
                response = self.handle_message(message, ctx)
                self.socket.send_multipart([
                    client,
                    b'',
                    PPP_RESPONSE,
                    str(bounce_count).encode('utf8'),
                    request_id,
                    b'',
                    response,
                ])
                self.mark_as_not_busy_if_needed()
                return LISTEN_MESSAGE_RESULT_HANDLED_REQUEST
            elif message_type == PPP_RESPONSE:
                self.mark_as_not_busy_if_needed()
                self.bounce_count -= 1
                return message.decode('utf8')
        elif len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
            return LISTEN_MESSAGE_RESULT_HEARTBEAT
        else:
            log.warn(
                'Invalid message: %s, assuming socket dead', frames)
            return LISTEN_MESSAGE_RESULT_INVALID

    def mark_as_busy_if_needed(self):
        if self.bounce_count == 0:
            self.busy_lock.acquire()

    def mark_as_not_busy_if_needed(self):
        if self.bounce_count == 0:
            self.busy_lock.release()

    def handle_heartbeat_timeout(self):
        self.liveness -= 1
        if self.liveness == 0:
            log.warn('Heartbeat failure, can\'t reach queue')
            log.warn('Reconnecting in %0.2fs...' % self.interval)
            time.sleep(self.interval)

            if self.interval < INTERVAL_MAX:
                self.interval *= 2
            self.shutdown_socket(send_shutdown=False)
            self.socket = worker_socket(
                self.addr,
                self.z_context,
                self.poller
            )
            self.socket_name = self.socket.getsockopt_string(
                zmq.IDENTITY
            )
            self.liveness = HEARTBEAT_LIVENESS
            self.interval = INTERVAL_INIT

    def send_heartbeat(self):
        self.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        self.socket.send(PPP_HEARTBEAT)

    def shutdown_socket(self, send_shutdown=True):
        if send_shutdown:
            self.socket.send(PPP_SHUTDOWN)
        self.poller.unregister(self.socket)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()

    @_encoded
    def handle_message(self, req, extraContext={}):
        kind = req.get('kind')
        if kind == 'init':
            raise Exception('Init trigger is deprecated, '
                            'use init event instead')

        name = req.get('name')
        param = req.get('param', {})
        ctx = req.get('context', {})
        ctx.update(extraContext)

        if kind == 'provider':
            action = param.pop('action')
            return self.call_provider(ctx, name, action, param)
        elif kind == 'handler':
            return self.call_handler(ctx, name, param)
        elif kind == 'event':
            return self.call_event_func(name, param)
        else:
            return self.call_func(ctx, kind, name, param)

    def send_action(self, action_name, payload):
        if self.request_id is None:
            # Sending non-nested request
            self.request_id = self.generate_request_id()
        self.bounce_count += 1
        self.mark_as_busy_if_needed()
        message = {
            'method': 'POST',
            'payload': payload,
        }
        self.socket.send_multipart([
            self.socket_name.encode('utf8'),
            b'',
            PPP_REQUEST,
            str(self.bounce_count).encode('utf8'),
            self.request_id,
            b'',
            json.dumps(message).encode('utf8')
        ])
        return self.run_message_loop(send_heartbeat=False)


class OneOffWorker(Worker):

    def __init__(self, z_context, addr, stopper, registry=None,
                 action_name=None, payload={}):
        Worker.__init__(self, z_context, addr, stopper, registry=None)
        self.action_name = action_name
        self.payload = payload

    def run(self):
        self.setup_zmq_sockets()
        self._result = self.send_action(self.action_name, self.payload)
        self.shutdown_socket()

    def join(self):
        threading.Thread.join(self)
        return self._result


class ZmqTransport(CommonTransport):
    """
    ZmqTransport will start the working thread which run it own zmq socket.
    Since the zmq socket is not thread safe, the worker will be responabile for
    doing their own heartbeat to the keep alive. To skygear-server it just
    like multiple worker process.
    """

    def __init__(self, addr, context=None,
                 registry=None, threading=4, limit=10):
        super().__init__(registry)
        if context is None:
            context = zmq.Context()

        self._addr = addr
        self._context = context
        self._threading = threading
        self.threads = []
        self.threads_opened = 0
        self.limit = limit

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
            self.start_worker_at_index(i)

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
                self.start_worker_at_index(i)
            i = i + 1
            if i >= self._threading:
                i = 0
            busy_count = len(
                [t for t in self.threads if t.busy_lock.locked()]
            )
            if busy_count == self._threading and busy_count < self.limit:
                self.start_worker_at_index(self._threading)
                self._threading += 1

    def start_worker_at_index(self, index):
        t = Worker(self._context, self._addr, self.stopper)
        if index < len(self.threads):
            self.threads[index] = t
        else:
            self.threads.append(t)
        t.start()
        self.threads_opened = self.threads_opened + 1

    def stop(self):
        self.stopper.set()
        for t in self.threads:
            t.join()

    def send_action(self, action_name, payload, url=None, timeout=60):
        worker = threading.current_thread()
        if isinstance(worker, Worker):
            # Nested request
            result = worker.send_action(action_name, payload)
            return json.loads(result)

        new_worker = OneOffWorker(
            self._context,
            self._addr,
            self.stopper,
            action_name=action_name,
            payload=payload,
        )
        new_worker.start()
        result = new_worker.join()
        return json.loads(result)
