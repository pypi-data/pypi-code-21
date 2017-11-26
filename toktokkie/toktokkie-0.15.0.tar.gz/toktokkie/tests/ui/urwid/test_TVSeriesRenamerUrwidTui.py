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
from toktokkie.ui.urwid.TVSeriesRenamerUrwidTui import TVSeriesRenamerUrwidTui
from toktokkie.utils.renaming.objects.RenamerConfirmation import \
    RenamerConfirmation


class LoopDummy(object):
    def draw_screen(self):
        pass


# noinspection PyTypeChecker
class UnitTests(unittest.TestCase):

    def setUp(self):
        self.tui = TVSeriesRenamerUrwidTui()
        self.tui.loop = LoopDummy()
        shutil.copytree(os.path.join(
            "toktokkie", "tests", "resources", "directories"), "temp_testing")

    def tearDown(self):
        self.tui.quit()
        shutil.rmtree("temp_testing")

    def test_parsing_non_media_directory_non_recursive(self):
        self.tui.dir_entry.set_edit_text("temp_testing")

        self.assertFalse(self.tui.recursive_check.get_state())
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(self.tui.confirmation, None)

    def test_parsing_media_directory_non_recursive(self):
        self.tui.dir_entry.set_edit_text(os.path.join(
            "temp_testing", "Game of Thrones"))

        self.assertFalse(self.tui.recursive_check.get_state())
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(len(self.tui.confirmation), 26)

    def test_parsing_recusively(self):

        for series in os.listdir("temp_testing"):
            if series not in ["Game of Thrones", "Re Zero"]:
                if os.path.isdir(os.path.join("temp_testing", series)):
                    shutil.rmtree(os.path.join("temp_testing", series))

        self.tui.dir_entry.set_edit_text("temp_testing")
        self.tui.recursive_check.set_state(True)

        self.assertTrue(self.tui.recursive_check.get_state())
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(len(self.tui.confirmation), 74)

    def test_parsing_while_renaming(self):

        self.tui.dir_entry.set_edit_text(os.path.join(
            "temp_testing", "Game of Thrones"))

        self.tui.renaming = True
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(self.tui.confirmation, None)

    def test_parsing_directory_with_extra_slashes(self):

        self.tui.dir_entry.set_edit_text(
            os.path.join("temp_testing", "Game of Thrones") +
            os.path.sep + os.path.sep)
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(len(self.tui.confirmation), 26)

    def test_parsing_directory_without_episodes(self):

        self.tui.dir_entry.set_edit_text(
            os.path.join("temp_testing", "ShowWithoutSeasons") +
            os.path.sep + os.path.sep)
        self.tui.search(None)

        while self.tui.parsing:
            pass

        self.assertEqual(self.tui.confirmation, None)

    def test_removing_selection(self):

        self.tui.confirmation = [
            RenamerConfirmation(TVEpisode(
                "test", 1, 1, "Test", PlexTvdbScheme)),
            RenamerConfirmation(TVEpisode(
                "test2", 2, 1, "Test", PlexTvdbScheme)),
            RenamerConfirmation(TVEpisode(
                "test", 3, 1, "Test", PlexTvdbScheme))]
        self.tui.refresh()
        self.assertEqual(len(self.tui.confirmation), 3)

        self.tui.middle_body[0].set_state(True)
        self.tui.middle_body[2].set_state(True)
        self.tui.remove_selection(None)

        self.assertEqual(len(self.tui.confirmation), 1)
        self.assertEqual(self.tui.confirmation[0].episode.episode_number, 2)

        self.tui.middle_body[0].set_state(True)
        self.tui.remove_selection(None)
        self.assertEqual(self.tui.confirmation, None)

    def test_renaming(self):
        self.test_parsing_media_directory_non_recursive()
        self.tui.confirm(None)

        while self.tui.renaming:
            pass

        self.assertTrue(os.path.isfile(os.path.join(
            "temp_testing", "Game of Thrones", "Season 1",
            "Game of Thrones - S01E01 - Winter Is Coming.mkv")))
        self.assertEqual(self.tui.confirmation, None)
        self.assertEqual(self.tui.renamer, None)

    def test_confirming_while_renaming(self):
        self.test_parsing_media_directory_non_recursive()
        self.tui.renaming = True
        self.tui.confirm(None)

        self.assertFalse(os.path.isfile(os.path.join(
            "temp_testing", "Game of Thrones", "Season 1",
            "Game of Thrones - S01E01 - Winter Is Coming.mkv")))

        self.tui.renaming = False
        self.tui.renamer = None
        self.tui.confirmation = None

        self.tui.confirm(None)
        self.assertFalse(os.path.isfile(os.path.join(
            "temp_testing", "Game of Thrones", "Season 1",
            "Game of Thrones - S01E01 - Winter Is Coming.mkv")))
