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
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication
    from toktokkie.ui.qt.StartPageQtGui import StartPageQtGui
except ImportError:
    Qt = QTest = StartPageQtGui = QApplication = None

import sys
import unittest


class UnitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        if QApplication is None:
            raise unittest.SkipTest(u"Skipping on import error")

        sys.argv = [sys.argv[0], u"-platform", u"minimal"]
        cls.app = QApplication(sys.argv)

    def setUp(self):
        sys.argv = [sys.argv[0], u"-platform", u"minimal"]
        self.form = StartPageQtGui()

    def tearDown(self):
        self.form.destroy()

    def test(self):
        pass
