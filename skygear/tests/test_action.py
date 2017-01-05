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
import unittest
from unittest.mock import MagicMock

from .. import action


class TestPushNotification(unittest.TestCase):
    def setUp(self):
        self.mock_container = MagicMock()

    def tearDown(self):
        self.mock_container = None

    def test_push_device(self):
        action.push_device(self.mock_container,
                           'device01',
                           {'apns': {'alert': 'hello'}})
        self.mock_container.send_action\
            .assert_called_once_with('push:device', {
                'device_ids': ['device01'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_devices(self):
        action.push_devices(self.mock_container,
                            ['device01', 'device02', 'device03'],
                            {'apns': {'alert': 'hello'}})
        self.mock_container.send_action\
            .assert_called_once_with('push:device', {
                'device_ids': ['device01', 'device02', 'device03'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_device_with_topic(self):
        action.push_device(self.mock_container,
                           'device01',
                           {'apns': {'alert': 'hello'}},
                           topic='io.skygear.example.app')
        self.mock_container.send_action\
            .assert_called_once_with('push:device', {
                'topic': 'io.skygear.example.app',
                'device_ids': ['device01'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_devices_with_topic(self):
        action.push_devices(self.mock_container,
                            ['device01', 'device02', 'device03'],
                            {'apns': {'alert': 'hello'}},
                            topic='io.skygear.example.app')
        self.mock_container.send_action\
            .assert_called_once_with('push:device', {
                'topic': 'io.skygear.example.app',
                'device_ids': ['device01', 'device02', 'device03'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_user(self):
        action.push_user(self.mock_container,
                         'user01',
                         {'apns': {'alert': 'hello'}})
        self.mock_container.send_action\
            .assert_called_once_with('push:user', {
                'user_ids': ['user01'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_users(self):
        action.push_users(self.mock_container,
                          ['user01', 'user02', 'user03'],
                          {'apns': {'alert': 'hello'}})
        self.mock_container.send_action\
            .assert_called_once_with('push:user', {
                'user_ids': ['user01', 'user02', 'user03'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_user_with_topic(self):
        action.push_user(self.mock_container,
                         'user01',
                         {'apns': {'alert': 'hello'}},
                         topic='io.skygear.example.app')
        self.mock_container.send_action\
            .assert_called_once_with('push:user', {
                'topic': 'io.skygear.example.app',
                'user_ids': ['user01'],
                'notification': {'apns': {'alert': 'hello'}}
            })

    def test_push_users_with_topic(self):
        action.push_users(self.mock_container,
                          ['user01', 'user02', 'user03'],
                          {'apns': {'alert': 'hello'}},
                          topic='io.skygear.example.app')
        self.mock_container.send_action\
            .assert_called_once_with('push:user', {
                'topic': 'io.skygear.example.app',
                'user_ids': ['user01', 'user02', 'user03'],
                'notification': {'apns': {'alert': 'hello'}}
            })
