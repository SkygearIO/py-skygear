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

# `options` is the py-skygear options read from argv or os.environ.
options = argparse.Namespace()


def add_app_arguments(ap: argparse.ArgumentParser):
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


def add_skygear_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--skygear-address', metavar='ADDR', action='store',
                    default='tcp://127.0.0.1:5555',
                    help="Binds to this socket for skygear",
                    env_var='SKYGEAR_ADDRESS')
    ap.add_argument('--skygear-endpoint', metavar='ENDPOINT', action='store',
                    default='http://127.0.0.1:3000',
                    help="Send to this addres for skygear handlers",
                    env_var='SKYGEAR_ENDPOINT')
    ap.add_argument('--pubsub-url', action='store', default=None,
                    env_var='PUBSUB_URL',
                    help="The URL of the pubsub server, should start with "
                         "ws:// or wss:// and include the path")


def add_static_asset_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--collect-assets', metavar='DIST', action='store',
                    help="Collect static assets to a directory")
    ap.add_argument('--force-assets', action='store_true',
                    help="Remove dist folder before proceeding")
    ap.add_argument('--serve-static-assets', action='store_true',
                    env_var='SERVE_STATIC_ASSETS',
                    help="Enable to serve static asset from plugin process")
    ap.add_argument('--ignore-public-html', action='store_true',
                    env_var='IGNORE_PUBLIC_HTML',
                    help="Ignore public_html directory for static assets.")


def add_plugin_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--subprocess', dest='subprocess', action='store',
                    nargs='+',
                    metavar=('(init|op|hook|handler|timer)', 'name'),
                    help='Trigger subprocess everytime for debug')
    ap.add_argument('--http', action='store_true',
                    help='Trigger http web server',
                    env_var='HTTP')
    ap.add_argument('--http-addr', metavar='HTTP_ADDR', action='store',
                    default='0.0.0.0:8000',
                    help='Address where http web server listen to. In the \
                    format of {HOST}:{PORT}.',
                    env_var='HTTP_ADDR')
    ap.add_argument('--zmq-thread-pool', metavar='ZMQ_THREAD_POOL',
                    action='store',
                    default=4, type=int,
                    help='Number of thread in ZMQTransport thread pool',
                    env_var='ZMQ_THREAD_POOL')
    ap.add_argument('--zmq-thread-limit', metavar='ZMQ_THREAD_LIMIT',
                    action='store',
                    default=10, type=int,
                    help='Max number of thread in ZMQTransport thread pool',
                    env_var='ZMQ_THREAD_LIMIT')
    ap.add_argument('modules', nargs='*', default=[])  # env_var: LOAD_MODULES


def add_fs_asset_store_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--asset-store-url-prefix', action='store',
                    metavar='PREFIX', env_var='ASSET_STORE_URL_PREFIX',
                    help='URL prefix of fs asset store (Only applicable for fs \
                          asset store')
    ap.add_argument('--asset-store-secret', action='store', metavar='PATH',
                    env_var='ASSET_STORE_SECRET',
                    help='Secret for signing assets on fs asset store')


def add_s3_asset_store_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--asset-store-access-key', action='store', metavar='KEY',
                    env_var='ASSET_STORE_ACCESS_KEY',
                    help='Access key for s3 asset store')
    ap.add_argument('--asset-store-secret-key', action='store',
                    metavar='SECRET', env_var='ASSET_STORE_SECRET_KEY',
                    help='Secret key for s3 asset store')
    ap.add_argument('--asset-store-region', action='store', metavar='REGION',
                    env_var='ASSET_STORE_REGION',
                    help='Region for s3 asset store')
    ap.add_argument('--asset-store-bucket', action='store', metavar='BUCKET',
                    env_var='ASSET_STORE_BUCKET',
                    help='Bucket name for s3 asset store')
    ap.add_argument('--asset-store-s3-url-prefix', action='store',
                    metavar='PREFIX', env_var='ASSET_STORE_S3_URL_PREFIX',
                    help='URL prefix for S3 asset store')


def add_cloud_asset_store_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--cloud-asset-host', action='store', metavar='HOST',
                    env_var='CLOUD_ASSET_HOST',
                    help='Host of cloud asset store')
    ap.add_argument('--cloud-asset-token', action='store', metavar='TOKEN',
                    env_var='CLOUD_ASSET_TOKEN',
                    help='Token of cloud asset store')
    ap.add_argument('--cloud-asset-public-prefix', action='store',
                    metavar='PREFIX', env_var='CLOUD_ASSET_PUBLIC_PREFIX',
                    help='URL prefix of public asset on cloud asset store')
    ap.add_argument('--cloud-asset-private-prefix', action='store',
                    metavar='PREFIX', env_var='CLOUD_ASSET_PRIVATE_PREFIX',
                    help='URL prefix of private asset on cloud asset store')


def add_asset_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--asset-store', action='store', metavar='(fs|s3|cloud)',
                    default='fs', env_var='ASSET_STORE',
                    help='Type of asset store')
    ap.add_argument('--asset-store-public', action='store_true',
                    help='Make asset public accessible',
                    env_var='ASSET_STORE_PUBLIC')
    add_fs_asset_store_arguments(ap)
    add_s3_asset_store_arguments(ap)
    add_cloud_asset_store_arguments(ap)


def add_logging_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--loglevel', action='store', default='INFO',
                    help="Log level",
                    env_var='LOG_LEVEL')


def add_debug_arguments(ap: argparse.ArgumentParser):
    ap.add_argument('--debug', action='store_true',
                    help='Enable debugging features',
                    env_var='DEBUG')


def get_argument_parser():
    ap = argparse.ArgumentParser(description='Skygear Plugin runner')
    add_app_arguments(ap)
    add_skygear_arguments(ap)
    add_plugin_arguments(ap)
    add_asset_arguments(ap)
    add_static_asset_arguments(ap)
    add_logging_arguments(ap)
    add_debug_arguments(ap)
    return ap


def _module_name(name):
    if '~' in name and not name.endswith('~py'):
        return ''
    elif name.endswith('~py'):
        return name[:-3]
    else:
        return name


def _parse_load_modules_envvar(val):
    """
    Return a list of modules by parsing the LOAD_MODULES environment
    variable.

    The module name may be suffixed with a runtime specifier such as
    `~js` or `~py`. If a runtime specifier exists and the specified runtime
    is not python, the module will not be loaded.
    """
    if not val:
        return []

    modules = []
    if ':' in val:
        modules = val.split(':')
    elif ',' in val:
        modules = val.split(',')
    else:
        modules = val.split(' ')

    return [_module_name(m) for m in modules if _module_name(m)]


def parse_args():
    global options
    options = get_argument_parser().parse_args(namespace=options)

    # configargparse does not support env_var for positional argument,
    # therefore the LOAD_MODULES env_var is loaded manually.
    if not options.modules:
        options.modules = _parse_load_modules_envvar(os.getenv('LOAD_MODULES'))

    return options
