# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = "2.1.0rc3"
__version_info__ = (2, 1, 0, -99)

# If it's a git checkout try to add the commit
if "dev" in __version__:
    try:
        import os
        import subprocess
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".git")):
            r = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip("\n")
            __version__ += "-" + r
    except Exception as e:
        print(e)
