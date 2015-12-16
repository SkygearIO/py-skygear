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
import datetime

from .registry import get_registry

_registry = get_registry()


def op(name, *args, **kwargs):
    def our_op(func):
        _registry.register("op", name, func, *args, **kwargs)
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

        _registry.register("timer", name, func, *args, **kwargs)
        return func
    return our_every


def handler(name, *args, **kwargs):
    def skygear_handler(func):
        _registry.register("handler", name, func, *args, **kwargs)
        return func
    return skygear_handler


def hook(name, *args, **kwargs):
    def skygear_hook(func):
        def hook_func(record, original_record, db):
            # return the record for user
            func(record, original_record, db)
            return record

        _registry.register("hook", name, hook_func, *args, **kwargs)
        return func

    return skygear_hook


def register_save_hook(name, func, *args, **kwargs):
    def hook_func(record, original_record, db):
        func(record, original_record, db)
        return record
    _registry.register("hook", name, hook_func, *args, **kwargs)


def register_delete_hook(name, func, *args, **kwargs):
    def hook_func(record, original_record, db):
        func(record, db)
        return record
    _registry.register("hook", name, hook_func, *args, **kwargs)


def before_save(type_, *args, **kwargs):
    kwargs['type'] = type_

    def wrapper(func):
        register_save_hook("beforeSave", func, *args, **kwargs)
        return func
    return wrapper


def after_save(type_, *args, **kwargs):
    kwargs['type'] = type_

    def wrapper(func):
        register_save_hook("afterSave", func, *args, **kwargs)
        return func
    return wrapper


def before_delete(type_, *args, **kwargs):
    kwargs['type'] = type_

    def wrapper(func):
        register_delete_hook("beforeDelete", func, *args, **kwargs)
        return func
    return wrapper


def after_delete(type_, *args, **kwargs):
    kwargs['type'] = type_

    def wrapper(func):
        register_delete_hook("afterDelete", func, *args, **kwargs)
        return func
    return wrapper


def provides(provider_type, provider_id, *args, **kwargs):
    def skygear_provider(klass):
        provider = klass()
        _registry.register_provider(provider_type, provider_id, provider,
                                    *args, **kwargs)
        return klass
    return skygear_provider
