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
import os
from typing import List, Dict
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.pack_searchers.PackSearcher import PackSearcher
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode
from toktokkie.utils.xdcc.updating.AutoSearcher import AutoSearcher
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager
from xdcc_dl.xdcc.MultipleServerDownloader import MultipleServerDownloader


class Series(object):
    """
    Class that models a Series for the XDCC Updater. It is essentially a light
    wrapper around a dictionary, which can be stored as JSON data
    """

    def __init__(self, destination_directory: str, search_name: str,
                 quality_identifier: str, bot_preference: str, season: int,
                 search_engines: List[str], naming_scheme: str,
                 search_pattern: str, episode_offset: int = 0) -> None:
        """
        Creates a new Series object

        :param destination_directory: The destination directory to which this
                                      series points to
        :param search_name:           The name used to identify the episodes
                                      using XDCC search engines
        :param quality_identifier:    The quality specifier
        :param bot_preference:        The bot from which to
                                      fetch the episodes from
        :param season:                The season of the series in use
        :param search_engines:        The search engines to use
        :param naming_scheme:         The naming scheme to use
        :param search_pattern:        The search pattern to use
        :param episode_offset:        An offset for the episode counter,
                                      for seasons that start with an episode
                                      other than 1
        """

        self.data = {
            "destination_directory": destination_directory,
            "search_name": search_name,
            "quality_identifier": quality_identifier,
            "bot_preference": bot_preference,
            "season": season,
            "search_engines": search_engines,
            "naming_scheme": naming_scheme,
            "search_pattern": search_pattern,
            "episode_offset": episode_offset
        }

    def to_dict(self) -> Dict[str, str or int or List[str]]:
        """
        Turns the data into a dictionary

        :return: The data as dictionary
        """
        return self.data

    def is_same(self, data: Dict[str, str or int or List[str]]) -> bool:
        """
        Checks if this show is equal to another dictionary

        :param data: The data to check
        :return:     true if it is the same, false otherwise
        """
        equal = True
        for key in data:
            if data[key] != self.data[key]:
                equal = False
        return equal

    # noinspection PyUnresolvedReferences
    def equals(self, series: "__class__") -> bool:
        """
        Checks if a series object is equal to this one

        :param series: The series to compare to
        :return:       True if the two series are the same, False otherwise
        """
        equal = True
        equal = equal and series.get_bot_preference() == \
            self.get_bot_preference()
        equal = equal and series.get_destination_directory() == \
            self.get_destination_directory()
        equal = equal and series.get_naming_scheme() == \
            self.get_naming_scheme()
        equal = equal and series.get_quality_identifier() == \
            self.get_quality_identifier()
        equal = equal and series.get_season() == \
            self.get_season()
        equal = equal and series.get_search_pattern() == \
            self.get_search_pattern()
        equal = equal and series.get_search_name() == \
            self.get_search_name()
        equal = equal and series.get_naming_scheme() == \
            self.get_naming_scheme()
        equal = equal and series.get_episode_offset() == \
            self.get_episode_offset()
        return equal

    def update(self, verbose: bool = False) -> None:
        """
        Updates the Series

        :param verbose: Sets the verbosity of the update process
        :return: None
        """
        print(self.get_search_name())

        MetaDataManager.generate_media_directory(
            self.data["destination_directory"], media_type="tv_series"
        )
        season_dir = os.path.join(
            self.data["destination_directory"],
            "Season " + str(self.data["season"])
        )

        if not os.path.isdir(season_dir):
            os.makedirs(season_dir)

        self.check_existing_episode_names(season_dir)
        self.download_new_episodes(season_dir, verbose)

    def check_existing_episode_names(self, season_dir: str) -> None:
        """
        Checks the already existing episodes if they still
        have the most up-to-date episode names

        :param season_dir: The season directory to check
        :return:           None
        """
        show_name = os.path.basename(self.data["destination_directory"])

        for i, episode in enumerate(sorted(os.listdir(season_dir))):
            episode_file = os.path.join(season_dir, episode)

            # + self.data["episode_offset"]  I think this is actually wrong
            episode_number = i + 1

            tv_episode = TVEpisode(
                episode_file, episode_number, self.data["season"], show_name,
                SchemeManager.get_scheme_from_scheme_name(
                    self.data["naming_scheme"]
                )
            )
            tv_episode.rename()

    def download_new_episodes(self, season_dir: str, verbose: bool = False) \
            -> None:
        """
        Downloads new episodes found using the XDCC pack searchers

        :param season_dir: The Season directory
                           in which the files will be stored
        :param verbose:    Sets the verbosity of the download output
        :return:           None
        """
        first_non_existing_episode = \
            len(os.listdir(season_dir)) + 1 + self.data["episode_offset"]
        episode_to_check = first_non_existing_episode

        download_queue = []
        search_result = self.search_for_episode(episode_to_check)

        while search_result is not None:
            download_queue.append(search_result)
            episode_to_check += 1
            search_result = self.search_for_episode(episode_to_check)

        for i, pack in enumerate(download_queue):
            pack.set_directory(season_dir)
            pack.set_filename(
                "xdcc_updater_" +
                str(i).zfill(int(len(download_queue) / 10) + 1),
                override=True
            )
            pack.set_original_filename(
                pack.original_filename.replace("'", "_")
            )  # Fix for incorrect file names

        verbosity = 2 if verbose else 1
        MultipleServerDownloader("random", verbosity).download(download_queue)

        show_name = os.path.basename(self.data["destination_directory"])
        renaming_scheme = SchemeManager.get_scheme_from_scheme_name(
            self.data["naming_scheme"]
        )
        episode_number = first_non_existing_episode

        for pack in download_queue:
            TVEpisode(
                pack.get_filepath(),
                episode_number,
                self.data["season"],
                show_name,
                renaming_scheme
            ).rename()
            episode_number += 1

    def search_for_episode(self, episode: int) -> XDCCPack or None:
        """
        Searches for a specific episode, and returns the resultant XDCC Pack

        :param episode: The episode to search for
        :return:        The XDCCPack, or None if no episode pack was found
        """
        search_query = AutoSearcher.generate_search_string(
            self.data["search_pattern"], self.data["search_name"], episode,
            self.data["quality_identifier"])

        search = PackSearcher(self.data["search_engines"]).search(search_query)

        for result in search:
            if result.get_bot() == self.data["bot_preference"] \
                    and AutoSearcher.matches_pattern(
                        self.data["search_pattern"], result.get_filename(),
                        self.data["search_name"], episode,
                        self.data["quality_identifier"]):

                return result

        return None

    def get_destination_directory(self) -> str:
        """
        :return: The destination directory
        """
        return self.data["destination_directory"]

    def get_search_name(self) -> str:
        """
        :return: The search name
        """
        return self.data["search_name"]

    def get_quality_identifier(self) -> str:
        """
        :return: The quality identifier
        """
        return self.data["quality_identifier"]

    def get_bot_preference(self) -> str:
        """
        :return: The bot preference
        """
        return self.data["bot_preference"]

    def get_season(self) -> int:
        """
        :return: The season number
        """
        return self.data["season"]

    def get_search_engines(self) -> List[str]:
        """
        :return: The search engines
        """
        return self.data["search_engines"]

    def get_naming_scheme(self) -> str:
        """
        :return: The naming scheme
        """
        return self.data["naming_scheme"]

    def get_search_pattern(self) -> str:
        """
        :return: The search pattern
        """
        return self.data["search_pattern"]

    def get_episode_offset(self) -> int:
        """
        :return: The episode offset
        """
        return self.data["episode_offset"]

    def set_destination_directory(self, directory: str) -> None:
        """
        :param directory: The destination directory
        :return:          None
        """
        self.data["destination_directory"] = directory

    def set_search_name(self, name: str) -> None:
        """
        :param name: The search name
        :return:     None
        """
        self.data["search_name"] = name

    def set_quality_identifier(self, quality: str) -> None:
        """
        :param quality: The Quality identifier
        :return:        None
        """
        self.data["quality_identifier"] = quality

    def set_bot_preference(self, bot: str) -> None:
        """
        :param bot: The bot preference
        :return:    None
        """
        self.data["bot_preference"] = bot

    def set_season(self, season: int) -> None:
        """
        :param season: The season
        :return:       None
        """
        self.data["season"] = season

    def set_search_engines(self, search_engines: List[str]) -> None:
        """
        :param search_engines: The search engines
        :return:               None
        """
        self.data["search_engines"] = search_engines

    def set_naming_scheme(self, naming_scheme: str) -> None:
        """
        :param naming_scheme: The naming scheme
        :return:              None
        """
        self.data["naming_scheme"] = naming_scheme

    def set_search_pattern(self, pattern: str) -> None:
        """
        :param pattern: The pattern
        :return:        None
        """
        self.data["search_pattern"] = pattern

    def set_episode_offset(self, episode_offset: int) -> None:
        """
        :param episode_offset: The episode offset
        :return: None
        """
        self.data["episode_offset"] = episode_offset


def from_dict(data: Dict[str, str or int or List[str]]) -> Series:
    """
    Creates a Series object from a dictionary

    :param data: The data to turn into a Series object
    :return:     The Series object
    """
    episode_offset = 0 \
        if "episode_offset" not in data.keys() \
        else data["episode_offset"]
    return Series(
        data["destination_directory"], data["search_name"],
        data["quality_identifier"], data["bot_preference"], data["season"],
        data["search_engines"], data["naming_scheme"], data["search_pattern"],
        episode_offset
    )
