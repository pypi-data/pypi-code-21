#!/usr/bin/python
# -*- coding: utf-8 -*-

# utils.py file is part of slpkg.

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

from slpkg.splitting import split_package


class Utils(object):
    """Class with usefull utilities
    """
    def case_sensitive(self, lst):
        """Create dictionary from list with key in lower case
        and value with default
        """
        dictionary = {}
        for pkg in lst:
            dictionary[pkg.lower()] = pkg
        return dictionary

    def dimensional_list(self, lists):
        """Create one dimensional list
        """
        one_list = []
        for lst in lists:
            one_list += lst
        return one_list

    def remove_dbs(self, double):
        """Remove double item from list
        """
        one = []
        for dup in double:
            if dup not in one:
                one.append(dup)
        return one

    def read_file(self, registry):
        """Returns reading file
        """
        with open(registry, "r") as file_txt:
            read_file = file_txt.read()
            file_txt.close()
            return read_file

    def package_name(self, PACKAGES_TXT):
        """Returns list with all the names of packages repository
        """
        packages = []
        for line in PACKAGES_TXT.splitlines():
            if line.startswith("PACKAGE NAME:"):
                packages.append(split_package(line[14:].strip())[0])
        return packages

    def check_downloaded(self, path, maybe_downloaded):
        """Check if files downloaded and return downloaded
        packages
        """
        downloaded = []
        for pkg in maybe_downloaded:
            if os.path.isfile(path + pkg):
                downloaded.append(pkg)
        return downloaded

    def read_config(self, config):
        """Read config file and returns first uncomment line
        and stop. Used for Slackware mirrors
        """
        for line in config.splitlines():
            line = line.lstrip()
            if line and not line.startswith("#"):
                return line

    def debug(self, test):
        """Function used for print some stuff for debugging
        """
        print(test)
