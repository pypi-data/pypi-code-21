#!/usr/bin/python
# -*- coding: utf-8 -*-

# check.py file is part of slpkg.

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


from distutils.version import LooseVersion

from slpkg.messages import Msg
from slpkg.toolbar import status
from slpkg.splitting import split_package
from slpkg.upgrade_checklist import choose_upg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package

from slpkg.binary.greps import repo_data
from slpkg.binary.repo_init import RepoInit


def pkg_upgrade(repo, skip, flag):
    """Checking packages for upgrade
    """
    Msg().checking()
    PACKAGES_TXT = RepoInit(repo).fetch()[0]
    pkgs_for_upgrade = []
    # name = data[0]
    # location = data[1]
    # size = data[2]
    # unsize = data[3]
    data = repo_data(PACKAGES_TXT, repo, flag="")
    for pkg in installed():
        status(0.0005)
        inst_pkg = split_package(pkg)
        for name in data[0]:
            if name:    # this tips because some pkg_name is empty
                repo_pkg = split_package(name[:-4])
            if (repo_pkg[0] == inst_pkg[0] and
                LooseVersion(repo_pkg[1]) > LooseVersion(inst_pkg[1]) and
                repo_pkg[3] >= inst_pkg[3] and
                    inst_pkg[0] not in skip and
                    repo_pkg[1] != "blacklist"):
                pkgs_for_upgrade.append(repo_pkg[0])
    Msg().done()
    if "--checklist" in flag:
        pkgs_for_upgrade = choose_upg(pkgs_for_upgrade)
    return pkgs_for_upgrade


def installed():
    """Return all installed packages
    """
    return find_package("", _meta_.pkg_path)
