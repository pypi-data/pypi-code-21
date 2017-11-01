# coding=utf-8
import fudge
import httpretty
from click.testing import CliRunner
from fudge.inspector import arg

from mali import cli
from mali_commands.projects import max_project_display_name, max_project_description, min_project_display_name
from tests.base import BaseCliTest


class TestProject(BaseCliTest):
    project_id = BaseCliTest.some_random_shit_number_int63()
    user_org = 'user_org_' + BaseCliTest.some_random_shit()

    @httpretty.activate
    def test_create_project_too_long_display_name(self):
        project_display_name = '9' * (max_project_display_name + 1)

        runner = CliRunner()
        params = ['projects', 'create', '--displayName', project_display_name]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEquals(result.output, 'Usage: cli projects create [OPTIONS]\n\nError: Invalid value for "--displayName": needs to be shorter than %s characters\n' % max_project_display_name)

    @httpretty.activate
    def test_create_project_too_short_display_name(self):
        project_display_name = ''

        runner = CliRunner()
        params = ['projects', 'create', '--displayName', project_display_name]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEquals(result.output, 'Usage: cli projects create [OPTIONS]\n\nError: Invalid value for "--displayName": needs to be longer than %s characters\n' % min_project_display_name)

    @httpretty.activate
    def test_create_project_too_long_description(self):
        project_description = '9' * (max_project_description + 1)
        project_display_name = 'display_' + self.some_random_shit()

        runner = CliRunner()
        params = ['projects', 'create', '--displayName', project_display_name, '--description', project_description]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEquals(result.output, 'Usage: cli projects create [OPTIONS]\n\nError: Invalid value for "--description": needs to be shorter than %s characters\n' % max_project_description)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_create_project_no_org(self, handle_api):
        project_display_name = 'display_' + self.some_random_shit()

        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects',
            {
                'display_name': project_display_name
            },
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['projects', 'create', '--displayName', project_display_name], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_create_project_with_org(self, handle_api):
        org = 'org_' + self.some_random_shit()
        project_display_name = 'display_' + self.some_random_shit()

        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects',
            {
                'display_name': project_display_name,
                'org': org,
            },
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['projects', 'create', '--displayName', project_display_name, '--org', org], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_list_projects(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects',
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["projects", "list"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_list_projects_params_json(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects',
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["-o", "json", "projects", "list"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_list_projects_params_json_old(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects',
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["projects", "list", "-o", "json"], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.commons.handle_api')
    def test_transfer_project(self, handle_api):
        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            'projects/{project_id}/transfer'.format(project_id=self.project_id),
            {
                'transfer_to': self.user_org,
            }
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ["projects", "transfer", "--projectId", self.project_id, "--transferTo", self.user_org], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)
