"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

from hgicommon.data_source import ListDataSource, MultiDataSource


class TestMultiDataSource(unittest.TestCase):
    """
    Tests for `MultiDataSource`.
    """
    def setUp(self):
        self.data = [i for i in range(10)]
        self.sources = [ListDataSource([self.data[i]]) for i in range(len(self.data))]

    def test_init_change_of_source_list_has_no_effect(self):
        source = MultiDataSource(self.sources)
        self.sources.pop()
        self.assertCountEqual(source.get_all(), self.data)

    def test_get_all_when_no_sources(self):
        source = MultiDataSource()
        self.assertEqual(len(source.get_all()), 0)

    def test_get_all_when_sources(self):
        source = MultiDataSource(self.sources)
        self.assertIsInstance(source.get_all()[0], type(self.data[0]))
        self.assertCountEqual(source.get_all(), self.data)


class TestListDataSource(unittest.TestCase):
    """
    Tests for `ListDataSource`.
    """
    def setUp(self):
        self.data = [i for i in range(10)]

    def test_init_data_optional(self):
        source = ListDataSource()
        for datum in self.data:
            source.data.append(datum)
        self.assertCountEqual(source.get_all(), self.data)

    def test_init_data_can_be_changed(self):
        source = ListDataSource(self.data)
        self.data.append(11)
        self.assertCountEqual(source.get_all(), self.data)

    def test_get_all(self):
        source = ListDataSource(self.data)
        self.assertCountEqual(source.get_all(), self.data)


if __name__ == "__main__":
    unittest.main()
