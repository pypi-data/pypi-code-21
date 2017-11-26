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
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager


class Iconizer(object):
    """
    Class that handles the iconizing of multiple directories using icon files
    """

    def __init__(self, procedure_override: str = "") -> None:
        """
        Initializes the Iconizer's iconizing procedure.
        By default, it will try to find the most appropriate
        procedure for the current system

        :param procedure_override: Can be used to override the
                                   automatic procedure detection
        """
        if procedure_override:
            self.procedure = \
                ProcedureManager.get_procedure_from_procedure_name(
                    procedure_override
                )
        else:
            self.procedure = ProcedureManager.get_applicable_procedure()

    def recursive_iconize(self, directory: str) -> None:
        """
        Recursively checks a directory for media directories,
        then iconizes them

        :param directory: the directory to check
        :return:          None
        """
        directories = \
            MetaDataManager.find_recursive_media_directories(directory)
        for directory in directories:
            self.iconize_directory(directory)

    def iconize_directory(self, directory: str) -> None:
        """
        Iconizes a single directory containing a .meta/icons directory

        :param directory: The directory to iconize
        :return:          None
        """
        icon_directory = os.path.join(directory, ".meta", "icons")
        if os.path.isdir(icon_directory):
            self.procedure.iconize(
                directory, os.path.join(icon_directory, "main")
            )
            self.__inner_iconize__(directory, icon_directory)

    def __inner_iconize__(self, directory: str, icon_directory: str) -> None:
        """
        Iconizes inner directories of a directory containing a
        .meta/icons directory

        :param directory:       The parent directory
        :param icon_directory:  The path to the icon directory
        :return:                None
        """
        for child in os.listdir(directory):
            child_dir = os.path.join(directory, child)

            if os.path.isdir(child_dir) and not child.startswith("."):
                child_icon = os.path.join(icon_directory, child)
                self.procedure.iconize(child_dir, child_icon)
                self.__inner_iconize__(child_dir, icon_directory)

    def reverse_iconization(self, directory: str) -> None:
        """
        Reverses every folder iconization under the current directory

        :param directory: The directory to de-iconize
        :return:          None
        """
        self.procedure.reset_iconization_state(directory)
        for child in os.listdir(directory):
            child_dir = os.path.join(directory, child)
            if os.path.isdir(child_dir):
                self.reverse_iconization(child_dir)
