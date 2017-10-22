#!/usr/bin/python
# -*- coding: utf-8 -*-

# repoenable.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.dialog_box import DialogUtil
from slpkg.__metadata__ import MetaData as _meta_


class RepoEnable(object):
    """Read repositories.conf file and update with new enabled or
    disabled repositories
    """
    def __init__(self):
        self.meta = _meta_
        self.msg = Msg()
        self.tag = "[REPOSITORIES]"
        self.tag_line = False
        self.repositories_conf = "repositories.conf"
        self.conf = Utils().read_file(
            self.meta.conf_path + self.repositories_conf)
        self.enabled = []
        self.disabled = []
        self.selected = []

    def choose(self):
        """Choose repositories
        """
        keys = """
Choose repositories at the right side for enable or to the
left side for disable.

Keys: SPACE   select or deselect the highlighted repositories,
             move it between the left and right lists
          ^       move the focus to the left list
          $       move the focus to the right list
        TAB     move focus
      ENTER   press the focused button

      Disabled  <-------- REPOSITORIES ------->  Enabled"""
        self.read_enabled()
        self.read_disabled()
        text, title, backtitle, status = keys, " Repositories ", "", False
        self.selected = DialogUtil(self.disabled, text, title, backtitle,
                                   status).buildlist(self.enabled)
        if self.selected is not None:
            self.update_repos()
        else:
            self.selected = self.enabled
        self.clear_screen()
        self.reference()

    def read_enabled(self):
        """Read enable repositories
        """
        for line in self.conf.splitlines():
            line = line.lstrip()
            if self.tag in line:
                self.tag_line = True
            if (line and self.tag_line and not line.startswith("#") and
                    self.tag not in line):
                self.enabled.append(line)
        self.tag_line = False

    def read_disabled(self):
        """Read disable repositories
        """
        for line in self.conf.splitlines():
            line = line.lstrip()
            if self.tag in line:
                self.tag_line = True
            if self.tag_line and line.startswith("#"):
                line = "".join(line.split("#")).strip()
                self.disabled.append(line)
        self.tag_line = False

    def update_repos(self):
        """Update repositories.conf file with enabled or disabled
        repositories
        """
        with open("{0}{1}".format(self.meta.conf_path,
                                  self.repositories_conf), "w") as new_conf:
            for line in self.conf.splitlines():
                line = line.lstrip()
                if self.tag in line:
                    self.tag_line = True
                if self.tag_line and line.startswith("#"):
                    repo = "".join(line.split("#")).strip()
                    if repo in self.selected:
                        new_conf.write(line.replace(line, repo + "\n"))
                        continue
                if (self.tag_line and not line.startswith("#") and
                        line != self.tag):
                    repo = line.strip()
                    if repo not in self.selected:
                        new_conf.write(line.replace(line, "# " + line + "\n"))
                        continue
                new_conf.write(line + "\n")

    def clear_screen(self):
        """Clear screen
        """
        os.system("clear")

    def reference(self):
        """Reference enable repositories
        """
        total_enabled = ", ".join(self.selected)
        if len(total_enabled) < 1:
            total_enabled = ("{0}Are you crazy? This is a package "
                             "manager for packages :p{1}".format(
                                 self.meta.color["RED"],
                                 self.meta.color["ENDC"]))
        self.msg.template(78)
        print("| Enabled repositories:")
        self.msg.template(78)
        print("| {0}".format(total_enabled))
        self.msg.template(78)
        print("{0}Total {1}/{2} repositories enabled.{3}\n".format(
            self.meta.color["GREY"], len(self.selected),
            len(self.enabled + self.disabled), self.meta.color["ENDC"]))
