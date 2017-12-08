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
from collections import defaultdict
from copy import deepcopy

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
            'event': {},
        }
        self.param_map = {
            'op': [],
            'handler': [],
            'hook': [],
            'timer': [],
            'event': [],
            'provider': [],
        }
        self.handler = defaultdict(dict)
        self.providers = {}
        self.static_assets = {}
        self.exception_handlers = {}

    def _add_param_handler(self, param):
        new_param_list = []

        # Check existing param. Remove existing param if it overlaps with
        # the one being registered.
        for old_param in self.param_map['handler']:
            if not old_param.get('name') == param.get('name'):
                new_param_list.append(old_param)
                continue

            methods_intersection = set(old_param.get('methods')) & \
                set(param.get('methods'))

            if not methods_intersection:
                new_param_list.append(old_param)

        for method in param.get('methods'):
            new_param = deepcopy(param)
            new_param['methods'] = [method]
            new_param_list.append(new_param)
        self.param_map['handler'] = new_param_list

    def _add_param(self, kind, param):
        """
        Add a extension point param dict to the registry. If existing param
        dict overlaps the specified param dict, the existing param
        dict will be removed from the registry.

        An extension point param dict contains registration information of
        an extension point (i.e. cloud function).

        A param dict is an overlap of another when:
        - for handler: having the same name and method
        - others: having the same name
        """
        if kind == 'handler':
            return self._add_param_handler(param)

        param_list = self.param_map[kind]

        # Check existing param. Remove existing param if it overlaps with
        # the one being registered.
        for i in range(len(param_list)):
            if param_list[i].get('name') == param.get('name'):
                del param_list[i]
                break
        param_list.append(param)

    def register_hook(self, name, func, *args, **kwargs):
        if kwargs['type'] is None:
            raise ValueError("type is required for hook")
        if kwargs['trigger'] is None:
            raise ValueError("trigger is required for hook")
        kwargs['name'] = name

        if name in self.func_map['hook']:
            log.warning("Replacing previously registered hook '%s'.", name)

        self.func_map['hook'][name] = func
        self._add_param('hook', kwargs)

        log.debug("Registered hook '%s' to skygear!", name)

    def register_event(self, name, func, *args, **kwargs):
        if name in self.func_map['event']:
            log.warning("Replacing previously registered event handler '%s'",
                        name)

        self.func_map['event'][name] = func
        self._add_param('event', {
            'name': name
        })

    def register_op(self, name, func, *args, **kwargs):
        if name in self.func_map['op']:
            log.warning("Replacing previously registered lambda '%s'.", name)

        self.func_map['op'][name] = func
        self._add_param('op', {
            'name': name,
            'key_required': kwargs.get('key_required',
                                       kwargs.get('auth_required', False)),
            'user_required': kwargs.get('user_required', False),
        })

        log.debug("Registered lambda '%s' to skygear!", name)

    def register_timer(self, name, func, *args, **kwargs):
        kwargs['name'] = name

        if name in self.func_map['op']:
            log.warning("Replacing previously registered timer '%s'.", name)

        self.func_map['timer'][name] = func
        self._add_param('timer', kwargs)

        log.debug("Registered timer '%s' to skygear!", name)

    def register_handler(self, name, func, *args, **kwargs):
        methods = kwargs.get('method', ['GET', 'POST', 'PUT'])
        if isinstance(methods, str):
            methods = [methods]

        for m in methods:
            if m in self.handler[name]:
                log.warning(
                    "Replacing previously registered handler '%s' (%s).",
                    name,
                    m
                )
            self.handler[name][m] = func
        self._add_param('handler', {
            'name': name,
            'methods': methods,
            'key_required': kwargs.get('key_required', False),
            'user_required': kwargs.get('user_required', False),
        })

        log.debug("Registered handler '%s' (%s) to skygear!",
                  name,
                  ', '.join(methods))

    def register_provider(self, provider_type, provider_id, provider,
                          **kwargs):
        kwargs['type'] = provider_type
        kwargs['id'] = provider_id

        if provider_id in self.providers:
            log.warning("Replacing previously registered provider '%s'.",
                        provider_id)

        self.providers[provider_id] = provider
        self._add_param('provider', kwargs)

        log.debug("Registered provider '%s' to skygear!", provider_id)

    def register_static_assets(self, prefix, func):
        self.static_assets[prefix] = func

    def get_static_assets(self, request_path):
        for prefix, loader in self.static_assets.items():
            if request_path.startswith(prefix):
                subpath = request_path[len(prefix):]
                return loader(), subpath
        raise KeyError('Unable to find static assets loader with '
                       'request_path "{}"'.format(request_path))

    def func_list(self):
        return self.param_map

    def get_func(self, kind, name):
        return self.func_map[kind][name]

    def get_provider(self, name):
        return self.providers[name]

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
