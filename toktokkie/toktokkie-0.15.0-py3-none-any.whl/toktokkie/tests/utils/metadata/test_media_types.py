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

import os
import shutil
import unittest
from toktokkie.utils.metadata.media_types.Base import Base
from toktokkie.utils.metadata.media_types.TvSeries import TvSeries
from toktokkie.utils.metadata.media_types.AnimeSeries import AnimeSeries
from toktokkie.utils.metadata.media_types.Ebook import Ebook
from toktokkie.utils.metadata.media_types.LightNovel import LightNovel


class MediaTypesUnitTests(unittest.TestCase):
    """
    Tests the Media Type classes
    """

    media_types = [Base, TvSeries, AnimeSeries, Ebook, LightNovel]

    def test_defining_attributes(self):
        """
        Tests defining the attributes of the various media types
        :return: None
        """
        for media_type in self.media_types:
            attrs = media_type.define_attributes()
            self.assertTrue("required" in attrs)
            self.assertTrue("optional" in attrs)
            self.assertTrue("extenders" in attrs)
            self.assertEqual(len(attrs), 3)

    def test_valid_json(self):
        """
        Tests if valid JSON files are read correctly
        :return: None
        """
        totalcount = 0
        json_dir = "toktokkie/tests/resources/json/media_types/valid"
        for media_type in self.media_types:
            count = 0
            for json_file in os.listdir(json_dir):
                if json_file.startswith(media_type.identifier):
                    count += 1
                    self.prepare_json_directory(
                        os.path.join(json_dir, json_file)
                    )
                    media_type("test_media_type")
                    shutil.rmtree("test_media_type")
            # Just make sure at least 1 test per media type
            self.assertTrue(count > 0)
            totalcount += count
        self.assertEqual(totalcount, len(os.listdir(json_dir)))

    def test_invalid_json(self):
        """
        Tests if incorrect JSON is detected correctly
        :return: None
        """
        totalcount = 0
        json_dir = "toktokkie/tests/resources/json/media_types/invalid"
        for media_type in self.media_types:
            count = 0
            for json_file in os.listdir(json_dir):
                if json_file.startswith(media_type.identifier):
                    count += 1
                    self.prepare_json_directory(
                        os.path.join(json_dir, json_file)
                    )

                    try:
                        media_type("test_media_type")
                        self.fail()
                    except AttributeError:
                        pass

                    shutil.rmtree("test_media_type")
            self.assertTrue(count > 0)  # Make sure 1+ tests per media type
            totalcount += count
        self.assertEqual(totalcount, len(os.listdir(json_dir)))

    def test_modifying_base(self):
        """
        Tests modifying an existing Base JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types/valid/base.json"
        )
        base = Base("test_media_type")
        base.name = "New"

        new_base = Base("test_media_type")
        self.assertNotEqual(new_base.name, "New")

        base.write_changes()

        new_base = Base("test_media_type")
        self.assertEqual(new_base.name, "New")
        shutil.rmtree("test_media_type")

    def test_modifying_tv_series(self):
        """
        Tests modifying an existing TvSeries JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types/"
            "valid/tv_series_minimal.json"
        )
        tv = TvSeries("test_media_type")
        tv.audio_langs = ["ENG", "JAP"]

        new_tv = TvSeries("test_media_type")
        self.assertNotEqual(new_tv.audio_langs, ["ENG", "JAP"])

        tv.write_changes()

        new_tv = TvSeries("test_media_type")
        self.assertEqual(new_tv.audio_langs, ["ENG", "JAP"])
        shutil.rmtree("test_media_type")

    def test_modifying_anime_series(self):
        """
        Tests modifying an existing AnimeSeries JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types/valid/"
            "anime_series_minimal.json"
        )
        anime = AnimeSeries("test_media_type")
        anime.myanimelist_url = "M@L"

        new_anime = AnimeSeries("test_media_type")
        self.assertNotEqual(new_anime.myanimelist_url, "M@L")
        self.assertEqual(new_anime.myanimelist_url, "")

        anime.write_changes()

        new_anime = AnimeSeries("test_media_type")
        self.assertEqual(new_anime.myanimelist_url, "M@L")
        shutil.rmtree("test_media_type")

    def test_modifying_ebook(self):
        """
        Tests modifying an existing Ebook JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types/valid/ebook.json"
        )
        ebook = Ebook("test_media_type")
        ebook.isbn = "AAAAAA"

        new_ebook = Ebook("test_media_type")
        self.assertNotEqual(new_ebook.isbn, "AAAAAA")

        ebook.write_changes()

        new_ebook = Ebook("test_media_type")
        self.assertEqual(new_ebook.isbn, "AAAAAA")
        shutil.rmtree("test_media_type")

    def test_modifying_light_novel(self):
        """
        Tests modifying an existing LightNovel JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types"
            "/valid/light_novel_minimal.json"
        )

        ln = LightNovel("test_media_type")
        ln.novelupdates_url = "N"

        new_ln = LightNovel("test_media_type")
        self.assertNotEqual(new_ln.novelupdates_url, "N")

        ln.write_changes()

        new_ln = LightNovel("test_media_type")
        self.assertEqual(new_ln.novelupdates_url, "N")
        shutil.rmtree("test_media_type")

    def test_removing_optional_attribute(self):
        """
        Tests removing an optional attribute from a JSON file
        :return: None
        """
        self.prepare_json_directory(
            "toktokkie/tests/resources/json/media_types/valid/"
            "tv_series_complete.json"
        )
        tv = TvSeries("test_media_type")
        tv.tvdb_url = None

        new_tv = TvSeries("test_media_type")
        self.assertNotEqual(new_tv.tvdb_url, "")

        tv.write_changes()

        new_tv = TvSeries("test_media_type")
        self.assertEqual(new_tv.tvdb_url, "")
        shutil.rmtree("test_media_type")

    def test_generating_media_type_directories(self):
        """
        Tests generating new media type directories
        :return: None
        """

        for media_type in self.media_types:
            if os.path.isdir(media_type.identifier):
                shutil.rmtree(media_type.identifier)
            x = media_type(media_type.identifier, True)
            self.assertEqual(media_type.identifier, x.name)
            x.name = "X"
            x.write_changes()

        for media_type in self.media_types:
            x = media_type(media_type.identifier, True)
            self.assertNotEqual(media_type.identifier, x.name)
            self.assertEqual("X", x.name)
            shutil.rmtree(media_type.identifier)

        for media_type in self.media_types:
            x = media_type(media_type.identifier, True, True)
            self.assertEqual(media_type.identifier, x.name)
            shutil.rmtree(media_type.identifier)

    @staticmethod
    def prepare_json_directory(json_file: str):
        """
        Prepares the test directory for a JSON file
        :param json_file: The JSON file to test
        :return: None
        """
        if os.path.isdir("test_media_type"):
            shutil.rmtree("test_media_type")
        os.makedirs("test_media_type/.meta")
        shutil.copyfile(json_file, "test_media_type/.meta/info.json")
