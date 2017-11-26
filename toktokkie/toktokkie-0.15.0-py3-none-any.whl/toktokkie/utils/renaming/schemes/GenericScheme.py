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

# imports
import tvdb_api
from requests.exceptions import ConnectionError
from tvdb_exceptions import tvdb_episodenotfound, tvdb_seasonnotfound, \
    tvdb_shownotfound


class GenericScheme(object):
    """
    Class that models a generic renaming scheme
    """

    def __init__(self, series_name: str, season_number: int,
                 episode_number: int) -> None:
        """
        Initializes a Scheme object for a single episode

        :param series_name:    the episode's series' name
        :param season_number:  the episode's season number
        :param episode_number: the episode's episode number
        """
        self.series_name = series_name
        self.season_number = season_number
        self.episode_number = episode_number

    def generate_episode_name(self) -> str:
        """
        Generates an episode name for the specified series with regards to its
        episode and season numbers.
        Sanitizes the episode name beforehand

        :return: the generated name
        """
        sanitized = self.apply_scheme()
        illegal_characters = [
            '/', '\\', '?', '<', '>', ':', '*', '|', "\"", '^'
        ]
        for illegal_character in illegal_characters:
            sanitized = sanitized.replace(illegal_character, "")
        return sanitized

    def apply_scheme(self) -> str:  # pragma: no cover
        """
        Applies the scheme to the episode information
        and returns it as a string

        :return: the generated episode name
        """
        raise NotImplementedError

    @staticmethod
    def get_scheme_name() -> str:  # pragma: no cover
        """
        :return: The scheme's name
        """
        raise NotImplementedError()

    @staticmethod
    def get_tvdb_episode_name(series_name: str, season_number: int,
                              episode_number: int) -> str:
        """
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
            episode_name = episode_info['episodename']

        except (tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound,
                ConnectionError, KeyError) as e:
            # If not found, or other error, just return generic name
            if str(e) == "cache_location":  # pragma: no cover
                print("TheTVDB.com is down!")
            episode_name = "Episode " + str(episode_number)

        return episode_name
