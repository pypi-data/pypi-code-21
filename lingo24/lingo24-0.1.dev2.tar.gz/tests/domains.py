import json

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.domains import Domain, DomainCollection
from lingo24.exceptions import APIError, DoesNotExist

from .base import BaseTestCase


class DomainTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(Domain(1, 'aaa'), Domain(1, 'aaa'))
        self.assertNotEqual(Domain(1, 'aaa'), Domain(2, 'aaa'))
        self.assertNotEqual(Domain(1, 'aaa'), Domain(1, 'xxx'))


class DomainCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_make_item(self):
        domain = self.client.domains.make_item(id=1, name='aaa')
        self.assertEqual(domain, Domain(1, 'aaa'))

    def test_equality(self):
        self.assertEqual(self.client.domains, self.client.domains)

    def test_clone(self):
        domains = self.client.domains
        clone = domains.clone()
        self.assertEqual(domains, clone)
        self.assertIsNot(domains, clone)

    def test_item_url_path(self):
        self.assertEqual(self.client.domains.item_url_path(123), 'domains/123')

    def test_sort(self):
        domains = self.client.domains
        domains_by_name = domains.sort('name')
        domains_by_description = domains_by_name.sort('description')
        self.assertNotEqual(domains, domains_by_name)
        self.assertNotEqual(domains_by_name, domains_by_description)
        self.assertDictEqual(domains.make_query_dict(page_index=0), {'page': 0, 'size': 4})
        self.assertDictEqual(domains_by_name.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'name'})
        self.assertDictEqual(domains_by_description.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'description'})

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/123', text=json.dumps({
            'id': 123,
            'name': 'aaa',
        }))
        domain = self.client.domains.get(123)
        self.assertEqual(domain, Domain(123, 'aaa'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/123', status_code=404)
        self.assertRaises(DoesNotExist, self.client.domains.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/123', status_code=500)
        self.assertRaises(APIError, self.client.domains.get, 123)


class DomainCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.domains.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.domains), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.domains)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_Error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=0&size=4', status_code=500)
        it = iter(self.client.domains)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.domains[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.domains[i], 0)
        self.assertRaises(TypeError, lambda i: self.client.domains[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[2:9:2])
        self.assertRaises(StopIteration, it.next)


class DomainCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/domains/?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'name': 'aaa'},
                {'id': 2, 'name': 'bbb'},
                {'id': 3, 'name': 'ccc'},
                {'id': 4, 'name': 'ddd'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/domains/?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'name': 'eee'},
                {'id': 6, 'name': 'fff'},
                {'id': 7, 'name': 'ggg'},
                {'id': 8, 'name': 'hhh'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'name': 'iii'},
                {'id': 10, 'name': 'jjj'},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/domains/?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.domains.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.domains), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.domains)
        self.assertEqual(it.next(), Domain(1, 'aaa'))
        self.assertEqual(it.next(), Domain(2, 'bbb'))
        self.assertEqual(it.next(), Domain(3, 'ccc'))
        self.assertEqual(it.next(), Domain(4, 'ddd'))
        self.assertEqual(it.next(), Domain(5, 'eee'))
        self.assertEqual(it.next(), Domain(6, 'fff'))
        self.assertEqual(it.next(), Domain(7, 'ggg'))
        self.assertEqual(it.next(), Domain(8, 'hhh'))
        self.assertEqual(it.next(), Domain(9, 'iii'))
        self.assertEqual(it.next(), Domain(10, 'jjj'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.domains[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.domains[i], 10)
        self.assertEqual(self.client.domains[5], Domain(6, 'fff'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[:5])
        self.assertEqual(it.next(), Domain(1, 'aaa'))
        self.assertEqual(it.next(), Domain(2, 'bbb'))
        self.assertEqual(it.next(), Domain(3, 'ccc'))
        self.assertEqual(it.next(), Domain(4, 'ddd'))
        self.assertEqual(it.next(), Domain(5, 'eee'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[2:9])
        self.assertEqual(it.next(), Domain(3, 'ccc'))
        self.assertEqual(it.next(), Domain(4, 'ddd'))
        self.assertEqual(it.next(), Domain(5, 'eee'))
        self.assertEqual(it.next(), Domain(6, 'fff'))
        self.assertEqual(it.next(), Domain(7, 'ggg'))
        self.assertEqual(it.next(), Domain(8, 'hhh'))
        self.assertEqual(it.next(), Domain(9, 'iii'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[7:])
        self.assertEqual(it.next(), Domain(8, 'hhh'))
        self.assertEqual(it.next(), Domain(9, 'iii'))
        self.assertEqual(it.next(), Domain(10, 'jjj'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.domains[2:9:2])
        self.assertEqual(it.next(), Domain(3, 'ccc'))
        self.assertEqual(it.next(), Domain(5, 'eee'))
        self.assertEqual(it.next(), Domain(7, 'ggg'))
        self.assertEqual(it.next(), Domain(9, 'iii'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.client.domains.get_page(1))
        self.assertEqual(it.next(), Domain(5, 'eee'))
        self.assertEqual(it.next(), Domain(6, 'fff'))
        self.assertEqual(it.next(), Domain(7, 'ggg'))
        self.assertEqual(it.next(), Domain(8, 'hhh'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.client.domains.get_page(10))
        self.assertRaises(StopIteration, it.next)
