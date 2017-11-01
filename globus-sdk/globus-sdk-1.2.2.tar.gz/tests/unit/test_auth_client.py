try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from tests.framework import (CapturedIOTestCase,
                             get_client_data, get_user_data,
                             SDKTESTER1A_NATIVE1_AUTH_RT)
from globus_sdk.exc import AuthAPIError


class AuthClientTests(CapturedIOTestCase):

    def setUp(self):
        """
        Instantiates an AuthClient with an access_token authorizer
        """
        super(AuthClientTests, self).setUp()

        # get access token
        client_id = get_client_data()["native_app_client1"]["id"]
        form_data = {'refresh_token': SDKTESTER1A_NATIVE1_AUTH_RT,
                     'grant_type': 'refresh_token',
                     'client_id': client_id}
        token_res = globus_sdk.AuthClient().oauth2_token(form_data)
        self.access_token = token_res["access_token"]

        # make auth client
        self.ac = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(self.access_token),
            client_id=client_id)

    def test_get_identities_singleton(self):
        """
        gets identities with single username and id values, validates results.
        """
        # get single ID
        id_res = self.ac.get_identities(
            ids=get_user_data()["sdktester1a"]["id"])
        sdk_identity = id_res["identities"][0]
        for item in get_user_data()["sdktester1a"]:
            self.assertEqual(sdk_identity[item],
                             get_user_data()["sdktester1a"][item])

        # get single username
        id_res = self.ac.get_identities(
            usernames=get_user_data()["sdktester1a"]["username"])
        sdk_identity = id_res["identities"][0]
        for item in get_user_data()["sdktester1a"]:
            self.assertEqual(sdk_identity[item],
                             get_user_data()["sdktester1a"][item])

    def get_identity(self, identities, uid=None, username=None):
        """
        helper for getting identities since response order isn't guaranteed
        """
        for identity in identities:
            if identity["id"] == uid or identity["username"] == username:
                return identity
        return None

    def test_get_identites_ids(self):
        """
        gets identities with a list of ids, validates results
        """
        unused_id = "12345678-1234-1234-1234-1234567890ab"
        ids = [get_user_data()["sdktester1a"]["id"],
               get_user_data()["go"]["id"], unused_id]
        id_res = self.ac.get_identities(ids=ids)

        # validate sdk
        sdk_identity = self.get_identity(
            id_res["identities"], uid=get_user_data()["sdktester1a"]["id"])
        for item in get_user_data()["sdktester1a"]:
            self.assertEqual(sdk_identity[item],
                             get_user_data()["sdktester1a"][item])

        # validate go
        go_identity = self.get_identity(id_res["identities"],
                                        uid=get_user_data()["go"]["id"])
        for item in get_user_data()["go"]:
            self.assertEqual(go_identity[item], get_user_data()["go"][item])
        unused_identity = self.get_identity(id_res["identities"],
                                            uid=unused_id)

        # confirm unused id isn't returned
        self.assertIsNone(unused_identity)

    def test_get_identities_usernames(self):
        """
        gets identities with a list of usernames, validates results.
        """
        unused_username = "unused@unused.org"
        usernames = [get_user_data()["sdktester1a"]["username"],
                     get_user_data()["go"]["username"], unused_username]
        id_res = self.ac.get_identities(usernames=usernames)

        # validate sdk
        sdk_identity = self.get_identity(
            id_res["identities"],
            username=get_user_data()["sdktester1a"]["username"])
        for item in get_user_data()["sdktester1a"]:
            self.assertEqual(sdk_identity[item],
                             get_user_data()["sdktester1a"][item])

        # validate go
        go_identity = self.get_identity(
            id_res["identities"], username=get_user_data()["go"]["username"])
        for item in get_user_data()["go"]:
            self.assertEqual(go_identity[item], get_user_data()["go"][item])
        unused_identity = self.get_identity(id_res["identities"],
                                            username=unused_username)

        # validate unused
        self.assertEqual(unused_identity["username"], unused_username)
        self.assertEqual(unused_identity["name"], None)
        self.assertEqual(unused_identity["status"], "unused")

    def test_get_identities_errors(self):
        """
        Confirms bad and unauthorized requests to get_identities throw errors
        """
        # bad request
        with self.assertRaises(AuthAPIError) as apiErr:
            self.ac.get_identities(usernames=["a", "b"], ids=["0", "1"])
        self.assertEqual(apiErr.exception.http_status, 400)
        self.assertEqual(apiErr.exception.code, "INVALID_PARAMETERS")

        # no auth
        with self.assertRaises(AuthAPIError) as apiErr:
            globus_sdk.AuthClient().get_identities()
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "UNAUTHORIZED")

    def test_oauth2_get_authorize_url(self):
        """
        Gets an authorize url with no auth flow and a mock auth flow.
        Confirms expected results. Further tested in integration tests.
        """
        # no auth flow raises an error
        with self.assertRaises(ValueError):
            self.ac.oauth2_get_authorize_url()

        # set up mock auth flow
        mock_url = "test-url-return-value.org"
        mock_flow = mock.Mock()
        mock_flow.get_authorize_url = mock.Mock(return_value=mock_url)
        self.ac.current_oauth2_flow_manager = mock_flow

        # get and validate results from mock auth flow
        url_res = self.ac.oauth2_get_authorize_url()
        self.assertEqual(url_res, mock_url)
        mock_flow.get_authorize_url.assert_called_once()

    def test_oauth2_exchange_code_for_tokens(self):
        """
        Confirms flow required to exchange code,
        Does a mock exchange for tokens, validates results.
        Further tested in integration tests.
        """
        # no auth flow
        with self.assertRaises(ValueError):
            self.ac.oauth2_exchange_code_for_tokens("")

        # set up mock auth flow
        mock_flow = mock.Mock()
        mock_code = "mock-code"
        mock_tokens = {"access_token": "mock_token"}
        mock_flow.exchange_code_for_tokens = mock.Mock(
            return_value=mock_tokens)
        self.ac.current_oauth2_flow_manager = mock_flow

        # exchange and validate results from mock auth flow
        token_res = self.ac.oauth2_exchange_code_for_tokens(mock_code)
        self.assertEqual(token_res, mock_tokens)
        mock_flow.exchange_code_for_tokens.assert_called_once_with(mock_code)

    def test_oauth2_refresh_token(self):
        """
        Gets an access token from the testing Refresh Token, validates results
        """
        param = {"client_id": self.ac.client_id}
        ref_res = self.ac.oauth2_refresh_token(
            SDKTESTER1A_NATIVE1_AUTH_RT, additional_params=param)
        self.assertIn("access_token", ref_res)
        self.assertIn("expires_in", ref_res)
        self.assertIn("scope", ref_res)
        self.assertEqual(ref_res["resource_server"], "auth.globus.org")
        self.assertEqual(ref_res["token_type"], "Bearer")

        # without valid client id
        with self.assertRaises(AuthAPIError) as apiErr:
            ref_res = self.ac.oauth2_refresh_token(SDKTESTER1A_NATIVE1_AUTH_RT)
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "Error")  # json is malformed?

    def test_oauth2_revoke_token(self):
        """
        Revokes the access_token used in test AuthClient's authorizer
        Confirms can no longer make authorized requests
        """
        param = {"client_id": self.ac.client_id}
        rev_res = self.ac.oauth2_revoke_token(self.access_token,
                                              additional_params=param)
        self.assertFalse(rev_res["active"])

        with self.assertRaises(AuthAPIError) as apiErr:
            self.ac.get_identities()
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "UNAUTHORIZED")

    def test_oauth2_token(self):
        """
        Gets an access_token using oauth2/token directly, validates results.
        """
        client_id = get_client_data()["native_app_client1"]["id"]
        form_data = {'refresh_token': SDKTESTER1A_NATIVE1_AUTH_RT,
                     'grant_type': 'refresh_token',
                     'client_id': client_id}
        # valid client
        token_res = globus_sdk.AuthClient().oauth2_token(form_data)
        self.assertIn("access_token", token_res)
        self.assertIn("expires_in", token_res)
        self.assertIn("scope", token_res)

    def test_oauth2_userinfo(self):
        """
        Gets userinfo, validates results
        Confirms unauthorized client cannot access userinfo
        """
        userinfo_res = self.ac.oauth2_userinfo()
        self.assertEqual(
            userinfo_res["preferred_username"],
            get_user_data()["sdktester1a"]["username"])
        self.assertEqual(
            userinfo_res["name"],
            get_user_data()["sdktester1a"]["name"])
        self.assertEqual(
            userinfo_res["sub"],
            get_user_data()["sdktester1a"]["id"])

        # unauthorized client
        with self.assertRaises(AuthAPIError) as apiErr:
            globus_sdk.AuthClient().oauth2_userinfo()
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "FORBIDDEN")
