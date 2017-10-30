#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

string_helpers
==============

Provides
--------

 * quote

"""


def quote(code):
    """Returns quoted code if not already quoted and if possible

    Parameters
    ----------

    code: String
    \tCode thta is quoted

    """

    try:
        code = code.rstrip()

    except AttributeError:
        # code is not a string, may be None --> There is no code to quote
        return code

    if code and code[0] + code[-1] not in ('""', "''", "u'", '"') \
       and '"' not in code:
        return 'u"' + code + '"'
    else:
        return code
