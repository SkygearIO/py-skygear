import logging
import json
import sys

from ..registry import get_registry
from .common import _get_engine
from .encoding import (
    deserialize_record,
    serialize_record,
    _serialize_exc,
)

log = logging.getLogger(__name__)


# a decorator intended to be used in ConsoleTransport's member method.
# it encapsulates return value or exception thrown into a response,
# then write it to the console
def _serialize(func):
    def serialize_with_exc(self, *args, **kwargs):
        d = {}
        try:
            d['result'] = func(self, *args, **kwargs)
        except Exception as e:
            d['error'] = _serialize_exc(e)
        self.write(json.dumps(d))

    return serialize_with_exc


class ConsoleTransport:

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, registry=None):
        if registry is None:
            registry = get_registry()
        self._registry = registry

        self.input = stdin
        self.output = stdout

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)

    @_serialize
    def handle_call(self, kind, name, *args):
        param = json.loads(self.read())

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
            return self.provider(obj, args[0], param)

        return obj, args, kwargs

    def op(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def handler(self, func):
        return func()

    def hook(self, func, record_dict):
        record = deserialize_record(record_dict)
        with _get_engine().begin() as conn:
            func(record, conn)
        return serialize_record(record)

    def timer(self, func):
        return func()

    def provider(self, provider, action, data):
        return provider.handle_action(action, data)
