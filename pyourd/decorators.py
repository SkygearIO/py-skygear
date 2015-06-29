from .transmitter import get_transmitter

trans = get_transmitter()

def op(name, *args, **kwargs):
    def our_op(func):
        trans.register("op", name, func, *args, **kwargs)
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
