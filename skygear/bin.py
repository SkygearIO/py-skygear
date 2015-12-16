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
import sys
from importlib.machinery import SourceFileLoader

import configargparse as argparse

from .container import SkygearContainer
from .registry import get_registry
from .transmitter import ConsoleTransport, ZmqTransport

log = logging.getLogger(__name__)


def get_arguments():
    ap = argparse.ArgumentParser(description='Skygear Plugin runner')
    ap.add_argument('--skygear-address', metavar='ADDR', action='store',
                    default='tcp://127.0.0.1:5555',
                    help="Binds to this socket for skygear",
                    env_var='SKYGEAR_ADDRESS')
    ap.add_argument('--skygear-endpoint', metavar='ENDPOINT', action='store',
                    default='http://127.0.0.1:3000',
                    help="Send to this addres for skygear handlers",
                    env_var='SKYGEAR_ENDPOINT')
    ap.add_argument('--apikey', metavar='APIKEY', action='store',
                    default=None,
                    help="API Key of the application",
                    env_var='SKYGEAR_APIKEY')
    ap.add_argument('--appname', metavar='APPNAME', action='store',
                    default='',
                    help="Application name of the skygear daemon",
                    env_var='SKYGEAR_APPNAME')
    ap.add_argument('--loglevel', action='store', default='INFO',
                    help="Log level")
    ap.add_argument('--subprocess', dest='subprocess', action='store',
                    nargs='+',
                    metavar=('(init|op|hook|handler|timer)', 'name'),
                    help='Trigger subprocess everytime for debug')
    ap.add_argument('plugin')

    return ap


def main():
    ap = get_arguments()
    options = ap.parse_args()
    setup_logging(options)
    run_plugin(options)


def run_plugin(options):
    if not options.plugin:
        log.error("Usage: py-skygear plugin.py")
        sys.exit(1)
    SourceFileLoader('plugin', options.plugin).load_module()

    SkygearContainer.set_default_app_name(options.appname)
    SkygearContainer.set_default_endpoint(options.skygear_endpoint)
    SkygearContainer.set_default_apikey(options.apikey)

    if options.subprocess is not None:
        return stdin(options.subprocess)

    log.info(
        "Connecting to address %s" % options.skygear_address)
    transport = ZmqTransport(options.skygear_address)
    transport.run()


stdin_usage = "Example usage: py-skygear sample.py --subprocess \
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


def setup_logging(options):
    # TODO: Make it load a stadard python logging config.
    logger = logging.getLogger()
    level = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }.get(options.loglevel, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('''\
%(asctime)s %(levelname)-5.5s \
[%(name)s:%(lineno)s][%(threadName)s] %(message)s\
''')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
