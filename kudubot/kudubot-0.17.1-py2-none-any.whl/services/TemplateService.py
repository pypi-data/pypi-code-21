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
from typing import List, Dict
from kudubot.entities.Message import Message
from kudubot.services.HelperService import HelperService


class TemplateService(HelperService):
    u"""
    This is a Template for a Service class.
    # TODO Change this description
    """

    @staticmethod
    def define_identifier():
        u"""
        Defines the identifier for this service

        :return: The service's identifier
        """
        # TODO Implement
        return u"todo"

    def define_command_name(self, language):
        u"""
        Defines the command prefix for the service.
        By default, '/' followed by the service identifier from
        self.define_identifier() is used.

        :param language: The language in which to define the command name
        :return: The command name in the specified language
        """
        # TODO Remove or Implement
        return {
            u"en": u"/todo",
            u"de": u"/todo"
        }[language]

    @staticmethod
    def define_requirements():
        u"""
        Defines required Services for this Service

        :return: The list of required services
        """
        # TODO Implement
        return []

    def determine_language(self, message):
        u"""
        Determines the language of a message

        :param message: The message to check for the language
        :return: The language of the message
        """
        # TODO Implement
        return u"en"

    def define_language_text(self):
        u"""
        Defines the dictionary used for translating strings using the
        self.reply_translated() or self.translate() methods

        The format is:

            term: {lang: value}

        :return: The dictionary for use in translating
        """
        # TODO Implement
        return {
            u"@{Example}": {u"en": u"Example", u"de": u"Beispiel"}
        }

    def define_help_message(self, language):
        u"""
        Defines the help message of the service in various languages

        :param language: The language to use
        :return: The help message in the language
        """
        # TODO Implement
        return {
            u"en": u"Example",
            u"de": u"Beispiel"
        }[language]

    def define_syntax_description(self, language):
        u"""
        Defines the Syntax description of the Service in various languages

        :param language: The language in which to return the syntax message
        :return: The syntax message
        """
        # TODO Implement
        return {
            u"en": u"Example",
            u"de": u"Beispiel"
        }[language]

    def handle_message(self, message):
        u"""
        Handles an applicable message
        # TODO Describe what this Service does

        :param message: The message to handle
        """
        # TODO Implement
        pass

    def is_applicable_to(self, message):
        u"""
        Checks if a Message is applicable to this Service
        # TODO Describe what this Service checks for

        :param message: The message to check
        :return: True if the Message is applicable, False otherwise
        """
        # TODO Implement
        return False
