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
import shutil
import unittest
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.IrcServer import IrcServer
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from toktokkie.utils.xdcc.XDCCDownloadManager import XDCCDownloadManager
from toktokkie.utils.renaming.schemes.PlexTvdbScheme import PlexTvdbScheme


class UnitTests(unittest.TestCase):

    def setUp(self):
        shutil.copytree(
            u"toktokkie/tests/resources/directories",
            u"temp_testing"
        )
        self.game_of_thrones = os.path.join(u"temp_testing", u"Game of Thrones")

    def tearDown(self):
        shutil.rmtree(u"temp_testing")

    def test_download_preparer(self):

        destination_dir, season_dir = XDCCDownloadManager.prepare_directory(
            self.game_of_thrones, u"Game of Thrones", 1)
        self.assertEqual(destination_dir, self.game_of_thrones)
        self.assertEqual(
            season_dir,
            os.path.join(self.game_of_thrones, u"Season 1")
        )
        self.assertTrue(MetaDataManager.is_media_directory(
            self.game_of_thrones, u"tv_series"))

    def test_download_preparer_with_non_matching_show_name(self):

        self.assertFalse(MetaDataManager.is_media_directory(
            os.path.join(self.game_of_thrones, u"Not Game of Thrones")))
        destination_dir, season_dir = XDCCDownloadManager.prepare_directory(
            self.game_of_thrones, u"Not Game of Thrones", 1)

        self.assertEqual(
            destination_dir,
            os.path.join(self.game_of_thrones, u"Not Game of Thrones")
        )
        self.assertEqual(season_dir, os.path.join(destination_dir, u"Season 1"))
        self.assertTrue(MetaDataManager.is_media_directory(
            destination_dir, u"tv_series"))

    def test_retrieving_max_episode_and_season_numbers(self):

        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                self.game_of_thrones
            )
        self.assertEqual(season, 2)
        self.assertEqual(episode, 10)

        shutil.rmtree(os.path.join(self.game_of_thrones, u"Season 2"))

        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                self.game_of_thrones
            )
        self.assertEqual(season, 1)
        self.assertEqual(episode, 11)

    def test_retrieving_max_epi_and_season_numbers_on_non_tv_series_dir(self):

        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                os.path.join(u"temp_testing", u"OtherMedia")
            )

        self.assertEqual(season, 1)
        self.assertEqual(episode, 0)

    def test_retrieving_max_epi_and_season_numbers_on_non_media_dir(self):
        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                os.path.join(u"temp_testing", u"NotAShow")
            )

        self.assertEqual(season, 1)
        self.assertEqual(episode, 0)

    def test_retrieving_max_epi_and_season_numbers_on_show_without_seas(self):

        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                os.path.join(u"temp_testing", u"ShowWithoutSeasons")
            )

        self.assertEqual(season, 1)
        self.assertEqual(episode, 0)

    def test_auto_renaming(self):

        packs = [XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1),
                 XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
                 XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)]

        packs[0].set_filename(u"Episode 01.mkv")
        packs[1].set_filename(u"Episode 02.mkv")
        packs[2].set_filename(u"Episode 03.mkv")

        for pack in packs:
            pack.set_directory(os.path.join(self.game_of_thrones, u"Season 1"))

        XDCCDownloadManager.auto_rename(PlexTvdbScheme, 1, packs)

        self.assertTrue(os.path.isfile(os.path.join(
            self.game_of_thrones, u"Season 1",
            u"Game of Thrones - S01E01 - Winter Is Coming.mkv"
        )))
        self.assertTrue(os.path.isfile(os.path.join(
            self.game_of_thrones, u"Season 1",
            u"Game of Thrones - S01E02 - The Kingsroad.mkv"
        )))
        self.assertTrue(os.path.isfile(os.path.join(
            self.game_of_thrones, u"Season 1",
            u"Game of Thrones - S01E03 - Lord Snow.mkv"
        )))

    def test_preliminary_auto_renaming_results(self):

        packs = [XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1),
                 XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
                 XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)]

        results = XDCCDownloadManager.get_preliminary_renaming_results(
            PlexTvdbScheme, 1, packs, 1, u"Game of Thrones")

        self.assertEqual(results[0],
                         u"Game of Thrones - S01E01 - Winter Is Coming")
        self.assertEqual(results[1],
                         u"Game of Thrones - S01E02 - The Kingsroad")
        self.assertEqual(results[2],
                         u"Game of Thrones - S01E03 - Lord Snow")
