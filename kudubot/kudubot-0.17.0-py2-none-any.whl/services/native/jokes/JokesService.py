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
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from kudubot.entities.Message import Message
from kudubot.services.HelperService import HelperService


class JokesService(HelperService):
    u"""
    A Service that tells jokes
    """

    @staticmethod
    def define_identifier():
        u"""
        :return: The service's identifier
        """
        return u"jokes"

    @staticmethod
    def define_requirements():
        u"""
        :return: An empty list as this service has no requirements
        """
        return []

    def define_syntax_description(self, language):
        u"""
        :param language: The language to use
        :return: The syntax description for this language
        """
        return {u"en": u"/joke", u"de": u"/witz"}[language]

    def define_help_message(self, language):
        u"""
        :param language: The language to use
        :return: The help message for the specified language
        """
        return {u"en": u"Tells a joke", u"de": u"Erzählt einen Witz"}[language]

    def determine_language(self, message):
        u"""
        Determines the language for a message
        :param message: The message to analyze
        :return: The language that this message was in
        """
        if message.message_body.lower().strip() == u"/witz":
            return u"de"
        else:
            return u"en"

    def define_language_text(self):
        u"""
        :return: A dictionary used for translations
        """
        return {u"@response_title": {u"en": u"Joke", u"de": u"Witz"}}

    def is_applicable_to(self, message):
        u"""
        Checks if a message is applicable to this service
        :param message: The message to analyze
        :return: True if applicable, False otherwise
        """
        return message.message_body.strip().lower() in [u"/joke", u"/witz"]

    def handle_message(self, message):
        u"""
        Handles an incoming message
        :param message:
        :return:
        """
        language = self.determine_language(message)

        if language == u"de":
            joke = self.load_german_joke()
        elif language == u"en":
            joke = self.load_english_joke()
        else:
            joke = u"ERROR_LANG_NOT_FOUND"

        self.reply(self.translate(u"@response_title", language), joke, message)

    # noinspection PyMethodMayBeStatic
    def load_german_joke(self):
        u"""
        Fetches a German joke from the internet
        :return: The joke
        """
        html = requests.get(u"http://witze.net/zuf%C3%A4llige-witze").text
        return BeautifulSoup(html, u"html.parser").select(u".joke")[0].text

    # noinspection PyMethodMayBeStatic
    def load_english_joke(self):
        u"""
        Fetches an English joke from the internet
        :return: The joke
        """
        html = requests.get(u"https://www.ajokeaday.com/jokes/random")
        soup = BeautifulSoup(html.text, u"html.parser")
        return soup.select(u"p")[1].text
