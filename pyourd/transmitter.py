import sys
import logging
import json
import traceback

log = logging.getLogger(__name__)

_single = None


def get_transmitter(media=None):
    global _single
    if not _single:
        if media is None:
            _single = ConsoleTransport(sys.stdin, sys.stdout)
    return _single


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


def _serialize_exc(e):
    return {
        'name': str(e),
        'desc': traceback.format_exc(),
    }


def _read_op_args(io):
    in_data = io.read()
    if in_data:
        try:
            payload = json.loads(in_data)
            args = payload['args']
        except:
            args = []
    else:
        args = []
    return args


def _call_op(func, args):
    if isinstance(args, dict):
        return func(**args)
    elif isinstance(args, list):
        return func(*args)
    else:
        msg = "Unsupported args type '{0}'".format(type(args))
        raise Exception(msg)


# preprocess record before passing it to the hook
# this function mutates the record dictionary directly
def _preprocess_record(record):
    data = record['data']
    if data:
        del record['data']
        for key, value in data.items():
            record[key] = value


# postproess record before returning it for serialization
# this function mutates the record dictionary directly
def _postprocess_record(record):
    data = {}
    deleting_keys = set()
    for key, value in record.items():
        if not key.startswith('_'):
            data[key] = value
            deleting_keys.add(key)
    for key in deleting_keys:
        del record[key]
    record['data'] = data


class ConsoleTransport(object):

    def __init__(self, stdin, stdout):
        log.debug("Setup ourd connection")
        self.input = stdin
        self.output = stdout
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
        return self.output.write(json.dumps(self.param_map))

    def read(self):
        if not self.input.isatty():
            return "".join(self.input)
        else:
            return ""

    def write(self, obj, format='text'):
        return self.output.write(obj)

    @_serialize
    def op(self, command):
        func = self.func_map['op'][command]

        args = _read_op_args(self)
        output = _call_op(func, args)

        return output

    @_serialize
    def handler(self, end_point):
        _input = self.read()
        return self.func_map['handler'][end_point](_input, self)

    @_serialize
    def hook(self, evt):
        func = self.func_map['hook'][evt]

        in_data = self.read()
        record = json.loads(in_data)
        _preprocess_record(record)

        func(record, None)

        _postprocess_record(record)
        return record

    @_serialize
    def timer(self, name):
        return self.func_map['timer'][name](self)
