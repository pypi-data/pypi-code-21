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

import requests

from src.network.scout.findable import Findable


class GitHubScout(Findable):
    ENDPOINT_URL = "https://api.github.com/repos/"
    ENDPOINT_URL_SUFFIX = "/contents"

    def __init__(self):
        super(GitHubScout, self).__init__()

    def find(self, repo_owner, repo_name, file):
        url = GitHubScout.ENDPOINT_URL + repo_owner + "/" + repo_name + GitHubScout.ENDPOINT_URL_SUFFIX
        return self.find_in_request_contents(url, file)

    def find_in_request_contents(self, url, file):
        request = requests.get(url)
        if request.status_code == 200:
            result = request.json()
            return self._analyse_contents(result, file)
        return None

    def _analyse_contents(self, contents, file):
        for entry in contents:
            if entry["type"] == "file" and entry["name"] == file:
                return entry["download_url"]
            elif entry["type"] == "dir":
                return self.find_in_request_contents(entry["url"], file)

    def find_in_directory(self, repo_owner, repo_name, directory_path, file):
        url = GitHubScout.ENDPOINT_URL+repo_owner+"/"+repo_name+GitHubScout.ENDPOINT_URL_SUFFIX+"/"+directory_path
        return self.find_in_request_contents(url, file)