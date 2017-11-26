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
import re
from typing import List


class AutoSearcher(object):
    """
    Class that handles various types of automatic XDCC pack searching
    """

    search_patterns = {
        "horriblesubs": "[HorribleSubs] @search_name - @episode_zfill_2 "
                        "[@quality_p_notation].mkv",
        "sakura & c-w 4:3": "@search_name - @episode_zfill_2 "
                            "@quality_4:3_x_notation [Sakura][C-W]",
        "amazon": "@search_name - @episode_zfill_2 (Amazon).mkv",
        "doki_h264": "[Doki] @search_name - @episode_zfill_2 "
                     "(@quality_x_notation h264 AAC)",
        "doki_hevc": "[Doki] @search_name - @episode_zfill_2 "
                     "(@quality_x_notation HEVC AAC)",
        "namibsun": "@episode_raw_@search_name"
    }

    check_patterns = {
        "horriblesubs": "^\[HorribleSubs\] @search_name - @episode_zfill_2 "
                        "\[@quality_p_notation\].mkv$",
        "sakura & c-w 4:3": "^@search_name - @episode_zfill_2 "
                            "\[(x264-AC3-BD)@quality_4:3_x_notation\]"
                            "\[Sakura\]\[C-W\]\[[0-9A-Z]+\].mkv$",
        "amazon": "^@search_name - @episode_zfill_2 \(Amazon\).mkv$",
        "doki_h264": "\[Doki\] @search_name - @episode_zfill_2 "
                     "\(@quality_x_notation h264 AAC\) \[[0-9A-Z]+\].mkv",
        "doki_hevc": "\[Doki\] @search_name - @episode_zfill_2 "
                     "\(@quality_x_notation HEVC AAC\) \[[0-9A-Z]+\].mkv",
        "namibsun": "^[0-9]+_test.txt$"
    }

    quality_patterns = {
        "480p": {
            "p_notation": "480p",
            "x_notation": "848x480",
            "4:3_x_notation": "640x480"
        },
        "720p": {
            "p_notation": "720p",
            "x_notation": "1280x720",
            "4:3_x_notation": "960x720"
        },
        "1080p": {
            "p_notation": "1080p",
            "x_notation": "1920x1080",
            "4:3_x_notation": "1440x1080"
        }
    }

    @staticmethod
    def get_available_patterns() -> List[str]:
        """
        :return: The currently available patterns
        """
        return list(AutoSearcher.search_patterns.keys())

    @staticmethod
    def generate_search_string(pattern: str, show: str, episode: int,
                               quality: str) -> str:
        """
        Generates a search string from a given pattern
        and the provided information

        :param pattern: The pattern to use
        :param show:    The show's name
        :param episode: The episode to generate a string for
        :param quality: The quality of the episode to search for
        :return:        The search string
        """
        search_pattern = AutoSearcher.search_patterns[pattern]
        return AutoSearcher.fill_in_pattern(
            search_pattern, show, episode, quality
        )

    @staticmethod
    def matches_pattern(pattern: str, episode_name: str, show: str,
                        episode: int, quality: str) -> bool:
        """
        Checks if an episode name fits the specified pattern

        :param pattern:      The pattern identifier to check
        :param episode_name: The episode name to check (The entire file name)
        :param show:         The show to check against
        :param episode:      The episode to check against
        :param quality:      The quality to check against
        :return:             True if it matches, false otherwise
        """
        regex_pattern = AutoSearcher.check_patterns[pattern]
        regex = re.compile(AutoSearcher.fill_in_pattern(
            regex_pattern, show, episode, quality, regex=True)
        )
        return bool(re.search(regex, episode_name))

    @staticmethod
    def fill_in_pattern(pattern: str, show: str, episode: int, quality: str,
                        regex: bool = False) -> str:
        """
        Fills a pattern with the @ replacers

        :param pattern: The pattern to fill
        :param show:    The show to use
        :param episode: The episode to use
        :param quality: The quality to use
        :param regex:   Replaces any Regex characters in the input through
                        escaped ones
        :return:        The filled in pattern
        """
        if regex:
            show = show.replace("[", "\[")
            show = show.replace("]", "\]")
            show = show.replace("(", "\(")
            show = show.replace(")", "\)")

        pattern = pattern.replace("@search_name", show)
        pattern = pattern.replace("@episode_raw", str(episode))
        pattern = pattern.replace("@episode_zfill_2", str(episode).zfill(2))
        pattern = pattern.replace(
            "@quality_p_notation",
            AutoSearcher.quality_patterns[quality]["p_notation"]
        )
        pattern = pattern.replace(
            "@quality_x_notation",
            AutoSearcher.quality_patterns[quality]["x_notation"]
        )
        pattern = pattern.replace(
            "@quality_4:3_x_notation",
            AutoSearcher.quality_patterns[quality]["4:3_x_notation"]
        )
        return pattern
