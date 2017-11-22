# coding=utf-8
import fudge
import httpretty
from fudge.inspector import arg

from mali import cli
from .base import BaseCliTest
from click.testing import CliRunner


class TestOrgs(BaseCliTest):
    user_org = "user_org_" + BaseCliTest.some_random_shit()
    email_domain = "domain_%s@%s" % (BaseCliTest.some_random_shit(), BaseCliTest.some_random_shit())

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_list_orgs(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'orgs',
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["orgs", "list"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_create_org(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'orgs',
            {
                'org': self.user_org,
            }
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["orgs", "create", "--org", self.user_org], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_auto_join_org_create(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'orgs/{org}/autoJoin'.format(org=self.user_org),
            {
                'domains': [self.email_domain],
            }
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["orgs", "autoJoinDomain", "--org", self.user_org, "--domain", self.email_domain], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)
