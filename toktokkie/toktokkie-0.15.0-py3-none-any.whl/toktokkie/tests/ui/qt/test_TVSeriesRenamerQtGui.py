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
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QLineEdit
    from toktokkie.ui.qt.TVSeriesRenamerQtGui import TVSeriesRenamerQtGui
except ImportError:
    Qt = QTest = QLineEdit = TVSeriesRenamerQtGui = QApplication = None

import os
import sys
import time
import shutil
import unittest
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode
from toktokkie.utils.renaming.schemes.PlexTvdbScheme import PlexTvdbScheme
from toktokkie.utils.renaming.objects.RenamerConfirmation import \
    RenamerConfirmation


class DummySignal(object):

    def __init__(self, method):
        self.method = method

    def emit(self, *args):
        self.method(*args)


class UnitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        if QApplication is None:
            raise unittest.SkipTest("Skipping on import error")

        sys.argv = [sys.argv[0], "-platform", "minimal"]
        cls.app = QApplication(sys.argv)

    def setUp(self):
        sys.argv = [sys.argv[0], "-platform", "minimal"]
        self.form = TVSeriesRenamerQtGui()

        self.form.populate_list_signal = DummySignal(self.form.populate_list)
        self.form.visibility_switcher_signal = \
            DummySignal(self.form.meta_warning_label.setVisible)
        self.form.spinner_updater_signal = \
            DummySignal(self.form.update_spinner_text)

        shutil.copytree(
            os.path.join("toktokkie", "tests", "resources", "directories"),
            "temp_testing"
        )

    def tearDown(self):
        self.form.closeEvent(None)
        self.form.destroy()
        shutil.rmtree("temp_testing")

    def test_directory_parsing_non_recursive_non_media_directory(self):

        self.assertFalse(self.form.recursive_check.checkState())
        self.assertTrue(self.form.meta_warning_label.isVisibleTo(self.form))
        self.form.directory_entry.setText("temp_testing")

        while self.form.parsing:
            pass

        self.assertEqual(self.form.rename_list.topLevelItemCount(), 0)
        self.assertTrue(self.form.meta_warning_label.isVisibleTo(self.form))

    def test_directory_parsing_non_recursive_media_directory(self):

        self.assertFalse(self.form.recursive_check.checkState())
        self.assertTrue(self.form.meta_warning_label.isVisibleTo(self.form))
        self.form.directory_entry.setText(
            os.path.join("temp_testing", "Game of Thrones")
        )

        while self.form.parsing:
            pass

        self.assertEqual(self.form.rename_list.topLevelItemCount(), 26)
        self.assertFalse(self.form.meta_warning_label.isVisibleTo(self.form))

    def test_directory_parsing_recursive(self):

        for series in os.listdir("temp_testing"):
            if series not in ["Game of Thrones", "Re Zero"]:
                if os.path.isdir(os.path.join("temp_testing", series)):
                    shutil.rmtree(os.path.join("temp_testing", series))

        self.form.recursive_check.nextCheckState()
        self.assertTrue(self.form.recursive_check.checkState())
        self.form.directory_entry.setText("temp_testing")

        while self.form.parsing:
            pass

        self.assertEqual(74, self.form.rename_list.topLevelItemCount())
        self.assertFalse(self.form.meta_warning_label.isVisibleTo(self.form))

    def test_remove_selection(self):
        self.form.confirmation = [
            RenamerConfirmation(
                TVEpisode("test", 1, 1, "Test", PlexTvdbScheme)),
            RenamerConfirmation(
                TVEpisode("test2", 1, 2, "Test", PlexTvdbScheme))
        ]
        self.form.populate_list()
        self.form.confirmation += [RenamerConfirmation(
            TVEpisode("test", 1, 3, "Test", PlexTvdbScheme)
        )]
        self.assertEqual(2, self.form.rename_list.topLevelItemCount())

        self.form.rename_list.selectAll()
        QTest.mouseClick(self.form.selection_remover_button, Qt.LeftButton)

        self.assertEqual(1, self.form.rename_list.topLevelItemCount())

    def test_renaming(self):
        self.form.directory_entry.setText(os.path.join(
            "temp_testing", "Game of Thrones"
        ))

        while self.form.parsing:
            pass

        previous_item_amount = self.form.rename_list.topLevelItemCount()
        QTest.mouseClick(self.form.confirm_button, Qt.LeftButton)

        while self.form.renaming:
            pass

        self.assertTrue(os.path.isfile(os.path.join(
            "temp_testing", "Game of Thrones", "Season 1",
            "Game of Thrones - S01E01 - Winter Is Coming.mkv"
        )))

        while self.form.parsing:
            pass

        self.assertEqual(
            previous_item_amount,
            self.form.rename_list.topLevelItemCount()
        )

    def test_parsing_directory_with_slash_at_end(self):

        self.form.directory_entry.setText(
            os.path.join("temp_testing", "Game of Thrones") + os.path.sep
        )

        while self.form.parsing:
            pass

        self.assertEqual(self.form.rename_list.topLevelItemCount(), 26)
        self.assertFalse(self.form.meta_warning_label.isVisibleTo(self.form))

    def test_cancelling_mid_parse(self):

        self.form.directory_entry.setText(
            os.path.join("temp_testing", "Game of Thrones")
        )

        while self.form.parser_id == 0:
            pass

        self.form.cancel()
        self.form.parser_thread.join(0)

        self.assertEqual(self.form.rename_list.topLevelItemCount(), 0)
        self.assertTrue(self.form.meta_warning_label.isVisibleTo(self.form))

    def test_canceling_while_renaming(self):
        self.form.parsing = True
        self.form.renaming = True
        self.form.cancel()
        self.assertTrue(self.form.parsing)

    def test_renaming_while_renaming(self):
        self.form.renaming = True
        self.form.confirm()

    def test_spinner(self):
        self.form.renaming = True
        self.form.parsing = True
        self.form.start_spinner("rename")
        self.form.start_spinner("parse")
        time.sleep(0.5)
        self.form.renaming = False
        self.form.parsing = False
        time.sleep(0.5)
