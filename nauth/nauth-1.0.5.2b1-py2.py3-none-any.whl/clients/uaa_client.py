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
from requests.auth import HTTPBasicAuth
from nauth.utils import get_boolean_env

from nauth.clients.auth_client import AuthClient, AuthCheckTokenPayload
from nauth.errors import UaaLoginError, UaaAuthorizationError,\
    RefreshTokenExpiredError, AccessTokenRefreshError,\
    UserAlreadyExistsException, OldNewPasswordSameException,\
    UserNotFoundException

logger = logging.getLogger()

UAA_TENANT_GROUP_IDENTIFIER = '.tenant'
SSL_CERT_VERIFICATION = get_boolean_env("SSL_CERT_VERIFICATION")


class UaaClient(AuthClient):
    def __init__(self, auth_client_config):
        AuthClient.__init__(self, auth_client_config)
        self._sign_key = None

    @property
    def id_token_endpoint(self):
        if self._id_token_endpoint is None:
            return self.get_url_for_endpoint("/oauth/token/")
        return self._id_token_endpoint

    @property
    def check_token_endpoint(self):
        if self._check_token_endpoint is None:
            return self.get_url_for_endpoint("/check_token")
        return self._check_token_endpoint

    @property
    def user_management_endpoint(self):
        return self.get_url_for_endpoint("/Users")

    @property
    def password_reset_endpoint(self):
        if self._password_reset_endpoint is None:
            return self.get_url_for_endpoint("/reset_password")
        return self._password_reset_endpoint

    @property
    def password_reset_code_endpoint(self):
        return self.get_url_for_endpoint("/password_resets")

    @property
    def groups_endpoint(self):
        return self.get_url_for_endpoint("/Groups")

    def get_sign_key(self):
        if self._sign_key is None:
            auth = self._get_auth()
            token_key_url = self.get_url_for_endpoint("/token_key")
            res = requests.get(token_key_url, auth=auth,
                               verify=SSL_CERT_VERIFICATION)
            payload = AuthClient.get_json_payload(res)
            self._sign_key = payload["value"]
        return self._sign_key

    def get_id_token_data_payload(self, data):
        data = super(UaaClient, self).set_id_token_data_payload(data)
        return data

    def get_id_token(self, data, include_refresh_token=False):
        """
        Perform UAA login with password grant_type
        :param data: dictionary holding username and password keys.
                     Values shall pass credentials of UAA user.
        :param include_refresh_token:
                     Whether we want to return refresh token
                     as second return value.
        :return: access token or access token and refresh token
        :raises UaaLoginError: in case of unsuccessful login
        """
        data = self.get_id_token_data_payload(data)
        res = self._make_id_token_request(data)

        if res.status_code != requests.codes.ok:
            logger.error("HTTP Code: %s, HTTP Body: %s",
                         res.status_code, res.text)
            if res.status_code == requests.codes.unauthorized:
                raise UaaAuthorizationError
            else:
                raise UaaLoginError

        res = json.loads(res.text)
        if include_refresh_token:
            return res["access_token"], res["refresh_token"]
        return res["access_token"]

    def get_refreshed_id_token_data_payload(self, data):
        data["grant_type"] = "refresh_token"
        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret
        return data

    def get_refreshed_id_token(self, data):
        """
        Refresh access token using refresh token
        :param data: dictionary containing 'refresh_token' key
                     with appropriate value
        :return: access_token in case of success
        :raises RefreshTokenExpiredError:  in case of refresh token expiration
        :raises AccessTokenRefreshError: in case of any other error
                                        (status code != 200 and status != 401)
        """
        data = self.get_refreshed_id_token_data_payload(data)
        res = self._make_id_token_request(data)

        if res.status_code == requests.codes.unauthorized \
                and 'expired' in res.text:
            raise RefreshTokenExpiredError
        if res.status_code != requests.codes.ok:
            logger.error("HTTP Code: %s, HTTP Body: %s", res.status_code,
                         res.text)
            raise AccessTokenRefreshError

        res = json.loads(res.text)
        return res["access_token"]

    def _make_id_token_request(self, data):
        auth = self._get_auth()
        url = self.id_token_endpoint
        return requests.post(url, data=data, auth=auth,
                             verify=SSL_CERT_VERIFICATION)

    def _make_check_token_request(self, token):
        auth = self._get_auth()
        data = {"token": token}
        url = self.check_token_endpoint
        res = requests.post(url, data=data, auth=auth,
                            verify=SSL_CERT_VERIFICATION)
        return res

    def _get_access_token(self):
        auth = self._get_auth()
        url = self.id_token_endpoint
        params = {'grant_type': 'client_credentials', 'response_type': 'token'}
        res = requests.post(url, params=params, auth=auth,
                            verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.ok:
            res = json.loads(res.text)
            return res["access_token"]

        return None

    def _get_auth(self):
        return HTTPBasicAuth(self._client_id, self._client_secret)

    def _get_auth_header(self):
        access_token = self._get_access_token()
        if not access_token:
            return None

        return {'Authorization': 'Bearer ' + access_token}

    def get_check_token_response(self, token):
        res = self._make_check_token_request(token)

        if res.status_code == requests.codes.ok:
            res = AuthClient.get_json_payload(res)
            email = res["email"]
            user_id = self.get_userid(email=email)
            tenant = self.get_tenant(user_id) if user_id else None

            return AuthCheckTokenPayload(
                email=email,
                tenant=tenant
            )

        logger.error(res.text)
        logger.error("Unable to check token {}".format(token))

        return None

    def register_user(self, user, password, tenant=None, externalId=None):
        user_id = None
        data = {
            "userName": user.email,
            "name": {
                "givenName": user.first_name,
                "familyName": user.last_name
            },
            "emails": [{"value": user.email, "primary": True}],
            "password": password,
            "externalId": externalId,
        }

        res = requests.post(self.user_management_endpoint, json=data,
                            headers=self._get_auth_header(),
                            verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.created:
            res = json.loads(res.text)
            user_id = res['id']
        elif res.status_code == requests.codes.conflict:
            raise UserAlreadyExistsException(res.text)
        else:
            raise RuntimeError('User registration in UAA failed.'
                               ' Status code: {}, Response: {}'
                               .format(res.status_code, res.text))

        if tenant and tenant.name:
            group_name = tenant.name + UAA_TENANT_GROUP_IDENTIFIER
            try:
                group_id = self.get_group_id(group_name)
                if group_id:
                    self.add_user_to_group(group_id, user_id)
                else:
                    member_info = {'origin': 'uaa', 'type': 'USER',
                                   'value': user_id}
                    self.create_group(group_name, members=[member_info])

            except RuntimeError:
                raise

        return user_id

    def _get_password_reset_code(self, email):
        data = email
        res = requests.post(self.password_reset_code_endpoint, data=data,
                            headers=self._get_auth_header(),
                            verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.created:
            res = json.loads(res.text)
            return res["code"]
        else:
            logger.error('Failed to obtain UAA password reset code.'
                         ' Status code: {}, Response: {}'
                         .format(res.status_code, res.text))
            return None

    def get_password_reset_url(self, user_id=None, url=None, email=None):
        # Password reset URL points to the same endpoint for all UAA users
        code = self._get_password_reset_code(email)
        if code:
            return '{reset_url}?code={code}'.format(
                reset_url=self.password_reset_endpoint,
                code=code)
        else:
            return None

    def get_userid(self, email=None, user_name=None):
        """
        Get UAA user id. Provide either email or user_name parameter in order
        to obtain user's id. If both parameters are provided, user_name will be
        used.
        :param email: user's email
        :param user_name: user's name
        :return: UAA user ID
        """
        user_id = None
        if user_name:
            params = {'filter': 'userName eq "{}"'.format(user_name)}
        elif email:
            params = {'filter': 'email eq "{}"'.format(email)}
        else:
            raise ValueError('Provide email or user_name parameter.')

        res = requests.get(self.user_management_endpoint, params=params,
                           headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.ok:
            res = json.loads(res.text)
            if len(res["resources"]) > 0:
                user_id = res["resources"][0]["id"]
        else:
            logger.error("Failed to obtain UAA's user id."
                         "Status code: {}, Response: {}"
                         .format(res.status_code, res.text))
        return user_id

    def get_user_list(self, max_results=100):
        params = {'count': '{}'.format(str(max_results))}
        res = requests.get(self.user_management_endpoint, params=params,
                           headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code != requests.codes.ok:
            logger.error("Failed to obtain UAA's user list"
                         "Status code: {}, Response: {}"
                         .format(res.status_code, res.text))
            return None

        return json.loads(res.text)

    def update_user(self, user_id, user_name, email,
                    first_name, last_name, externalId=None):
        user_data = {
            'userName': user_name,
            'name': {
                'familyName': last_name,
                'givenName': first_name,
            },
            'emails': [
                {
                    'value': email,
                    'primary': True
                }
            ],
            'externalId': externalId
        }

        url = '{}/{}'.format(self.user_management_endpoint, user_id)
        headers = self._get_auth_header()
        headers['If-Match'] = '*'
        res = requests.put(url, json=user_data, headers=headers,
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code != requests.codes.ok:
            logger.error("Failed to update user {}"
                         "Status code: {}, Response: {}"
                         .format(user_id, res.status_code, res.text))
            raise RuntimeError('Failed to update user {}.'.format(user_id))
        return json.loads(res.text)

    def get_user_ids(self, email):
        """Returns (user_id, external_id) tuple for a user specified with email.

        :param email: User's email.
        :return: Tuple with (user_id, external_id).
        """
        user_id = None
        external_id = None
        params = {'filter': 'email eq "{}"'.format(email)}
        res = requests.get(self.user_management_endpoint, params=params,
                           headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.ok:
            res = json.loads(res.text)
            if len(res["resources"]) > 0:
                res0 = res["resources"][0]
                user_id = res0["id"]
                external_id = res0["externalId"]
        else:
            logger.error("Failed to obtain UAA's user ids."
                         "Status code: {}, Response: {}"
                         .format(res.status_code, res.text))
        return user_id, external_id

    def delete_user(self, email):
        user_id = self.get_userid(email=email)
        if not user_id:
            raise RuntimeError('Unable to get user_id for {}.'.format(email))
        self.delete_user_by_id(user_id)

    def delete_user_by_id(self, user_id):
        if not user_id:
            raise RuntimeError('Undefined used ID.')
        url = '{}/{}'.format(self.user_management_endpoint, user_id)
        res = requests.delete(url, headers=self._get_auth_header(),
                              verify=SSL_CERT_VERIFICATION)
        if res.status_code != requests.codes.ok:
            raise RuntimeError('Deleting user {} from UAA failed.'
                               'Status code: {}, Response {}'
                               .format(user_id, res.status_code, res.text))

    def get_tenant(self, user_id):
        tenant_name = None
        url = "{}/{}".format(self.user_management_endpoint,
                             user_id)
        res = requests.get(url, headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.ok:
            res = json.loads(res.text)
            groups = res["groups"]
            for group in groups:
                if UAA_TENANT_GROUP_IDENTIFIER in group["display"]:
                    tenant_name = group["display"]. \
                        replace(UAA_TENANT_GROUP_IDENTIFIER, '')

        return tenant_name

    def get_group_id(self, name):
        group_id = None
        params = {'filter': 'displayName eq "{}"'.format(name)}
        res = requests.get(self.groups_endpoint, params=params,
                           headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.ok:
            res = json.loads(res.text)
            if len(res["resources"]) > 0:
                group_id = res["resources"][0]["id"]

        return group_id

    def create_group(self, name, members=None):
        """
        Creates a new group in UAA. Raises RuntimeError in case of failure.
        :param name: displayName of new group
        :param members: List of dicts containing members info, as defined
        in https://docs.cloudfoundry.org/api/uaa/#create77
        :return: ID of created group
        """
        data = {'displayName': name}
        if members:
            data['members'] = members
        res = requests.post(self.groups_endpoint,
                            json=data, headers=self._get_auth_header(),
                            verify=SSL_CERT_VERIFICATION)
        if res.status_code == requests.codes.created:
            res = json.loads(res.text)
            group_id = res["id"]
            return group_id
        else:
            raise RuntimeError('Failed to create {} group.'
                               'Status code: {},'
                               ' Response: {}'.format(name, res.status_code,
                                                      res.text))

    def add_user_to_group(self, group_id, user_id):
        url = '{}/{}/members'.format(self.groups_endpoint, group_id)
        data = {'origin': 'uaa',
                'type': 'USER',
                'value': user_id}
        res = requests.post(url, json=data, headers=self._get_auth_header(),
                            verify=SSL_CERT_VERIFICATION)
        if res.status_code != requests.codes.created:
            raise RuntimeError('Failed to add user: {}, to group: {}.'
                               'Status code: {},'
                               ' Response: {}'.format(user_id,
                                                      group_id,
                                                      res.status_code,
                                                      res.text))

    def change_password(self, user_id, old_password, new_password):
        url = '{}/{}/password'.format(self.user_management_endpoint, user_id)
        data = {"oldPassword": old_password, "password": new_password}
        res = requests.put(url, json=data, headers=self._get_auth_header(),
                           verify=SSL_CERT_VERIFICATION)
        if res.status_code != requests.codes.ok:
            if res.status_code == requests.codes.unauthorized:
                raise UaaAuthorizationError('Failed to change password '
                                            'for user: {}. '
                                            'Reason: unauthorized.'
                                            .format(user_id))
            elif res.status_code == requests.codes.not_found:
                raise UserNotFoundException('Failed to change password '
                                            'for user: {}. '
                                            'Reason: user not found.'
                                            .format(user_id))
            elif res.status_code == requests.codes.unprocessable_entity:
                raise OldNewPasswordSameException('Failed to change password '
                                                  'for user: {}. Reason: '
                                                  'new password cannot be '
                                                  'the same as old password.'
                                                  .format(user_id))
            else:
                raise RuntimeError('Failed to change password for user: {}.'
                                   .format(user_id))
