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
from typing import Dict, List
from toktokkie.utils.metadata.media_types.TvSeries import TvSeries
from toktokkie.utils.parsing.myanimelist import parse_myanimelist_url


class AnimeSeries(TvSeries):
    u"""
    Models the anime_series media type
    """

    identifier = u"anime_series"
    u"""
    An identifier string that indicates the type
    """

    @property
    def myanimelist_url(self):
        url = self.resolve_inner_attribute(u"myanimelist_url")
        return url if url is not None else u""

    @myanimelist_url.setter
    def myanimelist_url(self, value):
        url = None if value == u"" else value
        self.store_inner_attribute(u"myanimelist_url", url)

    def load_myanimelist_data(self):
        u"""
        Fetches information from myanimelist.net for this metadata object
        :return: A dictionary with information from myanimelist.net with chosen
                 default values in case any values were not found
        """

        params = {
            u"type": (u"Type", u"str", u"?"),
            u"episodes": (u"Episodes", u"int", -1),
            u"status": (u"Status", u"str", u"?"),
            u"aired": (u"Aired", u"str", u"?"),
            u"studios": (u"Studios", u"List[str]", []),
            u"source": (u"Source", u"str", u"?"),
            u"genres": (u"Genres", u"List[str]", []),
            u"runtime": (u"Duration", u"str", u"?"),
            u"score": (u"Score", u"SCORE", u"?"),
            u"rank": (u"Ranked", u"RANK", u"?")
        }

        # noinspection PyTypeChecker
        return parse_myanimelist_url(self.myanimelist_url, params)

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
            u"required": {},
            u"optional": {u"myanimelist_url": unicode},
            u"extenders": {}
        })
        return super(AnimeSeries, AnimeSeries).define_attributes(additional)
