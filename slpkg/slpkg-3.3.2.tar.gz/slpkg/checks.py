#!/usr/bin/python
# -*- coding: utf-8 -*-

# checks.py file is part of slpkg.

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
from slpkg.arguments import usage
from slpkg.init import Initialization
from slpkg.__metadata__ import MetaData as _meta_


class Updates(object):
    """Checking for news in ChangeLog.txt
    """
    def __init__(self, repo):
        self.repo = repo
        self.meta = _meta_
        self.msg = Msg()
        self.check = 2
        self.st = ""
        self.count_repo = 0
        self.count_news = 0
        self._init = Initialization(True)
        self.all_repos = {
            "slack": self._init.slack,
            "sbo": self._init.sbo,
            "rlw": self._init.rlw,
            "alien": self._init.alien,
            "slacky": self._init.slacky,
            "conrad": self._init.conrad,
            "slonly": self._init.slonly,
            "ktown": self._init.ktown,
            "multi": self._init.multi,
            "slacke": self._init.slacke,
            "salix": self._init.salix,
            "slackl": self._init.slackl,
            "rested": self._init.rested,
            "msb": self._init.msb,
            "csb": self._init.csb,
            "connos": self._init.msb,
            "mles": self._init.mles
        }

    def status_bar(self):
        """Top view bar status
        """
        print("")
        self.msg.template(78)
        print("| Repository         Status")
        self.msg.template(78)

    def run(self):
        """Run and check if new in ChangeLog.txt
        """
        if (self.repo in self.meta.default_repositories and
                self.repo in self.meta.repositories):
            try:
                self.check = self.all_repos[self.repo]()
            except OSError:
                usage(self.repo)
                raise SystemExit()
        elif self.repo in self.meta.repositories:
            self.check = self._init.custom(self.repo)
        else:
            usage(self.repo)
            raise SystemExit()
        self.status_bar()
        self.status()
        self.print_status(self.repo)
        self.summary()

    def ALL(self):
        """Check ALL enabled repositories ChangeLogs
        """
        self.status_bar()
        for repo in self.meta.repositories:
            if repo in self.meta.default_repositories:
                try:
                    self.check = self.all_repos[repo]()
                except OSError:
                    usage(self.repo)
                    raise SystemExit()
            elif repo in self.meta.repositories:
                self.check = self._init.custom(repo)
            self.status()
            self.print_status(repo)
        self.summary()

    def status(self):
        """Set messages
        """
        self.count_repo += 1
        if self.check == 1:
            self.count_news += 1
            self.st = "{0}News in ChangeLog.txt{1}".format(
                self.meta.color["GREEN"], self.meta.color["ENDC"])
        elif self.check == 0:
            self.st = "No changes in ChangeLog.txt"

    def print_status(self, repo):
        """Print status
        """
        print("  {0}{1}{2}".format(repo, " " * (19 - len(repo)), self.st))

    def summary(self):
        """Print summary
        """
        print("\nSummary")
        print("=" * 79)
        cmd = "All repositories are updated."
        if self.count_repo == 1:
            cmd = "Repository is updated."
        if self.count_news > 0:
            cmd = "Run the command 'slpkg update'."
        print("{0}From {1} repositories need {2} updating. {3}{4}\n".format(
            self.meta.color["GREY"], self.count_repo, self.count_news, cmd,
            self.meta.color["ENDC"]))
