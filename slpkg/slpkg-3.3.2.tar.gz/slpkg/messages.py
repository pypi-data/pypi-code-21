#!/usr/bin/python
# -*- coding: utf-8 -*-

# messages.py file is part of slpkg.

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
import itertools

from slpkg.__metadata__ import MetaData as _meta_


class Msg(object):
    """Messages control
    """
    def __init__(self):
        self.meta = _meta_

    def pkg_not_found(self, bol, pkg, message, eol):
        """Print message when package not found
        """
        print("{0}No such package {1}: {2}{3}".format(bol, pkg, message, eol))

    def pkg_found(self, prgnam):
        """Print message when package found
        """
        print("| Package {0} is already installed".format(prgnam))

    def pkg_installed(self, pkg):
        """Print message when package installed
        """
        print("| Package {0} installed".format(pkg))

    def build_FAILED(self, prgnam):
        """Print error message if build failed
        """
        self.template(78)
        print("| Some error on the package {0} [ {1}FAILED{2} ]".format(
            prgnam, self.meta.color["RED"], self.meta.color["ENDC"]))
        self.template(78)
        print("| See log file in '{0}/var/log/slpkg/sbo/build_logs{1}' "
              "directory or read README".format(self.meta.color["CYAN"],
                                                self.meta.color["ENDC"]))
        self.template(78)
        print("")   # new line at end

    def template(self, max_len):
        """Print template
        """
        print("+" + "=" * max_len)

    def checking(self):
        """Message checking
        """
        sys.stdout.write("{0}Checking...{1}  ".format(self.meta.color["GREY"],
                                                      self.meta.color["ENDC"]))
        sys.stdout.flush()

    def reading(self):
        """Message reading
        """
        sys.stdout.write("{0}Reading package lists...{1}  ".format(
            self.meta.color["GREY"], self.meta.color["ENDC"]))
        sys.stdout.flush()

    def resolving(self):
        """Message resolving
        """
        sys.stdout.write("{0}Resolving dependencies...{1}  ".format(
            self.meta.color["GREY"], self.meta.color["ENDC"]))
        sys.stdout.flush()

    def done(self):
        """Message done
        """
        sys.stdout.write("\b{0}Done{1}\n".format(self.meta.color["GREY"],
                                                 self.meta.color["ENDC"]))

    def pkg(self, count):
        """Print singular plural
        """
        message = "package"
        if count > 1:
            message = message + "s"
        return message

    def not_found(self, if_upgrade):
        """Message not found packages
        """
        if if_upgrade:
            print("\nNot found packages for upgrade\n")
        else:
            print("\nNot found packages for installation\n")

    def upg_inst(self, if_upgrade):
        """Message installing or upgrading
        """
        if not if_upgrade:
            print("Installing:")
        else:
            print("Upgrading:")

    def answer(self):
        """Message answer
        """
        if self.meta.default_answer in ["y", "Y"]:
            answer = self.meta.default_answer
        else:
            try:
                answer = raw_input("Would you like to continue [y/N]? ")
            except EOFError:
                print("")
                raise SystemExit()
        return answer

    def security_pkg(self, pkg):
        """Warning message for some special reasons
        """
        print("")
        self.template(78)
        print("| {0}{1}*** WARNING ***{2}").format(
            " " * 27, self.meta.color["RED"], self.meta.color["ENDC"])
        self.template(78)
        print("| Before proceed with package '{0}' will you must read the\n"
              "| README file. You can use command 'slpkg -n {1}'").format(
                  pkg, pkg)
        self.template(78)
        print("")

    def reference(self, install, upgrade):
        """Reference list with packages installed
        and upgraded
        """
        self.template(78)
        print("| Total {0} {1} installed and {2} {3} upgraded".format(
            len(install), self.pkg(len(install)),
            len(upgrade), self.pkg(len(upgrade))))
        self.template(78)
        for installed, upgraded in itertools.izip_longest(install, upgrade):
            if upgraded:
                print("| Package {0} upgraded successfully".format(upgraded))
            if installed:
                print("| Package {0} installed successfully".format(installed))
        self.template(78)
        print("")

    def matching(self, packages):
        """Message for matching packages
        """
        print("\nNot found package with the name [ {0}{1}{2} ]. "
              "Matching packages:\nNOTE: Not dependenc"
              "ies are resolved\n".format(self.meta.color["CYAN"],
                                          "".join(packages),
                                          self.meta.color["ENDC"]))
