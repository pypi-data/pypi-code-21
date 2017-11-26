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
import re
from typing import List


class AutoSearcher(object):
    u"""
    Class that handles various types of automatic XDCC pack searching
    """

    search_patterns = {
        u"horriblesubs": u"[HorribleSubs] @search_name - @episode_zfill_2 "
                        u"[@quality_p_notation].mkv",
        u"sakura & c-w 4:3": u"@search_name - @episode_zfill_2 "
                            u"@quality_4:3_x_notation [Sakura][C-W]",
        u"amazon": u"@search_name - @episode_zfill_2 (Amazon).mkv",
        u"doki_h264": u"[Doki] @search_name - @episode_zfill_2 "
                     u"(@quality_x_notation h264 AAC)",
        u"doki_hevc": u"[Doki] @search_name - @episode_zfill_2 "
                     u"(@quality_x_notation HEVC AAC)",
        u"namibsun": u"@episode_raw_@search_name"
    }

    check_patterns = {
        u"horriblesubs": u"^\[HorribleSubs\] @search_name - @episode_zfill_2 "
                        u"\[@quality_p_notation\].mkv$",
        u"sakura & c-w 4:3": u"^@search_name - @episode_zfill_2 "
                            u"\[(x264-AC3-BD)@quality_4:3_x_notation\]"
                            u"\[Sakura\]\[C-W\]\[[0-9A-Z]+\].mkv$",
        u"amazon": u"^@search_name - @episode_zfill_2 \(Amazon\).mkv$",
        u"doki_h264": u"\[Doki\] @search_name - @episode_zfill_2 "
                     u"\(@quality_x_notation h264 AAC\) \[[0-9A-Z]+\].mkv",
        u"doki_hevc": u"\[Doki\] @search_name - @episode_zfill_2 "
                     u"\(@quality_x_notation HEVC AAC\) \[[0-9A-Z]+\].mkv",
        u"namibsun": u"^[0-9]+_test.txt$"
    }

    quality_patterns = {
        u"480p": {
            u"p_notation": u"480p",
            u"x_notation": u"848x480",
            u"4:3_x_notation": u"640x480"
        },
        u"720p": {
            u"p_notation": u"720p",
            u"x_notation": u"1280x720",
            u"4:3_x_notation": u"960x720"
        },
        u"1080p": {
            u"p_notation": u"1080p",
            u"x_notation": u"1920x1080",
            u"4:3_x_notation": u"1440x1080"
        }
    }

    @staticmethod
    def get_available_patterns():
        u"""
        :return: The currently available patterns
        """
        return list(AutoSearcher.search_patterns.keys())

    @staticmethod
    def generate_search_string(pattern, show, episode,
                               quality):
        u"""
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
    def matches_pattern(pattern, episode_name, show,
                        episode, quality):
        u"""
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
    def fill_in_pattern(pattern, show, episode, quality,
                        regex = False):
        u"""
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
            show = show.replace(u"[", u"\[")
            show = show.replace(u"]", u"\]")
            show = show.replace(u"(", u"\(")
            show = show.replace(u")", u"\)")

        pattern = pattern.replace(u"@search_name", show)
        pattern = pattern.replace(u"@episode_raw", unicode(episode))
        pattern = pattern.replace(u"@episode_zfill_2", unicode(episode).zfill(2))
        pattern = pattern.replace(
            u"@quality_p_notation",
            AutoSearcher.quality_patterns[quality][u"p_notation"]
        )
        pattern = pattern.replace(
            u"@quality_x_notation",
            AutoSearcher.quality_patterns[quality][u"x_notation"]
        )
        pattern = pattern.replace(
            u"@quality_4:3_x_notation",
            AutoSearcher.quality_patterns[quality][u"4:3_x_notation"]
        )
        return pattern
