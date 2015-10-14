import argparse
import json
from importlib.machinery import SourceFileLoader
import sys

from .registry import get_registry
from .transmitter import (
    ConsoleTransport,
    ZmqTransport,
)
from .container import SkygearContainer


def get_arguments():
    ap = argparse.ArgumentParser(description='Skygear Plugin runner')
    ap.add_argument('--skygear-address', metavar='ADDR', action='store',
                    default='tcp://127.0.0.1:5555',
                    help="Binds to this socket for skygear")
    ap.add_argument('--skygear-endpoint', metavar='ENDPOINT', action='store',
                    default='http://127.0.0.1:3000',
                    help="Send to this addres for skygear handlers")
    ap.add_argument('--apikey', metavar='APIKEY', action='store',
                    default=None,
                    help="API Key of the application")
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
        print("Usage: pyskygear plugin.py", file=sys.stderr)
        sys.exit(1)
    SourceFileLoader('plugin', options.plugin).load_module()

    SkygearContainer.set_default_endpoint(options.skygear_endpoint)
    SkygearContainer.set_default_apikey(options.apikey)

    if options.subprocess is not None:
        return stdin(options.subprocess)

    print("Connecting to address %s" % options.skygear_address, file=sys.stdout)
    transport = ZmqTransport(options.skygear_address)
    transport.run()


stdin_usage = "Example usage: pyskygear sample.py --subprocess \
init|{op script}|{hook name}|{handler name}|{timer func_name}"


def stdin(_input):
    target = _input[0]
    if target not in ['init', 'op', 'hook', 'handler', 'timer', 'provider']:
        print(
            "Only init, op, hook, handler, timer and provider is support now",
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
