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

from .. import config as skyconfig
from .. import error as skyerr
from .common import CommonTransport, dict_from_base64_environ

log = logging.getLogger(__name__)


ACCEPTED_TARGETS = ['init', 'op', 'hook', 'handler', 'timer', 'provider']


class ConsoleTransport(CommonTransport):
    def __init__(self, args, stdin=sys.stdin, stdout=sys.stdout,
                 registry=None):
        super().__init__(registry)
        self.args = args

        self.input = stdin
        self.output = stdout

    def run(self):
        self.args = self.args
        target = self.args[0]
        if target not in ACCEPTED_TARGETS:
            print("Only init, op, hook, handler, timer and provider is"
                  " supported now", file=sys.stderr)
            sys.exit(1)
        if target == 'init':
            self.writeJSON(self.init_info())
        elif len(self.args) < 2:
            print("Missing param for %s", target, file=sys.stderr)
            sys.exit(1)
        else:
            try:
                self.handle_command(target, self.args)
            except skyerr.SkygearException as e:
                self.writeJSON(e.as_dict())

    def handle_command(self, target, args):
        param = self.readJSON()
        context = dict_from_base64_environ('SKYGEAR_CONTEXT')
        skyconfig.parse_config(dict_from_base64_environ('SKYGEAR_CONFIG'))

        if target == 'provider':
            output = self.call_provider(context, args[1], args[2], param)
        elif target == 'handler':
            output = self.call_handler(context, args[1], param)
        else:
            output = self.call_func(context, target, args[1], param)

        self.writeJSON(output)

    def readJSON(self):
        data = self.read()
        if not data:
            return {}
        try:
            return json.loads(data)
        except ValueError:
            msg = "unable to parse JSON string"
            logging.exception(msg)
            raise skyerr.SkygearException(msg, skyerr.UnexpectedError)

    def writeJSON(self, data):
        try:
            self.write(json.dumps(data))
        except TypeError:
            msg = "unable to serialize obj to JSON string"
            logging.exception(msg)
            raise skyerr.SkygearException(msg, skyerr.UnexpectedError)

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)
