# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-

import json
from collections import namedtuple

import pytest

from nauth.tests.fixtures.requests import post, get, delete  # noqa
from nauth.clients.auth_client import AuthClientConfig
from nauth.clients.uaa_client import UaaClient
from nauth.errors import RefreshTokenExpiredError, AccessTokenRefreshError, \
    UaaAuthorizationError


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.text = json.dumps(json_data)
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture(scope='module')
def uaa_client():
    auth_config = AuthClientConfig(
        client_id="test",
        client_secret="test",
        auth_host="http://test")
    client = UaaClient(auth_config)
    return client


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"email": "Test"}, 200)])
def test_get_check_token_response_returns_tenant(monkeypatch,
                                                 post, uaa_client):
    """
    get_check_token_response() should return proper tenant for an user
    """
    fake_tenant = 'fake tenant'
    fake_user_id = 'fake id'
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_userid',
                        lambda *args, **kwargs: fake_user_id)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_tenant',
                        lambda x, y: fake_tenant)

    token_payload = uaa_client.get_check_token_response("")

    assert fake_tenant == token_payload.tenant


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"access_token": "t"}, 200)])
def test_get_id_token_request(post, uaa_client):
    """
    get_id_token() should set response_type to id_token
    """
    data = {}

    uaa_client.get_id_token(data)
    expected = {
        "client_id": "test",
        "client_secret": "test",
        "scope": "openid",
        "grant_type": "password",
        "response_type": "id_token",
    }

    assert (post.data == expected)


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse("", 401)])
def test_get_id_token_error(monkeypatch, post, uaa_client):
    with pytest.raises(UaaAuthorizationError):
        uaa_client.get_id_token({})


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"access_token": "t"}, 200)])
def test_get_refreshed_id_token_request(post, uaa_client):
    """
    get_refreshed_id_token() should set response_type to access_token
    """
    data = {}

    uaa_client.get_refreshed_id_token(data)
    expected = {
        "client_id": "test",
        "client_secret": "test",
        "grant_type": "refresh_token",
    }

    assert (post.data == expected)


@pytest.mark.parametrize("value, exception",  # noqa
                         [(MockResponse("Refresh token expired", 401),
                           RefreshTokenExpiredError),
                          (MockResponse("Error", 500),
                           AccessTokenRefreshError)])
def test_refreshed_id_token_negative(monkeypatch, post, uaa_client, exception):
    with pytest.raises(exception):
        uaa_client.get_refreshed_id_token({})


@pytest.mark.parametrize("value", [MockResponse({'id': 'fake-id'},  # noqa
                                                201)])
def test_register_user(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_group_id',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.create_group',
                        lambda *args, **kwargs: None)

    expected_id = 'fake-id'

    User = namedtuple('User', ['email', 'first_name', 'last_name'])
    fake_user = User('fake@fake.com', 'fake', 'user')
    Tenant = namedtuple('Tenant', ['name'])
    fake_tenant = Tenant('fake_tenant')

    created_user_id = uaa_client.register_user(user=fake_user,
                                               password='', tenant=fake_tenant)

    assert expected_id == created_user_id


@pytest.mark.parametrize("value", [MockResponse({'id': 'fake-id'},  # noqa
                                                201)])
def test_register_user_tenant_exists(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_group_id',
                        lambda *args, **kwargs: 'fake-group-id')
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.add_user_to_group',
                        lambda *args, **kwargs: None)

    expected_id = 'fake-id'

    User = namedtuple('User', ['email', 'first_name', 'last_name'])
    fake_user = User('fake@fake.com', 'fake', 'user')
    Tenant = namedtuple('Tenant', ['name'])
    fake_tenant = Tenant('fake_tenant')

    created_user_id = uaa_client.register_user(user=fake_user,
                                               password='', tenant=fake_tenant)

    assert expected_id == created_user_id


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({'id': 'fake-id'}, 201)])
def test_register_user_group_creation_fails(monkeypatch, post, uaa_client):
    def create_group_failure(*args, **kwargs):
        raise RuntimeError

    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.create_group',
                        create_group_failure)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_group_id',
                        lambda *args, **kwargs: None)

    User = namedtuple('User', ['email', 'first_name', 'last_name'])
    fake_user = User('fake@fake.com', 'fake', 'user')
    Tenant = namedtuple('Tenant', ['name'])
    fake_tenant = Tenant('fake_tenant')

    with pytest.raises(RuntimeError):
        uaa_client.register_user(user=fake_user, password='',
                                 tenant=fake_tenant)


@pytest.mark.parametrize("value", [MockResponse({'code': 'fake-code'},  # noqa
                                                201)])
def test_get_password_reset_url(monkeypatch, post, uaa_client):
    """
    get_password_reset_url() should return a following URL:
     <reset_password_endpoint>/<reset_code>, where reset_code is obtained from
     UAA in _get_password_reset_code() method.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_code = 'fake-code'

    expected_url = '{reset_password_endpoint}?code={code}'.format(
        reset_password_endpoint=uaa_client.password_reset_endpoint,
        code=fake_code)

    assert expected_url == uaa_client.get_password_reset_url()


@pytest.mark.parametrize("value", [MockResponse(None,  # noqa
                                                500)])
def test_get_password_reset_url_failure(monkeypatch, post, uaa_client):
    """
    get_password_reset_url() should return a following URL:
     <reset_password_endpoint>/<reset_code>, where reset_code is obtained from
     UAA in _get_password_reset_code() method.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    assert uaa_client.get_password_reset_url() is None


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"resources": [{"id": "fake-id"}]},
                                       200)])
