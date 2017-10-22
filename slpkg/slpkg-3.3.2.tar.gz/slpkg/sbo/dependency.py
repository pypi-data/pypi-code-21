#!/usr/bin/python
# -*- coding: utf-8 -*-

# dependency.py file is part of slpkg.

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


import sys

from slpkg.toolbar import status
from slpkg.blacklist import BlackList
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.sbo.greps import SBoGrep


class Requires(object):
    """Resolving SBo dependencies
    """
    def __init__(self, flag):
        self.flag = flag
        self.meta = _meta_
        self.SLACKBUILDS_TXT = SBoGrep(name="").names()
        self.blacklist = BlackList().packages(pkgs=self.SLACKBUILDS_TXT,
                                              repo="sbo")
        self.dep_results = []

    def sbo(self, name):
        """Build all dependencies of a package
        """
        if (self.meta.rsl_deps in ["on", "ON"] and
                "--resolve-off" not in self.flag):
            sys.setrecursionlimit(10000)
            dependencies = []
            requires = SBoGrep(name).requires()
            if requires:
                for req in requires:
                    status(0.03)
                    # toolbar_width = status(index, toolbar_width, 1)
                    # avoid to add %README% as dependency and
                    # if require in blacklist
                    if "%README%" not in req and req not in self.blacklist:
                        dependencies.append(req)
                if dependencies:
                    self.dep_results.append(dependencies)
                    for dep in dependencies:
                        self.sbo(dep)
            return self.dep_results
        else:
            return []
