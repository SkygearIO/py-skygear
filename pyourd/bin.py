import argparse
import json
from importlib.machinery import SourceFileLoader
import sys

from .registry import get_registry
from .transmitter import (
    ConsoleTransport,
    ZmqTransport,
)


def get_arguments():
    ap = argparse.ArgumentParser(description="Ourd Plugin runner")
    ap.add_argument('--ourd-address', metavar="ADDR", action='store',
                    help="Binds to this socket for ourd",
                    default='tcp://127.0.0.1:6543')
    ap.add_argument('--subprocess', dest='subprocess', action='store',
                    nargs='+',
                    metavar=('(init|op|hook|handler|timer)', 'name'),
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
    SourceFileLoader('plugin', options.plugin).load_module()

    if options.subprocess is not None:
        return stdin(options.subprocess)

    print("Connecting to address %s" % options.ourd_address, file=sys.stdout)
    transport = ZmqTransport('tcp://127.0.0.1:5555')
    transport.run()


stdin_usage = "Example usage: pyourd sample.py --subprocess \
init|{op script}|{hook name}|{handler name}|{timer func_name}"


def stdin(_input):
    target = _input[0]
    if target not in ['init', 'op', 'hook', 'handler', 'timer', 'provider']:
        print("Only init, op, hook, handler, timer and provider is support now",
            file=sys.stderr)
        sys.exit(1)
    transport = ConsoleTransport()
    if target == 'init':
        json.dump(get_registry().func_list(), sys.stdout)
    elif len(_input) < 2:
        print("Missing param for %s", target, file=sys.stderr)
        sys.exit(1)
    else:
        transport.handle_call(target, *_input[1:])
