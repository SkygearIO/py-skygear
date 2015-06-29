import sys
import logging
import json


log = logging.getLogger(__name__)


_single = None

def get_transmitter(media=None):
    global _single
    if not _single:
        if media is None:
            _single = ConsoleTransport(sys.stdin, sys.stdout)
    return _single


class ConsoleTransport(object):

    def __init__(self, stdin, stdout):
        log.debug("Setup ourd connection")
        self.input = stdin
        self.output = stdout
        self.func_map = {
            'op': {},
            'handler': {},
            'hook': {}
        }
        self.param_map = {
            'op': [],
            'handler': {},
            'hook': []
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
        else:
            self.param_map['op'].append(name)
            log.debug("Op param is not yet support, you will get the io")
        log.debug("Registering %s:%s to ourd!!", kind, name)

    def func_list(self):
        return self.output.write(json.dumps(self.param_map))

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)

    def op(self, command):
        return self.func_map['op'][command](self)

    def handler(self, end_point):
        _input = self.read()
        return self.func_map['handler'][end_point](_input, self)

    def hook(self, evt):
        _input = self.read()
        new_obj = self.func_map['hook'][evt](_input, None)
        log.debug("Got new Object", new_obj)
        self.write(new_obj)
