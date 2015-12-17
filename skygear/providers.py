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


class BaseAuthProvider(object):
    def handle_action(self, action, data):
        auth_data = data.get('auth_data', {})
        if action == 'login':
            output = self.login(auth_data)
        elif action == 'logout':
            output = self.logout(auth_data)
        elif action == 'info':
            output = self.info(auth_data)
        return output

    def login(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement login method.")

    def logout(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement logout method.")

    def info(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement info method.")
