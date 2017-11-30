import json

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.locales import Locale, LocaleCollection
from lingo24.exceptions import APIError, DoesNotExist

from .base import BaseTestCase


class LocaleTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(Locale(1, 'aaa', 'AAA', 'xxx'), Locale(1, 'aaa', 'AAA', 'xxx'))
        self.assertNotEqual(Locale(1, 'aaa', 'AAA', 'xxx'), Locale(2, 'aaa', 'AAA', 'xxx'))
        self.assertNotEqual(Locale(1, 'aaa', 'AAA', 'xxx'), Locale(1, 'bbb', 'AAA', 'xxx'))
        self.assertNotEqual(Locale(1, 'aaa', 'AAA', 'xxx'), Locale(1, 'aaa', 'BBB', 'xxx'))
        self.assertNotEqual(Locale(1, 'aaa', 'AAA', 'xxx'), Locale(1, 'aaa', 'AAA', 'yyy'))


class LocaleCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_make_item(self):
        locale = self.client.locales.make_item(id=1, name='aaa', language='AAA', country='xxx')
        self.assertEqual(locale, Locale(1, 'aaa', 'AAA', 'xxx'))

    def test_equality(self):
        self.assertEqual(self.client.locales, self.client.locales)

    def test_clone(self):
        locales = self.client.locales
        clone = locales.clone()
        self.assertEqual(locales, clone)
        self.assertIsNot(locales, clone)

    def test_item_url_path(self):
        self.assertEqual(self.client.locales.item_url_path(123), 'locales/123')

    def test_sort(self):
        locales = self.client.locales
        locales_by_name = locales.sort('name')
        locales_by_description = locales_by_name.sort('description')
        self.assertNotEqual(locales, locales_by_name)
        self.assertNotEqual(locales_by_name, locales_by_description)
        self.assertDictEqual(locales.make_query_dict(page_index=0), {'page': 0, 'size': 4})
        self.assertDictEqual(locales_by_name.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'name'})
        self.assertDictEqual(locales_by_description.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'description'})

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/123', text=json.dumps({
            'id': 123,
            'name': 'aaa',
            'language': 'AAA',
            'country': 'xxx',
        }))
        locale = self.client.locales.get(123)
        self.assertEqual(locale, Locale(123, 'aaa', 'AAA', 'xxx'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/123', status_code=404)
        self.assertRaises(DoesNotExist, self.client.locales.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/123', status_code=500)
        self.assertRaises(APIError, self.client.locales.get, 123)


class LocaleCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.locales.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.locales), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.locales)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_Error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=0&size=4', status_code=500)
        it = iter(self.client.locales)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.locales[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.locales[i], 0)
        self.assertRaises(TypeError, lambda i: self.client.locales[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[2:9:2])
        self.assertRaises(StopIteration, it.next)


class LocaleCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/locales/?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'name': 'aaa', 'language': 'AAA', 'country': 'xxx'},
                {'id': 2, 'name': 'bbb', 'language': 'BBB', 'country': 'xxx'},
                {'id': 3, 'name': 'ccc', 'language': 'CCC', 'country': 'xxx'},
                {'id': 4, 'name': 'ddd', 'language': 'DDD', 'country': 'xxx'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/locales/?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'name': 'eee', 'language': 'EEE', 'country': 'xxx'},
                {'id': 6, 'name': 'fff', 'language': 'FFF', 'country': 'xxx'},
                {'id': 7, 'name': 'ggg', 'language': 'GGG', 'country': 'xxx'},
                {'id': 8, 'name': 'hhh', 'language': 'HHH', 'country': 'xxx'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'name': 'iii', 'language': 'III', 'country': 'xxx'},
                {'id': 10, 'name': 'jjj', 'language': 'JJJ', 'country': 'xxx'},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/locales/?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.locales.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.locales), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.locales)
        self.assertEqual(it.next(), Locale(1, 'aaa', 'AAA', 'xxx'))
        self.assertEqual(it.next(), Locale(2, 'bbb', 'BBB', 'xxx'))
        self.assertEqual(it.next(), Locale(3, 'ccc', 'CCC', 'xxx'))
        self.assertEqual(it.next(), Locale(4, 'ddd', 'DDD', 'xxx'))
        self.assertEqual(it.next(), Locale(5, 'eee', 'EEE', 'xxx'))
        self.assertEqual(it.next(), Locale(6, 'fff', 'FFF', 'xxx'))
        self.assertEqual(it.next(), Locale(7, 'ggg', 'GGG', 'xxx'))
        self.assertEqual(it.next(), Locale(8, 'hhh', 'HHH', 'xxx'))
        self.assertEqual(it.next(), Locale(9, 'iii', 'III', 'xxx'))
        self.assertEqual(it.next(), Locale(10, 'jjj', 'JJJ', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.locales[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.locales[i], 10)
        self.assertEqual(self.client.locales[5], Locale(6, 'fff', 'FFF', 'xxx'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[:5])
        self.assertEqual(it.next(), Locale(1, 'aaa', 'AAA', 'xxx'))
        self.assertEqual(it.next(), Locale(2, 'bbb', 'BBB', 'xxx'))
        self.assertEqual(it.next(), Locale(3, 'ccc', 'CCC', 'xxx'))
        self.assertEqual(it.next(), Locale(4, 'ddd', 'DDD', 'xxx'))
        self.assertEqual(it.next(), Locale(5, 'eee', 'EEE', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[2:9])
        self.assertEqual(it.next(), Locale(3, 'ccc', 'CCC', 'xxx'))
        self.assertEqual(it.next(), Locale(4, 'ddd', 'DDD', 'xxx'))
        self.assertEqual(it.next(), Locale(5, 'eee', 'EEE', 'xxx'))
        self.assertEqual(it.next(), Locale(6, 'fff', 'FFF', 'xxx'))
        self.assertEqual(it.next(), Locale(7, 'ggg', 'GGG', 'xxx'))
        self.assertEqual(it.next(), Locale(8, 'hhh', 'HHH', 'xxx'))
        self.assertEqual(it.next(), Locale(9, 'iii', 'III', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[7:])
        self.assertEqual(it.next(), Locale(8, 'hhh', 'HHH', 'xxx'))
        self.assertEqual(it.next(), Locale(9, 'iii', 'III', 'xxx'))
        self.assertEqual(it.next(), Locale(10, 'jjj', 'JJJ', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.locales[2:9:2])
        self.assertEqual(it.next(), Locale(3, 'ccc', 'CCC', 'xxx'))
        self.assertEqual(it.next(), Locale(5, 'eee', 'EEE', 'xxx'))
        self.assertEqual(it.next(), Locale(7, 'ggg', 'GGG', 'xxx'))
        self.assertEqual(it.next(), Locale(9, 'iii', 'III', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.client.locales.get_page(1))
        self.assertEqual(it.next(), Locale(5, 'eee', 'EEE', 'xxx'))
        self.assertEqual(it.next(), Locale(6, 'fff', 'FFF', 'xxx'))
        self.assertEqual(it.next(), Locale(7, 'ggg', 'GGG', 'xxx'))
        self.assertEqual(it.next(), Locale(8, 'hhh', 'HHH', 'xxx'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.client.locales.get_page(10))
        self.assertRaises(StopIteration, it.next)
