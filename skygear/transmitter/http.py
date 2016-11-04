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

from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from .common import CommonTransport
from .encoding import _serialize_exc

log = logging.getLogger(__name__)


class HttpTransport(CommonTransport):
    """
    HttpTransport implements a transport protocol between skygear and
    plugin that communicates over a HTTP connection.
    """

    def _url_map(self):
        """
        Returns a URL routing map.
        """
        return Map([
            Rule('/', endpoint='_'),
            ])

    def __init__(self, addr, registry=None, debug=False):
        super().__init__(registry)
        self.url_map = self._url_map()
        if ':' in addr:
            hostname, port = addr.split(':', 2)
        else:
            hostname = addr
            port = 8000
        self.hostname = hostname.strip() if hostname.strip() else '0.0.0.0'
        try:
            self.port = int(port)
        except:
            self.port = 8000
        self.debug = debug

    @Request.application
    def dispatch(self, request):
        """
        Application from the view of the plugin web server.
        """

        # Returns an HTTP response in JSON format
        try:
            output = self._dispatch(request)
        except Exception as e:
            log.exception("exception while handling request")
            output = dict(error=_serialize_exc(e).as_dict())
        return Response(json.dumps(output), mimetype="application/json")

    def _dispatch(self, request):
        """
        Dispatches request to a plugin extension point function.
        """
        kind, name, ctx, param = self.read_request(request)
        if kind == 'init':
            raise Exception('Init trigger is deprecated, '
                            'use init event instead')
        elif kind == 'provider':
            action = param.pop('action')
            return self.call_provider(ctx, name, action, param)
        elif kind == 'handler':
            return self.call_handler(ctx, name, param)
        elif kind == 'event':
            return self.call_event_func(name, param)
        else:
            return self.call_func(ctx, kind, name, param)

    def read_request(self, request):
        """
        Reads and returns HTTP request.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        _, values = adapter.match()

        request_data = request.get_data(as_text=True)
        req = json.loads(request_data) if request_data else {}

        kind = req.get('kind')
        name = req.get('name')
        param = req.get('param', {})
        ctx = req.get('context', {})

        return kind, name, ctx, param

    def run(self):
        """
        Start the web server.
        """
        run_simple(self.hostname, self.port, self.dispatch,
                   threaded=True,
                   use_reloader=self.debug)
