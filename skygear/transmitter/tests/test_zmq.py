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

from ...transmitter.zmq import (HEARTBEAT_INTERVAL, HEARTBEAT_LIVENESS,
                                ZmqTransport)


class TestZmq(unittest.TestCase):
    def test_numebr_of_thread_startup(self):
        context = zmq.Context()
        transport = ZmqTransport('tcp://0.0.0.0:12345',
                                 context=context,
                                 threading=5)
        transport.start()
        self.assertEqual(len(transport.threads), 5)
        for t in transport.threads:
            self.assertEqual(t.is_alive(), True)
        transport.stop()
        for t in transport.threads:
            self.assertEqual(t.is_alive(), False)
        context.destroy()

    def test_worker_dead(self):
        context = zmq.Context()
        t = threading.Thread(target=dead_router,
                             args=(context, 'tcp://0.0.0.0:23456', 3,))
        t.start()
        transport = ZmqTransport('tcp://0.0.0.0:23456',
                                 context=context,
                                 threading=3)
        transport.start()
        transport.stop()
        time.sleep(HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS * 2)
        alive_threads = [_t for _t in transport.threads if _t.is_alive()]
        self.assertEqual(len(alive_threads), 0)
        self.assertEqual(transport.threads_opened, 3)
        t.join()
        context.destroy()

    def test_maintain_worker_count(self):
        context = zmq.Context()
        t = threading.Thread(target=dead_router,
                             args=(context, 'tcp://0.0.0.0:34567', 3,))
        t.start()
        transport = ZmqTransport('tcp://0.0.0.0:34567',
                                 context=context,
                                 threading=3)
        transport.start()
        transport_t = threading.Thread(
            target=transport.maintain_workers_count)
        transport_t.start()
        time.sleep(HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS * 2)
        alive_threads = [_t for _t in transport.threads if _t.is_alive()]
        self.assertEqual(len(alive_threads), 3)
        transport.stop()
        transport_t.join()
        self.assertEqual(transport_t.is_alive(), False)
        alive_threads = [_t for _t in transport.threads if _t.is_alive()]
        self.assertEqual(len(alive_threads), 0)
        self.assertEqual(transport.threads_opened, 6)
        t.join()
        context.destroy()


def dead_router(context, addr, count):
    """
    This router will send malformed frame that crash the worker
    """
    router = context.socket(zmq.ROUTER)
    router.bind(addr)
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
