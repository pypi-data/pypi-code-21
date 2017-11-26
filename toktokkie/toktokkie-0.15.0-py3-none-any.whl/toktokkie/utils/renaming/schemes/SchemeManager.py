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
from typing import List
from toktokkie.utils.renaming.schemes.GenericScheme import GenericScheme
from toktokkie.utils.renaming.schemes.PlexTvdbScheme import PlexTvdbScheme


class SchemeManager(object):
    """
    Class that manages the various implemented renaming schemes
    """

    implemented_schemes = [PlexTvdbScheme]
    """
    List of currently implemented schemes
    """

    @staticmethod
    def get_all_schemes() -> List[type(GenericScheme)]:
        """
        :return: A list of all implemented schemes
        """
        return SchemeManager.implemented_schemes

    @staticmethod
    def get_scheme_names() -> List[str]:
        """
        :return: A list of implemented scheme names
        """
        scheme_names = []
        for scheme in SchemeManager.implemented_schemes:
            scheme_names.append(scheme.get_scheme_name())
        return scheme_names

    @staticmethod
    def get_scheme_from_scheme_name(scheme_name: str) -> type(GenericScheme):
        """
        Turns a scheme name into a Scheme class and returns it

        :param scheme_name: the scheme name of the scheme to return
        :return:            the scheme's class, or None if the name did not
                            match any implemented scheme
        """
        for scheme in SchemeManager.implemented_schemes:
            if scheme_name == scheme.get_scheme_name():
                return scheme
        return None
