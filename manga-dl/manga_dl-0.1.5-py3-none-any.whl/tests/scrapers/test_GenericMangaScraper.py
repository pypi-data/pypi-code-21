"""
Copyright 2015-2017 Hermann Krumrey

This file is part of manga-dl.

manga-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

manga-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with manga-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
import unittest
from manga_dl.scrapers.GenericMangaScraper import GenericMangaScraper


class UnitTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_abstract_class(self):
        try:
            GenericMangaScraper.get_series_name("test")
            self.assertTrue(False)
        except NotImplementedError:
            pass

        try:
            GenericMangaScraper.url_match("test")
            self.assertTrue(False)
        except NotImplementedError:
            pass

        try:
            GenericMangaScraper.scrape_volumes_from_url("Test", "test")
            self.assertTrue(False)
        except NotImplementedError:
            pass
