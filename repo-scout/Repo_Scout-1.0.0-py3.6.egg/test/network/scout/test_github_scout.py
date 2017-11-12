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

import unittest, json

from src.network.scout.github_scout import GitHubScout

try:
    from unittest.mock import patch
    from unittest.mock import mock
except ImportError:
    from mock import patch
    import mock


def mocked_request_get(*args, **kwargs):
    json_string = """[
          {
            "name": "debian",
            "path": "debian",
            "sha": "a2020dddb26679443870ca853ac6b7488dd4210d",
            "size": 0,
            "url": "http://api.example.com/fileOnly",
            "html_url": "https://github.com/Parcks/plugins/tree/master/debian",
            "git_url": "https://api.github.com/repos/Parcks/plugins/git/trees/a2020dddb26679443870ca853ac6b7488dd4210d",
            "download_url": null,
            "type": "dir",
            "_links": {
              "self": "https://api.github.com/repos/Parcks/plugins/contents/debian?ref=master",
              "git": "https://api.github.com/repos/Parcks/plugins/git/trees/a2020dddb26679443870ca853ac6b7488dd4210d",
              "html": "https://github.com/Parcks/plugins/tree/master/debian"
            }
          },
          {
            "name": "fedora",
            "path": "fedora",
            "sha": "d564d0bc3dd917926892c55e3706cc116d5b165e",
            "size": 0,
            "url": "http://api.example.com/fileOnly",
            "html_url": "https://github.com/Parcks/plugins/tree/master/fedora",
            "git_url": "https://api.github.com/repos/Parcks/plugins/git/trees/d564d0bc3dd917926892c55e3706cc116d5b165e",
            "download_url": null,
            "type": "dir",
            "_links": {
              "self": "https://api.github.com/repos/Parcks/plugins/contents/fedora?ref=master",
              "git": "https://api.github.com/repos/Parcks/plugins/git/trees/d564d0bc3dd917926892c55e3706cc116d5b165e",
              "html": "https://github.com/Parcks/plugins/tree/master/fedora"
            }
          },
          {
            "name": "testPlugin.ppl",
            "path": "testPlugin.ppl",
            "sha": "a7ac9a74c61a993fe9c8129689fb5594eff74621",
            "size": 213,
            "url": "http://api.example.com/fileOnly",
            "html_url": "https://github.com/Parcks/plugins/blob/master/testPlugin.ppl",
            "git_url": "https://api.github.com/repos/Parcks/plugins/git/blobs/a7ac9a74c61a993fe9c8129689fb5594eff74621",
            "download_url": "https://raw.githubusercontent.com/Parcks/plugins/master/testPlugin.ppl",
            "type": "file",
            "_links": {
              "self": "https://api.github.com/repos/Parcks/plugins/contents/testPlugin.ppl?ref=master",
              "git": "https://api.github.com/repos/Parcks/plugins/git/blobs/a7ac9a74c61a993fe9c8129689fb5594eff74621",
              "html": "https://github.com/Parcks/plugins/blob/master/testPlugin.ppl"
            }
          }
        ]"""
    json_only_file = """[
          {
            "name": "testPlugin.ppl",
            "path": "testPlugin.ppl",
            "sha": "a7ac9a74c61a993fe9c8129689fb5594eff74621",
            "size": 213,
            "url": "http://api.example.com/fileOnly",
            "html_url": "https://github.com/Parcks/plugins/blob/master/testPlugin.ppl",
            "git_url": "https://api.github.com/repos/Parcks/plugins/git/blobs/a7ac9a74c61a993fe9c8129689fb5594eff74621",
            "download_url": "https://raw.githubusercontent.com/Parcks/plugins/master/testPlugin.ppl",
            "type": "file",
            "_links": {
              "self": "https://api.github.com/repos/Parcks/plugins/contents/testPlugin.ppl?ref=master",
              "git": "https://api.github.com/repos/Parcks/plugins/git/blobs/a7ac9a74c61a993fe9c8129689fb5594eff74621",
              "html": "https://github.com/Parcks/plugins/blob/master/testPlugin.ppl"
            }
          }
        ]"""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://api.example.com':
        return MockResponse(json.loads(json_string), 200)
    elif args[0] == 'http://api.example.com/fileOnly':
        return MockResponse(json.loads(json_only_file), 200)

    return MockResponse(None, 404)


class TestGitHubScout(unittest.TestCase):
    def setUp(self):
        self.scout = GitHubScout()

    @mock.patch('requests.get', side_effect=mocked_request_get)
    @patch.object(GitHubScout, "find_in_request_contents")
    def test_find_calls_find_in_request_contents(self, mock, patched_requests):
        self.scout.find("owner", "name", "file")
        self.assertTrue(mock.called)

    @mock.patch('requests.get', side_effect=mocked_request_get)
    @patch.object(GitHubScout, "_analyse_contents")
    def test_find_in_requests_contents_calls__analyse_contents(self, mock, patched_requests):
        self.scout.find_in_request_contents("http://api.example.com", "dummy.file")
        self.assertTrue(mock.called)

    @mock.patch('requests.get', side_effect=mocked_request_get)
    @patch.object(GitHubScout, "_analyse_contents")
    def test_find_in_requests_contents_does_not_call__analyse_contents_on_bad_url(self, mock, patched_requests):
        self.scout.find_in_request_contents("http://bad.url", "dummy.file")
        self.assertFalse(mock.called)

    @mock.patch('requests.get', side_effect=mocked_request_get)
    @patch.object(GitHubScout, "find_in_request_contents")
    def test_find_in_directory_calls_find_in_request_contents(self, mock, patched_requests):
        self.scout.find_in_directory("owner", "name", "dir", "file")
        self.assertTrue(mock.called)

    @mock.patch('requests.get', side_effect=mocked_request_get)
    def test_find_in_request_contents_returns_download_url_if_found(self, patched_requests):
        result = self.scout.find_in_request_contents("http://api.example.com", "testPlugin.ppl")
        self.assertEqual("https://raw.githubusercontent.com/Parcks/plugins/master/testPlugin.ppl", result)

    @mock.patch('requests.get', side_effect=mocked_request_get)
    def test_find_in_request_contents_returns_None_if_not_found(self, patched_requests):
        result = self.scout.find_in_request_contents("http://api.example.com", "notFound")
        self.assertIsNone(result)
