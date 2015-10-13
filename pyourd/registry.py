import logging

log = logging.getLogger(__name__)


def get_registry():
    return _registry


class Registry:
    """Registry holds a mapping of registred functions and their parameters that
    are callable by Ourd plugin system.

    Developers are not expected to create an instance directly. Instead, they
    should use the function get_registry() to the shared instance.
    """

    def __init__(self):
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
            'provider': [],
        }
        self.providers = {}

    def register(self, kind, name, func, *args, **kwargs):
        self.func_map[kind][name] = func
        if kind == 'handler':
            # TODO: param checking
            self.param_map['handler'][name] = kwargs
        elif kind == 'hook':
            del self.func_map[kind][name]
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

    def register_provider(self, provider_type, provider_id, provider,
                          **kwargs):
        kwargs['type'] = provider_type
        kwargs['id'] = provider_id
        self.param_map['provider'].append(kwargs)
        self.providers[provider_id] = provider

    def func_list(self):
        return self.param_map

    def get_obj(self, kind, name, type_=None):
        if kind == 'provider':
            return self.providers[name]
        elif type_:
            return self.func_map[kind]['%s:%s' % (type_, name)]
        else:
            return self.func_map[kind][name]

_registry = Registry()
