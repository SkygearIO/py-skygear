import json
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


def handler(name, *args, **kwargs):
    def ourd_handler(func):
        trans.register("handler", name, func, *args, **kwargs)
        return func
    return ourd_handler


def hook(name, *args, **kwargs):
    def ourd_hook(func):
        trans.register("hook", name, func, *args, **kwargs)
        return func
    return ourd_hook
