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
                "horriblesubs", "One-Punch Man", 1, "720p"
            ),
            "[HorribleSubs] One-Punch Man - 01 [720p].mkv"
        )
        self.assertEqual(
            AutoSearcher.generate_search_string(
                "horriblesubs", "One-Punch Man", 11, "1080p"
            ),
            "[HorribleSubs] One-Punch Man - 11 [1080p].mkv"
        )

    def test_pattern_matcher(self):

        episode_name = AutoSearcher.generate_search_string(
            "horriblesubs", "One-Punch Man", 5, "480p"
        )
        self.assertTrue(AutoSearcher.matches_pattern(
            "horriblesubs", episode_name, "One-Punch Man", 5, "480p")
        )

    def test_doki_search_string(self):

        search = "[Doki] Saenai Heroine no Sodatekata Flat - " \
                 "01 (1280x720 h264 AAC) [07EE0E22].mkv"
        show = "Saenai Heroine no Sodatekata Flat"
        generated = \
            AutoSearcher.generate_search_string("doki_h264", show, 1, "720p")

        self.assertTrue(search.startswith(generated))
        self.assertTrue(AutoSearcher.matches_pattern(
            "doki_h264", search, show, 1, "720p"
        ))
