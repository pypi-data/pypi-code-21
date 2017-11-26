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

from __future__ import absolute_import
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Ebook import Ebook
from toktokkie.utils.parsing.myanimelist import parse_myanimelist_url


class LightNovel(Ebook):
    u"""
    Models the light_novel media type
    """

    identifier = u"light_novel"
    u"""
    An identifier string that indicates the type
    """

# Getters
    @property
    def illustrator(self):
        return unicode(self.resolve_inner_attribute(u"illustrator"))

    @property
    def official_translation(self):
        return bool(self.resolve_inner_attribute(u"official_translation"))

    @property
    def myanimelist_url(self):
        url = self.resolve_inner_attribute(u"myanimelist_url")
        return url if url is not None else u""

    @property
    def novelupdates_url(self):
        url = self.resolve_inner_attribute(u"novelupdates_url")
        return url if url is not None else u""

    # Setters
    @illustrator.setter
    def illustrator(self, value):
        self.store_inner_attribute(u"illustrator", value)

    @official_translation.setter
    def official_translation(self, value):
        self.store_inner_attribute(u"official_translation", value)

    @myanimelist_url.setter
    def myanimelist_url(self, value):
        url = None if value == u"" else value
        self.store_inner_attribute(u"myanimelist_url", url)

    @novelupdates_url.setter
    def novelupdates_url(self, value):
        url = None if value == u"" else value
        self.store_inner_attribute(u"novelupdates_url", url)

    def load_myanimelist_data(self):
        u"""
        Fetches information from myanimelist.net for this metadata object
        :return: A dictionary with information from myanimelist.net with chosen
                 default values in
                 case any values were not found
        """
        params = {
            u"volumes": (u"Volumes", u"int", -1),
            u"status": (u"Status", u"str", u"?"),
            u"published": (u"Published", u"str", u"?"),
            u"genres": (u"Genres", u"List[str]", []),
            u"score": (u"Score", u"SCORE", u"?"),
            u"rank": (u"Ranked", u"RANK", u"?")
        }

        # noinspection PyTypeChecker
        return parse_myanimelist_url(self.myanimelist_url, params)

    def load_novelupdates_data(self):
        u"""
        Downloads data from novelupdates.com
        :return: The data parsed from novelupdates.com
        """

        data = {u"licensed": u"?", u"completely_translated": u"?"}

        html = requests.get(self.novelupdates_url)
        retries = 0
        while html.status_code != 200 and retries < 10:
            time.sleep(1)
            retries += 1
            html = requests.get(self.novelupdates_url)

        soup = BeautifulSoup(
            u"" if html.status_code != 200 else html.text, u"html.parser"
        )

        data[u"licensed"] = \
            soup.find_all(u"div", id=u"showlicensed")[0].text.strip()
        data[u"completely_translated"] = \
            soup.find_all(u"div", id=u"showtranslated")[0].text.strip()
        return data

    # noinspection PyDefaultArgument
    @staticmethod
    def define_attributes(additional=[]):
        u"""
        Defines additional attributes for this media type
        :param additional: Further additional parameters
                           for use with child classes
        :return: The attributes of the Media Type
        """
        additional.append({
            u"required": {u"official_translation": bool},
            u"optional": {u"myanimelist_url": unicode, u"novelupdates_url": unicode},
            u"extenders": {}
        })
        return super(LightNovel, LightNovel).define_attributes(additional)
