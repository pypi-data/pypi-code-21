# coding=utf-8
import fudge
import httpretty
from fudge.inspector import arg

from mali import cli
from .base import BaseCliTest
from click.testing import CliRunner


class TestAuth(BaseCliTest):
    client_id = 'client_id_' + BaseCliTest.some_random_shit()
    auth0 = 'auth0_auth_' + BaseCliTest.some_random_shit()
    access_token = 'access_token_' + BaseCliTest.some_random_shit()
    refresh_token = 'refresh_token_' + BaseCliTest.some_random_shit()
    id_token = 'id_token_' + BaseCliTest.some_random_shit()

    @httpretty.activate
    def test_whoami(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["auth", "whoami"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.pixy_flow')
    @fudge.patch('mali_commands.config.Config.update_and_save')
    def test_init_auth(self, pixy_flow, update_and_save_config):
        access_token = 'access_token'
        refresh_token = 'refresh_token'
        id_token = 'id_token'

        pixy_flow.expects_call().returns((access_token, refresh_token, id_token)).times_called(1)
        update_and_save_config.expects_call().with_args(
            {
                'token': {
                    'access_token': access_token,
                    'id_token': id_token,
                    'refresh_token': refresh_token
                }
            }
        ).returns(None).times_called(1)

        runner = CliRunner()
        result = runner.invoke(cli, ["auth", "init"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('werkzeug.serving.make_server')
    @fudge.patch('webbrowser.open')
    @fudge.patch('mali_commands.commons.auth0_oauth_token')
    def test_pixy_flow(self, make_server, webbrowser_open, auth0_oauth_token):
        from mali_commands.commons import pixy_flow, build_auth0_url

        port = self.some_random_shit_number_int63()
        srv = fudge.Fake().has_attr(port=port).provides('serve_forever')

        make_server.expects_call().with_args('127.0.0.1', arg.any(), arg.any()).returns(srv)

        ctx = fudge.Fake().has_attr(local_web_server=True, client_id=self.client_id, auth0=self.auth0)

        webbrowser_open.expects_call()

        verifier = arg.any()
        code = None

        redirect_url = 'http://localhost:%s/console/auth/init' % port

        auth0_oauth_token.expects_call()\
            .with_args(build_auth0_url(self.auth0), code, verifier, self.client_id, redirect_url).returns({
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'id_token': self.id_token,
            })

        pixy_flow(ctx)
