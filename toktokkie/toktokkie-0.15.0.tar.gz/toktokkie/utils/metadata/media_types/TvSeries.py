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

import os
import tvdb_api
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Base import Base
from tvdb_exceptions import tvdb_episodenotfound, tvdb_seasonnotfound,\
    tvdb_shownotfound


class TvSeries(Base):
    """
    Models the tv_series media type
    """

    identifier = "tv_series"
    """
    An identifier string that indicates the type
    """

    # Getters
    @property
    def resolutions(self) -> List[Dict[str, int]]:
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute("resolutions")

    @property
    def audio_langs(self) -> List[str]:
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute("audio_langs")

    @property
    def subtitle_langs(self) -> List[str]:
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute("subtitle_langs")

    @property
    def tvdb_url(self) -> str:
        url = self.resolve_inner_attribute("tvdb_url")
        return url if url is not None else ""

    @property  # Doesn't get a setter
    def seasons(self) -> Dict[str, Dict[str, object]] or None:
        if self.child_key and self.extender_key:
            return None
        else:
            return self.resolve_inner_attribute("seasons")

    # Setters
    @resolutions.setter
    def resolutions(self, value: List[Dict[str, int]]):

        # Custom equality checker
        def equals(x: List[Dict[str, int]], y: List[Dict[str, int]]):
            if len(x) != len(y):
                return False
            else:
                for i, item in enumerate(x):
                    if item["x"] != y[i]["x"] or item["y"] != y[i]["y"]:
                        return False
            return True

        self.store_inner_attribute("resolutions", value, equals)

    @audio_langs.setter
    def audio_langs(self, value: List[str]):
        self.store_inner_attribute("audio_langs",
                                   list(map(lambda x: x.strip(), value)))

    @subtitle_langs.setter
    def subtitle_langs(self, value: List[str]):
        self.store_inner_attribute("subtitle_langs",
                                   list(map(lambda x: x.strip(), value)))

    @tvdb_url.setter
    def tvdb_url(self, value: str):
        url = None if value == "" else value
        self.store_inner_attribute("tvdb_url", url)

    def get_child_names(self) -> List[str]:
        """
        Method that fetches all children items (The seasons, in this case)
        :return: A list of children names
        """
        children = os.listdir(self.path)
        children = list(filter(
            lambda x:
            not x.startswith(".") and
            os.path.isdir(os.path.join(self.path, x)),
            children
        ))
        return children

    def load_tvdb_data(self) -> Dict[str, str or int or List[str]]:
        """
        Loads a series' TVDB info
        :return: The TVDB info, consisting of a dictionary with the values
                 `firstaired`, `runtime`, `episode_count`,
                 `season_count` and `genres`
        """

        try:
            tvdb_client = tvdb_api.Tvdb()
            data = tvdb_client[self.name]

            episode_count = 0
            for key, season in data.items():
                if key < 1:
                    continue
                else:
                    episode_count += len(season)

            return {
                "firstaired": data["firstaired"],
                "runtime": data["runtime"],
                "episode_count": episode_count,
                "season_count": max([len(data) - 1, 1]),
                "genres": list(filter(
                    lambda x: x != "", data["genre"].split("|")
                ))
            }

        except (tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound,
                ConnectionError, KeyError):
            # If not found, or other error, just return empty dict
            return {
                "firstaired": "?",
                "runtime": "?",
                "episode_count": -1,
                "season_count": -1,
                "genres": []
            }

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
            "required": {
                "resolutions": list,
                "audio_langs": list,
                "subtitle_langs": list
            },
            "optional": {"tvdb_url": str},
            "extenders": {"seasons": dict}
        })
        return super(TvSeries, TvSeries).define_attributes(additional)
