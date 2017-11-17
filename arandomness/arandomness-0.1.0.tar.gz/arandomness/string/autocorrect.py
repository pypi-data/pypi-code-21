#! /usr/bin/env python

"""Autocorrect word using list of possible words

Copyright:
    autocorrect.py  autocorrect word using list of possible words
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

from arandomness.string import max_substring
from difflib import get_close_matches

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.1'


def autocorrect(query, possibilities, delta=0.75):
    """Attempts to figure out what possibility the query is

    This autocorrect function is rather simple right now with plans for later
    improvement. Right now, it just attempts to finish spelling a word as much
    as possible, and then determines which possibility is closest to said word.

    Args:

        query (unicode): query to attempt to complete

        possibilities (list): list of unicodes of possible answers for query

        delta (float): minimum delta similarity between query and
                       any given possibility for possibility to be considered.
                       Delta used by difflib.get_close_matches().

    Returns:
        unicode: best guess of correct answer

    Raises:
        AssertionError: raised if no matches found

    Example:
        .. code-block:: Python

            >>> autocorrect('bowtei', ['bowtie2', 'bot'])
            'bowtie2'

    """

    # TODO: Make this way more robust and awesome using probability, n-grams?

    possibilities = [possibility.lower() for possibility in possibilities]

    # Don't waste time for exact matches
    if query in possibilities:
        return query

    # Complete query as much as possible
    options = [word for word in possibilities if word.startswith(query)]
    if len(options) > 0:
        possibilities = options
        query = max_substring(options)

    # Identify possible matches and return best match
    matches = get_close_matches(query, possibilities, cutoff=delta)

    # Raise error if no matches
    try:
        assert len(matches) > 0
    except AssertionError:
        raise AssertionError('No matches for "{0}" found'.format(query))

    return matches[0]
