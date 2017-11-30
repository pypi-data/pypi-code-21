import json

import requests
import requests_mock

from mock import Mock, patch

from lingo24.business_documents.auth import (
    Authenticator,
    DictAuthenticationStore,
    )
from lingo24.exceptions import APIError

from .base import BaseTestCase


mock_time = Mock()
mock_time.return_value = 10000


class AuthenticatorTestCase(BaseTestCase):
    def test_ease_endpoint_url(self):
        default_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertURLEqual(default_authenticator.ease_endpoint_url, 'https://ease.lingo24.com/')

        live_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', endpoint='live')
        self.assertURLEqual(live_authenticator.ease_endpoint_url, 'https://ease.lingo24.com/')

        demo_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', endpoint='demo')
        self.assertURLEqual(demo_authenticator.ease_endpoint_url, 'https://ease-demo.lingo24.com/')

    def test_api_endpoint_url(self):
        default_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertURLEqual(default_authenticator.api_endpoint_url, 'https://api.lingo24.com/docs/v1/')

        live_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', endpoint='live')
        self.assertURLEqual(live_authenticator.api_endpoint_url, 'https://api.lingo24.com/docs/v1/')

        demo_authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', endpoint='demo')
        self.assertURLEqual(demo_authenticator.api_endpoint_url, 'https://api-demo.lingo24.com/docs/v1/')

    def test_authorization_url(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertURLEqual(authenticator.authorization_url, 'https://ease.lingo24.com/oauth/authorize?response_type=code&client_id=xxx&redirect_uri=https%3A%2F%2Fwww.example.com%2Fcallback')

    @patch('time.time', mock_time)
    def test_access_token_expired_expired(self):
        store = DictAuthenticationStore({
            'expires_at': 5000,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        self.assertTrue(authenticator.access_token_expired)

    @patch('time.time', mock_time)
    def test_access_token_expired_not_expired(self):
        store = DictAuthenticationStore({
            'expires_at': 15000,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        self.assertFalse(authenticator.access_token_expired)

    def test_access_token_expired_empty_store(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertFalse(authenticator.access_token_expired)

    @patch('time.time', mock_time)
    def test_access_token_not_expired(self):
        store = DictAuthenticationStore({
            'access_token': 'aaa',
            'expires_at': 15000,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        self.assertEqual(authenticator.access_token, 'aaa')

    @requests_mock.mock()
    @patch('time.time', mock_time)
    def test_access_token_expired(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', text=json.dumps({
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123
        }))
        store = DictAuthenticationStore({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_at': 5000,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        self.assertEqual(authenticator.access_token, 'ccc')
        self.assertDictEqual(authenticator.store.get(), {
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123,
            'expires_at': 10123,
        })

    def test_access_token_empty_store(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertRaises(ValueError, lambda: authenticator.access_token)

    @requests_mock.mock()
    def test_request_access_token_date_header(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?code=zzz', text=json.dumps({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 123,
        }), headers={'Date': 'Sat, 1 Jan 2000 00:00:00 GMT'})
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.request_access_token('zzz')
        x = authenticator.store.get()
        self.assertDictEqual(authenticator.store.get(), {
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 123,
            'expires_at': 946684923,
        })

    @requests_mock.mock()
    @patch('time.time', mock_time)
    def test_request_access_token_no_date_header(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?code=zzz', text=json.dumps({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 123,
        }))
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.request_access_token('zzz')
        self.assertDictEqual(authenticator.store.get(), {
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 123,
            'expires_at': 10123,
        })

    @requests_mock.mock()
    def test_request_access_token_server_error(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?code=zzz', status_code=500)
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        self.assertRaises(APIError, authenticator.request_access_token, 'zzz')

    @requests_mock.mock()
    def test_refresh_access_token_date_header(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', text=json.dumps({
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123
        }), headers={'Date': 'Sat, 1 Jan 2000 00:00:00 GMT'})
        store = DictAuthenticationStore({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 111,
            'expires_at': 222,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        authenticator.refresh_access_token()
        self.assertDictEqual(authenticator.store.get(), {
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123,
            'expires_at': 946684923,
        })

    @requests_mock.mock()
    @patch('time.time', mock_time)
    def test_refresh_access_token_no_date_header(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', text=json.dumps({
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123
        }))
        store = DictAuthenticationStore({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 111,
            'expires_at': 222,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        authenticator.refresh_access_token()
        self.assertDictEqual(authenticator.store.get(), {
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123,
            'expires_at': 10123,
        })

    @requests_mock.mock()
    def test_refresh_access_token_server_error(self, m):
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', status_code=500)
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        store = DictAuthenticationStore({
            'access_token': 'aaa',
            'refresh_token': 'bbb',
            'expires_in': 111,
            'expires_at': 222,
        })
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback', store)
        self.assertRaises(APIError, authenticator.refresh_access_token)
