import json
import datetime
from .transmitter import get_transmitter


trans = get_transmitter()


def read_op_args(io):
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


def call_op(func, args):
    if isinstance(args, dict): 
        return func(**args)
    elif isinstance(args, list):
        return func(*args)
    else:
        msg = "Unsupported args type '{0}'".format(type(args))
        raise Exception(msg)


def op(name, *args, **kwargs):
    def our_op(func):
        def op_caller(io):
            args = read_op_args(io)
            output = call_op(func, args)
            io.write(json.dumps(output))
        trans.register("op", name, op_caller, *args, **kwargs)
        return func
    return our_op


def every(interval, name=None, *args, **kwargs):
    if isinstance(interval, datetime.timedelta):
        interval = "@every {0}s".format(interval.total_seconds())
    elif isinstance(interval, int):
        interval = "@every {0}s".format(interval)
    elif not isinstance(interval, str):
        msg = "Expecting int, timedelta or str for interval. Got '%s'." \
                .format(type(interval).__name__)
        raise Exception(msg)
    kwargs['spec'] = interval
    kwargs['name'] = name

    def our_every(func):
        name = kwargs.pop('name', None) or \
                func.__module__ + "." + func.__name__ 

        trans.register("timer", name, func, *args, **kwargs)
        return func
    return our_every


def handler(name, *args, **kwargs):
    def ourd_handler(func):
        trans.register("handler", name, func, *args, **kwargs)
        return func
    return ourd_handler


# preprocess record before passing it to the hook
# this function mutates the record dictionary directly
def preprocess_record(record):
    data = record['data']
    if data:
        del record['data']
        for key, value in data.items():
            record[key] = value


# postproess record before returning it for serialization
# this function mutates the record dictionary directly
def postprocess_record(record):
    data = {}
    deleting_keys = set()
    for key, value in record.items():
        if not key.startswith('_'):
            data[key] = value
            deleting_keys.add(key)
    for key in deleting_keys:
        del record[key]
    record['data'] = data


def hook(name, *args, **kwargs):
    def ourd_hook(func):
        def hook_caller(io, db):
            in_data = io.read()
            record = json.loads(in_data)

            preprocess_record(record)
            func(record, db)
            postprocess_record(record)

            out_data = json.dumps(record)
            io.write(out_data)

        trans.register("hook", name, hook_caller, *args, **kwargs)
        return func
    return ourd_hook