def test_get_userid(monkeypatch, get, uaa_client):
    """
    get_userid() should create a GET /Users request with proper filter and
    return id of found user.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_email = "test@test.com"
    found_id = uaa_client.get_userid(email=fake_email)

    expected_params = {'filter': 'email eq "{}"'.format(fake_email)}
    assert expected_params == get.params
    assert "fake-id" == found_id


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"resources": [{"id": "fake-id"}]},
                                       200)])
def test_get_user_list(monkeypatch, get, uaa_client):
    """
    get_user_list() should create a GET /Users request
    and return list of found user.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    max_results = 99
    expected_params = {'count': '{}'.format(str(max_results))}
    result = uaa_client.get_user_list(max_results)

    assert expected_params == get.params
    assert result == {"resources": [{"id": "fake-id"}]}


@pytest.mark.parametrize("value", [MockResponse(None, 500)])  # noqa
def test_get_userid_failure(monkeypatch, get, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_email = "test@test.com"
    found_id = uaa_client.get_userid(email=fake_email)
    assert found_id is None


@pytest.mark.parametrize("value", [MockResponse(None, 200)])  # noqa
def test_delete_user(monkeypatch, delete, uaa_client):
    """
    delete_user() should make a delete request on /Users/<user_id> path
    """
    fake_id = 'fake_id'
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_userid',
                        lambda *args, **kwargs: fake_id)

    fake_email = "test@test.com"

    uaa_client.delete_user(email=fake_email)

    assert "{}/{}".format(uaa_client.user_management_endpoint,
                          fake_id) == delete.url


@pytest.mark.parametrize("value", [MockResponse(None, 200)])  # noqa
def test_delete_user_no_userid(monkeypatch, delete, uaa_client):
    """
    delete_user() should raise a RuntimeError when userid was not obtained.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_userid',
                        lambda *args, **kwargs: None)

    fake_email = "test@test.com"

    with pytest.raises(RuntimeError):
        uaa_client.delete_user(email=fake_email)


@pytest.mark.parametrize("value", [MockResponse(None, 404)])  # noqa
def test_delete_user_failure(monkeypatch, delete, uaa_client):
    """
    delete_user() should raise a RuntimeError when UAA returns status code
    different than 200.
    """
    fake_id = 'fake_id'
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient.get_userid',
                        lambda *args, **kwargs: fake_id)

    fake_email = "test@test.com"

    with pytest.raises(RuntimeError):
        uaa_client.delete_user(email=fake_email)


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({'groups':
                                            [{'display': 'scim.read'},
                                             {'display': 'scim.write'},
                                             {'display': 'Fake tenant.tenant'}
                                             ]
                                        }, 200)])
def test_get_tenant(monkeypatch, get, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)
    fake_tenant = 'Fake tenant'
    user_id = 'fake-id'
    found_tenant = uaa_client.get_tenant(user_id)

    expected_url = '{}/{}'.format(uaa_client.user_management_endpoint, user_id)
    assert expected_url == get.url
    assert fake_tenant == found_tenant


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse(None, 500)])
def test_get_tenant_failure(monkeypatch, get, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    found_tenant = uaa_client.get_tenant('')
    assert found_tenant is None


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"resources": [{"id": "fake-id"}]},
                                       200)])
def test_get_group_id(monkeypatch, get, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_group_id = 'fake-id'
    fake_group_name = 'fake-group'

    found_group_id = uaa_client.get_group_id(fake_group_name)

    expected_params = {'filter': 'displayName eq "{}"'.format(fake_group_name)}
    assert expected_params == get.params
    assert fake_group_id == found_group_id


@pytest.mark.parametrize("value", [MockResponse({"id": "fake-id"},  # noqa
                                                201)])
def test_create_group(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    expected_group_id = 'fake-id'

    created_group_id = uaa_client.create_group(name='', members=[])

    assert expected_group_id == created_group_id


@pytest.mark.parametrize("value", [MockResponse(None, 500)])  # noqa
def test_create_group_failure(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError):
        uaa_client.create_group(name='', members=['fake_member'])


@pytest.mark.parametrize("value", [MockResponse(None, 201)])  # noqa
def test_add_user_to_group(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    group_id = 'fake-group-id'
    user_id = 'fake-user-id'

    expected_post_json = {'origin': 'uaa',
                          'type': 'USER',
                          'value': user_id}

    uaa_client.add_user_to_group(group_id=group_id, user_id=user_id)

    assert expected_post_json == post.json


@pytest.mark.parametrize("value", [MockResponse(None, 500)])  # noqa
def test_add_user_to_group_failure(monkeypatch, post, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    group_id = 'fake-group-id'
    user_id = 'fake-user-id'

    with pytest.raises(RuntimeError):
        uaa_client.add_user_to_group(group_id=group_id, user_id=user_id)
