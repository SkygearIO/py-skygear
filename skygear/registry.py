# Copyright 2015 Oursky Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

log = logging.getLogger(__name__)


def get_registry():
    return _registry


def _iter_class_hierarchy(klass):
    klasses = [klass]
    while klasses:
        cls = klasses.pop()
        yield cls
        klasses += list(cls.__bases__)


class Registry:
    """Registry holds a mapping of registred functions and their parameters that
    are callable by Skygear plugin system.

    Developers are not expected to create an instance directly. Instead, they
    should use the function get_registry() to the shared instance.
    """

    def __init__(self):
        self.func_map = {
            'op': {},
            'hook': {},
            'timer': {},
        }
        self.param_map = {
            'op': [],
            'handler': [],
            'hook': [],
            'timer': [],
            'provider': [],
        }
        self.handler = {}
        self.providers = {}
        self.static_assets = {}
        self.exception_handlers = {}

    def register(self, kind, name, func, *args, **kwargs):
        if kind == 'handler':
            return self._register_handler(name, func, kwargs)
        self.func_map[kind][name] = func
        if kind == 'hook':
            if kwargs['type'] is None:
                raise ValueError("type is required for hook")
            if kwargs['trigger'] is None:
                raise ValueError("trigger is required for hook")
            kwargs['name'] = name
            self.param_map['hook'].append(kwargs)
        elif kind == 'op':
            self.param_map['op'].append({
                'name': name,
                'auth_required': kwargs.get('auth_required',
                                            kwargs.get('key_required', False)),
                'user_required': kwargs.get('user_required', False),
                })
        elif kind == 'timer':
            kwargs['name'] = name
            self.param_map['timer'].append(kwargs)
        else:
            raise Exception("Unrecognized transport kind '%d'.".format(kind))

        log.debug("Registering %s:%s to skygear!!", kind, name)

    def _register_handler(self, name, func, kwargs):
        methods = kwargs.get('method', ['GET', 'POST', 'PUT'])
        if isinstance(methods, str):
            methods = [methods]
        self.param_map['handler'].append({
            'name': name,
            'methods': methods,
            'key_required': kwargs.get('key_required', False),
            'user_required': kwargs.get('user_required', False),
        })
        if name not in self.handler:
            self.handler[name] = {}
        for m in methods:
            self.handler[name][m] = func

    def register_provider(self, provider_type, provider_id, provider,
                          **kwargs):
        kwargs['type'] = provider_type
        kwargs['id'] = provider_id
        self.param_map['provider'].append(kwargs)
        self.providers[provider_id] = provider

    def register_static_assets(self, prefix, func):
        self.static_assets[prefix] = func

    def get_static_assets(self, request_path):
        for prefix, loader in self.static_assets.items():
            if request_path.startswith(prefix):
                subpath = request_path[len(prefix)+1:]
                return loader(), subpath
        raise KeyError('Unable to find static assets loader with '
                       'request_path "{}"'.format(request_path))

    def func_list(self):
        return self.param_map

    def get_obj(self, kind, name):
        if kind == 'provider':
            return self.providers[name]
        else:
            return self.func_map[kind][name]

    def get_handler(self, name, method):
        return self.handler[name].get(method, None)

    def get_exception_handler(self, klass):
        for cls in _iter_class_hierarchy(klass):
            if cls in self.exception_handlers:
                return self.exception_handlers[cls]
        return None

    def register_exception_handler(self, klass, func):
        self.exception_handlers[klass] = func


_registry = Registry()
