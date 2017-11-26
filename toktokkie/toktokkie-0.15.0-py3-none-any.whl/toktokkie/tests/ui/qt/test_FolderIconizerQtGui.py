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
    from PyQt5.QtWidgets import QApplication
    from toktokkie.ui.qt.FolderIconizerQtGui import FolderIconizerQtGui
except ImportError:
    Qt = QTest = FolderIconizerQtGui = QApplication = None

import os
import sys
import time
import shutil
import unittest
from toktokkie.utils.iconizing.Iconizer import Iconizer
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class UnitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        if QApplication is None:
            raise unittest.SkipTest("Skipping on import error")

        sys.argv = [sys.argv[0], "-platform", "minimal"]
        cls.app = QApplication(sys.argv)

    def setUp(self):
        sys.argv = [sys.argv[0], "-platform", "minimal"]
        self.form = FolderIconizerQtGui()
        shutil.copytree(
            os.path.join("toktokkie", "tests", "resources", "directories"),
            "temp_testing"
        )

    def tearDown(self):
        self.form.closeEvent(None)
        self.form.destroy()
        Iconizer().reverse_iconization("temp_testing")
        shutil.rmtree("temp_testing")

    def test_non_recursive_iconizing(self):
        if self.form.recursive_check.checkState():
            self.form.recursive_check.nextCheckState()

        self.form.directory_path_edit.setText(
            os.path.join("temp_testing", "Game of Thrones")
        )
        QTest.mouseClick(self.form.start_button, Qt.LeftButton)

        icon_ext = ".ico" if sys.platform == "win32" else ".png"

        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:
            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(
                    os.path.join("temp_testing", "Game of Thrones"))),
                os.path.abspath(
                    os.path.join(
                        "temp_testing",
                        "Game of Thrones",
                        ".meta", "icons", "main" + icon_ext)
                )
            )

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(
                    os.path.join(
                        "temp_testing", "Game of Thrones", "Season 1"
                    ))
                ),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones",
                    ".meta", "icons", "Season 1" + icon_ext
                ))
            )

            self.assertEqual(procedure.get_icon_file(
                os.path.join("temp_testing", "The Big Bang Theory")), None
            )

    def test_recursive_iconizing(self):
        if not self.form.recursive_check.checkState():
            self.form.recursive_check.nextCheckState()

        self.form.directory_path_edit.setText("temp_testing")
        QTest.mouseClick(self.form.start_button, Qt.LeftButton)

        icon_ext = ".ico" if sys.platform == "win32" else ".png"

        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(
                    os.path.join("temp_testing", "Game of Thrones"))),
                os.path.abspath(
                    os.path.join("temp_testing", "Game of Thrones",
                                 ".meta", "icons", "main" + icon_ext)))

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "Game of Thrones", "Season 1"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones",
                    ".meta", "icons", "Season 1" + icon_ext)))

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "The Big Bang Theory"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "The Big Bang Theory", ".meta",
                    "icons", "main" + icon_ext)))

    def test_spinner(self):

        class DummySignal(object):

            current = ""

            def emit(self, string):
                self.current = string

        signal = DummySignal()
        self.form.spinner_update_signal = signal

        self.form.iconizing = True
        self.form.start_spinner()
        time.sleep(0.5)

        self.assertTrue(signal.current.startswith("Iconizing"))
        self.form.iconizing = False
        time.sleep(0.5)

        self.assertEqual(signal.current, "Start")

    def test_spinner_updater(self):
        self.form.update_spinner("BlaBla")
        self.assertEqual(self.form.start_button.text(), "BlaBla")
