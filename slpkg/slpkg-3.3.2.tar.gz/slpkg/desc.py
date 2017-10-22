#!/usr/bin/python
# -*- coding: utf-8 -*-

# desc.py file is part of slpkg.

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
from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.sbo.greps import SBoGrep


class PkgDesc(object):
    """Print package description from the repository
    """
    def __init__(self, name, repo, paint):
        self.name = name
        self.repo = repo
        self.paint = paint
        self.meta = _meta_
        self.msg = Msg()
        self.COLOR = ""
        self.lib = ""
        color_text = {
            "red": self.meta.color["RED"],
            "green": self.meta.color["GREEN"],
            "yellow": self.meta.color["YELLOW"],
            "cyan": self.meta.color["CYAN"],
            "grey": self.meta.color["GREY"],
            "": ""
        }
        self.COLOR = color_text[self.paint]
        if self.repo in self.meta.repositories and self.repo != "sbo":
            self.lib = self.meta.lib_path + "{0}_repo/PACKAGES.TXT".format(
                self.repo)

    def view(self):
        """Print package description by repository
        """
        print("")   # new line at start
        description, count = "", 0
        if self.repo == "sbo":
            description = SBoGrep(self.name).description()
        else:
            PACKAGES_TXT = Utils().read_file(self.lib)
            for line in PACKAGES_TXT.splitlines():
                if line.startswith(self.name + ":"):
                    description += line[len(self.name) + 2:] + "\n"
                    count += 1
                    if count == 11:
                        break
        if description:
            print("{0}{1}{2}".format(self.COLOR, description,
                                     self.meta.color["ENDC"]))
        else:
            self.msg.pkg_not_found("", self.name, "No matching", "\n")
            raise SystemExit(1)
        if description and self.repo == "sbo":
            print("")
