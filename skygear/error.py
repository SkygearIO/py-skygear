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
NotAuthenticated = 101
PermissionDenied = 102
AccessKeyNotAccepted = 103
AccessTokenNotAccepted = 104
InvalidCredentials = 105
InvalidSignature = 106
BadRequest = 107
InvalidArgument = 108
Duplicated = 109
ResourceNotFound = 110
NotSupported = 111
NotImplemented = 112
ConstraintViolated = 113
IncompatibleSchema = 114
AtomicOperationFailure = 115
PartialOperationFailure = 116
UndefinedOperation = 117
PluginUnavailable = 118
PluginTimeout = 119

UnexpectedError = 10000


class SkygearException(Exception):
    """
    An exception object to be raised by plugin to indicate that
    the requested operation is not successful, or that the operation
    is aborted for whatever reason.
    """
    def __init__(self, message, code=UnexpectedError, info=None):
        self.message = message
        self.code = code
        self.info = info or {}
        super(SkygearException, self).__init__(message)

    def as_dict(self):
        return {
            'message': self.message,
            'code': self.code,
            'info': self.info,
            }

    @classmethod
    def from_dict(cls, error_dict):
        message = error_dict.get('message', "An error has occurred.")
        code = error_dict.get('code', UnexpectedError)
        info = error_dict.get('info', {})
        return cls(message, code, info)
