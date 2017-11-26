u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
import os
import sys
from subprocess import Popen, check_output, CalledProcessError
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class GnomeProcedure(GenericProcedure):
    u"""
    Iconizing Procedure used on Linux system using Gnome and Gnome-derivative
    desktop environments
    """

    @staticmethod
    def is_applicable():
        u"""
        The Gnome procedure is applicable if the system is running Linux
        as well as a Gnome environment, like the Gnome DE or Cinnamon

        :return: True, if the procedures is applicable, False otherwise
        """
        path_divider = u";" if sys.platform == u"win32" else u":"
        paths = os.environ[u"PATH"].split(path_divider)
        gvfs_installed = False
        for path in paths:
            if os.access(os.path.join(path, u"gio"), os.X_OK):
                gvfs_installed = True

        gvfs_check = False
        if gvfs_installed:  # pragma: no cover

            try:
                gvfs_out = check_output([
                    u"gio", u"set", u"-t", u"string", u".",
                    u"metadata::custom-icon", u"a"]).decode()
            except CalledProcessError:
                gvfs_out = u"Not Supported"

            if gvfs_out.rstrip().lstrip() == u"":
                Popen([u"gio", u"set", u"-t", u"unset", u".",
                       u"metadata::custom-icon"]).wait()
                gvfs_check = True

            try:
                return sys.platform.startswith(u"linux") \
                       and gvfs_installed and gvfs_check
            except KeyError:  # pragma: no cover
                return False

    @staticmethod
    def iconize(directory, icon_file):
        u"""
        Iconizes the given directory using gvfs and the provided icon file
        The icon file should be a PNG file
        The file extension may be omiited, i.e. icon instead of icon.png

        :param directory: The directory to iconize
        :param icon_file: The icon file to use.
        :return:          None
        """
        if not icon_file.endswith(u".png"):
            icon_file += u".png"

        if GnomeProcedure.is_applicable():  # pragma: no cover
            Popen([u"gio", u"set", u"-t", u"string", directory,
                   u"metadata::custom-icon", u"file://" + icon_file])\
                .wait()

    @staticmethod
    def reset_iconization_state(directory):
        u"""
        Resets the iconization state of the given directory using the unset
        option of gvfs-set-attribute
        :param directory: the directory to de-iconize
        :return:          None
        """
        if GnomeProcedure.is_applicable():  # pragma: no cover
            Popen([
                u"gio", u"set", u"-t", u"unset",
                directory, u"metadata::custom-icon"]).wait()

    @staticmethod
    def get_icon_file(directory):
        u"""
        Returns the path to the given directory's icon file, if it is iconized.
         If not, None is returned

        :param directory: The directory to check
        :return:          Either the path to the icon file or None
                          if no icon file exists
        """
        if not GnomeProcedure.is_applicable():  # pragma: no cover
            return None

        else:  # pragma: no cover

            gvfs_info = check_output([u"gio", u"info", directory]).decode()

            if u"metadata::custom-icon: file://" in gvfs_info:
                return gvfs_info.split(
                    u"metadata::custom-icon: file://")[1].split(u"\n")[0]
            else:
                return None

    @staticmethod
    def get_procedure_name():
        u"""
        :return: The name of the Procedure
        """
        return u"gnome"
