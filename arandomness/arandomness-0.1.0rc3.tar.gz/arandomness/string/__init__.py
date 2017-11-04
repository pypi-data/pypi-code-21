#! /usr/bin/env python

"""Initializes string package of arandomness

Copyright:
    __init__.py  initializes string package of arandomness
    Copyright (C) 2017  Alex Hyer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from arandomness.string.max_substring import max_substring
from arandomness.string.print_columns import print_columns

# I hate that this is not in alphabetical order, but it has to be in
# this order for relative imports to work.
# https://68.media.tumblr.com/77499dd5fdb75637bc6be2e539f5ea5f/tumblr_inline_osficvX4uf1qgozmu_540.gif
from arandomness.string.autocorrect import autocorrect

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.0'
