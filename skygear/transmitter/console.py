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
import os
import sys

from .common import CommonTransport, decode_base64_json

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
            self.write(json.dumps(self.init_info()))
        elif len(self.args) < 2:
            print("Missing param for %s", target, file=sys.stderr)
            sys.exit(1)
        else:
            param = json.loads(self.read())
            context_data = os.environ.get('SKYGEAR_CONTEXT')
            context = decode_base64_json(context_data) if context_data else {}
            if target == 'provider':
                output = self.call_provider(context, self.args[1],
                                            self.args[2], param)
            else:
                output = self.call_func(context, target, self.args[1], param)

            self.write(json.dumps(output))

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)
