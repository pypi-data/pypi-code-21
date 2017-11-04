#! /usr/bin/env python

"""Finds max substring shared by all strings starting at position

Copyright:
    max_substring.py  finds max substring of all strings starting at position
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

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.2'


def max_substring(words, position=0, _last_letter=''):
    """Finds max substring shared by all strings starting at position

    Args:

        words (list): list of unicode of all words to compare

        position (int): starting position in each word to begin analyzing
                        for substring

        _last_letter (unicode): last common letter, only for use
                                internally unless you really know what
                                you are doing

    Returns:
        unicode: max string common to all words

    Examples:
        .. code-block:: Python

            >>> max_substring(['aaaa', 'aaab', 'aaac'])
            'aaa'
            >>> max_substring(['abbb', 'bbbb', 'cbbb'], position=1)
            'bbb'
            >>> max_substring(['abc', 'bcd', 'cde'])
            ''
    """

    # If end of word is reached, begin reconstructing the substring
    try:
        letter = [word[position] for word in words]
    except IndexError:
        return _last_letter

    # Recurse if position matches, else begin reconstructing the substring
    if all(l == letter[0] for l in letter) is True:
        _last_letter += max_substring(words, position=position + 1,
                                      _last_letter=letter[0])
        return _last_letter
    else:
        return _last_letter
