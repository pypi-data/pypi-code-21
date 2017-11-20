try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from tests.framework import CapturedIOTestCase


class GlobusAuthorizationCodeFlowManagerTests(CapturedIOTestCase):

    def setUp(self):
        """
        Inits a GlobusAuthorizationCodeFlowManager using a mock AuthClient
        """
        super(GlobusAuthorizationCodeFlowManagerTests, self).setUp()

        self.ac = mock.Mock()
        self.ac.client_id = "client_id"
        self.ac.base_url = "base_url/"
        self.flow_manager = globus_sdk.auth.GlobusAuthorizationCodeFlowManager(
            self.ac, requested_scopes="scopes", redirect_uri="uri",
            state="state")

    def test_init_handles_iterable_scopes(self):
        flow_manager = globus_sdk.auth.GlobusAuthorizationCodeFlowManager(
            self.ac, requested_scopes=["scope1", "scope2"], redirect_uri="uri",
            state="state")
        self.assertEquals(flow_manager.requested_scopes, "scope1 scope2")

    def test_get_authorize_url(self):
        """
        Creates an authorize url, confirms results match object values
        Confirms additional params passed appear in the url
        """
        url = self.flow_manager.get_authorize_url()

        expected_vals = [self.ac.base_url + "v2/oauth2/authorize?",
                         "client_id=", self.ac.client_id,
                         "redirect_uri=", self.flow_manager.redirect_uri,
                         "scope=", self.flow_manager.requested_scopes,
                         "state=", self.flow_manager.state,
                         "response_type=code",
                         "access_type=online"
                         ]
        for val in expected_vals:
            self.assertIn(val, url)

        # confirm additional params are passed
        params = {"param1": "value1", "param2": "value2"}
        param_url = self.flow_manager.get_authorize_url(
            additional_params=params)
        for param, value in params.items():
            self.assertIn(param + "=" + value, param_url)

    def test_exchange_code_for_tokens(self):
        """
        Makes a token exchange with the mock AuthClient,
        Confirms AuthClient gets and sends correct data.
        """
        auth_code = "code"
        self.flow_manager.exchange_code_for_tokens(auth_code)

        expected = {"grant_type": "authorization_code",
                    "code": auth_code.encode("utf-8"),
                    "redirect_uri": self.flow_manager.redirect_uri}
        self.ac.oauth2_token.assert_called_with(expected)
