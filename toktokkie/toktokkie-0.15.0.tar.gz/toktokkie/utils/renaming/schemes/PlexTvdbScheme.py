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
from toktokkie.utils.renaming.schemes.GenericScheme import GenericScheme


class PlexTvdbScheme(GenericScheme):
    """
    Renaming Scheme class that generates an episode name
    in the following format:

        Show Name - SXXEXX - Episode Name

    using data from TheTvdb.com
    """

    def apply_scheme(self) -> str:
        """
        Applies the Plex Tvdb scheme to the episode

        :return: the generated name
        """
        episode_name = self.get_tvdb_episode_name(
            self.series_name,
            self.season_number,
            self.episode_number
        )

        episode_number = str(self.episode_number).zfill(2) \
            if self.episode_number >= 0 \
            else str(self.episode_number).zfill(3)
        season_number = str(self.season_number).zfill(2) \
            if self.season_number >= 0 \
            else str(self.season_number).zfill(3)

        return self.series_name + " - S" + season_number + \
            "E" + episode_number + " - " + episode_name

    @staticmethod
    def get_scheme_name() -> str:
        """
        :return: The scheme's name
        """
        return "Plex (TVDB)"
