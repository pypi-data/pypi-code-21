# coding: utf-8
import os
import spur
import shlex
import logging
import simplejson as json
from unittest2 import TestCase
from branchesv import branches, utils

logger = logging.getLogger('deployv')


class TestBranches(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gitbranch = branches.GitBranch()
        cls.shell = spur.LocalShell()
        cls._clone_test_repos('branch_test/')
        cls.branches_config = utils.simplify_path(
            cls.gitbranch.get_branches('branch_test/')
        )

    @staticmethod
    def _clone_test_repos(path_to_clone):
        shell = spur.LocalShell()
        repos = [('https://github.com/Vauxoo/deploy-templates.git', 'deploy-templates'),
                 ('https://github.com/Vauxoo/docker_entrypoint.git', 'docker_entrypoint'),
                 ('https://github.com/Vauxoo/pylint-conf', 'docker_entrypoint/pylint')]
        for repo in repos:
            clone = 'git clone {repo} {path}'.format(
                repo=repo[0],
                path=os.path.join(path_to_clone, repo[1]))
            shell.run(shlex.split(clone))

    def test_10_is_branch(self):
        is_branch = self.gitbranch.is_branch('branch_test/deploy-templates')
        self.assertTrue(is_branch)

    def test_20_get_recursive_branches(self):
        path = 'branch_test/'
        repos_names = []
        repos = self.gitbranch.get_recursive_branches(path)
        self.assertIsInstance(repos, list)
        self.assertEquals(len(repos), 3)
        for repo in repos:
            repos_names.append(repo['name'])
        self.assertIn('deploy-templates', repos_names)
        self.assertIn('docker_entrypoint', repos_names)
        self.assertIn('pylint-conf', repos_names)

    def test_30_get_branches(self):
        recursive_repos = self.gitbranch.get_branches('branch_test/docker_entrypoint',
                                                      recursive=True)
        self.assertEquals(len(recursive_repos), 2)
        norecursive_repos = self.gitbranch.get_branches('branch_test/docker_entrypoint',
                                                        recursive=False)
        self.assertEquals(len(norecursive_repos), 1)

    def test_40_set_branch(self):
        clone_branch_latest = self.gitbranch.set_branch(self.branches_config[0],
                                                        'branch_test/test40')
        self.assertEqual(clone_branch_latest.get('name'),
                         self.branches_config[0].get('name'))
        self.assertTrue(os.path.exists(os.path.join('branch_test/test40',
                                                    self.branches_config[0].get('path'))))
#        cmd = ('git -C branch_test/test40/{repo}/ log'
#               ' --pretty=format:\'%H\' -n 1'.format(repo=clone_branch_latest['name']))
#        res = self.shell.run(shlex.split(cmd))
#        current_commit = res.output
#        self.assertEqual(current_commit.strip(), self.branches_config[0].get('commit'))

    def test_60_action_file(self):
        branches.action_file('branch_test', 'action_file',
                             'branch_test')
        self.assertTrue(os.path.exists('branch_test/action_file'))

    def test_99_cleanup(self):
        utils.clean_files('branch_test')
