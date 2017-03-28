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


class Record:
    def __init__(
            self, id, owner_id, acl,
            created_at=None, created_by=None,
            updated_at=None, updated_by=None, data=None):

        self._id = id
        self._owner_id = owner_id
        self._acl = acl
        self._created_at = created_at
        self._created_by = created_by
        self._updated_at = updated_at
        self._updated_by = updated_by

        self._data = data or {}

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, item):
        return item in self._data

    @property
    def id(self):
        return self._id

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def acl(self):
        return self._acl

    @property
    def created_at(self):
        return self._created_at

    @property
    def created_by(self):
        return self._created_by

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def updated_by(self):
        return self._updated_by

    @property
    def data(self):
        return self._data

    def get(self, key, default=None):
        return self._data.get(key, default)


# RecordID is immutable. Developer is not expected to modify a record's id
# once instantiated
class RecordID:
    def __init__(self, type_, key):
        if not type_:
            raise ValueError('RecordID.type cannot be None or empty')
        if not key:
            raise ValueError('RecordID.key cannot be None or empty')
        self._type = type_
        self._key = key

    @property
    def type(self):
        return self._type

    @property
    def key(self):
        return self._key


ACCESS_CONTROL_ENTRY_LEVEL_WRITE = 'write'
ACCESS_CONTROL_ENTRY_LEVEL_READ = 'read'


class AccessControlEntry:
    def __init__(self, level):
        self.level = level


ACCESS_CONTROL_ENTRY_RELATION_FRIEND = 'friend'
ACCESS_CONTROL_ENTRY_RELATION_FOLLOW = 'follow'


class PublicAccessControlEntry(AccessControlEntry):
    def __init__(self, level):
        super().__init__(level)


class RelationalAccessControlEntry(AccessControlEntry):
    def __init__(self, relation, level):
        super().__init__(level)
        self.relation = relation


class RoleAccessControlEntry(AccessControlEntry):
    def __init__(self, role, level):
        super().__init__(level)
        self.role = role


class DirectAccessControlEntry(AccessControlEntry):
    def __init__(self, user_id, level):
        super().__init__(level)
        self.user_id = user_id


class Asset:
    def __init__(self, name, content_type):
        self.name = name
        self.content_type = content_type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError('Asset.name cannot be None or empty')
        self._name = name


class Location:
    def __init__(self, lng, lat):
        self.lng = lng
        self.lat = lat


class Reference:
    def __init__(self, recordID):
        self.recordID = recordID

    @property
    def recordID(self):
        return self._recordID

    @recordID.setter
    def recordID(self, recordID):
        if recordID is None:
            raise ValueError('Reference.recordID cannot be None')
        self._recordID = recordID


class UnknownValue:
    def __init__(self, underlyingType):
        self.underlyingType = underlyingType

    @property
    def underlyingType(self):
        return self._underlyingType

    @underlyingType.setter
    def underlyingType(self, underlyingType):
        self._underlyingType = underlyingType
