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
from unittest.mock import patch

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from .. import restful
from ..error import SkygearException


def create_request(*args, **kwargs):
    content_type = kwargs.pop('content_type', None)
    builder = EnvironBuilder(*args, **kwargs)
    if content_type:
        builder.content_type = content_type
    return Request(builder.get_environ())


def test_get_ident_none():
    req = create_request(method='POST', path='/hello/world')
    assert restful.get_ident('/hello/world', req) is None


def test_get_ident_none_with_slash():
    req = create_request(method='POST', path='/hello/world/')
    assert restful.get_ident('/hello/world', req) is None


def test_get_ident():
    req = create_request(method='POST', path='/hello/world/ident')
    assert restful.get_ident('/hello/world', req) == 'ident'


def test_get_ident_with_slash():
    req = create_request(method='POST', path='/hello/world/ident/')
    assert restful.get_ident('/hello/world', req) == 'ident'


def test_has_func():
    class HelloWorld:
        var = True

        def func():
            pass

    assert restful.has_func(HelloWorld(), 'func') is True
    assert restful.has_func(HelloWorld(), 'non-existent') is False
    assert restful.has_func(HelloWorld(), 'var') is False


class BlankRestfulResource(restful.RestfulResource):
    def index(self):
        pass

    def create(self):
        pass

    def delete(self, ident):
        pass

    def update(self, ident):
        pass

    def get(self, ident):
        pass


class TestRestfulResource(unittest.TestCase):
    def test_get_allowed_methods_create(self):
        class HelloWorld(restful.RestfulResource):
            def create(self):
                pass

        assert HelloWorld.get_allowed_methods() == ['POST']

    def test_get_allowed_methods_delete(self):
        class HelloWorld(restful.RestfulResource):
            def delete(self, ident):
                pass

        assert HelloWorld.get_allowed_methods() == ['DELETE']

    def test_get_allowed_methods_index(self):
        class HelloWorld(restful.RestfulResource):
            def index(self):
                pass

        assert HelloWorld.get_allowed_methods() == ['GET']

    def test_get_allowed_methods_get(self):
        class HelloWorld(restful.RestfulResource):
            def get(self, ident):
                pass

        assert HelloWorld.get_allowed_methods() == ['GET']

    def test_update_allowed_methods_update(self):
        class HelloWorld(restful.RestfulResource):
            def update(self, ident):
                pass

        assert HelloWorld.get_allowed_methods() == ['PUT']

    def test_get_payload(self):
        resource = BlankRestfulResource()
        resource.request = create_request(method='POST', path='/',
                                          data='{"json": "this is"}',
                                          content_type='application/json')
        assert resource.get_payload() == {'json': 'this is'}

    def test_get_payload_empty(self):
        resource = BlankRestfulResource()
        resource.request = create_request(method='POST', path='/')
        assert resource.get_payload() == {}

    @patch.object(BlankRestfulResource, 'get')
    def test_handle_request_get(self, mock):
        mock.return_value = {'json': 'this is'}
        resource = BlankRestfulResource()
        request = create_request(method='GET', path='/hello/1')
        assert resource.handle_request('/hello', request) == mock.return_value
        mock.assert_called_once_with('1')

    @patch.object(BlankRestfulResource, 'create')
    def test_handle_request_create(self, mock):
        mock.return_value = {'json': 'this is'}
        resource = BlankRestfulResource()
        request = create_request(method='POST', path='/hello')
        assert resource.handle_request('/hello', request) == mock.return_value
        mock.assert_called_once_with()

    @patch.object(BlankRestfulResource, 'update')
    def test_handle_request_update(self, mock):
        mock.return_value = {'json': 'this is'}
        resource = BlankRestfulResource()
        request = create_request(method='PUT', path='/hello/1')
        assert resource.handle_request('/hello', request) == mock.return_value
        mock.assert_called_once_with('1')

    @patch.object(BlankRestfulResource, 'index')
    def test_handle_request_index(self, mock):
        mock.return_value = {'result': {'json': 'this is'}}
        resource = BlankRestfulResource()
        request = create_request(method='GET', path='/hello')
        assert resource.handle_request('/hello', request) == mock.return_value
        mock.assert_called_once_with()

    @patch.object(BlankRestfulResource, 'delete')
    def test_handle_request_delete(self, mock):
        mock.return_value = {'json': 'this is'}
        resource = BlankRestfulResource()
        request = create_request(method='DELETE', path='/hello/1')
        assert resource.handle_request('/hello', request) == mock.return_value
        mock.assert_called_once_with('1')

    def test_handle_request_invalid(self):
        resource = BlankRestfulResource()
        request = create_request(method='WHAT', path='/hello/1')
        with self.assertRaises(SkygearException):
            resource.handle_request('/hello', request)


