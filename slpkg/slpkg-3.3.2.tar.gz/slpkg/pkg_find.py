#!/usr/bin/python
# -*- coding: utf-8 -*-

# pkg_find.py file is part of slpkg.

# Copyright 2014-2017 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from slpkg.messages import Msg
from slpkg.sbo.greps import SBoGrep
from slpkg.pkg.manager import PackageManager
from slpkg.__metadata__ import MetaData as _meta_


class FindFromRepos(object):
    """Find packages from all enabled repositories
    """
    def __init__(self):
        self.cache = ""
        self.p_cache = ""
        self.find_cache = ""
        self.count_pkg = 0
        self.count_repo = 0
        self.meta = _meta_
        self.cyan = self.meta.color["CYAN"]
        self.grey = self.meta.color["GREY"]
        self.endc = self.meta.color["ENDC"]

    def find(self, pkg, flag):
        """Start to find packages and print
        """
        print("\nPackages with name matching [ {0}{1}{2} ]\n".format(
            self.cyan, ", ".join(pkg), self.endc))
        Msg().template(78)
        print("| {0}  {1}{2}{3}".format("Repository", "Package", " " * 54,
                                        "Size"))
        Msg().template(78)
        for repo in _meta_.repositories:
            PACKAGES_TXT = PackageManager(pkg).list_lib(repo)
            packages, sizes = PackageManager(pkg).list_greps(repo, PACKAGES_TXT)
            for find, size in zip(packages, sizes):
                for p in pkg:
                    if "--case-ins" in flag:
                        self.p_cache = p.lower()
                        self.find_cache = find.lower()
                    else:
                        self.p_cache = p
                        self.find_cache = find
                    if self.p_cache in self.find_cache:
                        if self.cache != repo:
                            self.count_repo += 1
                        self.cache = repo
                        self.count_pkg += 1
                        ver = self.sbo_version(repo, find)
                        print("  {0}{1}{2}{3}{4} {5}{6:>11}".format(
                            self.cyan, repo, self.endc,
                            " " * (12 - len(repo)),
                            find + ver, " " * (53 - len(find + ver)),
                            size))
        print("\nFound summary")
        print("=" * 79)
        print("{0}Total found {1} packages in {2} repositories.{3}\n".format(
            self.grey, self.count_pkg, self.count_repo, self.endc))

    def sbo_version(self, repo, find):
        """
        Add version to SBo packages
        """
        ver = ""
        if repo == "sbo":
            ver = "-" + SBoGrep(find).version()
        return ver
