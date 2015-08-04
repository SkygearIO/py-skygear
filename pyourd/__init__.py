import sys

from .decorators import hook, handler, op, every, provides
from .transmitter import get_transmitter

__all__ = [hook, handler, op, every, provides]


def stdin():
    _input = sys.argv
    if len(_input) <= 1:
        print("Example usage: python sample.py init|{op script}|{hook name}|{handler name}|{timer func_name}|{provider provider_id action}")
        sys.exit(1)
    target = _input[1]
    if target not in ['init', 'op', 'hook', 'handler', 'timer', 'provider']:
        print("Only init, op, hook, handler, timer and provider is support now")
        sys.exit(1)
    transport = get_transmitter()
    if target == 'init':
        transport.func_list()
    elif len(_input) <= 2:
        print("Missing param for %s", target)
        sys.exit(1)
    else:
        command = _input[2]
        if target == 'op':
            transport.op(command)
        elif target == 'hook':
            transport.hook(command)
        elif target == 'handler':
            transport.handler(command)
        elif target == 'timer':
            transport.timer(command)
        elif target == 'provider':
            if len(_input) <= 3:
                sys.stdout.write("Missing provider action.\n")
            action = _input[3]
            transport.provider(command, action)
