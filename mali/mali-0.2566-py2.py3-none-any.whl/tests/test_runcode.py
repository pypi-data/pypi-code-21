# -*- coding: utf8 -*-
import os

import fudge
from click.testing import CliRunner
from fudge.inspector import arg

from mali import cli
from mali_commands.utilities import source_tracking
from .base import BaseCliTest


class TestAuth(BaseCliTest):
    # TODO: add a test with git init
    def test_code_no_source_not_even_in_dir(self):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}.git'.format(org, repo)
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--tracking-repository", hurl + '1'],
                catch_exceptions=True)
            self.assertEquals(
                result.exception.args[0],
                "Couldn't determinate the remote origin of the current directory, please provide --source-repository url")

    def test_code_bad_source(self):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}.git'.format(org, repo)
        s_url = self.some_random_shit(size=10)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["code", "track", "--org", org_id, "--source-repository", s_url, "--tracking-repository", hurl + '1'],
            catch_exceptions=True)
        self.assertEquals(
            result.exception.args[0],
            "Source repository: {} is invalid".format(s_url))

    def test_code_bad_target(self):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}.git'.format(org, repo)
        s_url = self.some_random_shit(size=10)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["code", "track", "--org", org_id, "--source-repository", gurl, "--tracking-repository", s_url],
            catch_exceptions=True)
        self.assertEquals(
            result.exception.args[0],
            "Tracking repository: {} is invalid".format(s_url))

    def test_code_same_url(self):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}.git'.format(org, repo)

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--source-repository", gurl, "--tracking-repository", gurl],
                catch_exceptions=True)
            self.assertEquals(
                result.exception.args[0],
                "The repository repository can't be the same as the source one")
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--source-repository", gurl, "--tracking-repository", hurl],
                catch_exceptions=True)
            self.assertEquals(
                result.exception.args[0],
                "The repository repository can't be the same as the source one")
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--source-repository", hurl, "--tracking-repository", hurl],
                catch_exceptions=True)
            self.assertEquals(
                result.exception.args[0],
                "The repository repository can't be the same as the source one")
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--source-repository", hurl, "--tracking-repository", gurl],
                catch_exceptions=True)
            self.assertEquals(
                result.exception.args[0],
                "The repository repository can't be the same as the source one")

    def test_code_diff_ogs(self):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}{}/{}xx.git'.format(org, self.some_random_shit(size=2), repo)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["code", "track", "--org", org_id, "--source-repository", hurl, "--tracking-repository", gurl],
            catch_exceptions=True)
        self.assertEquals(
            result.exception.args[0],
            "The tracking repository must belong to the same organization as the source (/{})".format(org))

        hurl = 'https://simhub.com/{}{}/{}x'.format(org, self.some_random_shit(size=2), repo)
        gurl = 'git@simhub.com:{}/{}.git'.format(org, repo)

        result = runner.invoke(
            cli,
            ["code", "track", "--org", org_id, "--source-repository", gurl, "--tracking-repository", hurl],
            catch_exceptions=True)
        self.assertEquals(
            result.exception.args[0],
            "The tracking repository must belong to the same organization as the source (/{})".format(org))

    @fudge.patch('mali_commands.commons.handle_api')
    def test_code_works_with_explicit_source(self, handle_api):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}_1.git'.format(org, repo)
        encoded_url = source_tracking.remote_to_template(hurl)

        handle_api.expects_call().with_matching_args(
            arg.any(),  # ctx
            arg.any(),  # http method
            '{}/code/track?src={}'.format(org_id, encoded_url),
            {
                'target': gurl
            }
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["code", "track", "--org", org_id, "--source-repository", hurl, "--tracking-repository", gurl],
            catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def test_code_works_without_explicit_source(self, handle_api):
        user_id, org_id, org, repo = (self.some_random_shit(size=10) for _ in range(4))
        hurl = 'https://simhub.com/{}/{}'.format(org, repo)
        gurl = 'git@simhub.com:{}/{}_1.git'.format(org, repo)
        encoded_url = source_tracking.remote_to_template(hurl)

        runner = CliRunner()
        with runner.isolated_filesystem():
            import git
            g = git.Repo.init('.')
            g.git.remote('add', 'origin', hurl)
            handle_api.expects_call().with_matching_args(
                arg.any(),  # ctx
                arg.any(),  # http method
                '{}/code/track?src={}'.format(org_id, encoded_url),
                {
                    'target': gurl
                }
            ).returns({})

            result = runner.invoke(
                cli,
                ["code", "track", "--org", org_id, "--tracking-repository", gurl],
                catch_exceptions=False)
            self.assertEquals(result.exit_code, 0)

    def testget_org_from_remote_url(self):
        from mali_commands.utilities import source_tracking
        x = source_tracking.get_org_from_remote_url(os.getcwd())
        self.assertIsNone(x)
        repo = '://simhub.com/{}/{}'.format(self.some_random_shit(size=6), self.some_random_shit(size=9))
        x = source_tracking.remote_to_template('http' + repo)
        self.assertEquals(x, 'https' + repo)
