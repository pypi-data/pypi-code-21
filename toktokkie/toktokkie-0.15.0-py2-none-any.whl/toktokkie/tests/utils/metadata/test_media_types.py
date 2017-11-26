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

from __future__ import absolute_import
import os
import shutil
import unittest
from toktokkie.utils.metadata.media_types.Base import Base
from toktokkie.utils.metadata.media_types.TvSeries import TvSeries
from toktokkie.utils.metadata.media_types.AnimeSeries import AnimeSeries
from toktokkie.utils.metadata.media_types.Ebook import Ebook
from toktokkie.utils.metadata.media_types.LightNovel import LightNovel


class MediaTypesUnitTests(unittest.TestCase):
    u"""
    Tests the Media Type classes
    """

    media_types = [Base, TvSeries, AnimeSeries, Ebook, LightNovel]

    def test_defining_attributes(self):
        u"""
        Tests defining the attributes of the various media types
        :return: None
        """
        for media_type in self.media_types:
            attrs = media_type.define_attributes()
            self.assertTrue(u"required" in attrs)
            self.assertTrue(u"optional" in attrs)
            self.assertTrue(u"extenders" in attrs)
            self.assertEqual(len(attrs), 3)

    def test_valid_json(self):
        u"""
        Tests if valid JSON files are read correctly
        :return: None
        """
        totalcount = 0
        json_dir = u"toktokkie/tests/resources/json/media_types/valid"
        for media_type in self.media_types:
            count = 0
            for json_file in os.listdir(json_dir):
                if json_file.startswith(media_type.identifier):
                    count += 1
                    self.prepare_json_directory(
                        os.path.join(json_dir, json_file)
                    )
                    media_type(u"test_media_type")
                    shutil.rmtree(u"test_media_type")
            # Just make sure at least 1 test per media type
            self.assertTrue(count > 0)
            totalcount += count
        self.assertEqual(totalcount, len(os.listdir(json_dir)))

    def test_invalid_json(self):
        u"""
        Tests if incorrect JSON is detected correctly
        :return: None
        """
        totalcount = 0
        json_dir = u"toktokkie/tests/resources/json/media_types/invalid"
        for media_type in self.media_types:
            count = 0
            for json_file in os.listdir(json_dir):
                if json_file.startswith(media_type.identifier):
                    count += 1
                    self.prepare_json_directory(
                        os.path.join(json_dir, json_file)
                    )

                    try:
                        media_type(u"test_media_type")
                        self.fail()
                    except AttributeError:
                        pass

                    shutil.rmtree(u"test_media_type")
            self.assertTrue(count > 0)  # Make sure 1+ tests per media type
            totalcount += count
        self.assertEqual(totalcount, len(os.listdir(json_dir)))

    def test_modifying_base(self):
        u"""
        Tests modifying an existing Base JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types/valid/base.json"
        )
        base = Base(u"test_media_type")
        base.name = u"New"

        new_base = Base(u"test_media_type")
        self.assertNotEqual(new_base.name, u"New")

        base.write_changes()

        new_base = Base(u"test_media_type")
        self.assertEqual(new_base.name, u"New")
        shutil.rmtree(u"test_media_type")

    def test_modifying_tv_series(self):
        u"""
        Tests modifying an existing TvSeries JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types/"
            u"valid/tv_series_minimal.json"
        )
        tv = TvSeries(u"test_media_type")
        tv.audio_langs = [u"ENG", u"JAP"]

        new_tv = TvSeries(u"test_media_type")
        self.assertNotEqual(new_tv.audio_langs, [u"ENG", u"JAP"])

        tv.write_changes()

        new_tv = TvSeries(u"test_media_type")
        self.assertEqual(new_tv.audio_langs, [u"ENG", u"JAP"])
        shutil.rmtree(u"test_media_type")

    def test_modifying_anime_series(self):
        u"""
        Tests modifying an existing AnimeSeries JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types/valid/"
            u"anime_series_minimal.json"
        )
        anime = AnimeSeries(u"test_media_type")
        anime.myanimelist_url = u"M@L"

        new_anime = AnimeSeries(u"test_media_type")
        self.assertNotEqual(new_anime.myanimelist_url, u"M@L")
        self.assertEqual(new_anime.myanimelist_url, u"")

        anime.write_changes()

        new_anime = AnimeSeries(u"test_media_type")
        self.assertEqual(new_anime.myanimelist_url, u"M@L")
        shutil.rmtree(u"test_media_type")

    def test_modifying_ebook(self):
        u"""
        Tests modifying an existing Ebook JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types/valid/ebook.json"
        )
        ebook = Ebook(u"test_media_type")
        ebook.isbn = u"AAAAAA"

        new_ebook = Ebook(u"test_media_type")
        self.assertNotEqual(new_ebook.isbn, u"AAAAAA")

        ebook.write_changes()

        new_ebook = Ebook(u"test_media_type")
        self.assertEqual(new_ebook.isbn, u"AAAAAA")
        shutil.rmtree(u"test_media_type")

    def test_modifying_light_novel(self):
        u"""
        Tests modifying an existing LightNovel JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types"
            u"/valid/light_novel_minimal.json"
        )

        ln = LightNovel(u"test_media_type")
        ln.novelupdates_url = u"N"

        new_ln = LightNovel(u"test_media_type")
        self.assertNotEqual(new_ln.novelupdates_url, u"N")

        ln.write_changes()

        new_ln = LightNovel(u"test_media_type")
        self.assertEqual(new_ln.novelupdates_url, u"N")
        shutil.rmtree(u"test_media_type")

    def test_removing_optional_attribute(self):
        u"""
        Tests removing an optional attribute from a JSON file
        :return: None
        """
        self.prepare_json_directory(
            u"toktokkie/tests/resources/json/media_types/valid/"
            u"tv_series_complete.json"
        )
        tv = TvSeries(u"test_media_type")
        tv.tvdb_url = None

        new_tv = TvSeries(u"test_media_type")
        self.assertNotEqual(new_tv.tvdb_url, u"")

        tv.write_changes()

        new_tv = TvSeries(u"test_media_type")
        self.assertEqual(new_tv.tvdb_url, u"")
        shutil.rmtree(u"test_media_type")

    def test_generating_media_type_directories(self):
        u"""
        Tests generating new media type directories
        :return: None
        """

        for media_type in self.media_types:
            if os.path.isdir(media_type.identifier):
                shutil.rmtree(media_type.identifier)
            x = media_type(media_type.identifier, True)
            self.assertEqual(media_type.identifier, x.name)
            x.name = u"X"
            x.write_changes()

        for media_type in self.media_types:
            x = media_type(media_type.identifier, True)
            self.assertNotEqual(media_type.identifier, x.name)
            self.assertEqual(u"X", x.name)
            shutil.rmtree(media_type.identifier)

        for media_type in self.media_types:
            x = media_type(media_type.identifier, True, True)
            self.assertEqual(media_type.identifier, x.name)
            shutil.rmtree(media_type.identifier)

    @staticmethod
    def prepare_json_directory(json_file):
        u"""
        Prepares the test directory for a JSON file
        :param json_file: The JSON file to test
        :return: None
        """
        if os.path.isdir(u"test_media_type"):
            shutil.rmtree(u"test_media_type")
        os.makedirs(u"test_media_type/.meta")
        shutil.copyfile(json_file, u"test_media_type/.meta/info.json")
