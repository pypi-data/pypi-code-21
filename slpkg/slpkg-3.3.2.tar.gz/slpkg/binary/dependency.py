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
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.binary.greps import Requires


class Dependencies(object):
    """Resolving binary dependencies
    """
    def __init__(self, repo, black):
        self.repo = repo
        self.black = black
        self.dep_results = []
        self.meta = _meta_

    def binary(self, name, flag):
        """Build all dependencies of a package
        """
        if self.meta.rsl_deps in ["on", "ON"] and "--resolve-off" not in flag:
            sys.setrecursionlimit(10000)
            dependencies = []
            requires = Requires(name, self.repo).get_deps()
            if requires:
                for req in requires:
                    status(0)
                    if req and req not in self.black:
                        dependencies.append(req)
                if dependencies:
                    self.dep_results.append(dependencies)
                    for dep in dependencies:
                        self.binary(dep, flag)
            return self.dep_results
        else:
            return []
