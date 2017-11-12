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
from abc import ABCMeta, abstractmethod


class Findable(object):
    def __init__(self):
        __metaclass__ = ABCMeta

    @abstractmethod
    def find(self, repo_owner, repo_name, file):
        """
        Find a file in a repository
        :param repo_owner: The name of the owner of the repository
        :param repo_name: The name of the repository
        :param file: The file to search
        :type repo_owner: str
        :type repo_name: str
        :type file: str
        :return: The url where the file contents can be downloaded
        :rtype: str
        """
        pass

    @abstractmethod
    def find_in_request_contents(self, url, file):
        """
        Searches the file in the contents of the api url
        :param url: The url whose contents should be found
        :param file: The file to find in the contents
        :return: An url to the contents of the file
        """
        pass

    @abstractmethod
    def find_in_directory(self, repo_owner, repo_name, directory_path, file):
        """
        Searches the file in a directory in a repository
        :param repo_owner: The name of the owner of the repository
        :param repo_name: The name of the repository
        :param directory_path: The directory path to search in
        :param file: The file to search
        :type repo_name: str
        :type repo_owner: str
        :type directory_path: str
        :type file: str
        :return: The url where the file contents can be downloaded
        :rtype: str
        """
        pass
