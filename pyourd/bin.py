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
    get_transmitter('zmq')
    plugin = SourceFileLoader('plugin', options.plugin).load_module()
    print("Connecting to address %s" % options.ourd_address, file=sys.stdout)
    try:
        loop = asyncio.get_event_loop()
        # TODO: handling zmq event
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        loop.close()
