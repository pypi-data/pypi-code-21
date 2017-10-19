"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from hqlib.metric_source import VersionControlSystem


class VersionControlSystemTests(unittest.TestCase):
    """ Unit tests for the version control system class. """

    def test_ignore_branch_not_in_includes(self):
        """ Test that branches not in the list of branches to include are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foo', list_of_branches_to_include=['bar']))

    def test_ignore_branch_in_ignore_list(self):
        """ Test that branches in the list of branches to ignore are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foo', list_of_branches_to_ignore=['foo']))

    def test_ignore_branch_that_matches(self):
        """ Test that branches that match the regular expression of branches to ignore are ignored. """
        self.assertTrue(VersionControlSystem._ignore_branch('foobar', re_of_branches_to_ignore='foo.*'))

    def test_do_not_ignore_branches_by_default(self):
        """ Test that branches are not ignored by default. """
        self.assertFalse(VersionControlSystem._ignore_branch('foo'))
