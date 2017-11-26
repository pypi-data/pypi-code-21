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


class GenericProcedure(object):
    """
    Class that models the behaviour of an iconizing procedure
    """

    @staticmethod
    def is_applicable() -> bool:
        """
        Checks if the iconizing procedure is applicable to the current system

        :return: True, if the procedure is applicable
        """
        return True

    @staticmethod
    def iconize(directory: str, icon_file: str) -> None:
        """
        Iconizes a given directory with a given icon file using the procedure

        :param directory: The directory to iconize
        :param icon_file: The icon with which to iconize the directory
        :return:          None
        """
        return

    @staticmethod
    def reset_iconization_state(directory: str) -> None:
        """
        Resets the iconization state of the given directory
        :param directory: the directory to de-iconize
        :return:          None
        """
        return

    @staticmethod
    def get_icon_file(directory: str) -> str or None:
        """
        Returns the path to the given directory's icon file, if it is iconized.
        If not, None is returned

        :param directory: The directory to check
        :return:          Either the path to the icon file or
                          None if no icon file exists
        """
        return None

    @staticmethod
    def get_procedure_name() -> str:
        """
        :return: The name of the Procedure
        """
        return "generic"
