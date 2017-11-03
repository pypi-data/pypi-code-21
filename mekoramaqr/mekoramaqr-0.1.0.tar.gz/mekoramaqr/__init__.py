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


import os

from blocks import Block, BlockType, BlockTypes
from mekolevel import MekoLevel
from mekoqr import MekoQR

__version__ = "0.1.0"

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_resource(*path):
    """Get the path to a resource file
    
    Args:
        - paths (str): filename within resources directory. If several are given they are concatenated by os.path.join.

    Returns:
        (str) Absolute path

    """
    return os.path.join(_ROOT, 'resources', *path)


