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
Long running processes example.

There are two requests:

fib1
    Delegate each calculation to separate process with asyncio coroutine.
    The processes are managed with process pool executor (one worker per
    CPU).
fib2
    Run calculation and block until it is finished.

The requests can be tested with `siege`, for example::

    $ siege -b -c 2 -r 1 http://localhost:8090/fib1/500000
    ...
    HTTP/1.1 200   3.34 secs:  104494 bytes ==> GET  /fib1/500000
    HTTP/1.1 200   3.51 secs:  104494 bytes ==> GET  /fib1/500000
    ...

    $ siege -b -c 2 -r 1 http://localhost:8090/fib2/500000
    ...
    HTTP/1.1 200   3.19 secs:  104494 bytes ==> GET  /fib2/500000
    HTTP/1.1 200   6.30 secs:  104494 bytes ==> GET  /fib2/500000
    ...

"""

import asyncio
from concurrent.futures import ProcessPoolExecutor

from tawf import Application

import logging
logging.basicConfig(level=logging.DEBUG)

app = Application()
executor = ProcessPoolExecutor()
loop = asyncio.get_event_loop()


@app.route('/fib1/{n}')
async def fib(n: int):
    r = await loop.run_in_executor(executor, _fib, n)
    return r


@app.route('/fib2/{n}')
def fib(n: int):
    r = _fib(n)
    return r


def _fib(n):
    a, b = 1, 1
    for i in range(n-1):
        a, b = b, a + b
    return a


if __name__ == '__main__':
    app.listen(8090, address='0.0.0.0')
    loop.run_forever()


# vim: sw=4:et:ai
