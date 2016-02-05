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
import base64
import json

from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from .common import CommonTransport
from .encoding import _serialize_exc


def encode_base64_json(data):
    """
    Encode dict-like data into a base64 encoded JSON string.

    This can be used to put dict-like data into HTTP headers.
    """
    return base64.b64encode(bytes(json.dumps(data), 'utf-8'))


def decode_base64_json(data):
    """
    Decode dict-like data from a base64 encoded JSON string.

    This can be used to get dict-like data into HTTP headers.
    """
    return json.loads(base64.b64decode(data).decode('utf-8'))


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
            Rule('/init', endpoint='init'),
            Rule('/op/<name>', endpoint='op'),
            Rule('/hook/<name>', endpoint='hook'),
            Rule('/provider/<name>/<action>', endpoint='provider'),
            Rule('/timer/<name>', endpoint='timer'),
        ])

    def __init__(self, addr, registry=None):
        super().__init__(registry)
        self.url_map = self._url_map()

    @Request.application
    def dispatch(self, request):
        """
        Application from the view of the plugin web server.
        """

        # Returns an HTTP response in JSON format
        try:
            output = self._dispatch(request)
        except Exception as e:
            self.logger.exception("exception while handling request")
            output = dict(error=_serialize_exc(e).as_dict())
        return Response(json.dumps(output), mimetype="application/json")

    def _dispatch(self, request):
        """
        Dispatches request to a plugin extension point function.
        """
        endpoint, values, context, param = self.read_request(request)
        if endpoint == 'init':
            return self.init_info()
        else:
            if endpoint == 'provider':
                return self.call_provider(context, values['name'],
                                          values['action'], param)
            else:
                return self.call_func(context, endpoint, values['name'], param)

    def read_request(self, request):
        """
        Reads and returns HTTP request.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()

        request_data = request.get_data(as_text=True)
        param = json.loads(request_data) if request_data else {}

        context_data = request.headers.get('X-Skygear-Plugin-Context')
        context = decode_base64_json(context_data) if context_data else {}

        return endpoint, values, context, param

    def run(self):
        """
        Start the web server.
        """
        run_simple('0.0.0.0', 8000, self.dispatch)
