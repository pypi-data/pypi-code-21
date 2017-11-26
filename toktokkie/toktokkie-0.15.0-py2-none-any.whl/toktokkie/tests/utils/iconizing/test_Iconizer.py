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
from toktokkie.utils.iconizing.Iconizer import Iconizer
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class IconizerUnitTests(unittest.TestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(u"toktokkie", u"tests", u"resources", u"directories"),
            u"temp_testing"
        )
        self.game_of_thrones = os.path.join(u"temp_testing", u"Game of Thrones")
        self.native_iconizer = Iconizer()

    def tearDown(self):
        self.native_iconizer.reverse_iconization(u"temp_testing")
        shutil.rmtree(u"temp_testing")

    def test_native_iconizing(self):

        self.assertEqual(
            self.native_iconizer.procedure.get_icon_file(self.game_of_thrones),
            None
        )
        self.native_iconizer.recursive_iconize(u"temp_testing")

        if self.native_iconizer.procedure != GenericProcedure:

            self.assertNotEqual(
                self.native_iconizer.procedure.get_icon_file(
                    self.game_of_thrones
                ),
                None
            )
            self.assertTrue(
                self.native_iconizer.procedure.get_icon_file(
                    self.game_of_thrones) in [
                    os.path.join(
                        self.game_of_thrones,
                        u".meta", u"icons", u"main.png"),
                    os.path.join(
                        self.game_of_thrones,
                        u".meta", u"icons", u"main.ico")
                ]
            )

        self.native_iconizer.reverse_iconization(u"temp_testing")
        self.assertEqual(
            self.native_iconizer.procedure.get_icon_file(self.game_of_thrones),
            None
        )

    # noinspection PyMethodMayBeStatic
    def test_no_iconizer_available(self):

        iconizer = Iconizer()
        iconizer.procedure = GenericProcedure

        # Just to check that no errors are thrown
        iconizer.recursive_iconize(u"temp_testing")

    def test_iconizer_override(self):

        procedure = ProcedureManager.get_applicable_procedure()
        iconizer = Iconizer(procedure.get_procedure_name())
        self.native_iconizer = iconizer
        self.test_native_iconizing()

    def test_iconizing_not_exisiting_directory(self):
        self.assertFalse(os.path.exists(u"NotADirectory"))
        self.native_iconizer.iconize_directory(u"NotADirectory")
        self.assertFalse(os.path.exists(u"NotADirectory"))

    def test_iconizer_with_none_procedure(self):
        iconizer = Iconizer(procedure_override=u"SomeNotExistingProcedure")
        self.assertEqual(iconizer.procedure, GenericProcedure)

        iconizer_target = os.path.join(u"temp_testing", u"Game of Thrones")

        iconizer.iconize_directory(iconizer_target)
        iconizer.reverse_iconization(iconizer_target)
