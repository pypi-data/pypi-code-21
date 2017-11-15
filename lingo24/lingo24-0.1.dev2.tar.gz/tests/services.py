import json

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.services import Service, ServiceCollection
from lingo24.exceptions import APIError, DoesNotExist

from .base import BaseTestCase


class ServiceTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(Service(1, 'aaa', 'AAA'), Service(1, 'aaa', 'AAA'))
        self.assertNotEqual(Service(1, 'aaa', 'AAA'), Service(2, 'aaa', 'AAA'))
        self.assertNotEqual(Service(1, 'aaa', 'AAA'), Service(1, 'xxx', 'AAA'))
        self.assertNotEqual(Service(1, 'aaa', 'AAA'), Service(1, 'aaa', 'xxx'))


class ServiceCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_make_item(self):
        service = self.client.services.make_item(id=1, name='aaa', description='AAA')
        self.assertEqual(service, Service(1, 'aaa', 'AAA'))

    def test_equality(self):
        self.assertEqual(self.client.services, self.client.services)

    def test_clone(self):
        services = self.client.services
        clone = services.clone()
        self.assertEqual(services, clone)
        self.assertIsNot(services, clone)

    def test_item_url_path(self):
        self.assertEqual(self.client.services.item_url_path(123), 'services/123')

    def test_sort(self):
        services = self.client.services
        services_by_name = services.sort('name')
        services_by_description = services_by_name.sort('description')
        self.assertNotEqual(services, services_by_name)
        self.assertNotEqual(services_by_name, services_by_description)
        self.assertDictEqual(services.make_query_dict(page_index=0), {'page': 0, 'size': 4})
        self.assertDictEqual(services_by_name.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'name'})
        self.assertDictEqual(services_by_description.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'description'})

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/123', text=json.dumps({
            'id': 123,
            'name': 'aaa',
            'description': 'AAA',
        }))
        service = self.client.services.get(123)
        self.assertEqual(service, Service(123, 'aaa', 'AAA'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/123', status_code=404)
        self.assertRaises(DoesNotExist, self.client.services.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/123', status_code=500)
        self.assertRaises(APIError, self.client.services.get, 123)


class ServiceCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.services.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.services), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.services)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_Error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=0&size=4', status_code=500)
        it = iter(self.client.services)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.services[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.services[i], 0)
        self.assertRaises(TypeError, lambda i: self.client.services[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.services[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.services[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.services[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.services[2:9:2])
        self.assertRaises(StopIteration, it.next)


class ServiceCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/services/?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'name': 'aaa', 'description': 'AAA'},
                {'id': 2, 'name': 'bbb', 'description': 'BBB'},
                {'id': 3, 'name': 'ccc', 'description': 'CCC'},
                {'id': 4, 'name': 'ddd', 'description': 'DDD'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/services/?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'name': 'eee', 'description': 'EEE'},
                {'id': 6, 'name': 'fff', 'description': 'FFF'},
                {'id': 7, 'name': 'ggg', 'description': 'GGG'},
                {'id': 8, 'name': 'hhh', 'description': 'HHH'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'name': 'iii', 'description': 'III'},
                {'id': 10, 'name': 'jjj', 'description': 'JJJ'},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/services/?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.services.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.services), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.services)
        self.assertEqual(it.next(), Service(1, 'aaa', 'AAA'))
        self.assertEqual(it.next(), Service(2, 'bbb', 'BBB'))
        self.assertEqual(it.next(), Service(3, 'ccc', 'CCC'))
        self.assertEqual(it.next(), Service(4, 'ddd', 'DDD'))
        self.assertEqual(it.next(), Service(5, 'eee', 'EEE'))
        self.assertEqual(it.next(), Service(6, 'fff', 'FFF'))
        self.assertEqual(it.next(), Service(7, 'ggg', 'GGG'))
        self.assertEqual(it.next(), Service(8, 'hhh', 'HHH'))
        self.assertEqual(it.next(), Service(9, 'iii', 'III'))
        self.assertEqual(it.next(), Service(10, 'jjj', 'JJJ'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.services[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.services[i], 10)
        self.assertEqual(self.client.services[5], Service(6, 'fff', 'FFF'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.services[:5])
        self.assertEqual(it.next(), Service(1, 'aaa', 'AAA'))
        self.assertEqual(it.next(), Service(2, 'bbb', 'BBB'))
        self.assertEqual(it.next(), Service(3, 'ccc', 'CCC'))
        self.assertEqual(it.next(), Service(4, 'ddd', 'DDD'))
        self.assertEqual(it.next(), Service(5, 'eee', 'EEE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.services[2:9])
        self.assertEqual(it.next(), Service(3, 'ccc', 'CCC'))
        self.assertEqual(it.next(), Service(4, 'ddd', 'DDD'))
        self.assertEqual(it.next(), Service(5, 'eee', 'EEE'))
        self.assertEqual(it.next(), Service(6, 'fff', 'FFF'))
        self.assertEqual(it.next(), Service(7, 'ggg', 'GGG'))
        self.assertEqual(it.next(), Service(8, 'hhh', 'HHH'))
        self.assertEqual(it.next(), Service(9, 'iii', 'III'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.services[7:])
        self.assertEqual(it.next(), Service(8, 'hhh', 'HHH'))
        self.assertEqual(it.next(), Service(9, 'iii', 'III'))
        self.assertEqual(it.next(), Service(10, 'jjj', 'JJJ'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.services[2:9:2])
        self.assertEqual(it.next(), Service(3, 'ccc', 'CCC'))
        self.assertEqual(it.next(), Service(5, 'eee', 'EEE'))
        self.assertEqual(it.next(), Service(7, 'ggg', 'GGG'))
        self.assertEqual(it.next(), Service(9, 'iii', 'III'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.client.services.get_page(1))
        self.assertEqual(it.next(), Service(5, 'eee', 'EEE'))
        self.assertEqual(it.next(), Service(6, 'fff', 'FFF'))
        self.assertEqual(it.next(), Service(7, 'ggg', 'GGG'))
        self.assertEqual(it.next(), Service(8, 'hhh', 'HHH'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.client.services.get_page(10))
        self.assertRaises(StopIteration, it.next)
