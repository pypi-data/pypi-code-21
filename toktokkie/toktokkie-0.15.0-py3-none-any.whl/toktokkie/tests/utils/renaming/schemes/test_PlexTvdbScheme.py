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
from toktokkie.utils.renaming.schemes.PlexTvdbScheme import PlexTvdbScheme


class PlexTvdbSchemeUnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor_and_name_generator(self):
        scheme = PlexTvdbScheme("Game of Thrones", 1, 1)
        self.assertEqual(scheme.generate_episode_name(),
                         "Game of Thrones - S01E01 - Winter Is Coming")
        scheme = PlexTvdbScheme("Game of Thrones", 0, 10)
        self.assertEqual(scheme.generate_episode_name(),
                         "Game of Thrones - S00E10 - "
                         "The Politics of Power A Look Back at Season 3")
        scheme = PlexTvdbScheme("Game of Thrones", 1, -1)
        self.assertEqual(scheme.generate_episode_name(),
                         "Game of Thrones - S01E-01 - Episode -1")
        scheme = PlexTvdbScheme("Game of Thrones", -1, 100)
        self.assertEqual(scheme.generate_episode_name(),
                         "Game of Thrones - S-01E100 - Episode 100")
        scheme = PlexTvdbScheme("blargoblap", 1, 1)
        self.assertEqual(scheme.generate_episode_name(),
                         "blargoblap - S01E01 - Episode 1")
