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
import traceback
from datetime import datetime

import strict_rfc3339

from .error import SkygearException, UnexpectedError
from .models import (Asset, DirectAccessControlEntry, Location,
                     PublicAccessControlEntry, Record, RecordID, Reference,
                     RelationalAccessControlEntry, RoleAccessControlEntry,
                     UnknownValue)


def _serialize_exc(e):
    if isinstance(e, SkygearException):
        return e

    return SkygearException(
        str(e),
        UnexpectedError,
        {'trace': traceback.format_exc()})


def deserialize_record(obj):
    return _RecordDecoder().decode(obj)


def deserialize_or_none(obj):
    if obj:
        return deserialize_record(obj)
    else:
        return None


def serialize_record(record):
    return _RecordEncoder().encode(record)


class _RecordDecoder:
    def decode(self, d):
        id = self.decode_id(d['_id'])
        owner_id = d['_ownerID']
        acl = self.decode_acl(d['_access'])

        created_at = None
        if d.get('_created_at', None):
            created_at = self.decode_date_value(d['_created_at'])
        created_by = d.get('_created_by', None)

        updated_at = None
        if d.get('_updated_at', None):
            updated_at = self.decode_date_value(d['_updated_at'])
        updated_by = d.get('_updated_by', None)

        data_dict = {k: v for k, v in d.items() if not k.startswith('_')}

        data = self.decode_dict(data_dict)

        return Record(
            id=id,
            owner_id=owner_id,
            acl=acl,
            created_at=created_at,
            created_by=created_by,
            updated_at=updated_at,
            updated_by=updated_by,
            data=data)

    def decode_id(self, s):
        ss = s.split('/')
        return RecordID(ss[0], ss[1])

    def decode_acl(self, l):
        if l is None:
            return None
        if not isinstance(l, list):
            raise TypeError('expect ACL to be a list')

        return [self.decode_ace(d) for d in l]

    def decode_ace(self, d):
        level = d.get('level', None)
        if level is None:
            raise ValueError("ace must have level")
        relation = d.get('relation', None)
        role = d.get('role', None)
        user_id = d.get('user_id', None)
        public = d.get('public', None)
        if user_id is not None:
            return DirectAccessControlEntry(d['user_id'], level)
        elif relation is not None:
            return RelationalAccessControlEntry(relation, level)
        elif role is not None:
            return RoleAccessControlEntry(role, level)
        elif public is not None:
            return PublicAccessControlEntry(level)
        else:
            raise ValueError("invalid ace")

    def decode_dict(self, d):
        return {k: self.decode_value(v) for k, v in d.items()}

    def decode_list(self, l):
        return [self.decode_value(v) for v in l]

    def decode_value(self, v):
        if isinstance(v, dict):
            type_ = v.get('$type')
            if type_ == 'date':
                return self.decode_date(v)
            elif type_ == 'asset':
                return self.decode_asset(v)
            elif type_ == 'geo':
                return self.decode_location(v)
            elif type_ == 'ref':
                return self.decode_ref(v)
            elif type_ == 'unknown':
                return self.decode_unknown_value(v)
            else:
                return self.decode_dict(v)
        elif isinstance(v, list):
            return self.decode_list(v)
        else:
            return v

    def decode_date(self, d):
        return self.decode_date_value(d['$date'])

    def decode_date_value(self, s):
        ts = strict_rfc3339.rfc3339_to_timestamp(s)
        return datetime.fromtimestamp(ts)

    def decode_asset(self, d):
        return Asset(d['$name'], d.get('$content_type', None))

    def decode_location(self, d):
        return Location(d['$lng'], d['$lat'])

    def decode_ref(self, d):
        return Reference(self.decode_id(d['$id']))

    def decode_unknown_value(self, d):
        return UnknownValue(d['$underlying_type'])


class _RecordEncoder:
    def encode(self, record):
        d = self.encode_dict(record.data)
        d['_id'] = self.encode_id(record.id)
        d['_ownerID'] = record.owner_id
        d['_access'] = self.encode_acl(record.acl)
        if record.created_at is not None:
            # New record don't have following value yet
            d['_created_at'] = self._encode_datetime(record.created_at)
            d['_created_by'] = record.created_by
        if record.updated_at is not None:
            d['_updated_at'] = self._encode_datetime(record.updated_at)
            d['_updated_by'] = record.updated_by
        return d

    def encode_id(self, id):
        return '%s/%s' % (id.type, id.key)

    def encode_acl(self, acl):
        if acl is None:
            return None

        return [self.encode_ace(e) for e in acl]

    def encode_ace(self, ace):
        if isinstance(ace, RelationalAccessControlEntry):
            return {
                'level': ace.level,
                'relation': ace.relation,
            }
        elif isinstance(ace, DirectAccessControlEntry):
            return {
                'level': ace.level,
                'user_id': ace.user_id,
            }
        elif isinstance(ace, RoleAccessControlEntry):
            return {
                'level': ace.level,
                'role': ace.role
            }
        elif isinstance(ace, PublicAccessControlEntry):
            return {
                'level': ace.level,
                'public': True
            }
        else:
            raise ValueError('Unknown type of ACE = %s', type(ace))

    def encode_dict(self, d):
        return {k: self.encode_value(v) for k, v in d.items()}

    def encode_list(self, l):
        return [self.encode_value(v) for v in l]

    def encode_value(self, v):
        if isinstance(v, dict):
            return self.encode_dict(v)
        elif isinstance(v, list):
            return self.encode_list(v)
        elif isinstance(v, datetime):
            return self.encode_datetime(v)
        elif isinstance(v, Asset):
            return self.encode_asset(v)
        elif isinstance(v, Location):
            return self.encode_location(v)
        elif isinstance(v, Reference):
            return self.encode_ref(v)
        elif isinstance(v, UnknownValue):
            return self.encode_unknown_value(v)
        else:
            return v

    def _encode_datetime(self, dt):
        ts = dt.timestamp()
        return strict_rfc3339.timestamp_to_rfc3339_utcoffset(ts)

    def encode_datetime(self, dt):
        return {
            '$type': 'date',
            '$date': self._encode_datetime(dt),
        }

    def encode_asset(self, asset):
        return {
            '$type': 'asset',
            '$name': asset.name,
            '$content_type': asset.content_type
        }

    def encode_location(self, location):
        return {
            '$type': 'geo',
            '$lng': location.lng,
            '$lat': location.lat,
        }

    def encode_ref(self, ref):
        return {
            '$type': 'ref',
            '$id': self.encode_id(ref.recordID),
        }

    def encode_unknown_value(self, unknown_value):
        data = {
            '$type': 'unknown',
        }
        if unknown_value.underlyingType:
            data['$underlying_type'] = unknown_value.underlyingType
        return data
