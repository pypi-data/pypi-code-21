from unittest import TestCase
from uuid import uuid4

from gitbarry.utils import git


class UtilsGitTests(TestCase):
    def test_assert_is_git_repo(self):
        git.assert_is_git_repo()

    def test_get_current_branch(self):
        self.assertIsNotNone(git.get_current_branch())

    def test_get_local_branches(self):
        local_branches = git.get_local_branches()
        self.assertIsInstance(local_branches, list)
        self.assertGreater(len(local_branches), 0)

    def test_create__switch_merge(self):
        # Need to create branch because gitlab ci created detached repository for test
        git.create_new_branch('ci-branch', False)

        current_branch = git.get_current_branch()
        new_branch_name = "ci-testing-branch_balba-%s" % str(uuid4())
        git.create_new_branch(new_branch_name, False)
        self.assertIn(new_branch_name, git.get_local_branches())

        git.swith_to_branch(new_branch_name)
        switched = git.get_current_branch()
        self.assertEqual(switched, new_branch_name)

        git.swith_to_branch(current_branch)
        switched = git.get_current_branch()
        self.assertEqual(switched, current_branch)

        git.merge(new_branch_name)

        git.delete_branch(new_branch_name)
        self.assertNotIn(new_branch_name, git.get_local_branches())

