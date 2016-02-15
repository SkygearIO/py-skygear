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
import logging
import signal
import sys
from importlib.machinery import SourceFileLoader

from .container import SkygearContainer
from .options import parse_args
from .transmitter import ConsoleTransport, HttpTransport, ZmqTransport

log = logging.getLogger(__name__)


def main():
    options = parse_args()
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

    log.debug("Install signal handler for SIGTERM")
    signal.signal(signal.SIGTERM, sigterm_handler)

    if options.subprocess is not None:
        transport = ConsoleTransport(options.subprocess)
    elif options.http:
        transport = HttpTransport(options.http_addr, debug=options.debug)
    else:
        log.info(
            "Connecting to address %s" % options.skygear_address)
        transport = ZmqTransport(options.skygear_address)
    transport.run()


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


def sigterm_handler(signum, frame):
    """
    When docker stops the container, it sends PID 1 with SIGTERM.
    This function exits the program when SIGTERM is received.

    Remember not to run this program in a shell as PID 1 because the shell may
    not forward the signal.
    """
    sys.exit(1)
