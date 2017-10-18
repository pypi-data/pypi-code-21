#
"""human_time - Handle human readable date formats."""
# Copyright © 2014-2017  James Rowe <jnrowe@gmail.com>
#
# This file is part of jnrbase.
#
# jnrbase is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# jnrbase is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# jnrbase.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import re


def human_timestamp(timestamp):
    """Format a relative time.

    Args:
        timestamp (datetime.datetime): Event to generate relative timestamp
            against
    Returns:
        str: Human readable date and time offset
    """
    numstr = '. a two three four five six seven eight nine ten'.split()

    matches = [
        60 * 60 * 24 * 365,
        60 * 60 * 24 * 28,
        60 * 60 * 24 * 7,
        60 * 60 * 24,
        60 * 60,
        60,
        1,
    ]
    match_names = ['year', 'month', 'week', 'day', 'hour', 'minute', 'second']

    delta = int((datetime.datetime.utcnow() - timestamp).total_seconds())
    for scale in matches:
        i = delta // scale
        if i:
            name = match_names[matches.index(scale)]
            break
    else:
        raise ValueError('Timestamp invalid: {!r}'.format(timestamp))

    if i == 1 and name in ('year', 'month', 'week'):
        result = 'last {}'.format(name)
    elif i == 1 and name == 'day':
        result = 'yesterday'
    elif i == 1 and name == 'hour':
        result = 'about an hour ago'
    else:
        result = 'about {} {}{} ago'.format(i if i > 10 else numstr[i], name,
                                            's' if i > 1 else '')
    return result


def parse_timedelta(delta):
    """Parse human readable frequency.

    Args:
        delta (str): Frequency to parse
    """
    match = re.fullmatch(r"""
            ^(\d+(?:|\.\d+))  # value, possibly float
            \ *
            ([hdwmy])$  # units
         """, delta, re.IGNORECASE | re.VERBOSE)
    if not match:
        raise ValueError('Invalid ‘frequency’ value')
    value, units = match.groups()
    units_i = 'hdwmy'.index(units.lower())
    # hours per hour/day/week/month/year
    multiplier = (1, 24, 168, 672, 8760)
    return datetime.timedelta(hours=float(value) * multiplier[units_i])
