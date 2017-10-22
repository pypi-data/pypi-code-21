#!/usr/bin/python
# -*- coding: utf-8 -*-

# health.py file is part of slpkg.

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


import os

from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package


class PackageHealth(object):
    """Health check installed packages
    """
    def __init__(self, mode):
        self.mode = mode
        self.meta = _meta_
        self.msg = Msg()
        self.pkg_path = _meta_.pkg_path
        self.installed = []
        self.cn = 0

    def packages(self):
        """Get all installed packages from /var/log/packages/ path
        """
        self.installed = find_package("", self.pkg_path)

    def check(self, line, pkg):
        line = line.replace("\n", "")
        try:
            if (not line.endswith("/") and
                    not line.endswith(".new") and
                    not line.startswith("dev/") and
                    not line.startswith("install/") and
                    "/incoming/" not in line):
                if not os.path.isfile(r"/" + line):
                    self.cn += 1
                    print("Not installed: {0}/{1}{2} --> {3}".format(
                        self.meta.color["RED"], line, self.meta.color["ENDC"],
                        pkg))
                elif not self.mode:
                    print(line)
        except IOError:
            print("")
            raise SystemExit()

    def test(self):
        """Get started test each package and read file list
        """
        self.packages()
        self.cf = 0
        for pkg in self.installed:
            if os.path.isfile(self.meta.pkg_path + pkg):
                self.lf = 0
                with open(self.pkg_path + pkg, "r") as fopen:
                    for line in fopen:
                        if "\0" in line:
                            print("Null: {0}").format(line)
                            break
                        self.cf += 1     # count all files
                        self.lf += 1     # count each package files
                        if self.lf > 19:
                            self.check(line, pkg)
        self.results()

    def results(self):
        """Print results
        """
        print("")
        per = int(round((float(self.cf) / (self.cf + self.cn)) * 100))
        if per > 90:
            color = self.meta.color["GREEN"]
        elif per < 90 and per > 60:
            color = self.meta.color["YELLOW"]
        elif per < 60:
            color = self.meta.color["RED"]
        health = "{0}{1}%{2}".format(color, str(per), self.meta.color["ENDC"])
        self.msg.template(78)
        print("| {0}{1}{2}{3}{4}".format(
            "Total files", " " * 7, "Not installed", " " * 40, "Health"))
        self.msg.template(78)
        print("| {0}{1}{2}{3}{4:>4}".format(
            self.cf, " " * (18-len(str(self.cf))),
            self.cn, " " * (55-len(str(self.cn))),
            health))
        self.msg.template(78)
