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
import os
from typing import Tuple, List
from xdcc_dl.entities.XDCCPack import XDCCPack
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from toktokkie.utils.renaming.schemes.GenericScheme import GenericScheme
from itertools import ifilter


class XDCCDownloadManager(object):
    u"""
    Class containing helper methods for the XDCC Download Manager UIs
    """

    @staticmethod
    def prepare_directory(directory, series_name, season):
        u"""
        Prepares the destination directory to be a valid 'tv_series'-type
        media directory

        :param directory:   The directory to prepare
        :param series_name: The series' name
        :param season:      The target season
        :return:            The valid media directory,
                            The selected season directory
        """
        if os.path.basename(directory) == series_name:
            destination_directory = directory
        else:
            destination_directory = os.path.join(directory, series_name)

        MetaDataManager.generate_media_directory(
            destination_directory, media_type=u"tv_series"
        )

        season_directory = \
            os.path.join(destination_directory, u"Season " + unicode(season))
        if not os.path.isdir(season_directory):
            os.makedirs(season_directory)

        return destination_directory, season_directory

    @staticmethod
    def get_max_season_and_episode_number(directory):
        u"""
        Figure out the maximum season and episode number currently existing
        in the given directory

        :param directory: The directory to parse
        :return:          The maximum season number, The maximum episode number
        """
        if not MetaDataManager.is_media_directory(directory, u"tv_series"):
            return 1, 0
        else:

            seasons = list(ifilter(
                lambda x: x.startswith(u"Season "), os.listdir(directory)
            ))

            if len(seasons) == 0:
                return 1, 0
            else:

                max_season = \
                    max(seasons, key=lambda x: int(x.split(u"Season ")[1]))
                max_episodes = 0

                ignore_flags = \
                    [u"OP ", u"ED ", u"OP-", u"ED-", u"OP_", u"ED_", u".", u"_"]
                for episode in os.listdir(os.path.join(directory, max_season)):
                    ignored = False
                    for flag in ignore_flags:
                        if episode.startswith(flag):
                            ignored = True

                    if not ignored:
                        max_episodes += 1

                return int(max_season.rsplit(u"Season ", 1)[1]), max_episodes

    @staticmethod
    def auto_rename(renaming_scheme, starting_episode,
                    packs):
        u"""
        Starts the auto-renaming process of only the newly aquired files

        :param renaming_scheme:  The renaming scheme to use
        :param starting_episode: The starting episode number
                                 (ignored if < length packs)
        :param packs:            The downloaded XDCC Packs
        :return:                 None
        """
        season_directory = os.path.dirname(packs[0].get_filepath())
        season_number = \
            int(os.path.basename(season_directory).rsplit(u"Season ", 1)[1])
        series_name = os.path.basename(os.path.dirname(season_directory))
        episode = starting_episode

        for pack in packs:

            TVEpisode(
                pack.get_filepath(),
                episode,
                season_number,
                series_name,
                renaming_scheme
            ).rename()
            episode += 1

    @staticmethod
    def get_preliminary_renaming_results(renaming_scheme,
                                         starting_episode,
                                         packs,
                                         season_number, series_name):
        u"""
        Checks how the packs will be renamed using the current scheme

        :param renaming_scheme:  The renaming scheme to use
        :param starting_episode: The starting episode
        :param packs:            The packs to use
        :param season_number:    The season currently
                                 associated with these packs
        :param series_name;      The series name currently
                                 associated with these packs
        :return:                 A list of the new episode names
        """
        new_names = []
        episode = starting_episode

        for pack in packs:
            new_names.append(TVEpisode(
                pack.get_filepath(),
                episode,
                season_number,
                series_name,
                renaming_scheme
            ).get_new_name())
            episode += 1

        return new_names
