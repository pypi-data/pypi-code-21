from collections import namedtuple
import json
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

import pytest

from nauth.tests.fixtures.requests import get, delete, post  # noqa
from nauth.clients.auth_client import AuthClientConfig
from nauth.clients.auth0_client import Auth0Client


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.text = json.dumps(json_data)
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture
def send_register_user_request(monkeypatch):
    def mock_register_user_request(*args, **kwargs):
        json_res = {"user_id": "fake_provider|fake_user_id"}
        res = MockResponse(json_res, 201)
        return res
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.'
                        '_send_register_user_request',
                        mock_register_user_request)


@pytest.fixture
def send_update_user_request(monkeypatch):
    def mock_update_user_request(*args, **kwargs):
        json_res = {}
        res = MockResponse(json_res, 200)
        return res
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.'
                        '_send_update_user_request', mock_update_user_request)


@pytest.fixture
def send_identity_request(monkeypatch):
    def mock_identity_request(*args, **kwargs):
        json_res = {}
        res = MockResponse(json_res, 201)
        return res
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.'
                        '_send_identity_request', mock_identity_request)


@pytest.fixture
def send_register_user_request_failure(monkeypatch):
    def mock_register_user_request(*args, **kwargs):
        json_res = {"user_id": "fake_provider|fake_user_id"}
        res = MockResponse(json_res, 500)
        return res
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.'
                        '_send_register_user_request',
                        mock_register_user_request)


@pytest.fixture(scope='module')
def auth0_client():
    auth_config = AuthClientConfig(
        client_id="test",
        client_secret="test",
        auth_host="http://test")
    client = Auth0Client(auth_config)
    return client


def test_register_user(auth0_client, send_register_user_request,
                       send_update_user_request, send_identity_request):
    """
    register_user() shall run without raising exception if responses
     from Auth0 are correct.
    """
    User = namedtuple('User', ['name', 'email'])
    test_user = User('tomato', 'tomato@potato.com')
    Tenant = namedtuple('Tenant', ['name'])
    test_tenant = Tenant('tenant')
    password = 'potato'

    auth0_client.register_user(test_user, password, test_tenant)


def test_register_user_(auth0_client, send_register_user_request_failure,
                        send_update_user_request, send_identity_request):
    """
    register_user() shall raise exception when one of Auth0 responses fails.
    """
    User = namedtuple('User', ['name', 'email'])
    test_user = User('tomato', 'tomato@potato.com')
    Tenant = namedtuple('Tenant', ['name'])
    test_tenant = Tenant('tenant')
    password = 'potato'

    with pytest.raises(RuntimeError):
        auth0_client.register_user(test_user, password, test_tenant)


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({'ticket': 'http://fake-url.com'},
                                       200)])
def test_send_register_user_request(monkeypatch, post, auth0_client):
    monkeypatch.setattr('nauth.clients.auth0_client.'
                        'Auth0Client._get_auth_header',
                        lambda x: None)

    Tenant = namedtuple('Tenant', ['name'])
    fake_tenant = Tenant('tenant')

    expected_request_json = {'email': 'fake@fake.com',
                             'email_verified': True,
                             'connection': 'fake_connection',
                             'password': 'fake_pass',
                             'user_metadata': {'tenant': fake_tenant.name}}

    auth0_client._send_register_user_request(
        username=expected_request_json['email'],
        connection=expected_request_json['connection'],
        password=expected_request_json['password'],
        tenant=fake_tenant)

    assert expected_request_json == post.json


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({'ticket': 'http://fake-url.com'},
                                       200)])
def test_get_password_reset_url(monkeypatch, post, auth0_client):
    monkeypatch.setattr('nauth.clients.auth0_client.'
                        'Auth0Client._get_auth_header',
                        lambda x: None)

    expected_url = 'http://fake-url.com'

    assert expected_url == auth0_client.get_password_reset_url(user_id='',
                                                               email='',
                                                               url='')


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse([{'user_id': 'fake_id'}], 200)])
def test_get_userid(monkeypatch, get, auth0_client):
    """
    get_userid() should create a GET /api/v2/users
    request with proper query and
    return id of found user.
    """
    monkeypatch.setattr('nauth.clients.auth0_client.'
                        'Auth0Client._get_auth_header',
                        lambda x: None)

    fake_email = "test@test.com"
    found_id = auth0_client.get_userid(email=fake_email)

    expected_query = 'q=' + quote('email:"{}"'.format(fake_email))
    assert expected_query in get.url
    assert "fake_id" == found_id


@pytest.mark.parametrize("value", [MockResponse(None, 204)])  # noqa
def test_delete_user(monkeypatch, delete, auth0_client):
    fake_id = 'fake_id'
    monkeypatch.setattr('nauth.clients.auth0_client.'
                        'Auth0Client._get_auth_header',
                        lambda x: None)
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.get_userid',
                        lambda x, y: fake_id)

    fake_email = "test@test.com"
    auth0_client.delete_user(email=fake_email)

    assert "{}/{}".format(auth0_client.user_management_endpoint,
                          fake_id) == delete.url


@pytest.mark.parametrize("value", [MockResponse(None, 200)])  # noqa
def test_delete_user_no_userid(monkeypatch, delete, auth0_client):
    """
    delete_user() should raise a RuntimeError when userid was not obtained.
    """
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client'
                        '._get_auth_header',
                        lambda x: None)
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.get_userid',
                        lambda x, y: None)

    fake_email = "test@test.com"

    with pytest.raises(RuntimeError):
        auth0_client.delete_user(email=fake_email)


@pytest.mark.parametrize("value", [MockResponse(None, 404)])  # noqa
def test_delete_user_failure(monkeypatch, delete, auth0_client):
    """
    delete_user() should raise a RuntimeError when Auth0 returns status code
    different than 200.
    """
    fake_id = 'fake_id'
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client'
                        '._get_auth_header',
                        lambda x: None)
    monkeypatch.setattr('nauth.clients.auth0_client.Auth0Client.get_userid',
                        lambda x, y: fake_id)

    fake_email = "test@test.com"

    with pytest.raises(RuntimeError):
        auth0_client.delete_user(email=fake_email)
