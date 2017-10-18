"""Tests for our `pwdc info` subcommand."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

gitlab_test_repo="sallamand/test"


class TestGetProject(TestCase):
    def test_returns_multiple_lines(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_project'], stdout=PIPE).communicate()[0]
        lines = output.split('\n')
        self.assertTrue(len(lines) != 1)

    def test_returns_get_project(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_project'], stdout=PIPE).communicate()[0]
        self.assertTrue('path-with-namespace: '+gitlab_test_repo in output)
