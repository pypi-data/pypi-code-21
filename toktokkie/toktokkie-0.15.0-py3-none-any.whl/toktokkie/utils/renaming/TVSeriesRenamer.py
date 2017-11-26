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
from typing import List
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from toktokkie.utils.renaming.schemes.GenericScheme import GenericScheme
from toktokkie.utils.renaming.objects.RenamerConfirmation import \
    RenamerConfirmation


class TVSeriesRenamer(object):
    """
    Class that handles the renaming of episode files using thetvdb.com
    and a exchangeable naming schemes
    """

    def __init__(self, directory: str, naming_scheme: GenericScheme,
                 recursive: bool = False) -> None:
        """
        Constructor of the Renamer class.
        It stores the directory path to the class variable
        reserved for it and parses it.

        If the directory does not contain valid episodes,
        the self.episodes variable will remain an empty array

        :param directory: the directory to be used
        :param recursive: Flag to recursively check the directory
                          for episode files
        """
        # Local Variables
        self.episodes = []
        self.confirmed = False
        self.naming_scheme = naming_scheme

        if recursive:
            directories = MetaDataManager.find_recursive_media_directories(
                directory, media_type="tv_series")
        elif MetaDataManager.is_media_directory(
                directory, media_type="tv_series"):
            directories = [directory]
        else:
            return

        self.__add_directory_contents__(directories)

    def __add_directory_contents__(self, directories: List[str]) -> None:
        """
        Add the content of a list of directories directory
        to the internal Episode list

        :param directories: the directories to be parsed for episode content
        :return:            None
        """
        for directory in directories:

            show_name = os.path.basename(directory)
            if not show_name:
                show_name = os.path.dirname(directory)

            seasons = os.listdir(directory)
            specials = []

            for season in seasons:

                season_path = os.path.join(directory, season)

                # Skip over .meta directory and any loose files
                if season == ".meta" or not os.path.isdir(season_path):
                    continue

                # If the season directory's name does not start with "Season",
                # add this subdirectory to the list of special seasons
                if not season.lower().startswith("season"):
                    specials.append(season_path)
                else:
                    season_number = int(season.lower().split("season ")[1])
                    self.__add_season_to_episodes__(
                        season_path, season_number, show_name
                    )

            # Add the special episodes to the Episode list
            self.__add_specials_to_episodes__(specials, show_name)

    def __add_season_to_episodes__(self, season_directory: str,
                                   season_number: int, show_name: str) -> None:
        """
        Adds a 'season' subdirectory's content to the internal Episode List

        :param season_directory: The season directory path to be parsed
        :param season_number:    The season number of the season to be parsed
        :param show_name:        The show name associated with this season
        :return:                 None
        """

        # get the episode file names and sort them alphabetically
        episodes = os.listdir(season_directory)
        episodes.sort(key=lambda x: x.lower())
        episode_number = 1

        for episode in episodes:
            # We don't want to rename openings and endings,
            # marked with 'OP' or 'ED' with a space afterwards
            # We also ignore hidden files starting with a '.'
            # and files starting with '_'
            ignore_flags = ["OP ", "ED ", "OP-", "ED-", "OP_", "ED_", ".", "_"]
            ignored = False
            for flag in ignore_flags:
                if episode.startswith(flag):
                    ignored = True
            if ignored:
                continue

            episode_path = os.path.join(season_directory, episode)
            self.episodes.append(TVEpisode(
                episode_path,
                episode_number,
                season_number,
                show_name,
                self.naming_scheme
            ))
            episode_number += 1

    def __add_specials_to_episodes__(self,
                                     list_of_special_directories: List[str],
                                     show_name: str) -> None:
        """
        Adds all special episodes like OVAs, Movies, etc. to the internal
        Episode list.

        :param list_of_special_directories: List of paths to the special season
                                            subdirectories
        :param show_name:                   The show name associated
                                            with these special seasons
        :return:                            None
        """
        special_episodes = []

        for special_season in list_of_special_directories:
            for episode in os.listdir(special_season):
                ignore_flags = \
                    ["OP ", "ED ", "OP-", "ED-", "OP_", "ED_", ".", "_"]
                ignored = False
                for flag in ignore_flags:
                    if episode.startswith(flag):
                        ignored = True
                if ignored:
                    continue

                special_episodes.append(os.path.join(special_season, episode))

        # Sort by filename
        special_episodes.sort(key=lambda x: os.path.basename(x).lower())

        special_episode_number = 1
        for special_episode in special_episodes:

            # Use season number 0 to specify that this is
            # part of a special season
            self.episodes.append(TVEpisode(
                special_episode,
                special_episode_number,
                0,
                show_name,
                self.naming_scheme
            ))
            special_episode_number += 1

    def request_confirmation(self) -> List[RenamerConfirmation]:
        """
        Wraps all episodes in the Episode list in RenamerConfirmation objects
        to enable a manual approval process for the renaming by the user

        :return: the confirmation prompt as list of RenamerConfirmation objects
        """
        confirmation = []
        for episode in self.episodes:
            confirmation.append(RenamerConfirmation(episode))
        return confirmation

    def confirm(self, confirmation: List[RenamerConfirmation]) -> None:
        """
        Confirms the rename process by getting the previously returned list of
        RenamerConfirmations and checking their status.
        Only confirmed objects will be put back into the episode list

        :param confirmation: the list of RenamerConfirmation objects previously
                             sent out by request_confirmation
        :return              None
        """
        # Clear the episode list
        self.episodes = []

        for item in confirmation:
            if item.confirmed:
                self.episodes.append(item.episode)

        self.confirmed = True

    def start_rename(self, noconfirm: bool = False) -> bool:
        """
        Renames all episodes in the Episode List
        Normally, this method requires that the selection
        has been manually approved by the user
        using request_confirmation() and confirm(). However,
        this may be bypassed by passing the noconfirm flag as 'True'

        :param noconfirm: Can be used to bypass confirming.
        :return:          True, if the renaming was successful, else False.
                          The renaming may fail if the user did not confirm()
                          beforehand and the noconfirm flag was not set
        """
        # If the result has not been confirmed before, return False
        # Do not return False if the noconfirm flag has been set though.
        if not self.confirmed and not noconfirm:
            return False

        for episode in self.episodes:
            episode.rename()

        return True
