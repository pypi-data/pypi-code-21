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
from toktokkie.utils.xdcc.updating.JsonHandler import JsonHandler
from toktokkie.utils.xdcc.updating.objects.Series import Series


class UnitTests(unittest.TestCase):

    default_series = [
        Series(
            u"3-gatsu no Lion", u"3-gatsu no Lion", u"1080p", u"CR-HOLLAND|NEW", 1,
            [u"nibl"], u"Plex (TVDB)", u"horriblesubs"),
        Series(
            u"Drifters", u"Drifters", u"1080p", u"CR-HOLLAND|NEW", 1,
            [u"nibl"], u"Plex (TVDB)", u"horriblesubs"
        )
    ]

    def setUp(self):

        shutil.copy(
            os.path.join(
                u"toktokkie", u"tests", u"resources", u"json", u"updater.json"
            ),
            u"test.json"
        )
        self.json_without_file = JsonHandler()
        self.json_with_file = JsonHandler(u"test.json")

    def tearDown(self):
        if os.path.isfile(u"test.json"):
            os.remove(u"test.json")
        if os.path.isfile(u"test-nofile.json"):
            os.remove(u"test-nofile.json")

    def test_loading_invalid_json(self):
        try:
            JsonHandler(os.path.join(u"toktokkie", u"tests", u"resources", u"json",
                                     u"invalid.json"))
            self.assertTrue(False)
        except ValueError:
            pass
        try:
            JsonHandler(os.path.join(u"toktokkie", u"tests", u"resources", u"json",
                                     u"invalid-updater.json"))
            self.assertTrue(False)
        except ValueError:
            pass
        try:
            JsonHandler(os.path.join(u"toktokkie", u"tests", u"resources", u"json",
                                     u"invalid-types-updater.json"))
            self.assertTrue(False)
        except ValueError:
            pass

    def test_storing_new_json(self):
        self.test_adding_series()
        self.json_without_file.store_json(u"test-nofile.json")

        self.assertTrue(os.path.isfile(u"test-nofile.json"))
        load_handler = JsonHandler(u"test-nofile.json")

        for series in load_handler.get_series():

            exists = False
            for inner_series in self.json_without_file.get_series():
                if series.equals(inner_series):
                    exists = True

            self.assertTrue(exists)

    def test_storing_existing_json(self):
        self.json_with_file.remove_series(self.default_series[1])
        self.json_with_file.store_json()

        load_handler = JsonHandler(u"test.json")
        self.assertEqual(len(load_handler.get_series()), 1)
        self.assertTrue(
            self.default_series[0].equals(load_handler.get_series()[0])
        )

    def test_handler_without_file(self):
        self.assertEqual(self.json_without_file.get_series(), [])

    def test_handler_with_file(self):

        for series in self.json_with_file.get_series():
            found = False

            for inner_series in self.default_series:
                if inner_series.equals(series):
                    found = True

            self.assertTrue(found)

    def test_adding_series(self):
        self.json_without_file.add_series(self.default_series[0])
        self.assertEqual(len(self.json_without_file.get_series()), 1)
        self.assertTrue(self.json_without_file.get_series()[0].equals(
            self.default_series[0])
        )
        self.json_without_file.add_series(self.default_series[1])
        self.assertEqual(len(self.json_without_file.get_series()), 2)
        self.assertTrue(self.json_without_file.get_series()[0].equals(
            self.default_series[0])
        )
        self.assertTrue(self.json_without_file.get_series()[1].equals(
            self.default_series[1])
        )

    def test_removing_series(self):
        self.test_adding_series()

        self.json_without_file.remove_series(self.default_series[0])
        self.assertTrue(self.json_without_file.get_series()[0].equals(
            self.default_series[1])
        )
        self.assertEqual(len(self.json_without_file.get_series()), 1)

        self.json_without_file.remove_series(self.default_series[1])
        self.assertEqual(len(self.json_without_file.get_series()), 0)

        self.json_without_file.remove_series(self.default_series[0])
        self.assertEqual(len(self.json_without_file.get_series()), 0)

    def test_getting_json_file_path(self):
        self.assertEqual(self.json_with_file.get_json_file_path(), u"test.json")
