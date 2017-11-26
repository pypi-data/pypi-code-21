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
import shutil
import unittest
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode
from toktokkie.utils.renaming.schemes.PlexTvdbScheme import PlexTvdbScheme


class TVEpisodeUnitTests(unittest.TestCase):

    def setUp(self):
        os.makedirs("temp_testing")
        with open(os.path.join("temp_testing", "episode_file"), 'w'):
            pass

    def tearDown(self):
        shutil.rmtree("temp_testing")

    def test_renaming(self):
        episode = TVEpisode(
            os.path.join("temp_testing", "episode_file"),
            1, 1, "Game of Thrones", PlexTvdbScheme
        )
        self.assertTrue(os.path.isfile(
            os.path.join("temp_testing", "episode_file"))
        )
        episode.rename()
        self.assertFalse(os.path.isfile(
            os.path.join("temp_testing", "episode_file"))
        )
        self.assertTrue(os.path.isfile(os.path.join(
            "temp_testing", "Game of Thrones - S01E01 - Winter Is Coming"
        )))

    def test_already_correct_name(self):
        self.test_renaming()
        episode = TVEpisode(
            os.path.join(
                "temp_testing", "Game of Thrones - S01E01 - Winter Is Coming"
            ),
            1, 1, "Game of Thrones", PlexTvdbScheme
        )
        episode.rename()
        self.assertFalse(os.path.isfile(
            os.path.join("temp_testing", "episode_file")
        ))
        self.assertTrue(os.path.isfile(
            os.path.join(
                "temp_testing", "Game of Thrones - S01E01 - Winter Is Coming"
            )
        ))
