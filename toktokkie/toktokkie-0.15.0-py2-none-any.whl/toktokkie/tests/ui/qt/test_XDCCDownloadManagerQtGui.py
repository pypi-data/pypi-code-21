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
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication
    from toktokkie.ui.qt.XDCCDownloadManagerQtGui import \
        XDCCDownloadManagerQtGui
except ImportError:
    Qt = QTest = XDCCDownloadManagerQtGui = QApplication = None

import os
import sys
import time
import shutil
import unittest
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.IrcServer import IrcServer
from toktokkie.utils.iconizing.Iconizer import Iconizer
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager, GenericProcedure


class DummySignal(object):

    def __init__(self, method):
        self.method = method

    def emit(self, *args):
        self.method(*args)


class UnitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        if QApplication is None:
            raise unittest.SkipTest(u"Skipping on import error")

        sys.argv = [sys.argv[0], u"-platform", u"minimal"]
        cls.app = QApplication(sys.argv)

    def setUp(self):
        sys.argv = [sys.argv[0], u"-platform", u"minimal"]
        self.form = XDCCDownloadManagerQtGui()

        self.form.spinner_updater_signal = \
            DummySignal(lambda x, y: x.setText(y))
        self.form.download_queue_refresh_signal = \
            DummySignal(self.form.refresh_download_queue)
        self.form.progress_updater_signal = \
            DummySignal(self.form.update_progress)
        self.form.show_download_completed_signal = \
            DummySignal(self.form.show_download_completed_message_box)

        shutil.copytree(
            os.path.join(u"toktokkie", u"tests", u"resources", u"directories"),
            u"temp_testing"
        )

    def tearDown(self):
        self.form.closeEvent(None)
        self.form.destroy()
        Iconizer().reverse_iconization(u"temp_testing")
        shutil.rmtree(u"temp_testing")

    def test_searching(self):
        self.form.search_term_edit.setText(u"1_test.txt")
        self.form.search_engine_combo_box.setCurrentText(u"namibsun")
        QTest.mouseClick(self.form.search_button, Qt.LeftButton)

        while self.form.searching:
            pass

        self.assertEqual(1, self.form.search_result_list.topLevelItemCount())
        self.form.search_result_list.selectAll()
        name = self.form.search_result_list.itemFromIndex(
            self.form.search_result_list.selectedIndexes()[0]).text(4)
        self.assertEqual(name, u"1_test.txt")

    def test_search_while_searching(self):

        self.form.search_term_edit.setText(u"1_test.txt")
        self.form.search_engine_combo_box.setCurrentText(u"All")
        QTest.mouseClick(self.form.search_button, Qt.LeftButton)

        time.sleep(0.5)

        self.form.search_term_edit.setText(u"2_test.txt")
        self.form.search_engine_combo_box.setCurrentText(u"namibsun")
        QTest.mouseClick(self.form.search_button, Qt.LeftButton)

        while self.form.searching:
            pass

        self.assertEqual(1, self.form.search_result_list.topLevelItemCount())
        self.form.search_result_list.selectAll()
        name = self.form.search_result_list.itemFromIndex(
            self.form.search_result_list.selectedIndexes()[0]).text(4)
        self.assertEqual(name, u"1_test.txt")

    def test_setting_directory(self):
        self.form.directory_edit.setText(
            os.path.join(u"temp_testing", u"Game of Thrones"))
        self.assertEqual(
            self.form.directory_edit.text(),
            os.path.join(u"temp_testing", u"Game of Thrones")
        )
        self.assertEqual(
            self.form.show_name_edit.text(),
            u"Game of Thrones"
        )
        self.assertEqual(
            self.form.episode_spin_box.value(),
            11
        )
        self.assertEqual(self.form.season_spin_box.value(), 2)

    def test_adding_episode_to_queue(self):
        self.test_searching()
        self.test_setting_directory()

        self.form.search_result_list.selectAll()
        QTest.mouseClick(self.form.add_to_queue_button, Qt.LeftButton)

        self.assertEqual(
            0,
            len(self.form.search_result_list.selectedIndexes())
        )
        self.assertEqual(1, self.form.download_queue.count())
        self.assertEqual(
            self.form.download_queue_list[0].get_filename(),
            u"1_test.txt"
        )

        self.form.download_queue.selectAll()
        episode_name = self.form.download_queue.itemFromIndex(
            self.form.download_queue.selectedIndexes()[0]).text()
        self.assertEqual(u"Game of Thrones - S02E11 - Episode 11", episode_name)

    def test_removing_packs_from_queue(self):
        self.test_adding_episode_to_queue()
        QTest.mouseClick(self.form.remove_from_queue_button, Qt.LeftButton)

        self.assertEqual(0, self.form.download_queue.count())

    def test_disabling_auto_renaming(self):
        self.test_adding_episode_to_queue()
        QTest.mouseClick(self.form.auto_rename_check, Qt.LeftButton)

        self.form.download_queue.selectAll()
        episode_name = self.form.download_queue.itemFromIndex(
            self.form.download_queue.selectedIndexes()[0]).text()
        self.assertEqual(u"1_test.txt", episode_name)

    def test_download_with_iconizing_and_auto_renaming(self):
        self.test_adding_episode_to_queue()
        self.test_setting_directory()
        QTest.mouseClick(self.form.download_button, Qt.LeftButton)

        while self.form.downloading:
            pass

        self.assertTrue(os.path.isfile(
            os.path.join(u"temp_testing", u"Game of Thrones", u"Season 2",
                         u"Game of Thrones - S02E11 - Episode 11.txt")
        ))
        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:
            self.assertNotEqual(procedure.get_icon_file(os.path.join(
                u"temp_testing", u"Game of Thrones"
            )), None)

    def test_download_without_iconizing_and_auto_renaming(self):
        self.test_adding_episode_to_queue()
        self.test_setting_directory()

        self.form.auto_rename_check.nextCheckState()
        self.form.iconize_check.nextCheckState()

        self.assertFalse(self.form.auto_rename_check.checkState())
        self.assertFalse(self.form.iconize_check.checkState())

        QTest.mouseClick(self.form.download_button, Qt.LeftButton)

        while self.form.downloading:
            pass

        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2", u"1_test.txt")))
        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:
            self.assertEqual(procedure.get_icon_file(os.path.join(
                u"temp_testing", u"Game of Thrones")), None)

    def test_download_while_downloading(self):
        self.test_adding_episode_to_queue()
        self.test_setting_directory()

        self.form.downloading = True
        QTest.mouseClick(self.form.download_button, Qt.LeftButton)

        self.assertFalse(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E11 - Episode 11.txt"
        )))
        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:
            self.assertEqual(procedure.get_icon_file(os.path.join(
                u"temp_testing", u"Game of Thrones")), None)

    def test_moving_queue_items(self):
        self.form.download_queue_list = [
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1),
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)
        ]

        self.form.refresh_download_queue()
        self.assertEqual(self.form.download_queue.count(), 3)
        self.form.download_queue.selectAll()

        QTest.mouseClick(self.form.move_up_button, Qt.LeftButton)
        self.assertEqual(len(self.form.download_queue.selectedIndexes()), 0)

        self.form.download_queue.selectAll()
        QTest.mouseClick(self.form.move_down_button, Qt.LeftButton)

        self.form.download_queue.selectAll()
