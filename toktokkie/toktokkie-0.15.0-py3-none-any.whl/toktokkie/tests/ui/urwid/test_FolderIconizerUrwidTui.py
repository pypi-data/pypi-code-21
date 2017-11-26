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
import sys
import time
import shutil
import unittest
from toktokkie.utils.iconizing.Iconizer import Iconizer
from toktokkie.ui.urwid.FolderIconizerUrwidTui import FolderIconizerUrwidTui
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class LoopDummy(object):
    def draw_screen(self):
        pass


# noinspection PyTypeChecker
class UnitTests(unittest.TestCase):

    def setUp(self):
        self.tui = FolderIconizerUrwidTui()
        self.tui.loop = LoopDummy()
        shutil.copytree(
            os.path.join("toktokkie", "tests", "resources", "directories"),
            "temp_testing"
        )

    def tearDown(self):
        Iconizer().reverse_iconization("temp_testing")
        self.tui.quit()
        shutil.rmtree("temp_testing")

    def test_non_recursive_iconizing(self):
        self.tui.recursive_check.set_state(False)

        self.tui.directory_edit.set_edit_text(os.path.join(
            "temp_testing", "Game of Thrones")
        )
        self.tui.iconize(None)

        icon_ext = ".ico" if sys.platform == "win32" else ".png"

        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "Game of Thrones"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones",
                    ".meta", "icons", "main" + icon_ext)))

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "Game of Thrones", "Season 1"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones", ".meta", "icons",
                    "Season 1" + icon_ext)))

            self.assertEqual(procedure.get_icon_file(os.path.join(
                "temp_testing", "The Big Bang Theory")), None)

    def test_recursive_iconizing(self):
        self.tui.recursive_check.set_state(True)

        self.tui.directory_edit.set_edit_text(os.path.join("temp_testing"))
        self.tui.iconize(None)

        icon_ext = ".ico" if sys.platform == "win32" else ".png"

        procedure = ProcedureManager.get_applicable_procedure()
        if procedure != GenericProcedure:

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "Game of Thrones"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones", ".meta",
                    "icons", "main" + icon_ext)))

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "Game of Thrones", "Season 1"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "Game of Thrones", ".meta",
                    "icons", "Season 1" + icon_ext)))

            self.assertEqual(
                os.path.abspath(procedure.get_icon_file(os.path.join(
                    "temp_testing", "The Big Bang Theory"))),
                os.path.abspath(os.path.join(
                    "temp_testing", "The Big Bang Theory", ".meta",
                    "icons", "main" + icon_ext)))

    def test_spinner(self):
        self.tui.iconizing = True
        self.tui.start_spinner()
        time.sleep(0.5)

        self.assertTrue(
            self.tui.iconize_button.get_label().startswith("Iconizing")
        )
        self.tui.iconizing = False
        time.sleep(0.5)

        self.assertEqual(self.tui.iconize_button.get_label(), "Start")

    def test_resetting_ui(self):
        self.test_non_recursive_iconizing()
        self.assertEqual(len(self.tui.list_walker), 2)
        self.tui.reset_ui(None)
        self.assertLess(2, len(self.tui.list_walker))
