"""
Repo Scout
Copyright (C) 2017  JValck - Setarit

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Setarit - parcks[at]setarit.com
"""
from __future__ import absolute_import
import unittest

from src.network.factory.scout_factory import ScoutFactory
from src.network.scout.github_scout import GitHubScout
from src.service.repo_scout import RepoScout

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

class TestRepoScout(unittest.TestCase):
    @patch.object(RepoScout, '_create_scout')
    def test_constructor_calls_create_scout(self, mock):
        facade = RepoScout()
        self.assertTrue(mock.called)

    @patch.object(ScoutFactory, 'create')
    def test_create_scout_calls_create_on_ScoutFactory(self, factory):
        facade = RepoScout()
        facade._create_scout("GitHub")
        self.assertEqual(2, factory.call_count)

    @patch.object(GitHubScout, "find")
    def test_find_calls_find_on_scout(self, mocked_find):
        facade = RepoScout()
        facade.find("owner", "name", "file")
        self.assertTrue(mocked_find.called)

    @patch.object(GitHubScout, "find_in_directory")
    def test_find_in_dir_calls_find_in_dir_on_scout(self, mocked_find_in_dir):
        facade = RepoScout()
        facade.find_in_directory("owner", "name", "dir", "file")
        self.assertTrue(mocked_find_in_dir.called)