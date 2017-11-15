import json

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.files import (
    BaseFileCollection,
    FileCollection,
    File,
)
from lingo24.exceptions import APIError, DoesNotExist

from .base import BaseTestCase


class FileTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_equality(self):
        self.assertEqual(File(self.client, 1, 'Test.txt', 'AAA'), File(self.client, 1, 'Test.txt', 'AAA'))
        self.assertNotEqual(File(self.client, 1, 'Test.txt', 'AAA'), File(None, 1, 'Test.txt', 'AAA'))
        self.assertNotEqual(File(self.client, 1, 'Test.txt', 'AAA'), File(self.client, 2, 'Test.txt', 'AAA'))
        self.assertNotEqual(File(self.client, 1, 'Test.txt', 'AAA'), File(self.client, 1, 'Test2.txt', 'AAA'))
        self.assertNotEqual(File(self.client, 1, 'Test.txt', 'AAA'), File(self.client, 1, 'Test.txt', 'BBB'))

    @requests_mock.mock()
    def test_get_content(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/1/content', text='xxx')
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        self.assertEqual(file_obj.content, 'xxx')

    @requests_mock.mock()
    def test_get_content_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/1/content', status_code=404)
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        self.assertIsNone(file_obj.content)

    @requests_mock.mock()
    def test_get_content_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/1/content', status_code=500)
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        self.assertRaises(APIError, lambda: file_obj.content)

    @requests_mock.mock()
    def test_set_content(self, m):
        def text_callback(request, context):
            self.assertEqual(request.text, 'xxx')

        m.put('https://api-demo.lingo24.com/docs/v1/files/1/content', text=text_callback)
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        file_obj.content = 'xxx'

    @requests_mock.mock()
    def test_set_content_error(self, m):
        m.put('https://api-demo.lingo24.com/docs/v1/files/1/content', status_code=500)

        def set_content():
            file_obj = File(self.client, 1, 'Test.txt', 'AAA')
            file_obj.content = 'xxx'

        self.assertRaises(APIError, set_content)

    @requests_mock.mock()
    def test_delete(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/files/1')
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        file_obj.delete()

    @requests_mock.mock()
    def test_delete_error(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/files/1', status_code=500)
        file_obj = File(self.client, 1, 'Test.txt', 'AAA')
        self.assertRaises(APIError, file_obj.delete)


class FileCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_make_item(self):
        file_obj = self.client.files.make_item(id=1, name='Test.txt', type='AAA')
        self.assertEqual(file_obj, File(self.client, 1, 'Test.txt', 'AAA'))

    def test_equality(self):
        self.assertEqual(self.client.files, self.client.files)

    def test_clone(self):
        files = self.client.files
        clone = files.clone()
        self.assertEqual(files, clone)
        self.assertIsNot(files, clone)

    def test_item_url_path(self):
        self.assertEqual(self.client.files.item_url_path(123), 'files/123')

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/123', text=json.dumps({
            'id': 123,
            'name': 'aaa',
            'type': 'AAA',
        }))
        locale = self.client.files.get(123)
        self.assertEqual(locale, File(self.client, 123, 'aaa', 'AAA'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/123', status_code=404)
        self.assertRaises(DoesNotExist, self.client.files.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/123', status_code=500)
        self.assertRaises(APIError, self.client.files.get, 123)

    @requests_mock.mock()
    def test_create(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'name': 'Test.txt',
                'type': 'SOURCE',
            })
            return json.dumps({
                'id': 12345,
                'name': 'Test.txt',
                'type': 'SOURCE',
            })

        m.post('https://api-demo.lingo24.com/docs/v1/files', text=text_callback)
        file_obj = self.client.files.create('Test.txt')
        self.assertEqual(file_obj, File(self.client, 12345, 
        
        'Test.txt', 'SOURCE'))

    @requests_mock.mock()
    def test_create_error(self, m):
        m.post('https://api-demo.lingo24.com/docs/v1/files', status_code=400)
        self.assertRaises(APIError, self.client.files.create, 'Test.txt')
