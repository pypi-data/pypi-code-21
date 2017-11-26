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
from subprocess import Popen
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class DesktopIniProcedure(GenericProcedure):
    """
    Class that models a Windows Explorer Desktop.ini-based iconizer
    """

    @staticmethod
    def is_applicable() -> bool:
        """
        The Desktop.ini iconizer is applicable if the system is running Windows

        :return: True if the iconizer is applicable to the system, else False
        """
        return sys.platform == "win32"

    @staticmethod
    def iconize(directory: str, icon_file: str) -> None:
        """
        Iconizes the given directory using hidden desktop.ini files
        with metadata.
        The icon file must be a .ico file,
        but the file extension may be omitted (e.g. icon instead of icon.ico)

        :param directory: The directory to iconize
        :param icon_file: The icon file to use
        :return:          None
        """
        # NOTE: This procedure is rather... interesting and derived from legacy
        # code I wrote in Autohotkey years ago.
        # It features some rather interesting Windows quirks.

        if not icon_file.endswith(".ico"):
            icon_file += ".ico"

        desktop_ini_file = os.path.join(directory, "desktop.ini")
        relative_path = os.path.relpath(icon_file, directory)

        # If the file already exists, set the attributes in a way
        # that the program can edit the file:
        # -r : Clears read-only state
        # -s : Clears the system file attribute
        # -h : Clears the hidden state
        if os.path.isfile(desktop_ini_file) and \
                DesktopIniProcedure.is_applicable():  # pragma: no cover
            Popen(["attrib", "-s", "-h", "-r", desktop_ini_file]).wait()

        # Write the folder icon information to the desktop.ini file,
        # deleting all previous content of the file
        with open(desktop_ini_file, 'w') as f:
            f.write("[.ShellClassInfo]\r\n")
            f.write("IconFile=" + relative_path + "\r\n")
            f.write("IconIndex=0\r\n")
            f.write("IconResource=" + relative_path + ",0\r\n")

        # Set the attributes of the desktop.ini file to hidden,
        # system file and read-only
        if DesktopIniProcedure.is_applicable():  # pragma: no cover
            Popen(["attrib", "+s", "+h", "+r", desktop_ini_file]).wait()

    @staticmethod
    def reset_iconization_state(directory: str) -> None:
        """
        Resets the iconization state of the given directory
        by simply deleting the desktop.ini file
        :param directory: the directory to de-iconize
        :return:          None
        """
        desktop_ini_file = os.path.join(directory, "desktop.ini")
        if os.path.isfile(desktop_ini_file):
            if DesktopIniProcedure.is_applicable():  # pragma: no cover
                Popen(["attrib", "-s", "-h", "-r", desktop_ini_file]).wait()
            os.remove(os.path.join(directory, "desktop.ini"))

    @staticmethod
    def get_icon_file(directory: str) -> str or None:
        """
        Returns the path to the given directory's icon file, if it is iconized.
        If not, None is returned

        :param directory: The directory to check
        :return:          Either the path to the icon file or None
                          if no icon file exists
        """
        desktop_ini_file = os.path.join(directory, "desktop.ini")

        if not os.path.isfile(desktop_ini_file):
            return None
        else:
            with open(desktop_ini_file, 'r') as ini:
                desktop_ini = ini.read()

            if "IconFile=" in desktop_ini:
                return os.path.join(
                    directory,
                    desktop_ini.split("IconFile=")[1].split("\n")[0]
                )
            else:
                return None

    @staticmethod
    def get_procedure_name() -> str:
        """
        :return: The name of the Procedure
        """
        return "desktop_ini"
