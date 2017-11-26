"""
Copyright 2017 Hermann Krumrey

This file is part of server-admintools.

server-admintools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

server-admintools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with server-admintools.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
from subprocess import Popen

"""
This module contains functions that help with permissions
"""


def is_sudo():
    """
    Checks if the current user has root privileges
    :return: True if the user has the privileges, False otherwise
    """
    return os.geteuid() == 0


def quit_if_not_sudo():
    """
    Quits the program in case the user does not have root privileges
    :return: None
    """
    if not is_sudo():
        print("You need root permissions for this action.")
        sys.exit(1)


def change_ownership(path, user):
    """
    Changes the ownership of a file or directory
    :param path: The path of the file or directory
                 whose owner should be changed
    :param user: The new owner of the file or directory
    :return: None
    """
    Popen(["chown", user, path, "-R"]).wait()
