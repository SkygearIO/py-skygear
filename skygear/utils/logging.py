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
import logging

from pythonjsonlogger import jsonlogger

from .context import current_request_id


class CloudLogFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname.lower()
        log_record['logger'] = record.name
        created = datetime.datetime.fromtimestamp(record.created)
        log_record['time'] = created.strftime('%Y-%m-%dT%H:%M:%SZ')

        if 'msg' not in log_record and 'message' in log_record:
            log_record['msg'] = log_record.pop('message')
        if 'error' not in log_record and 'exc_info' in log_record:
            log_record['error'] = log_record.pop('exc_info')


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        request_id = current_request_id()
        if request_id:
            record.request_id = str(request_id)
        return True


class RequestTagFilter(logging.Filter):
    def __init__(self, tag, name=''):
        super(RequestTagFilter, self).__init__(name)
        self.tag = tag

    def filter(self, record):
        # We use the super class filter method to check if the filter name
        # applies to the record name. We modify the record if this is True.
        if super(RequestTagFilter, self).filter(record):
            if not hasattr(record, 'tag') and self.tag:
                record.tag = self.tag
        return True


def setLoggerTag(logger, tag):
    logger.addFilter(RequestTagFilter(tag))
