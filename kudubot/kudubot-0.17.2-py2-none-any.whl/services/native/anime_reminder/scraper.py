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
import time
import json
import logging
import requests
from typing import List, Dict


logger = logging.getLogger(__name__)
u"""
The logger for this module
"""


def scrape_reddit_discussion_threads():
    u"""
    Scrapes /u/Holo_of_Yoitsu's post history for anime discussion threads
    :return: The parsed discussion threads as a list of dictionaries with
             descriptive keys
    """

    logger.debug(u"Fetching last 25 submitted reddit threads "
                 u"from /u/Holo_of_Yoitsu")

    html = requests.get(u"https://www.reddit.com/user/Holo_of_Yoitsu.json")
    while html.status_code != 200:  # Circumvent rate limiting if we're unlucky
        time.sleep(15)
        html = requests.get(u"https://www.reddit.com/user/Holo_of_Yoitsu.json")

    data = json.loads(html.text)

    threads = []

    for item in data[u"data"][u"children"]:

        url = item[u"data"][u"url"]
        title = item[u"data"][u"title"].split(u"[Spoilers] ", 1)[1]\
            .rsplit(u" discussion", 1)[0]

        show_name = title.rsplit(u" - ", 1)[0]
        episode = int(title.rsplit(u" - Episode ", 1)[1])

        threads.append({
            u"show_name": show_name, u"episode": episode, u"url": url
        })

        logger.debug(u"Found thread: " + unicode(threads[-1]))

    logger.debug(u"Finished retrieving data from reddit")

    return threads
