import sys

from .console import ConsoleTransport
from .zmq import ZmqTransport


__all__ = ['get_transmitter', 'ConsoleTransport', 'ZmqTransport']

_single = None


def get_transmitter(media=None, options=None):
    global _single
    if options is None:
        options = {}
    if not _single:
        if media is None:
            _single = ConsoleTransport(sys.stdin, sys.stdout)
        elif media == 'console':
            _single = ConsoleTransport(sys.stdin, sys.stdout)
        elif media == 'zmq':
            _single = ZmqTransport('tcp://127.0.0.1:5555')
    return _single
