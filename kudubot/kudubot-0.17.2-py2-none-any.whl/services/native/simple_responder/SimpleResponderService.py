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
import logging
from typing import List
from kudubot.entities.Message import Message
from kudubot.services.BaseService import BaseService


class SimpleResponderService(BaseService):
    u"""
    Class that implements a kudubot service that analyzes Strings and responds
    to them using a relatively simple ruleset
    """

    rules = [
        # Case Insensitive Equals
        ({u":)": u":) :) :)"},
         lambda incoming, key: incoming.lower() == key.lower()),

        # Case Sensitive Equals
        ({u"Hello World!": u"01001000 01100101 01101100 01101100 01101111 "
                          u"00100000 01010111 01101111 01110010 01101100 "
                          u"01100100 00100001",
          u"Ping": u"Pong",
          u"ping": u"pong"},
         lambda incoming, key: incoming == key),

        # Case Insensitive Contains
        ({u"würfel": u"4"},
         lambda incoming, key: incoming.lower().find(key.lower()) != -1),

        # Case Sensitive Contains
        ({u"FC Bayern": u"Deutscher Meister 2017!"},
         lambda incoming, key: incoming.find(key) != -1)
    ]
    u"""
    These are the rule-based responses for the Simple Responder Service

    The consist of a Tuple of a dictionary mapping strings to each other,
    as well as a lambda expression that return a boolean value.
    If that lambda expression returns true, the pattern matches and the
    dictionary value is returned as a response
    """

    @staticmethod
    def define_identifier():
        u"""
        Defines the Service's unique identifier

        :return: The unique identifier
        """
        return u"simple_responder"

    @staticmethod
    def define_requirements():
        u"""
        Defines the Service's dependency Services

        :return: A list of dependency Services for this Service
        """
        return []

    def __check_rules__(self, message_text):
        u"""
        Goes through all rules and returns the first appropriate response text

        :param message_text: The message text to analyze
        :return: The response, or an empty string if nothing was found
        """

        self.logger.debug(u"Checking Rules")

        for rule in self.rules:
            for sub_rule in dict(rule[0]):
                if rule[1](message_text, sub_rule):
                    logging.debug(u"Match found for rule " + repr(sub_rule))
                    return rule[0][sub_rule]

        return u""

    def is_applicable_to(self, message):
        u"""
        Checks if the Service is applicable to a given message

        :param message: The message to check
        :return: True if applicable, else False
        """
        return self.__check_rules__(message.message_body) != u""

    def handle_message(self, message):
        u"""
        Handles the message, provided this service is applicable to it

        :param message: The message to process
        :return: None
        """
        response = self.__check_rules__(message.message_body)
        if response != u"":
            self.reply(u"Simple Response", response, message)
