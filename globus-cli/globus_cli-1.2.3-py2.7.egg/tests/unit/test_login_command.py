try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk

from tests.framework.cli_testcase import CliTestCase, default_test_config

from globus_cli.config import AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME


class LoginCommandTests(CliTestCase):

    @mock.patch('globus_cli.commands.login.internal_auth_client')
    def test_login_validates_token(self, get_client):
        ac = mock.MagicMock(spec=globus_sdk.NativeAppAuthClient)
        get_client.return_value = ac

        self.run_line("globus login")

        conf = default_test_config()
        a_rt = conf['cli'][AUTH_RT_OPTNAME]
        t_rt = conf['cli'][TRANSFER_RT_OPTNAME]
        ac.oauth2_validate_token.assert_any_call(a_rt)
        ac.oauth2_validate_token.assert_any_call(t_rt)
