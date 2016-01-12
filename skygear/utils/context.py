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
import contextlib
import logging
import threading

log = logging.getLogger(__name__)


class RequestContextManager(threading.local):
    def __init__(self):
        self.clear()

    def push(self, context):
        self.stack.append(context)
        log.debug("Pushed request context: %s. Length: %d",
                  context, len(self.stack))

    def pop(self):
        if len(self.stack) == 1:
            raise Exception("Cannot pop the top-most context.")
        return self.stack.pop()

    def current(self):
        return self.stack[-1]

    def clear(self):
        self.stack = [{}]


_manager = RequestContextManager()


def _context_manager():
    return _manager


def push_context(context):
    _context_manager().push(context)


def current_context():
    return _context_manager().current()


def pop_context():
    return _context_manager().pop()


def clear_contexts():
    _context_manager().clear()


def current_user_id():
    """Return the current user ID of the current request context.

    If the user is not logged in or if the request context is not available.
    This function returns None.
    """
    return current_context().get("user_id", None)


@contextlib.contextmanager
def start_context(context):
    push_context(context)
    try:
        yield
    finally:
        pop_context()
