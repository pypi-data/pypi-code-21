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

from src.network.factory.scout_factory import ScoutFactory


class RepoScout:
    def __init__(self, repo_provider = "GitHub"):
        """
        Default constructor
        :param repo_provider: The name of the repository provider
        :type repo_provider: str
        """
        self._create_scout(repo_provider)

    def _create_scout(self, repo_provider):
        self.scout = ScoutFactory.create(repo_provider)

    def find(self, repo_owner, repo_name, file):
        return self.scout.find(repo_owner, repo_name, file)

    def find_in_directory(self, repo_owner, repo_name, directory_path, file):
        return self.scout.find_in_directory(repo_owner, repo_name, directory_path, file)