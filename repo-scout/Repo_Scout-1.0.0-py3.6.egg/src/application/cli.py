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
import argparse

from src.service.repo_scout import RepoScout


class Cli():
	def _create_parser(self):
	    parser = argparse.ArgumentParser(description="Find a file in a VCS", prog="RepoScout")
	    parser.add_argument("-p, --provider", dest="provider", help="The name of the VCS provider (Default: GitHub)",
	                        choices=["GitHub"], default="GitHub", metavar='PROV')
	    parser.add_argument("-o, --owner", dest="repo_owner", help="The name of the owner of the repository",
	                        required=True, metavar="OWNER")
	    parser.add_argument("-n, --name", dest="repo_name", help="The name of the repository to search in",
	                        required=True, metavar="NAME")
	    parser.add_argument("-m, --method", dest="method",
	                        help="Indicates if the file should be searched in a directory or just retrieve the first"
	                             " occurrence (Default: First)",
	                        choices=["InDirectory", "First"], default="First", metavar="METHOD")
	    parser.add_argument("-f, --file", dest="file", help="The name of the file to find",
	                        required=True, metavar="FILE")
	    parser.add_argument("-d, --directory", dest="directory_path", metavar="DIR",
	                        help="The path in the repository where the file should be searched")
	    return parser


	def run(self, args):
	    parser = self._create_parser()
	    arguments = parser.parse_args()
	    if arguments.method == "InDirectory" and arguments.directory_path is None:
	        parser.error("Directory path is required when searching in a directory")
	    scout = RepoScout(arguments.provider)
	    if arguments.method == "InDirectory":
	        result = scout.find_in_directory(arguments.repo_owner, arguments.repo_name, arguments.directory_path,
	                                         arguments.file)
	    else:
	        result = scout.find(arguments.repo_owner, arguments.repo_name, arguments.file)
	    print(result)
		