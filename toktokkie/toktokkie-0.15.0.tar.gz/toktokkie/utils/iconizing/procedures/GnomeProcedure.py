"""
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
import os
import sys
from subprocess import Popen, check_output, CalledProcessError
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class GnomeProcedure(GenericProcedure):
    """
    Iconizing Procedure used on Linux system using Gnome and Gnome-derivative
    desktop environments
    """

    @staticmethod
    def is_applicable() -> bool:
        """
        The Gnome procedure is applicable if the system is running Linux
        as well as a Gnome environment, like the Gnome DE or Cinnamon

        :return: True, if the procedures is applicable, False otherwise
        """
        path_divider = ";" if sys.platform == "win32" else ":"
        paths = os.environ["PATH"].split(path_divider)
        gvfs_installed = False
        for path in paths:
            if os.access(os.path.join(path, "gio"), os.X_OK):
                gvfs_installed = True

        gvfs_check = False
        if gvfs_installed:  # pragma: no cover

            try:
                gvfs_out = check_output([
                    "gio", "set", "-t", "string", ".",
                    "metadata::custom-icon", "a"]).decode()
            except CalledProcessError:
                gvfs_out = "Not Supported"

            if gvfs_out.rstrip().lstrip() == "":
                Popen(["gio", "set", "-t", "unset", ".",
                       "metadata::custom-icon"]).wait()
                gvfs_check = True

            try:
                return sys.platform.startswith("linux") \
                       and gvfs_installed and gvfs_check
            except KeyError:  # pragma: no cover
                return False

    @staticmethod
    def iconize(directory: str, icon_file: str) -> None:
        """
        Iconizes the given directory using gvfs and the provided icon file
        The icon file should be a PNG file
        The file extension may be omiited, i.e. icon instead of icon.png

        :param directory: The directory to iconize
        :param icon_file: The icon file to use.
        :return:          None
        """
        if not icon_file.endswith(".png"):
            icon_file += ".png"

        if GnomeProcedure.is_applicable():  # pragma: no cover
            Popen(["gio", "set", "-t", "string", directory,
                   "metadata::custom-icon", "file://" + icon_file])\
                .wait()

    @staticmethod
    def reset_iconization_state(directory: str) -> None:
        """
        Resets the iconization state of the given directory using the unset
        option of gvfs-set-attribute
        :param directory: the directory to de-iconize
        :return:          None
        """
        if GnomeProcedure.is_applicable():  # pragma: no cover
            Popen([
                "gio", "set", "-t", "unset",
                directory, "metadata::custom-icon"]).wait()

    @staticmethod
    def get_icon_file(directory: str) -> str or None:
        """
        Returns the path to the given directory's icon file, if it is iconized.
         If not, None is returned

        :param directory: The directory to check
        :return:          Either the path to the icon file or None
                          if no icon file exists
        """
        if not GnomeProcedure.is_applicable():  # pragma: no cover
            return None

        else:  # pragma: no cover

            gvfs_info = check_output(["gio", "info", directory]).decode()

            if "metadata::custom-icon: file://" in gvfs_info:
                return gvfs_info.split(
                    "metadata::custom-icon: file://")[1].split("\n")[0]
            else:
                return None

    @staticmethod
    def get_procedure_name() -> str:
        """
        :return: The name of the Procedure
        """
        return "gnome"
