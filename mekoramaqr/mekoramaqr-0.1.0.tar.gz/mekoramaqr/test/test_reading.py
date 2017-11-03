# MekoramaQR
# Copyright (C) 2017 by MekoramaQR contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from .. import get_resource

from ..mekoqr import MekoQR
from ..mekolevel import MekoLevel

class TestReading(unittest.TestCase):
    def test_axes(self):
        infile = get_resource("..","test","codes","axis.png")
        bt = MekoLevel.blocktypes

        level = None
        with open(infile, 'rb') as levelfile:
            qr = MekoQR(levelfile)
            level = MekoLevel(code=qr.code)
        self.assertIsNotNone(level)
        self.assertEqual(level.title, "Axis")
        self.assertEqual(level.author, "Test")
        self.assertEqual(len(level.getBlocks()), 46)
        mat = level.getBlockMatrix()
        # X axis brick
        self.assertEqual(mat[0][0][15].blocktype, bt.BRICK)
        # Y axis metal
        self.assertEqual(mat[0][15][0].blocktype, bt.METAL)
        # Z axis stone
        self.assertEqual(mat[15][0][0].blocktype, bt.STONE)

if __name__ == '__main__':
    unittest.main()