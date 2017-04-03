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
RecordQueryInvalid = 120
PluginInitializing = 121

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

    def readable_message(self):
        """
        This method returns a user readable string for the error.
        """
        # Make exception of the complexity check here because we need to
        # cover each error case.
        # pylama:ignore=C901
        # #lizard forgives the complexity
        if self.code == NotAuthenticated:
            return "You have to be authenticated to perform this operation."
        elif (self.code in [PermissionDenied, AccessKeyNotAccepted,
                            AccessTokenNotAccepted]):
            return "You are not allowed to perform this operation."
        elif self.code == InvalidCredentials:
            return "You are not allowed to log in because the credentials " + \
                "you provided are not valid."
        elif self.code in [InvalidSignature, BadRequest]:
            return "The server is unable to process the request."
        elif self.code == InvalidArgument:
            return "The server is unable to process the data."
        elif self.code == Duplicated:
            return "This request contains duplicate of an existing " + \
                "resource on the server."
        elif self.code == ResourceNotFound:
            return "The requested resource is not found."
        elif self.code == NotSupported:
            return "This operation is not supported."
        elif self.code == NotImplemented:
            return "This operation is not implemented."
        elif (self.code in [ConstraintViolated, IncompatibleSchema,
                            AtomicOperationFailure, PartialOperationFailure]):
            return "A problem occurred while processing this request."
        elif self.code == UndefinedOperation:
            return "The requested operation is not available."
        elif self.code in [PluginInitializing, PluginUnavailable]:
            return "The server is not ready yet."
        elif self.code == PluginTimeout:
            return "The server took too long to process."
        elif self.code == RecordQueryInvalid:
            return "A problem occurred while processing this request."
        return "An unexpected error has occurred."

    @classmethod
    def from_dict(cls, error_dict):
        message = error_dict.get('message', "An error has occurred.")
        code = error_dict.get('code', UnexpectedError)
        info = error_dict.get('info', {})
        return cls(message, code, info)
