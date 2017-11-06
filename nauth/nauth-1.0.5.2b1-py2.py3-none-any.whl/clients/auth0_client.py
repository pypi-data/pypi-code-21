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
import base64
from nauth.clients.auth_client import AuthClient
from nauth.utils import get_boolean_env

logger = logging.getLogger()

SSL_CERT_VERIFICATION = get_boolean_env("SSL_CERT_VERIFICATION")


class Auth0Client(AuthClient):
    @property
    def id_token_endpoint(self):
        if self._id_token_endpoint is None:
            return self.get_url_for_endpoint("/oauth/ro/")
        return self._id_token_endpoint

    @property
    def check_token_endpoint(self):
        if self._check_token_endpoint is None:
            return self.get_url_for_endpoint("/tokeninfo")
        return self._check_token_endpoint

    @property
    def user_management_endpoint(self):
        return self.get_url_for_endpoint("/api/v2/users")

    @property
    def password_reset_endpoint(self):
        return self.get_url_for_endpoint("api/v2/tickets/password-change")

    def _get_auth_header(self):
        return {'Authorization': 'Bearer ' + self._auth_management_token}

    def get_email_code_endpoint(self):
        return self.get_url_for_endpoint("/passwordless/start")

    def get_sign_key(self):
        return base64.b64decode(
            self._client_secret
                .replace("_", "/")
                .replace("-", "+")
        )

    def get_id_token_data_payload(self, data, include_refresh_token=False):
        data = super(Auth0Client, self).set_id_token_data_payload(data)
        data["connection"] = data.get("connection",
                                      "Username-Password-Authentication")
        return data

    def get_id_token(self, data, include_refresh_token=False):
        data = self.get_id_token_data_payload(data)
        res = self._make_id_token_request(data)

        if res.status_code == 200:
            res = json.loads(res.text)
            return res["id_token"]

        logger.error(res.text)
        logger.error("Unable to get id_token for {}".format(
            data.get("username", "no username provided")))

        return None

    def send_auth_code_to_email(self, data):
        url = self.get_email_code_endpoint()
        ndata = {
            "connection": "email",
            "send:": "code",
            "email": data["username"],
            "client_id": data["client_id"],
        }
        requests.post(url, data=ndata, verify=SSL_CERT_VERIFICATION)

    def _send_register_user_request(self, username, password=None, tenant=None,
                                    connection=None):
        if not connection:
            raise ValueError("Provide connection type for auth0 user.")

        data = {
            "email": username,
            "email_verified": True,
            "connection": connection
        }

        if password:
            data["password"] = password
        if tenant:
            data["user_metadata"] = {"tenant": tenant.name}

        auth_header = self._get_auth_header()
        res = requests.post(self.user_management_endpoint, json=data,
                            headers=auth_header,
                            verify=SSL_CERT_VERIFICATION)
        return res

    def _send_update_user_request(self, user_id, data):
        auth_header = self._get_auth_header()
        res = requests.patch(self.user_management_endpoint + '/' + user_id,
                             json=data, headers=auth_header,
                             verify=SSL_CERT_VERIFICATION)
        return res

    def _send_identity_request(self, user_id, data):
        auth_header = self._get_auth_header()
        res = requests.post(self.user_management_endpoint + '/' + user_id +
                            '/identities', json=data, headers=auth_header,
                            verify=SSL_CERT_VERIFICATION)
        return res

    def register_user(self, user, password, tenant=None):
        # We need an auth0 user with two types of connections,
        # password (for ncloud) and 'email' for allowing the user to
        # get codes via email to reauthorize ncloud. Auth0 doesn't
        # let you create a user with two types of connection (grr),
        # so we create two users, then link the accounts.

        # create a new Password-connection user
        res = self._send_register_user_request(username=user.email,
                                               password=password,
                                               tenant=tenant,
                                               connection="Username-Password"
                                                          "-Authentication")
        if res.status_code == 201:
            res = json.loads(res.text)
            password_connection_user_id = res["user_id"]
        else:
            raise RuntimeError('Failed to register new user (Password'
                               ' connection). Response: {}'.format(res.text))

        # create a user with the same email, but with an 'email' connection
        # (don't need meta, auth0 throws it away for secondary user any way)
        # TODO: not use carlos's email....
        res = self._send_register_user_request(
            username="chmsail@carlosmorales.com",
            connection="email")
        if res.status_code == 201:
            res = json.loads(res.text)
            email_connection_user_id = res["user_id"]
        else:
            raise RuntimeError('Failed to register new user (Email connection)'
                               '. Response: {}'.format(res.text))

        # Now patch what I just did to set the actual email. Stoopid Auth0
        update_data = {"email": user.email,
                       "client_id": self._client_id}
        res = self._send_update_user_request(email_connection_user_id,
                                             data=update_data)

        if res.status_code != 200:
            raise RuntimeError('Failed to update user (Email connection).'
                               ' Response: {}'.format(res.text))

        # now merge 'em
        (email_connection_provider,
         email_connection_id) = email_connection_user_id.split("|", 2)

        identity_data = {"provider": email_connection_provider,
                         "user_id": email_connection_id}

        res = self._send_identity_request(password_connection_user_id,
                                          data=identity_data)

        if res.status_code != 201:
            raise RuntimeError(
                'Failed to merge email and password connection users.'
                ' Response: {}'.format(res.text))

    def get_password_reset_url(self, user_id=None, url=None, email=None):
        data = {"user_id": user_id}
        if url is not None:
            data["result_url"] = url
        auth_header = self._get_auth_header()
        res = requests.post(self.password_reset_endpoint, data=data,
                            headers=auth_header,
                            verify=SSL_CERT_VERIFICATION)
        password_reset_url = json.loads(res.text).get('ticket', None)
        return password_reset_url

    def get_userid(self, email=None, user_name=None):
        user_id = None

        # See if the user is already in the authz database
        search = "email:\"" + email + "\""  # exact match
        data = {"search_engine": "v2", "q": search}
        headers = self._get_auth_header()

        req = requests.Request(
            'GET', self.user_management_endpoint,
            data=data, headers=headers)
        prepared = req.prepare()
        res = requests.get(
            self.user_management_endpoint + "?" + prepared.body,
            headers=headers)
        if res.status_code == 200:
            res = json.loads(res.text)
            if len(res) > 0:
                user_id = res[0]["user_id"]

        return user_id

    def delete_user(self, email):
        user_id = self.get_userid(email)
        if not user_id:
            raise RuntimeError('Unable to get user_id for {}.'.format(email))
        url = '{}/{}'.format(self.user_management_endpoint, user_id)
        res = requests.delete(url, headers=self._get_auth_header(),
                              verify=SSL_CERT_VERIFICATION)
        if res.status_code != 204:
            raise RuntimeError('Deleting user {} from Auth0 failed.'
                               'Status code: {}, Response {}'
                               .format(email, res.status_code, res.text))
