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
import shutil
import unittest
from toktokkie.utils.iconizing.procedures.DesktopIniProcedure import \
    DesktopIniProcedure


class DesktopIniUnitTests(unittest.TestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join("toktokkie", "tests", "resources", "directories"),
            "temp_testing"
        )
        self.game_of_thrones = os.path.join("temp_testing", "Game of Thrones")
        self.game_of_thrones_icon = os.path.join(
            self.game_of_thrones, ".meta", "icons", "main.ico"
        )

    def tearDown(self):
        shutil.rmtree("temp_testing")

    def test_applicability(self):
        self.assertEqual(
            sys.platform == "win32", DesktopIniProcedure.is_applicable()
        )

    def test_iconizing(self):
        DesktopIniProcedure.iconize(
            self.game_of_thrones, self.game_of_thrones_icon
        )
        self.assertEqual(
            DesktopIniProcedure.get_icon_file(self.game_of_thrones),
            self.game_of_thrones_icon
        )
        DesktopIniProcedure.reset_iconization_state(self.game_of_thrones)

    def test_iconizing_with_no_icon_extension(self):
        DesktopIniProcedure.iconize(
            self.game_of_thrones,
            self.game_of_thrones_icon.rsplit(".ico", 1)[0]
        )
        self.assertEqual(
            DesktopIniProcedure.get_icon_file(self.game_of_thrones),
            self.game_of_thrones_icon
        )
        DesktopIniProcedure.reset_iconization_state(self.game_of_thrones)

    def test_retrieving_icon_file(self):

        self.assertEqual(DesktopIniProcedure.get_icon_file(
            self.game_of_thrones), None)

        DesktopIniProcedure.iconize(
            self.game_of_thrones, self.game_of_thrones_icon
        )
        self.assertEqual(
            DesktopIniProcedure.get_icon_file(self.game_of_thrones),
            self.game_of_thrones_icon
        )
        DesktopIniProcedure.reset_iconization_state(self.game_of_thrones)
        self.assertEqual(
            DesktopIniProcedure.get_icon_file(self.game_of_thrones),
            None
        )

    def test_retrieving_icon_file_from_irrelevant_desktop_ini_file(self):
        self.assertEqual(
            DesktopIniProcedure.get_icon_file(
                os.path.join("temp_testing", "NotExistingShow")
            ),
            None
        )
