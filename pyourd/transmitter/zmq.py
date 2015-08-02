import zmq

import json
import logging

from ..registry import (
    get_registry
)
from .encoding import (
    deserialize_record,
    serialize_record,
    _serialize_exc,
)


log = logging.getLogger(__name__)


def _encoded(func):
    def encoded(self, input):
        decoded = input.decode('utf-8')
        deserialized = json.loads(decoded)

        retval = func(self, deserialized)

        serialized = json.dumps(retval)
        out = serialized.encode('utf-8')
        return out
    return encoded


class ZmqTransport:

    def __init__(self, addr, context=None, registry=None):
        if context is None:
            context = zmq.Context()
        if registry is None:
            registry = get_registry()

        self._registry = registry

        self._context = context
        self._socket = context.socket(zmq.REP)
        self._socket.connect(addr)

    def run(self):
        while True:
            message = self._socket.recv()
            response = self.handle_message(message)
            self._socket.send(response)

    @_encoded
    def handle_message(self, req):
        kind = req['kind']
        if kind == 'init':
            return self._registry.func_list()

        name = req['name']
        param = req.get('param')

        resp = {}
        try:
            resp['result'] = self.call_func(kind, name, param)
        except Exception as e:
            resp['error'] = _serialize_exc(e)

        return resp

    # the following methods are almost exactly the same as their counterpart
    # of ConsoleTransport, which probably can be factored out

    def call_func(self, kind, name, param):
        obj = self._registry.get_obj(kind, name)

        # derive args and kwargs
        if kind == 'op':
            if isinstance(param, list):
                args = param
                kwargs = {}
            elif isinstance(param, dict):
                args = []
                kwargs = param
            else:
                msg = "Unsupported args type '{0}'".format(type(param))
                raise ValueError(msg)

            return self.op(obj, *args, **kwargs)
        elif kind == 'handler':
            return self.handler(obj)
        elif kind == 'hook':
            return self.hook(obj, param)
        elif kind == 'timer':
            return self.timer(obj)
        elif kind == 'provider':
            action = param['action']
            return self.provider(obj, action, param)

        return obj, args, kwargs

    def op(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def handler(self, func):
        return func()

    def hook(self, func, record_dict):
        record = deserialize_record(record_dict)
        func(record)
        return serialize_record(record)

    def timer(self, func):
        return func()

    def provider(self, provider, action, data):
        return provider.handle_action(action, data)
