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

# imports
import unittest
from toktokkie.ui.urwid.StartScreenUrwidTui import StartScreenUrwidTui


class LoopDummy(object):
    def draw_screen(self):
        pass


# noinspection PyTypeChecker
class UnitTests(unittest.TestCase):

    def setUp(self):
        self.tui = StartScreenUrwidTui()
        self.tui.loop = LoopDummy()

    def tearDown(self):
        pass

    def test(self):
        pass
