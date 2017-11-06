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
import logging
import requests
from nauth.utils import get_boolean_env

try:
    # python2 import
    from urlparse import urljoin
except:
    # python3 import
    from urllib.parse import urljoin

logger = logging.getLogger()

SSL_CERT_VERIFICATION = get_boolean_env("SSL_CERT_VERIFICATION")


class AuthClient(object):
    def __init__(self, auth_client_config):
        """
        Marked as protected with getters method
        those fields shouldn't be changed by developer
        """
        self._client_id = auth_client_config.client_id
        self._client_secret = auth_client_config.client_secret
        self._auth_host = auth_client_config.auth_host
        self._id_token_endpoint = auth_client_config.id_token_endpoint
        self._check_token_endpoint = auth_client_config.check_token_endpoint
        self._user_management_endpoint = \
            auth_client_config.user_management_endpoint
        self._password_reset_endpoint = \
            auth_client_config.password_reset_endpoint
        self._auth_management_token = auth_client_config.auth_management_token

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def token_endpoint(self):
        return self._id_token_endpoint

    @property
    def auth_host(self):
        return self._auth_host

    @property
    def check_token_endpoint(self):
        return self._check_token_endpoint

    @property
    def password_reset_endpoint(self):
        return self._password_reset_endpoint

    def get_url_for_endpoint(self, endpoint):
        return urljoin(self._auth_host, endpoint)

    def get_id_token_data_payload(self, data):
        raise NotImplementedError("No id token payload")

    def get_sign_key(self):
        raise NotImplementedError("No sign key defined")

    def get_id_token(self, data, include_refresh_token=False):
        raise NotImplementedError("No id token defined")

    def get_refreshed_id_token(self, data):
        raise NotImplementedError("No refreshed id token defined")

    def set_id_token_data_payload(self, data):
        # Populate openid data constants
        data["scope"] = "openid"
        data["grant_type"] = "password"
        data["response_type"] = "id_token"

        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret
        return data

    def _make_id_token_request(self, data):
        url = self.token_endpoint
        return requests.post(url, data=data,
                             verify=SSL_CERT_VERIFICATION)

    def _make_check_token_request(self, token):
        data = {"id_token": token}
        url = self.check_token_endpoint
        return requests.post(url, data=data,
                             verify=SSL_CERT_VERIFICATION)

    def get_check_token_response(self, token):
        res = self._make_check_token_request(token)

        if res.status_code == 200:
            return AuthCheckTokenPayload.from_response(res)

        logger.error(res.text)
        logger.error("Unable to check token {}".format(token))

        return None

    def register_user(self, user, password, tenant=None):
        raise NotImplementedError("User registration is not implemented.")

    def get_password_reset_url(self, user_id=None, url=None, email=None):
        raise NotImplementedError("Getting password reset URL"
                                  " is not implemented.")

    def get_userid(self, email=None, user_name=None):
        raise NotImplementedError("Getting user ID is not implemented.")

    def change_password(self, user_id, old_password, new_password):
        raise NotImplementedError("Change password is not implemented.")

    @staticmethod
    def get_json_payload(res):
        return json.loads(res.text)


class AuthCheckTokenPayload(object):
    def __init__(self, email="", tenant=""):
        self.email = email
        self.tenant = tenant

    @classmethod
    def from_response(cls, response):
        res = json.loads(response.text)
        return cls(
            email=res["email"],
            tenant=res["user_metadata"]["tenant"])


class AuthClientConfig(object):
    def __init__(self, client_id="", client_secret="", sign_key="",
                 id_token_endpoint=None, check_token_endpoint=None,
                 user_management_endpoint=None, password_reset_endpoint=None,
                 auth_management_token=None,
                 auth_host="", auth_type="cloud"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sign_key = sign_key
        self.id_token_endpoint = id_token_endpoint
        self.check_token_endpoint = check_token_endpoint
        self.user_management_endpoint = user_management_endpoint
        self.password_reset_endpoint = password_reset_endpoint
        self.auth_management_token = auth_management_token
        self.auth_host = auth_host
        self.auth_type = auth_type

    @classmethod
    def from_config(cls, config):
        return cls(
            client_secret=config['AUTH_CLIENT_SECRET'],
            client_id=config['AUTH_CLIENT_ID'],
            id_token_endpoint=config.get('AUTH_AUTHENTICATION_URL', None),
            check_token_endpoint=config.get('AUTH_TOKENINFO_URL', None),
            user_management_endpoint=config.get('AUTH_MANAGEMENT_URL', None),
            password_reset_endpoint=config.get('AUTH_PASSWORD_RESET_URL',
                                               None),
            auth_management_token=config.get('AUTH_MANAGEMENT_TOKEN', None),
            auth_host=config['AUTH_HOST'],
            auth_type=config['AUTH_TYPE'])
