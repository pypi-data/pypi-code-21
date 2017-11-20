u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
from typing import List
from kudubot.services.ExternalService import ExternalService


class HelloWorldService(ExternalService):
    u"""
    A service that responds with a 'Hello World!' snippet in various languages.
    """

    def define_executable_file_url(self):
        u"""
        Defines a URL to the executable file used in this service

        :return: The URL to the executable file
        """
        return self.resolve_github_release_asset_url(
            u"namboy94", u"kudubot", u"helloworld_rust"
        )

    def define_executable_command(self):
        u"""
        Defines the command required to execute the executable file

        :return: The command list, for example ["java", "-jar"] for .jar files
        """
        return []

    @staticmethod
    def define_identifier():
        u"""
        Defines the identifier of the service

        :return: The service's identifier
        """
        return u"helloworld_rust"
