import globus_sdk
from tests.framework import (CapturedIOTestCase,
                             get_client_data, get_user_data,
                             SDKTESTER1A_NATIVE1_AUTH_RT)
from globus_sdk.exc import AuthAPIError


class NativeAppAuthClientTests(CapturedIOTestCase):

    def setUp(self):
        """
        Instantiates an NativeAppAuthClient
        """
        super(NativeAppAuthClientTests, self).setUp()

        self.nac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])

    def test_init(self):
        """
        Confirms value error when trying to init with an authorizer
        """
        with self.assertRaises(ValueError):
            globus_sdk.NativeAppAuthClient(
                client_id=get_client_data()["native_app_client1"]["id"],
                authorizer=globus_sdk.AccessTokenAuthorizer(""))

    def test_get_identities(self):
        """
        Confirms native apps aren't authorized to get_identities on their own
        """
        with self.assertRaises(AuthAPIError) as apiErr:
            self.nac.get_identities(ids=get_user_data()["sdktester1a"]["id"])
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "UNAUTHORIZED")

    def test_oauth2_refresh_token(self):
        """
        Sends a refresh_token grant, validates results
        Confirms received access_token can be used to authorize userinfo
        Returns the access token for use in test_oauth2_revoke_token
        """
        ref_res = self.nac.oauth2_refresh_token(SDKTESTER1A_NATIVE1_AUTH_RT)
        self.assertIn("access_token", ref_res)
        self.assertIn("expires_in", ref_res)
        self.assertIn("scope", ref_res)
        self.assertEqual(ref_res["resource_server"], "auth.globus.org")
        self.assertEqual(ref_res["token_type"], "Bearer")

        # confirm token can be used
        access_token = ref_res["access_token"]
        ac = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(access_token),
            client_id=get_client_data()["native_app_client1"]["id"])
        userinfo_res = ac.oauth2_userinfo()
        self.assertEqual(
            userinfo_res["sub"],
            get_user_data()["sdktester1a"]["id"])

        # return access_token
        return access_token

    def test_oauth2_revoke_token(self):
        """
        Gets an access_token from test_oauth2_refresh_token, then revokes it
        Confirms that the base AuthClient logic for handling Null Authorizers
        passes the client id correctly, and the token can no longer be used
        """
        # get and then revoke the token
        access_token = self.test_oauth2_refresh_token()
        rev_res = self.nac.oauth2_revoke_token(access_token)
        # validate results
        self.assertFalse(rev_res["active"])

        # confirm token is no longer usable
        with self.assertRaises(AuthAPIError) as apiErr:
            ac = globus_sdk.AuthClient(
                authorizer=globus_sdk.AccessTokenAuthorizer(access_token),
                client_id=get_client_data()["native_app_client1"]["id"])
            ac.oauth2_userinfo()
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "FORBIDDEN")
