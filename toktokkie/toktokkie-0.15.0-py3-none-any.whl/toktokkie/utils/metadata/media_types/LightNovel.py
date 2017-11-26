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

import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Ebook import Ebook
from toktokkie.utils.parsing.myanimelist import parse_myanimelist_url


class LightNovel(Ebook):
    """
    Models the light_novel media type
    """

    identifier = "light_novel"
    """
    An identifier string that indicates the type
    """

# Getters
    @property
    def illustrator(self) -> str:
        return str(self.resolve_inner_attribute("illustrator"))

    @property
    def official_translation(self) -> bool:
        return bool(self.resolve_inner_attribute("official_translation"))

    @property
    def myanimelist_url(self) -> str:
        url = self.resolve_inner_attribute("myanimelist_url")
        return url if url is not None else ""

    @property
    def novelupdates_url(self) -> str:
        url = self.resolve_inner_attribute("novelupdates_url")
        return url if url is not None else ""

    # Setters
    @illustrator.setter
    def illustrator(self, value: str):
        self.store_inner_attribute("illustrator", value)

    @official_translation.setter
    def official_translation(self, value: bool):
        self.store_inner_attribute("official_translation", value)

    @myanimelist_url.setter
    def myanimelist_url(self, value: str):
        url = None if value == "" else value
        self.store_inner_attribute("myanimelist_url", url)

    @novelupdates_url.setter
    def novelupdates_url(self, value: str):
        url = None if value == "" else value
        self.store_inner_attribute("novelupdates_url", url)

    def load_myanimelist_data(self) -> Dict[str, str or int or List[str]]:
        """
        Fetches information from myanimelist.net for this metadata object
        :return: A dictionary with information from myanimelist.net with chosen
                 default values in
                 case any values were not found
        """
        params = {
            "volumes": ("Volumes", "int", -1),
            "status": ("Status", "str", "?"),
            "published": ("Published", "str", "?"),
            "genres": ("Genres", "List[str]", []),
            "score": ("Score", "SCORE", "?"),
            "rank": ("Ranked", "RANK", "?")
        }

        # noinspection PyTypeChecker
        return parse_myanimelist_url(self.myanimelist_url, params)

    def load_novelupdates_data(self) -> Dict[str, str]:
        """
        Downloads data from novelupdates.com
        :return: The data parsed from novelupdates.com
        """

        data = {"licensed": "?", "completely_translated": "?"}

        html = requests.get(self.novelupdates_url)
        retries = 0
        while html.status_code != 200 and retries < 10:
            time.sleep(1)
            retries += 1
            html = requests.get(self.novelupdates_url)

        soup = BeautifulSoup(
            "" if html.status_code != 200 else html.text, "html.parser"
        )

        data["licensed"] = \
            soup.find_all("div", id="showlicensed")[0].text.strip()
        data["completely_translated"] = \
            soup.find_all("div", id="showtranslated")[0].text.strip()
        return data

    # noinspection PyDefaultArgument
    @staticmethod
    def define_attributes(additional: List[Dict[str, Dict[str, type]]]=[]) \
            -> Dict[str, Dict[str, type]]:
        """
        Defines additional attributes for this media type
        :param additional: Further additional parameters
                           for use with child classes
        :return: The attributes of the Media Type
        """
        additional.append({
            "required": {"official_translation": bool},
            "optional": {"myanimelist_url": str, "novelupdates_url": str},
            "extenders": {}
        })
        return super(LightNovel, LightNovel).define_attributes(additional)
