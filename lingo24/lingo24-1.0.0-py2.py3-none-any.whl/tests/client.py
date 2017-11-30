import json
import requests_mock
from mock import Mock, patch

from lingo24.business_documents import (
    Authenticator,
    Client,
    )

from .base import BaseTestCase


mock_time = Mock()
mock_time.return_value = 10000


class ClientTestCase(BaseTestCase):
    def test_api_endpoint_url(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
    
        default_client = Client(authenticator)
        self.assertURLEqual(default_client.api_endpoint_url, 'https://api.lingo24.com/docs/v1/')
    
        live_client = Client(authenticator, 'live')
        self.assertURLEqual(live_client.api_endpoint_url, 'https://api.lingo24.com/docs/v1/')
    
        demo_client = Client(authenticator, 'demo')
        self.assertURLEqual(demo_client.api_endpoint_url, 'https://api-demo.lingo24.com/docs/v1/')

    def test_make_url(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        client = Client(authenticator, 'demo')
        url = client.make_url('abc/def')
        self.assertEqual(url, 'https://api-demo.lingo24.com/docs/v1/abc/def')

    @requests_mock.mock()
    def test_status(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/status', text=json.dumps({
            'version': '1.2.3',
            'date': 1234567890,
        }))
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        client = Client(authenticator, 'demo')
        status = client.status
        self.assertEqual(status.version, '1.2.3')
        self.assertEqual(status.date, 1234567890)

    @requests_mock.mock()
    def test_authentication(self, m):
        def check_auth(request):
            return request.headers['Authorization'] == 'Bearer aaa'
        m.get('https://api-demo.lingo24.com/docs/v1/foo', additional_matcher=check_auth, text='{}')
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        client = Client(authenticator, 'demo')
        client.api_get('foo')

    @requests_mock.mock()
    @patch('time.time', mock_time)
    def test_authentication_expired_on_client(self, m):
        def check_auth(request):
            return request.headers['Authorization'] == 'Bearer ccc'
        m.get('https://api-demo.lingo24.com/docs/v1/foo', additional_matcher=check_auth, text='{}')
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', text=json.dumps({
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123
        }))
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa', 'refresh_token': 'bbb', 'expires_at': 1000})
        client = Client(authenticator, 'demo')
        client.api_get('foo')

    @requests_mock.mock()
    @patch('time.time', mock_time)
    def test_authentication_expired_on_server(self, m):
        def text_callback(request, context):
            if request.headers['Authorization'] == 'Bearer ccc':
                return '{}'
            else:
                context.status_code = 401
        m.get('https://api-demo.lingo24.com/docs/v1/foo', text=text_callback)
        m.post('https://api.lingo24.com/docs/v1/oauth2/access?refresh_token=bbb', text=json.dumps({
            'access_token': 'ccc',
            'refresh_token': 'ddd',
            'expires_in': 123
        }))
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa', 'refresh_token': 'bbb', 'expires_at': 50000})
        client = Client(authenticator, 'demo')
        client.api_get('foo')
