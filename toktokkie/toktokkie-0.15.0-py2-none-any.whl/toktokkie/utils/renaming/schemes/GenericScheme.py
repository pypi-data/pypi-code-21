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

# imports
from __future__ import absolute_import
import tvdb_api
from requests.exceptions import ConnectionError
from tvdb_exceptions import tvdb_episodenotfound, tvdb_seasonnotfound, \
    tvdb_shownotfound


class GenericScheme(object):
    u"""
    Class that models a generic renaming scheme
    """

    def __init__(self, series_name, season_number,
                 episode_number):
        u"""
        Initializes a Scheme object for a single episode

        :param series_name:    the episode's series' name
        :param season_number:  the episode's season number
        :param episode_number: the episode's episode number
        """
        self.series_name = series_name
        self.season_number = season_number
        self.episode_number = episode_number

    def generate_episode_name(self):
        u"""
        Generates an episode name for the specified series with regards to its
        episode and season numbers.
        Sanitizes the episode name beforehand

        :return: the generated name
        """
        sanitized = self.apply_scheme()
        illegal_characters = [
            u'/', u'\\', u'?', u'<', u'>', u':', u'*', u'|', u"\"", u'^'
        ]
        for illegal_character in illegal_characters:
            sanitized = sanitized.replace(illegal_character, u"")
        return sanitized

    def apply_scheme(self):  # pragma: no cover
        u"""
        Applies the scheme to the episode information
        and returns it as a string

        :return: the generated episode name
        """
        raise NotImplementedError

    @staticmethod
    def get_scheme_name():  # pragma: no cover
        u"""
        :return: The scheme's name
        """
        raise NotImplementedError()

    @staticmethod
    def get_tvdb_episode_name(series_name, season_number,
                              episode_number):
        u"""
        Finds the TVDB episode name for a specified episode

        :param series_name:    the episode's series name
        :param season_number:  the episode's season number
        :param episode_number: the episode's episode number
        :return:               the TVDB episode name,
                               or Episode <episode_number>
                               if any sort of error occurs
        """
        try:
            tvdb = tvdb_api.Tvdb()
            episode_info = tvdb[series_name][season_number][episode_number]
            episode_name = episode_info[u'episodename']

        except (tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound,
                ConnectionError, KeyError), e:
            # If not found, or other error, just return generic name
            if unicode(e) == u"cache_location":  # pragma: no cover
                print u"TheTVDB.com is down!"
            episode_name = u"Episode " + unicode(episode_number)

        return episode_name
