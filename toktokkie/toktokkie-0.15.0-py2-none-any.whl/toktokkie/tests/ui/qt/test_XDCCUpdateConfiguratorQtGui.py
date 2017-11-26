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
    from PyQt5.QtWidgets import QApplication, QFileDialog
    from toktokkie.ui.qt.XDCCUpdateConfiguratorQtGui import \
        XDCCUpdateConfiguratorQtGui
except ImportError:
    Qt = QTest = QFileDialog = QApplication = XDCCUpdateConfiguratorQtGui = \
        None

import os
import sys
import shutil
import unittest
from toktokkie.utils.xdcc.updating.objects.Series import Series
from toktokkie.utils.xdcc.updating.JsonHandler import JsonHandler


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
        self.form = XDCCUpdateConfiguratorQtGui()
        shutil.copytree(
            os.path.join(u"toktokkie", u"tests", u"resources", u"json"),
            u"json_test"
        )

    def tearDown(self):
        self.form.closeEvent(None)
        self.form.destroy()
        shutil.rmtree(u"json_test")
        if os.path.isfile(u"a_json_file.json"):
            os.remove(u"a_json_file.json")

    def test_loading_json(self):

        old_handler = self.form.json_handler

        # noinspection PyUnusedLocal,PyUnusedLocal,PyShadowingBuiltins
        def browse_file(a, b, filter=u""):
            return [os.path.join(u"json_test", u"updater.json")]

        QFileDialog.getOpenFileName = browse_file

        QTest.mouseClick(self.form.load_button, Qt.LeftButton)

        self.assertNotEqual(old_handler, self.form.json_handler)
        self.assertEqual(2, self.form.series_list.count())

    def test_loading_invalid_json_file(self):

        old_handler = self.form.json_handler

        # noinspection PyUnusedLocal,PyUnusedLocal,PyShadowingBuiltins
        def browse_file(a, b, filter=u""):
            return [os.path.join(u"json_test", u"invalid.json")]

        QFileDialog.getOpenFileName = browse_file
        QTest.mouseClick(self.form.load_button, Qt.LeftButton)

        self.assertEqual(old_handler, self.form.json_handler)

    def test_adding_new_series(self):
        QTest.mouseClick(self.form.new_button, Qt.LeftButton)
        self.assertEqual(len(self.form.json_handler.get_series()), 1)
        self.assertTrue(self.form.json_handler.get_series()[0].equals(
            Series(os.getcwdu(), u"New Series", u"1080p", u"Bot", 1, [u"nibl"],
                   u"Plex (TVDB)", u"horriblesubs")
        ))

    def test_delete_series(self):
        QTest.mouseClick(self.form.new_button, Qt.LeftButton)
        self.form.series_list.setCurrentRow(0)
        QTest.mouseClick(self.form.delete_button, Qt.LeftButton)

        self.assertEqual(len(self.form.json_handler.get_series()), 0)

    def test_saving_new_json_file(self):

        # noinspection PyUnusedLocal,PyShadowingBuiltins
        def save_file_location(a, b, c, filter=u"", options=u""):
            return [u"a_json_file.json"]

        QFileDialog.getSaveFileName = save_file_location

        QTest.mouseClick(self.form.new_button, Qt.LeftButton)
        QTest.mouseClick(self.form.new_button, Qt.LeftButton)
        QTest.mouseClick(self.form.new_button, Qt.LeftButton)

        QTest.mouseClick(self.form.save_button, Qt.LeftButton)

        while not self.form.file_loaded:
            pass

        self.assertTrue(os.path.join(u"a_json_file.json"))
        self.assertTrue(self.form.file_loaded)
        self.assertEqual(
            self.form.json_handler.get_json_file_path(),
            u"a_json_file.json"
        )
        self.assertEqual(
            len(JsonHandler(u"a_json_file.json").get_series()),
            len(self.form.json_handler.get_series())
        )

    def test_saving_to_previous_file(self):
        self.test_loading_json()
        self.assertTrue(self.form.file_loaded)

        os.remove(os.path.join(u"json_test", u"updater.json"))

        QTest.mouseClick(self.form.save_button, Qt.LeftButton)

        self.assertTrue(
            os.path.isfile(os.path.join(u"json_test", u"updater.json"))
        )

    def test_changing_series_info(self):
        self.test_loading_json()
        self.form.series_list.setCurrentRow(1)

        self.assertEqual(u"Drifters", self.form.search_name_edit.text())

        self.form.search_name_edit.setText(u"Not Drifters")
        self.assertNotEqual(u"Drifters", self.form.search_name_edit.text())

        QTest.mouseClick(self.form.confirm_button, Qt.LeftButton)

        self.assertEqual(
            u"Not Drifters",
            self.form.json_handler.get_series()[1].get_search_name()
        )

    def test_deleting_no_selection(self):
        self.test_adding_new_series()
        self.form.series_list.clearSelection()

        previous_length = self.form.series_list.count()
        QTest.mouseClick(self.form.delete_button, Qt.LeftButton)
        self.assertEqual(previous_length, self.form.series_list.count())

    def test_changing_series_info_no_selection(self):
        QTest.mouseClick(self.form.confirm_button, Qt.LeftButton)

    def test_loading_invalid_input(self):

        old_handler = self.form.json_handler

        # noinspection PyUnusedLocal,PyUnusedLocal,PyShadowingBuiltins
        def browse_file(a, b, filter=u""):
            return [u""]

        QFileDialog.getOpenFileName = browse_file

        QTest.mouseClick(self.form.load_button, Qt.LeftButton)

        self.assertEqual(old_handler, self.form.json_handler)
        self.assertEqual(0, self.form.series_list.count())

    def test_saving_to_invalid_json_location(self):
        # noinspection PyUnusedLocal,PyShadowingBuiltins
        def save_file_location(a, b, c, filter=u"", options=u""):
            return [u""]

        QFileDialog.getSaveFileName = save_file_location
        QTest.mouseClick(self.form.new_button, Qt.LeftButton)
        QTest.mouseClick(self.form.save_button, Qt.LeftButton)

        self.assertFalse(self.form.file_loaded)
