#!/usr/bin/python
# -*- coding: utf-8 -*-

# search.py file is part of slpkg.

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


from slpkg.utils import Utils
from slpkg.toolbar import status
from slpkg.blacklist import BlackList
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_


def search_pkg(name, repo):
    """Search if package exists in PACKAGES.TXT file
    and return the name.
    """
    PACKAGES_TXT = Utils().read_file(_meta_.lib_path + "{0}_repo/"
                                     "PACKAGES.TXT".format(repo))
    names = Utils().package_name(PACKAGES_TXT)
    blacklist = BlackList().packages(pkgs=names, repo=repo)
    for line in PACKAGES_TXT.splitlines():
        status(0)
        if line.startswith("PACKAGE NAME:  ") and len(line) > 16:
            pkg_name = split_package(line[15:])[0].strip()
            if name == pkg_name and name not in blacklist:
                return pkg_name
