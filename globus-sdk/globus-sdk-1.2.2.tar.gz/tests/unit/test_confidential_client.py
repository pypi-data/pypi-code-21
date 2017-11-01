try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from tests.framework import CapturedIOTestCase, get_client_data
from globus_sdk.exc import AuthAPIError


class ConfidentialAppAuthClientTests(CapturedIOTestCase):

    @classmethod
    def setUpClass(self):
        """
        Instantiates an ConfidentialAppAuthClient for confidential_app_client1
        and for resource_server_client
        """

        client_data = get_client_data()["confidential_app_client1"]
        self.cac = globus_sdk.ConfidentialAppAuthClient(
            client_id=client_data["id"],
            client_secret=client_data["secret"])

        client_data = get_client_data()["resource_server_client"]
        self.rsc = globus_sdk.ConfidentialAppAuthClient(
            client_id=client_data["id"],
            client_secret=client_data["secret"])

    def test_oauth2_client_credentials_tokens(self):
        """
        Get client credentials tokens, validate results
        Confirm tokens allow use of userinfo for the client
        Returns access_token for testing
        """
        with mock.patch.object(self.cac, 'oauth2_token',
                               side_effect=self.cac.oauth2_token) as m:
            token_res = self.cac.oauth2_client_credentials_tokens(
                requested_scopes="openid profile")
            m.assert_called_once_with(
                {"grant_type": "client_credentials",
                 "scope": "openid profile"})

        # validate results
        self.assertIn("access_token", token_res)
        self.assertIn("expires_in", token_res)
        self.assertIn("scope", token_res)
        self.assertEqual(token_res["resource_server"], "auth.globus.org")
        self.assertEqual(token_res["token_type"], "Bearer")

        # confirm usage of userinfo for client
        access_token = token_res["access_token"]
        ac = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(access_token))
        userinfo_res = ac.oauth2_userinfo()
        self.assertEqual(
            userinfo_res["sub"],
            get_client_data()["confidential_app_client1"]["id"])

    def test_oauth2_get_dependent_tokens(self):
        """
        Gets dependent tokens for a client access_token, validates results
        Confirms non resource servers are not allowed to use this resource
        Confirms tokens must have scope for the resource_server using them
        """
        # get access_token for confidential client to use the resource server
        scopes = "openid"  # TODO: add resource_server's scope
        tokens = self.cac.oauth2_client_credentials_tokens(
            requested_scopes=scopes).by_resource_server

        '''
        TODO: set up resource_server for testing against
        # resource server gets dependent tokens from the clients token
        # as if the client had sent the token to the resource server
        access_token = tokens["Resource Server Name"]["access_token"]
        dep_res = self.rsc.oauth2_get_dependent_tokens(access_token)

        # validate results
        for token_info in dep_res:
            self.assertEqual(token_info["token_type"], "Bearer")
            self.assertIn("scope", token_info)
            self.assertIn("access_token", token_info)
            self.assertIn("expires_in", token_info)
            self.assertIn("resource_server", token_info)

        # confirm invalid tokens are unauthorized
        invalid_token = tokens["auth.globus.org"]["access_token"]
        with self.assertRaises(AuthAPIError) as apiErr:
            self.rsc.oauth2_get_dependent_tokens(access_token)
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "Error")
        '''

        # confirm non resource servers are unauthorized
        # TODO: use valid token here instead
        invalid_token = tokens["auth.globus.org"]["access_token"]
        with self.assertRaises(AuthAPIError) as apiErr:
            self.cac.oauth2_get_dependent_tokens(invalid_token)
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "Error")

    def test_oauth2_token_introspect(self):
        """
        Introspects a client access_token, validates results
        Confirms invalid and revoked tokens are not seen as active
        """
        # get access_token and introspect it
        tokens = self.cac.oauth2_client_credentials_tokens()
        access_token = tokens["access_token"]
        intro_res = self.cac.oauth2_token_introspect(access_token)

        # validate results
        self.assertEqual(intro_res["sub"], self.cac.client_id)
        self.assertEqual(intro_res["client_id"], self.cac.client_id)
        self.assertEqual(
            intro_res["username"],
            get_client_data()["confidential_app_client1"]["username"])
        self.assertEqual(intro_res["name"],
                         "Python SDK Test Suite Confidential Client 1")
        self.assertEqual(intro_res["token_type"], "Bearer")
        self.assertIn("openid", intro_res["scope"])
        self.assertIn("email", intro_res["scope"])
        self.assertIn("profile", intro_res["scope"])
        self.assertIn("exp", intro_res)
        self.assertTrue(intro_res["active"])

        # revoked tokens are not active
        self.cac.oauth2_revoke_token(access_token)
        revoked_res = self.cac.oauth2_token_introspect(access_token)
        self.assertFalse(revoked_res["active"])

        # invalid tokens are not active
        invalid_res = self.cac.oauth2_token_introspect("invalid token")
        self.assertFalse(invalid_res["active"])
