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
import threading
import time
import unittest

import zmq

from ..transmitter.zmq import HEARTBEAT_INTERVAL, ZmqTransport

ZMQ_ADDR = 'tcp://0.0.0.0:12345'


class TestZmq(unittest.TestCase):
    def test_numebr_of_thread_startup(self):
        transport = ZmqTransport(ZMQ_ADDR, threading=5)
        transport.start()
        self.assertEqual(len(transport.threads), 5)
        for t in transport.threads:
            self.assertEqual(t.is_alive(), True)
        transport.stop()
        time.sleep(HEARTBEAT_INTERVAL * 2)
        for t in transport.threads:
            self.assertEqual(t.is_alive(), False)

    def test_worker_dead(self):
        t = threading.Thread(target=dead_router, args=(3,), daemon=True)
        t.start()
        transport = ZmqTransport(ZMQ_ADDR, threading=3)
        transport.start()
        liveness = [_t.is_alive() for _t in transport.threads]
        self.assertEqual(liveness, [True, True, True])
        time.sleep(HEARTBEAT_INTERVAL * 5)
        liveness = [_t.is_alive() for _t in transport.threads]
        self.assertEqual(liveness, [False, False, False])
        transport.stop()
        self.assertEqual(t.is_alive(), False)

    def test_maintain_worker_count(self):
        t = threading.Thread(target=dead_router, args=(3,), daemon=True)
        t.start()
        transport = ZmqTransport(ZMQ_ADDR, threading=3)
        transport.start()
        transport_t = threading.Thread(
            target=transport.maintain_workers_count,
            daemon=True)
        transport_t.start()
        liveness = [_t.is_alive() for _t in transport.threads]
        self.assertEqual(liveness, [True, True, True])
        time.sleep(HEARTBEAT_INTERVAL * 3)
        liveness = [_t.is_alive() for _t in transport.threads]
        self.assertEqual(liveness, [True, True, True])
        transport.stop()
        time.sleep(HEARTBEAT_INTERVAL)
        self.assertEqual(transport_t.is_alive(), False)
        self.assertEqual(t.is_alive(), False)


def dead_router(count):
    """
    This router will send malformed frame that crash the worker
    """
    context = zmq.Context()
    router = context.socket(zmq.ROUTER)
    router.bind(ZMQ_ADDR)
    poller = zmq.Poller()
    poller.register(router, zmq.POLLIN)
    i = 0
    while i < count:
        router.poll()
        frames = router.recv_multipart()
        if not frames:
            break
        frames.extend([b'good', b'bye'])
        router.send_multipart(frames)
        i = i + 1
    router.close()
