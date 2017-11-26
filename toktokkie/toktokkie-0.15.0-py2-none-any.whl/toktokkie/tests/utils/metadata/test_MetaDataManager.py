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
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager


class MetaDataManagerUnitTests(unittest.TestCase):

    def setUp(self):
        shutil.copytree(
            u"toktokkie/tests/resources/directories",
            u"temp_testing"
        )

    def tearDown(self):
        shutil.rmtree(u"temp_testing")

    def test_tv_series_directory_check(self):
        self.assertTrue(MetaDataManager.is_media_directory(
            os.path.join(u"temp_testing", u"Game of Thrones"),
            media_type=u"tv_series"))
        self.assertTrue(MetaDataManager.is_media_directory(
            os.path.join(u"temp_testing", u"The Big Bang Theory"),
            media_type=u"tv_series"))
        self.assertFalse(MetaDataManager.is_media_directory(
            os.path.join(u"temp_testing", u"NotAShow"),
            media_type=u"tv_series"))

    def test_recursive_tv_series_checker(self):
        directories = MetaDataManager.find_recursive_media_directories(
            u"temp_testing", media_type=u"tv_series"
        )
        self.assertEqual(len(directories), 5)
        self.assertTrue(os.path.join(u"temp_testing", u"Game of Thrones")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"The Big Bang Theory")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"Re Zero")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"ShowWithoutSeasons")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotExistingShow")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotAShow")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"OtherMedia")
                        not in directories)

    def test_recursive_tv_series_checker_with_single_folder(self):
        directories = MetaDataManager.find_recursive_media_directories(
            os.path.join(u"temp_testing", u"Game of Thrones"),
            media_type=u"tv_series")
        self.assertEqual(len(directories), 1)
        self.assertTrue(os.path.join(u"temp_testing", u"Game of Thrones")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"The Big Bang Theory")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"Re Zero")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"ShowWithoutSeasons")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotExistingShow")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotAShow")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"OtherMedia")
                        not in directories)

    def test_generic_recursive_media_checker(self):
        directories = MetaDataManager.find_recursive_media_directories(
            u"temp_testing")
        self.assertEqual(len(directories), 6)
        self.assertTrue(os.path.join(u"temp_testing", u"Game of Thrones")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"The Big Bang Theory")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"Re Zero")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"ShowWithoutSeasons")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotExistingShow")
                        in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"NotAShow")
                        not in directories)
        self.assertTrue(os.path.join(u"temp_testing", u"OtherMedia")
                        in directories)

    def test_permission_error(self):

        # noinspection PyUnusedLocal
        def permission_error(directory):
            raise IOError()

        backup = os.listdir
        os.listdir = permission_error

        results = MetaDataManager.find_recursive_media_directories(
            u"temp_testing"
        )
        self.assertEqual(results, [])

        os.listdir = backup

    def test_search_on_not_exisiting_directory(self):

        self.assertEqual(MetaDataManager.find_recursive_media_directories(
            u"NotExisitingDirectory"), [])

    def test_generating_new_media_directory(self):
        self.assertFalse(MetaDataManager.is_media_directory(
            os.path.join(u"temp_testing", u"New Show"), u"tv_series"))
        MetaDataManager.generate_media_directory(
            os.path.join(u"temp_testing", u"New Show"), u"tv_series"
        )
        self.assertTrue(MetaDataManager.is_media_directory(
            os.path.join(u"temp_testing", u"New Show"), u"tv_series"))

    def test_generating_exisiting_media_directory(self):
        game_of_thrones = os.path.join(u"temp_testing", u"Game of Thrones")

        self.assertTrue(MetaDataManager.is_media_directory(
            game_of_thrones, u"tv_series"))
        MetaDataManager.generate_media_directory(game_of_thrones, u"tv_series")
        self.assertTrue(MetaDataManager.is_media_directory(
            game_of_thrones, u"tv_series"))

    def test_generating_media_directory_from_normal_directory(self):
        test_directory = os.path.join(u"temp_testing", u"New Show")
        os.makedirs(test_directory)

        self.assertFalse(MetaDataManager.is_media_directory(test_directory))
        MetaDataManager.generate_media_directory(test_directory)
        self.assertTrue(MetaDataManager.is_media_directory(test_directory))

    def test_generating_media_directory_from_file(self):
        target_file = \
            os.path.join(u"temp_testing", u"Game of Thrones", u"watch_order")
        self.assertFalse(MetaDataManager.is_media_directory(target_file))

        try:
            MetaDataManager.generate_media_directory(target_file)
            self.assertTrue(False)
        except (IOError, OSError):
            pass

    def test_media_type_finder(self):
        self.assertEqual(u"tv_series", MetaDataManager.get_media_type(
            os.path.join(u"temp_testing", u"Game of Thrones")))
        self.assertEqual(u"", MetaDataManager.get_media_type(
            os.path.join(u"temp_testing", u"NotAShow")))
