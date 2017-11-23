u"""
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
# import os
from __future__ import absolute_import
import sys
# import shutil
import unittest
# from manga_dl.main import main


class UnitTests(unittest.TestCase):

    def setUp(self):
        sys.argv = [sys.argv[0]]

    def tearDown(self):
        pass

    def test(self):
        pass
        # sys.argv.append("http://mangafox.me/manga/magi_no_okurimono/")
        # main()
        # self.assertTrue(os.path.isdir("Magi No Okurimono"))
        # shutil.rmtree("Magi No Okurimono")
