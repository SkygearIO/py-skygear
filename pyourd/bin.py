import sys
import argparse
import asyncio
from importlib.machinery import SourceFileLoader

from .transmitter import get_transmitter


def get_arguments():
    ap = argparse.ArgumentParser(description="Ourd Plugin runner")
    ap.add_argument('--ourd-address', metavar="ADDR", action='store',
                    help="Binds to Ourd using this socket",
                    default='127.0.0.1:3000')
    ap.add_argument('--subprocess', dest='subprocess', action='store',
                    nargs='*',
                    help='Trigger subprocess everytime for debug')
    ap.add_argument('plugin')

    return ap

def main():
    ap = get_arguments()
    options = ap.parse_args()
    run_plugin(options)


def run_plugin(options):
    if not options.plugin:
        print("Usage: pyourd plugin.py", file=sys.stderr)
        sys.exit(1)
    if options.subprocess is not None:
        SourceFileLoader('plugin', options.plugin).load_module()
        return stdin(options.subprocess)
    get_transmitter(options.transport)
    plugin = SourceFileLoader('plugin', options.plugin).load_module()
    print("Connecting to address %s" % options.ourd_address, file=sys.stdout)
    try:
        loop = asyncio.get_event_loop()
        # TODO: handling zmq event
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        loop.close()


stdin_usage = "Example usage: pyourd sample.py --subprocess \
init|{op script}|{hook name}|{handler name}|{timer func_name}"

def stdin(_input):
    if len(_input) < 1:
        print(stdin_usage, file=sys.stderr)
        sys.exit(1)
    target = _input[0]
    if target not in ['init', 'op', 'hook', 'handler', 'timer']:
        print("Only init, op, hook, handler and timer is support now",
            file=sys.stderr)
        sys.exit(1)
    transport = get_transmitter()
    if target == 'init':
        transport.func_list()
    elif len(_input) < 2:
        print("Missing param for %s", target, file=sys.stderr)
        sys.exit(1)
    else:
        command = _input[1]
        if target == 'op':
            transport.op(command)
        elif target == 'hook':
            transport.hook(command)
        elif target == 'handler':
            transport.handler(command)
        elif target == 'timer':
            transport.timer(command)
