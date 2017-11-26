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
import unittest
from toktokkie.utils.xdcc.updating.AutoSearcher import AutoSearcher


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pattern_passing(self):
        self.assertLess(1, len(AutoSearcher.get_available_patterns()))

    def test_generating_search_strings(self):
        self.assertEqual(
            AutoSearcher.generate_search_string(
                u"horriblesubs", u"One-Punch Man", 1, u"720p"
            ),
            u"[HorribleSubs] One-Punch Man - 01 [720p].mkv"
        )
        self.assertEqual(
            AutoSearcher.generate_search_string(
                u"horriblesubs", u"One-Punch Man", 11, u"1080p"
            ),
            u"[HorribleSubs] One-Punch Man - 11 [1080p].mkv"
        )

    def test_pattern_matcher(self):

        episode_name = AutoSearcher.generate_search_string(
            u"horriblesubs", u"One-Punch Man", 5, u"480p"
        )
        self.assertTrue(AutoSearcher.matches_pattern(
            u"horriblesubs", episode_name, u"One-Punch Man", 5, u"480p")
        )

    def test_doki_search_string(self):

        search = u"[Doki] Saenai Heroine no Sodatekata Flat - " \
                 u"01 (1280x720 h264 AAC) [07EE0E22].mkv"
        show = u"Saenai Heroine no Sodatekata Flat"
        generated = \
            AutoSearcher.generate_search_string(u"doki_h264", show, 1, u"720p")

        self.assertTrue(search.startswith(generated))
        self.assertTrue(AutoSearcher.matches_pattern(
            u"doki_h264", search, show, 1, u"720p"
        ))
