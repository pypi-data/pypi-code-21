# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

""" Module for platform-specific constants and implementations, as well as
    compatibility layers to make use of the 'best' implementation available
    on a platform.
"""
import os
import sys
import platform
from functools import lru_cache

# do not import any tako-modules here to avoid circular dependencies


#
# OS
#

ON_DARWIN = platform.system() == 'Darwin'
""" ``True`` if executed on a Darwin platform, else ``False``. """
ON_LINUX = platform.system() == 'Linux'
""" ``True`` if executed on a Linux platform, else ``False``. """
ON_CYGWIN = sys.platform == 'cygwin'
""" ``True`` if executed on a Cygwin Windows platform, else ``False``. """
ON_MSYS = sys.platform == 'msys'
""" ``True`` if executed on an MSYS Windows platform, else ``False``. """


#
# Python & packages
#

PYTHON_VERSION_INFO = sys.version_info[:3]
""" Version of Python interpreter as three-value tuple. """

#
# Encoding
#

DEFAULT_ENCODING = sys.getdefaultencoding()
""" Default string encoding. """


if PYTHON_VERSION_INFO < (3, 5, 0):
    from pathlib import Path

    class DirEntry:
        def __init__(self, directory, name):
            self.__path__ = Path(directory) / name
            self.name = name
            self.path = str(self.__path__)
            self.is_symlink = self.__path__.is_symlink

        def inode(self):
            return os.stat(self.path, follow_symlinks=False).st_ino

        def is_dir(self, *, follow_symlinks=True):
            if follow_symlinks:
                return self.__path__.is_dir()
            else:
                return not self.__path__.is_symlink() \
                       and self.__path__.is_dir()

        def is_file(self, *, follow_symlinks=True):
            if follow_symlinks:
                return self.__path__.is_file()
            else:
                return not self.__path__.is_symlink() \
                       and self.__path__.is_file()

        def stat(self, *, follow_symlinks=True):
            return os.stat(self.path, follow_symlinks=follow_symlinks)

    def scandir(path):
        """ Compatibility layer for  `os.scandir` from Python 3.5+. """
        return (DirEntry(path, x) for x in os.listdir(path))
else:
    scandir = os.scandir


if ON_LINUX or ON_CYGWIN:
    PATH_DEFAULT = (os.path.expanduser('~/bin'), '/usr/local/sbin',
                    '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin',
                    '/usr/games', '/usr/local/games')
elif ON_DARWIN:
    PATH_DEFAULT = ('/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin')
else:
    PATH_DEFAULT = ()

#
# All constants as a dict
#

PLATFORM_INFO = {name: obj for name, obj in globals().items()
                 if name.isupper()}
""" The constants of this module as dictionary. """
