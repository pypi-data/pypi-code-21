u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import division
from __future__ import with_statement
from __future__ import absolute_import
import os
import sys
import unittest
from xdcc_dl.main import main
from io import open


class UnitTests(unittest.TestCase):

    def setUp(self):
        sys.argv = [sys.argv[0]]
        sys.argv.append(u"-v")
        sys.argv.append(u"0")
        sys.argv.append(u"-s")
        sys.argv.append(u"irc.namibsun.net")

    def tearDown(self):

        sys.argv = [sys.argv[0]]
        if os.path.isfile(u"1_test.txt"):
            os.remove(u"1_test.txt")
        if os.path.isfile(u"2_test.txt"):
            os.remove(u"2_test.txt")
        if os.path.isfile(u"3_test.txt"):
            os.remove(u"3_test.txt")

    def test_single_download(self):

        sys.argv.append(u"/msg xdcc_servbot xdcc send #1")
        main()

        self.check_content(1)

    def test_wrong_server(self):

        sys.argv.pop()
        sys.argv.pop()

        sys.argv.append(u"/msg xdcc_servbot xdcc send #1")
        self.assertFalse(os.path.isfile(u"1_test.txt"))

    def test_repeated_download(self):

        sys.argv.append(u"/msg xdcc_servbot xdcc send #2")

        with open(u"2_test.txt", u'w') as testtwo:
            testtwo.write(u"This is a Test File for XDCC File Transfers\n\n")
            testtwo.write(u"This is Pack 2")

        self.check_content(2)
        main()

        self.check_content(2)
        os.remove(u"2_test.txt")
        main()

        self.check_content(2)

    def test_resume(self):

        sys.argv.append(u"/msg xdcc_servbot xdcc send #3")

        with open(u"3_test.txt", u'w') as testthree:
            testthree.write(
                u"This is a Test File for XDCC File Transfers\n\n"
                u"This is Pack 3"
            )

        self.check_content(3)

        with open(u"3_test.txt", u'rb') as testthree:
            binary = testthree.read()

        with open(u"3_test.txt", u'wb') as testthree:
            testthree.write(binary[0:int(len(binary) / 2)])

        main()
        self.check_content(3)

    def test_range_downloading(self):

        sys.argv.append(u"/msg xdcc_servbot xdcc send #1-3")
        main()

        self.check_content(1)
        self.check_content(2)
        self.check_content(3)

    def test_range_downloading_with_steps(self):

        sys.argv.append(u"/msg xdcc_servbot xdcc send #1-3,2")
        main()

        self.check_content(1)
        self.assertFalse(os.path.isfile(u"2_test.txt"))
        self.check_content(3)

    def check_content(self, number):

        self.assertTrue(os.path.isfile(unicode(number) + u"_test.txt"))
        with open(unicode(number) + u"_test.txt", u'r') as f:

            content = f.read()
            self.assertTrue(
                u"This is a Test File for XDCC File Transfers" in content)
            self.assertTrue(u"This is Pack " + unicode(number) in content)
