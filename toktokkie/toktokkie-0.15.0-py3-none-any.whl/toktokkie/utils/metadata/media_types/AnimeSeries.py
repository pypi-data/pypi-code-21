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

from typing import Dict, List
from toktokkie.utils.metadata.media_types.TvSeries import TvSeries
from toktokkie.utils.parsing.myanimelist import parse_myanimelist_url


class AnimeSeries(TvSeries):
    """
    Models the anime_series media type
    """

    identifier = "anime_series"
    """
    An identifier string that indicates the type
    """

    @property
    def myanimelist_url(self) -> str:
        url = self.resolve_inner_attribute("myanimelist_url")
        return url if url is not None else ""

    @myanimelist_url.setter
    def myanimelist_url(self, value: str):
        url = None if value == "" else value
        self.store_inner_attribute("myanimelist_url", url)

    def load_myanimelist_data(self) -> Dict[str, str or int or List[str]]:
        """
        Fetches information from myanimelist.net for this metadata object
        :return: A dictionary with information from myanimelist.net with chosen
                 default values in case any values were not found
        """

        params = {
            "type": ("Type", "str", "?"),
            "episodes": ("Episodes", "int", -1),
            "status": ("Status", "str", "?"),
            "aired": ("Aired", "str", "?"),
            "studios": ("Studios", "List[str]", []),
            "source": ("Source", "str", "?"),
            "genres": ("Genres", "List[str]", []),
            "runtime": ("Duration", "str", "?"),
            "score": ("Score", "SCORE", "?"),
            "rank": ("Ranked", "RANK", "?")
        }

        # noinspection PyTypeChecker
        return parse_myanimelist_url(self.myanimelist_url, params)

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
            "required": {},
            "optional": {"myanimelist_url": str},
            "extenders": {}
        })
        return super(AnimeSeries, AnimeSeries).define_attributes(additional)
