#!/usr/bin/python
# -*- coding: utf-8 -*-

# repoinfo.py file is part of slpkg.

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

from slpkg.sizes import units
from slpkg.utils import Utils
from slpkg.repositories import Repo
from slpkg.repolist import RepoList
from slpkg.__metadata__ import MetaData as _meta_


class RepoInfo(object):
    """Repository information
    """
    def __init__(self):
        self.form = {
            "Last updated:": "",
            "Number of packages:": "",
            "Repo id:": "",
            "Default:": "",
            "Repo url:": "",
            "Status:": "",
            "Total compressed packages:": "",
            "Total uncompressed packages:": ""
        }
        self.meta = _meta_
        self.all_repos = Repo().default_repository()
        self.all_repos["slack"] = Repo().slack()
        self.all_repos.update(Repo().custom_repository())
        del RepoList().all_repos

    def view(self, repo):
        """
        View repository information
        """
        status = "{0}disabled{1}".format(self.meta.color["RED"],
                                         self.meta.color["ENDC"])
        self.form["Status:"] = status
        self.form["Default:"] = "no"
        if repo in self.meta.default_repositories:
            self.form["Default:"] = "yes"
        if (repo in self.meta.repositories and
                os.path.isfile(self.meta.lib_path + "{0}_repo/PACKAGES."
                               "TXT".format(repo))):
            status = "{0}enabled{1}".format(self.meta.color["GREEN"],
                                            self.meta.color["ENDC"])
            if repo != "sbo":
                data = self.repository_data(repo)
                size = units(data[1], data[2])
                self.form["Repo id:"] = repo
                self.form["Repo url:"] = self.all_repos[repo]
                self.form["Total compressed packages:"] = "{0} {1}".format(
                    str(size[1][0]), str(size[0][0]))
                self.form["Total uncompressed packages:"] = "{0} {1}".format(
                    str(size[1][1]), str(size[0][1]))
                self.form["Number of packages:"] = data[0]
                self.form["Status:"] = status
                self.form["Last updated:"] = data[3]
        elif (repo == "sbo" and os.path.isfile(self.meta.lib_path + "{0}_repo/"
                                               "SLACKBUILDS.TXT".format(repo))):
            status = "{0}enabled{1}".format(self.meta.color["GREEN"],
                                            self.meta.color["ENDC"])
            sum_sbo_pkgs = 0
            for line in (Utils().read_file(
                    self.meta.lib_path + "sbo_repo/SLACKBUILDS."
                    "TXT").splitlines()):
                if line.startswith("SLACKBUILD NAME: "):
                    sum_sbo_pkgs += 1
            changelog_txt = Utils().read_file(
                self.meta.log_path + "sbo/ChangeLog.txt")
            last_upd = changelog_txt.split("\n", 1)[0]
            self.form["Repo id:"] = repo
            self.form["Repo url:"] = self.all_repos[repo]
            self.form["Total compressed packages:"] = ""
            self.form["Total uncompressed packages:"] = ""
            self.form["Number of packages:"] = sum_sbo_pkgs
            self.form["Status:"] = status
            self.form["Last updated:"] = last_upd
        print("")
        for key, value in sorted(self.form.iteritems()):
            print self.meta.color["GREY"] + key + self.meta.color["ENDC"], value
        print("")
        raise SystemExit()

    def repository_data(self, repo):
        """
        Grap data packages
        """
        sum_pkgs, size, unsize, last_upd = 0, [], [], ""
        for line in (Utils().read_file(
                self.meta.lib_path + repo + "_repo/PACKAGES.TXT").splitlines()):
            if line.startswith("PACKAGES.TXT;"):
                last_upd = line[14:].strip()
            if line.startswith("PACKAGE NAME:"):
                sum_pkgs += 1
            if line.startswith("PACKAGE SIZE (compressed):  "):
                size.append(line[28:-2].strip())
            if line.startswith("PACKAGE SIZE (uncompressed):  "):
                unsize.append(line[30:-2].strip())
        if repo in ["salix", "slackl"]:
            log = Utils().read_file(
                self.meta.log_path + "{0}/ChangeLog.txt".format(repo))
            last_upd = log.split("\n", 1)[0]
        return [sum_pkgs, size, unsize, last_upd]
