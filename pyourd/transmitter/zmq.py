import zmq

import json
import logging

from .encoding import (
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

    def __init__(self, addr, context=None):
        if context is None:
            context = zmq.Context()
        self._context = context

        self._socket = context.socket(zmq.REP)
        self._socket.connect(addr)

        self.func_map = {
            'op': {},
            'handler': {},
            'hook': {},
            'timer': {},
        }
        self.param_map = {
            'op': [],
            'handler': {},
            'hook': [],
            'timer': [],
        }

    def register(self, kind, name, func, *args, **kwargs):
        self.func_map[kind][name] = func
        if kind == 'handler':
            # TODO: param checking
            self.param_map['handler'][name] = kwargs
        elif kind == 'hook':
            if kwargs['type'] is None:
                raise ValueError("type is required for hook")
            self.func_map[kind][kwargs['type'] + ':' + name] = func
            kwargs['trigger'] = name
            self.param_map['hook'].append(kwargs)
        elif kind == 'op':
            self.param_map['op'].append(name)
            log.debug("Op param is not yet support, you will get the io")
        elif kind == 'timer':
            kwargs['name'] = name
            self.param_map['timer'].append(kwargs)
        else:
            raise Exception("Unrecognized transport kind '%d'.".format(kind))

        log.debug("Registering %s:%s to ourd!!", kind, name)

    def func_list(self):
        return self.param_map

    def run(self):
        while True:
            message = self._socket.recv()
            response = self.handle_message(message)
            self._socket.send(response)

    @_encoded
    def handle_message(self, req):
        kind = req['kind']
        if kind == 'init':
            return self.func_list()

        func, args, kwargs = self._get_func(kind, req)
        resp = {}
        try:
            resp['result'] = func(*args, **kwargs)
        except Exception as e:
            resp['error'] = _serialize_exc(e)

        return resp

    def _get_func(self, kind, req):
        name = req['name']
        func = self.func_map[kind][name]

        # derive args and kwargs
        if kind == 'op':
            _args = req.get('args', [])
            if isinstance(_args, list):
                args = _args
                kwargs = {}
            elif isinstance(_args, dict):
                args = []
                kwargs = _args
        elif kind == 'handler':
            args = [req['input']]
            kwargs = {}
        elif kind == 'hook':
            args = [req['record']]
            kwargs = {}
        elif kind == 'timer':
            args = []
            kwargs = {}

        return func, args, kwargs
