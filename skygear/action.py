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


def push_device(container, device_id, notification):
    return push_devices(container, [device_id], notification)


def push_devices(container, device_ids, notification):
    params = {
            'device_ids': device_ids,
            'notification': notification,
            }
    return container.send_action('push:device', params)


def push_user(container, user_id, notification):
    return push_users(container, [user_id], notification)


def push_users(container, user_ids, notification):
    params = {
            'user_ids': user_ids,
            'notification': notification,
            }
    return container.send_action('push:user', params)
