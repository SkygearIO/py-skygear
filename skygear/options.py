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
import os

import configargparse as argparse

options = argparse.Namespace()


def get_argument_parser():
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
                    env_var='API_KEY')
    ap.add_argument('--masterkey', metavar='MASTERKEY', action='store',
                    default=None,
                    help="Master Key of the application",
                    env_var='MASTER_KEY')
    ap.add_argument('--appname', metavar='APPNAME', action='store',
                    default='',
                    help="Application name of the skygear daemon",
                    env_var='APP_NAME')
    ap.add_argument('--loglevel', action='store', default='INFO',
                    help="Log level",
                    env_var='LOG_LEVEL')
    ap.add_argument('--subprocess', dest='subprocess', action='store',
                    nargs='+',
                    metavar=('(init|op|hook|handler|timer)', 'name'),
                    help='Trigger subprocess everytime for debug')
    ap.add_argument('--http', action='store_true',
                    help='Trigger http web server',
                    env_var='HTTP')
    ap.add_argument('--http-addr', metavar='HTTP_ADDR', action='store',
                    default='0.0.0.0:8000',
                    help='Address where htp web server listen to',
                    env_var='HTTP_ADDR')
    ap.add_argument('--debug', action='store_true',
                    help='Enable debugging features',
                    env_var='DEBUG')
    ap.add_argument('--collect-assets', metavar='DIST', action='store',
                    help="Collect static assets to a directory")
    ap.add_argument('--force-assets', action='store_true',
                    help="Remove dist folder before proceeding")
    ap.add_argument('--serve-static-assets', action='store_true',
                    env_var='SERVE_STATIC_ASSETS',
                    help="Enable to serve static asset from plugin process")
    ap.add_argument('--pubsub-url', action='store', default=None,
                    env_var='PUBSUB_URL',
                    help="The URL of the pubsub server, should start with "
                         "ws:// or wss:// and include the path")
    ap.add_argument('modules', nargs='*', default=[])  # env_var: LOAD_MODULES
    return ap


def _parse_load_modules_envvar(val):
    if not val:
        return []

    if ':' in val:
        return val.split(':')
    elif ',' in val:
        return val.split(',')
    else:
        return val.split(' ')


def parse_args():
    global options
    options = get_argument_parser().parse_args(namespace=options)

    # configargparse does not support env_var for positional argument,
    # therefore the LOAD_MODULES env_var is loaded manually.
    if not options.modules:
        options.modules = _parse_load_modules_envvar(os.getenv('LOAD_MODULES'))

    return options
