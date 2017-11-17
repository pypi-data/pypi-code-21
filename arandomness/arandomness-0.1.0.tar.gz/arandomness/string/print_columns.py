#! /usr/bin/env python

"""Print text in fixed-width columns

Copyright:
    print_columns  print text in fixed-width columns
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

import textwrap

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Planning'
__version__ = '0.1.0a1'


def print_columns(*args):
    """Prints data in fixed-width columns.

    This function takes an arbitrarily long number of args consisting of
    unicodes and/or tuples, then uses PrettyTable to print them into
    columns. Tuples must be of the format (unicode, int). If an arg is an
    unicode, it is simply printed in a column where the column width is
    equal to the width of the unicode. If an arg is a tuple, the first item
    (unicode) of the tuple is printed in a column where the width of the
    column is equal to the second item (int) of the tuple. arg order
    determines column order, i.e. the first arg is printed in the first column.

    Args:
        *args: arbitrary numbers of tuples and unicodes to print,
               see above for details

    Raises:
        ValueError: raised if a tuple cannot be printed

    Example:
        .. code-block:: Python

            >>> print_columns(('hello', 5), 'bye', ('nope', 3))
            hello  bye  nop
                         e
    """

    # Todo, redo this