class SampleRestfulRecord(restful.RestfulRecord):
    record_type = 'sample'


class MockRestfulRecord(restful.RestfulRecord):
    record_type = 'sample'

    def _access_token(self):
        return 'ACCESS_TOKEN'

    def get_payload(self):
        return {'_id': 'sample/1', 'data': 'json'}

    def predicate(self):
        return []

    def query_options(self):
        return {'count': True}


class TestRestfulRecord(unittest.TestCase):
    def test_access_token_header(self):
        resource = SampleRestfulRecord()
        resource.request = create_request(headers={
            'X-Skygear-Access-Token': 'ACCESS_TOKEN',
            })
        assert resource._access_token() == 'ACCESS_TOKEN'

    def test_access_token_payload(self):
        resource = SampleRestfulRecord()
        resource.request = create_request(
            data='{"access_token": "ACCESS_TOKEN"}',
            content_type='application/json')
        assert resource._access_token() == 'ACCESS_TOKEN'

    def test_access_token_none(self):
        resource = SampleRestfulRecord()
        resource.request = create_request()
        assert resource._access_token() is None

    def test_handle_request_index(self):
        resource = MockRestfulRecord()

        with patch.object(resource, '_send_multi') as mock:
            resource.request = create_request()
            mock.return_value = [{'data': 'json'}]
            assert resource.index() == [{'data': 'json'}]
            mock.assert_called_once_with('record:query', database_id='_public',
                                         record_type='sample',
                                         predicate=[], count=True)

    def test_handle_request_create(self):
        resource = MockRestfulRecord()

        with patch.object(resource, '_send_single') as mock:
            mock.return_value = {'data': 'json'}
            assert resource.create() == {'data': 'json'}
            mock.assert_called_once_with('record:save', database_id='_public',
                                         records=[resource.get_payload()])

    def test_handle_request_get(self):
        resource = MockRestfulRecord()

        with patch.object(resource, '_send_single') as mock:
            mock.return_value = {'data': 'json'}
            assert resource.get('1') == {'data': 'json'}
            mock.assert_called_once_with('record:fetch', database_id='_public',
                                         ids=['sample/1'])

    def test_handle_request_update(self):
        resource = MockRestfulRecord()

        with patch.object(resource, '_send_single') as mock:
            mock.return_value = {'data': 'json'}
            assert resource.update('1') == {'data': 'json'}
            mock.assert_called_once_with('record:save', database_id='_public',
                                         records=[resource.get_payload()])

    def test_handle_request_delete(self):
        resource = MockRestfulRecord()

        with patch.object(resource, '_send_single') as mock:
            mock.return_value = {'data': 'json'}
            assert resource.delete('1') == {'data': 'json'}
            mock.assert_called_once_with('record:delete',
                                         database_id='_public',
                                         ids=['sample/1'])

    @patch('skygear.container.SkygearContainer.send_action')
    def test_send_multi(self, mock):
        mock.return_value = {'result': [{'data': 'json'}]}
        assert MockRestfulRecord()._send_multi('action', data='hello') \
            == {'result': [{'data': 'json'}]}
        mock.assert_called_once_with('action', {'data': 'hello'})

    @patch('skygear.container.SkygearContainer.send_action')
    def test_send_single(self, mock):
        mock.return_value = {'result': [{'data': 'json'}]}
        assert MockRestfulRecord()._send_single('action', data='hello') \
            == {'data': 'json'}
        mock.assert_called_once_with('action', {'data': 'hello'})
