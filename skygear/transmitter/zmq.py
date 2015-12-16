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

from ..registry import get_registry
from .common import _get_engine
from .encoding import _serialize_exc, deserialize_or_none, serialize_record

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


class ZmqTransport:
    """ZmqTransport implements the Paranoid-Pirate worker described in the zguide:
    http://zguide.zeromq.org/py:all#Robust-Reliable-Queuing-Paranoid-Pirate-Pattern
    """

    def __init__(self, addr, context=None, registry=None):
        if context is None:
            context = zmq.Context()
        if registry is None:
            registry = get_registry()

        self._addr = addr
        self._context = context
        self._registry = registry

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
        if kind == 'init':
            return self._registry.func_list()

        name = req['name']
        param = req.get('param')

        resp = {}
        try:
            resp['result'] = self.call_func(kind, name, param)
        except Exception as e:
            log.exception("Error occurred in call_func")
            resp['error'] = _serialize_exc(e)

        return resp

    # the following methods are almost exactly the same as their counterpart
    # of ConsoleTransport, which probably can be factored out

    def call_func(self, kind, name, param):
        # derive args and kwargs
        if kind == 'op':
            param = param.get('args', {})
            obj = self._registry.get_obj(kind, name)
            if isinstance(param, list):
                args = param
                kwargs = {}
            elif isinstance(param, dict):
                args = []
                kwargs = param
            else:
                msg = "Unsupported args type '{0}'".format(type(param))
                raise ValueError(msg)

            return self.op(obj, *args, **kwargs)
        elif kind == 'handler':
            obj = self._registry.get_obj(kind, name)
            return self.handler(obj)
        elif kind == 'hook':
            record_type = param['record']['_id'].split('/')[0]
            obj = self._registry.get_obj(kind, name, record_type)
            return self.hook(obj, param)
        elif kind == 'timer':
            obj = self._registry.get_obj(kind, name)
            return self.timer(obj)
        elif kind == 'provider':
            obj = self._registry.get_obj(kind, name)
            action = param['action']
            return self.provider(obj, action, param)

        return obj, args, kwargs

    def op(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def handler(self, func):
        return func()

    def hook(self, func, param):
        original_record = deserialize_or_none(param.get('original', None))
        record = deserialize_or_none(param.get('record', None))
        with _get_engine().begin() as conn:
            func(record, original_record, conn)
        return serialize_record(record)

    def timer(self, func):
        return func()

    def provider(self, provider, action, data):
        return provider.handle_action(action, data)
