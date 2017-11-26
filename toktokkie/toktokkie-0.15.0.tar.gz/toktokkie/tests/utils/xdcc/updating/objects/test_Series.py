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
from toktokkie.utils.xdcc.updating.objects.Series import Series
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.test_series = Series(
            "Updater Test Series", "test.txt", "1080p", "xdcc_servbot", 1,
            ["namibsun"], "Plex (TVDB)", "namibsun"
        )

    def tearDown(self):
        if os.path.isdir("Updater Test Series"):
            shutil.rmtree("Updater Test Series")

    def test_equality(self):
        self.assertTrue(self.test_series.equals(self.test_series))
        self.assertTrue(self.test_series.is_same(self.test_series.to_dict()))

    def test_setters_getters(self):
        self.test_series.set_naming_scheme("AAA")
        self.test_series.set_bot_preference("BBB")
        self.test_series.set_search_name("CCC")
        self.test_series.set_destination_directory("DDD")
        self.test_series.set_quality_identifier("EEE")
        self.test_series.set_season(2)
        self.test_series.set_search_engines(["FFF"])
        self.test_series.set_search_pattern("EEE")
        self.assertEqual(self.test_series.get_naming_scheme(), "AAA")
        self.assertEqual(self.test_series.get_bot_preference(), "BBB")
        self.assertEqual(self.test_series.get_search_name(), "CCC")
        self.assertEqual(self.test_series.get_destination_directory(), "DDD")
        self.assertEqual(self.test_series.get_quality_identifier(), "EEE")
        self.assertEqual(self.test_series.get_season(), 2)
        self.assertEqual(self.test_series.get_search_engines(), ["FFF"])
        self.assertEqual(self.test_series.get_search_pattern(), "EEE")

    def test_updating(self):
        self.test_series.update()

        season_directory = os.path.join("Updater Test Series", "Season 1")

        self.assertTrue(
            MetaDataManager.is_media_directory("Updater Test Series"))
        self.assertTrue(os.path.isdir(season_directory))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory,
            "Updater Test Series - S01E01 - Episode 1.txt"
        )))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory,
            "Updater Test Series - S01E02 - Episode 2.txt"
        )))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory,
            "Updater Test Series - S01E03 - Episode 3.txt"
        )))

        self.test_series.update(verbose=True)

        self.assertTrue(MetaDataManager.is_media_directory(
            "Updater Test Series"
        ))
        self.assertTrue(os.path.isdir(season_directory))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory, "Updater Test Series - S01E01 - Episode 1.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory, "Updater Test Series - S01E02 - Episode 2.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            season_directory, "Updater Test Series - S01E03 - Episode 3.txt")))

    def test_search_for_episodes_where_bot_does_not_match(self):
        self.test_series.set_bot_preference("Not A Bot")
        self.assertEqual(self.test_series.search_for_episode(1), None)
