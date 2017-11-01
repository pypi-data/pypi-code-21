try:
    import mock
except ImportError:
    from unittest import mock

from globus_sdk.authorizers import RefreshTokenAuthorizer
from tests.framework import CapturedIOTestCase


class RefreshTokenAuthorizerTests(CapturedIOTestCase):

    def setUp(self):
        """
        Sets up a RefreshTokenAuthorizer using a mock AuthClient for testing
        """
        super(RefreshTokenAuthorizerTests, self).setUp()
        # known values for testing
        self.refresh_token = "refresh_token_1"
        self.access_token = "access_token_1"
        self.expires_at = -1

        # response values for simulating a refresh token grant response
        self.response = mock.Mock()
        self.response.by_resource_server = {
            "rs1": {
                "expires_at_seconds": -1,
                "access_token": "access_token_2"
            }
        }
        self.rs_data = self.response.by_resource_server['rs1']

        # mock AuthClient for testing
        self.ac = mock.Mock()
        self.ac.oauth2_refresh_token = mock.Mock(
            return_value=self.response)

        self.authorizer = RefreshTokenAuthorizer(
            self.refresh_token, self.ac, access_token=self.access_token,
            expires_at=self.expires_at)

    def test_get_token_response(self):
        """
        Calls _get_token_response, confirms that the mock
        AuthClient is used and the known data was returned.
        """
        # get new_access_token
        res = self.authorizer._get_token_response()
        # confirm expected response
        self.assertEqual(res, self.response)
        # confirm mock ConfidentailAppAuthClient was used as expected
        self.ac.oauth2_refresh_token.assert_called_once_with(
            self.refresh_token)

    def test_multiple_resource_servers(self):
        """
        Sets the mock ConfidentialAppAuthClient to return multiple resource
        servers. Confirms GlobusError is raised when _extract_token_data is
        called.
        """
        self.response.by_resource_server = {
            "rs1": {
                "expires_at_seconds": -1,
                "access_token": "access_token_2"
            },
            "rs2": {
                "expires_at_seconds": -1,
                "access_token": "access_token_3"
            }
        }
        with self.assertRaises(ValueError) as err:
            self.authorizer._extract_token_data(self.response)
        self.assertIn("didn't return exactly one token", str(err.exception))
