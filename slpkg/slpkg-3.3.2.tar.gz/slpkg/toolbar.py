#!/usr/bin/python
# -*- coding: utf-8 -*-

# toolbar.py file is part of slpkg.

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
import time

from slpkg.__metadata__ import MetaData as _meta_


def status(sec):
    """Toolbar progressive status
    """
    if _meta_.prg_bar in ["on", "ON"]:
        syms = ["|", "/", "-", "\\"]
        for sym in syms:
            sys.stdout.write("\b{0}{1}{2}".format(_meta_.color["GREY"], sym,
                                                  _meta_.color["ENDC"]))
            sys.stdout.flush()
            time.sleep(float(sec))
