#
# TAWF ain't web framework.
#
# Copyright (C) 2015 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Calculator example to demonstrate parsing of function arguments.

Try it with::

    curl http://localhost:8090/calc/add/3/4
    curl http://localhost:8090/calc/div/2/3
    curl http://localhost:8090/calc/mul/2/3
    curl http://localhost:8090/calc/sub/3/4
"""

import asyncio
import operator

from tawf import Application

import logging
logging.basicConfig(level=logging.DEBUG)

ALLOWED_OPERATORS = {'add', 'sub', 'mul', 'div'}

def parse_op(op):
    """
    Find calculator function for operator `op`. 
    """
    if op not in ALLOWED_OPERATORS:
        raise ValueError('Unknow operator: {}'.format(op))
    if op == 'div':
        op = 'truediv'
    return getattr(operator, op)


app = Application()

@app.route('/calc/{op}/{a}/{b}')
def calc(op: parse_op, a: float, b: float):
    return op(a, b)


if __name__ == '__main__':
    app.listen(8090, address='0.0.0.0')
    loop = asyncio.get_event_loop()
    loop.run_forever()


# vim: sw=4:et:ai
