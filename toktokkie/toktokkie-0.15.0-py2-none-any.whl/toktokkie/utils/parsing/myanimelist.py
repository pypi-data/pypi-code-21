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
from typing import Dict, List, Tuple


def parse_myanimelist_url(url,
                          params):
    u"""
    Fetches information from myanimelist.net for a myanimelist URL
    and a set of attributes
    :param url: The myanimelist URL to parse
    :param params: A set of parameters to find in the myanimelist.net data.
                   Consists of tuple with the values:
                   identifier, type, default value
    :return: A dictionary with information from myanimelist.net
             with chosen default values in case any values were not found
    """
    data = {}
    for key, item in params.items():
        data[key] = item[2]  # Default values

    html = requests.get(url)
    retries = 0
    while html.status_code != 200 and retries < 10:
        time.sleep(1)
        retries += 1
        html = requests.get(url)

    soup = BeautifulSoup(
        u"" if html.status_code != 200 else html.text, u"html.parser"
    )
    sidebar = soup.find_all(u"div", u"js-scrollfix-bottom")

    if len(sidebar) == 0:
        return data

    divs = sidebar[0].find_all(u"div")

    for div in divs:
        text = div.text.replace(u"\n", u"").strip()

        for key, item in params.items():
            if text.startswith(item[0] + u":"):
                text = text.split(u":", 1)[1].strip()

                if item[1] == u"str":
                    data[key] = text
                if item[1] == u"int":
                    try:
                        data[key] = int(text)
                    except ValueError:
                        data[key] = -1
                elif item[1] == u"List[str]":
                    data[key] = text.split(u",")
                elif item[1] == u"SCORE":
                    data[key] = text.split(u"(")[0].strip()
                elif item[1] == u"RANK":
                    data[key] = text.split(u" ")[0].strip()

    return data
