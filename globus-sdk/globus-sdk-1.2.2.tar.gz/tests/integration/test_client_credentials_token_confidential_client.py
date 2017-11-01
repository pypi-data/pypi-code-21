try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from tests.framework import CapturedIOTestCase, get_client_data, GO_EP1_ID
from globus_sdk.exc import GlobusAPIError


class ClientCredentialsAuthorizerIntegrationTests(CapturedIOTestCase):

    def setUp(self):
        """
        Makes a client_credentials grant to get new tokens for testing
        Sets up an ConfidentialClient and a ClientCredentialsAuthorizer
        with a mock on_refresh function for testing their interactions
        """
        super(ClientCredentialsAuthorizerIntegrationTests, self).setUp()

        self.scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"

        client_id = get_client_data()["confidential_app_client1"]["id"]
        client_secret = get_client_data()["confidential_app_client1"]["secret"]
        self.internal_client = globus_sdk.ConfidentialAppAuthClient(
            client_id, client_secret)
        token_res = self.internal_client.oauth2_client_credentials_tokens(
            requested_scopes=self.scopes)
        token_data = token_res.by_resource_server["transfer.api.globus.org"]

        self.access_token = token_data["access_token"]
        self.expires_at = token_data["expires_at_seconds"]

        self.on_refresh = mock.Mock()

        self.authorizer = globus_sdk.ClientCredentialsAuthorizer(
            self.internal_client, scopes=self.scopes,
            access_token=self.access_token, expires_at=self.expires_at,
            on_refresh=self.on_refresh)
        self.tc = globus_sdk.TransferClient(authorizer=self.authorizer)

    def test_get_new_access_token(self):
        """
        Has the Authorizer get a new access_token via the ConfidentialAppClient
        Confirms on_refresh is called, and a different, valid token exists
        """
        # get new access token and confirm side effects
        self.authorizer._get_new_access_token()
        self.on_refresh.assert_called_once()
        self.assertNotEqual(self.access_token, self.authorizer.access_token)

        # confirm new token is usable
        get_res = self.tc.get_endpoint(GO_EP1_ID)
        self.assertEqual(get_res["id"], GO_EP1_ID)

    def test_invalid_access_token(self):
        """
        Invalidates the Authorizer's access_token, then makes a request
        Confirms new access_token is is gotten and request is successful.
        """
        self.internal_client.oauth2_revoke_token(self.access_token)

        # make request, confirm successful despite invalid access_token
        get_res = self.tc.get_endpoint(GO_EP1_ID)
        self.assertEqual(get_res["id"], GO_EP1_ID)
        # confirm new token was gotten
        self.on_refresh.assert_called_once()
        self.assertNotEqual(self.access_token, self.authorizer.access_token)

    def test_invalid_access_token_no_retry(self):
        """
        Invalidates the Authorizer's access_token, then makes a request
        with retry_401=False, confirms 401
        """
        self.internal_client.oauth2_revoke_token(self.access_token)

        # make request, confirm 401
        with self.assertRaises(GlobusAPIError) as apiErr:
            path = self.tc.qjoin_path("endpoint", GO_EP1_ID)
            self.tc.get(path, retry_401=False)
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "AuthenticationFailed")

    def test_multiple_resource_servers(self):
        """
        Attempts to create a ClientCredentialsAuthorizer with scopes
        that span multiple resource servers. Confirms GlobusError raised.
        """
        multi_server_scopes = (
            "urn:globus:auth:scope:transfer.api.globus.org:all email")

        with self.assertRaises(ValueError) as err:
            globus_sdk.ClientCredentialsAuthorizer(
                self.internal_client, scopes=multi_server_scopes)

        self.assertIn("didn't return exactly one token", str(err.exception))
        self.assertIn(multi_server_scopes, str(err.exception))
