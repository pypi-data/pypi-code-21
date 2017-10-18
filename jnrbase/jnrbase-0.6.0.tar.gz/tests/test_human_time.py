#
"""test_human_time - Test human readable time functions"""
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

from re import escape

from pytest import mark, raises

from jnrbase.human_time import human_timestamp, parse_timedelta


@mark.parametrize('delta,result', [
    ({'days': 365, }, 'last year'),
    ({'days': 70, }, 'about two months ago'),
    ({'days': 30, }, 'last month'),
    ({'days': 21, }, 'about three weeks ago'),
    ({'days': 4, }, 'about four days ago'),
    ({'days': 1, }, 'yesterday'),
    ({'hours': 5, }, 'about five hours ago'),
    ({'hours': 1, }, 'about an hour ago'),
    ({'minutes': 6, }, 'about six minutes ago'),
    ({'seconds': 12, }, 'about 12 seconds ago'),
])
def test_human_timestamp(delta, result):
    dt = datetime.datetime.utcnow() - datetime.timedelta(**delta)
    assert human_timestamp(dt) == result


def test_human_timestamp_invalid_delta():
    dt = datetime.datetime.utcnow() - datetime.timedelta(milliseconds=5)
    with raises(ValueError, match=escape(repr(dt))):
        human_timestamp(dt)


@mark.parametrize('string,dt', [
    ('3h', datetime.timedelta(0, 10800)),
    ('1d', datetime.timedelta(1)),
    ('1 d', datetime.timedelta(1)),
    ('0.5 y', datetime.timedelta(182, 43200)),
    ('0.5 Y', datetime.timedelta(182, 43200)),
])
def test_parse_timedelta(string, dt):
    assert parse_timedelta(string) == dt


def test_parse_invalid_timedelta():
    with raises(ValueError, match='Invalid ‘frequency’ value'):
        parse_timedelta('1 k')
