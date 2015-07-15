import json
import datetime
from .transmitter import get_transmitter

trans = get_transmitter()


def op(name, *args, **kwargs):
    def our_op(func):
        trans.register("op", name, func, *args, **kwargs)
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


def hook(name, *args, **kwargs):
    def ourd_hook(func):
        trans.register("hook", name, func, *args, **kwargs)
        return func
    return ourd_hook
