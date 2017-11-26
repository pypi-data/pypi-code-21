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
import os
import tvdb_api
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Base import Base
from tvdb_exceptions import tvdb_episodenotfound, tvdb_seasonnotfound,\
    tvdb_shownotfound
from itertools import imap
from itertools import ifilter


class TvSeries(Base):
    u"""
    Models the tv_series media type
    """

    identifier = u"tv_series"
    u"""
    An identifier string that indicates the type
    """

    # Getters
    @property
    def resolutions(self):
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute(u"resolutions")

    @property
    def audio_langs(self):
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute(u"audio_langs")

    @property
    def subtitle_langs(self):
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute(u"subtitle_langs")

    @property
    def tvdb_url(self):
        url = self.resolve_inner_attribute(u"tvdb_url")
        return url if url is not None else u""

    @property  # Doesn't get a setter
    def seasons(self):
        if self.child_key and self.extender_key:
            return None
        else:
            return self.resolve_inner_attribute(u"seasons")

    # Setters
    @resolutions.setter
    def resolutions(self, value):

        # Custom equality checker
        def equals(x, y):
            if len(x) != len(y):
                return False
            else:
                for i, item in enumerate(x):
                    if item[u"x"] != y[i][u"x"] or item[u"y"] != y[i][u"y"]:
                        return False
            return True

        self.store_inner_attribute(u"resolutions", value, equals)

    @audio_langs.setter
    def audio_langs(self, value):
        self.store_inner_attribute(u"audio_langs",
                                   list(imap(lambda x: x.strip(), value)))

    @subtitle_langs.setter
    def subtitle_langs(self, value):
        self.store_inner_attribute(u"subtitle_langs",
                                   list(imap(lambda x: x.strip(), value)))

    @tvdb_url.setter
    def tvdb_url(self, value):
        url = None if value == u"" else value
        self.store_inner_attribute(u"tvdb_url", url)

    def get_child_names(self):
        u"""
        Method that fetches all children items (The seasons, in this case)
        :return: A list of children names
        """
        children = os.listdir(self.path)
        children = list(ifilter(
            lambda x:
            not x.startswith(u".") and
            os.path.isdir(os.path.join(self.path, x)),
            children
        ))
        return children

    def load_tvdb_data(self):
        u"""
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
                u"firstaired": data[u"firstaired"],
                u"runtime": data[u"runtime"],
                u"episode_count": episode_count,
                u"season_count": max([len(data) - 1, 1]),
                u"genres": list(ifilter(
                    lambda x: x != u"", data[u"genre"].split(u"|")
                ))
            }

        except (tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound,
                ConnectionError, KeyError):
            # If not found, or other error, just return empty dict
            return {
                u"firstaired": u"?",
                u"runtime": u"?",
                u"episode_count": -1,
                u"season_count": -1,
                u"genres": []
            }

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
            u"required": {
                u"resolutions": list,
                u"audio_langs": list,
                u"subtitle_langs": list
            },
            u"optional": {u"tvdb_url": unicode},
            u"extenders": {u"seasons": dict}
        })
        return super(TvSeries, TvSeries).define_attributes(additional)
