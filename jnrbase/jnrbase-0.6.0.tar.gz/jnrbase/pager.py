#
"""pager - pager pipe support."""
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

import os

from subprocess import run


def pager(text, *, pager='less'):
    """Pass output through pager.

    Args:
        text (str): Text to page
        pager (str): Pager to use
    """
    if pager:
        if 'less' in pager and 'LESS' not in os.environ:
            os.environ['LESS'] = 'FRSX'
        run([pager, ], input=text.encode())
    else:
        print(text)
