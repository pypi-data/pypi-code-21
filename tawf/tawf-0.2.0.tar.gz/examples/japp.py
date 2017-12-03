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
JSON application example.
"""

import asyncio
import logging
from functools import partial

from tawf import Application, Method

logging.basicConfig(level=logging.DEBUG)

app = Application()

# each route to have content type application/json
route = partial(app.route, mimetype='application/json')

# save data in the list, only 10 records allowed
data_items = [['nothing']] * 10

@route('/data/{id}')
def data(id: int):
    if id >= len(data_items):
        raise ValueError('invalid id {}'.format(id))
    return data_items[id]


@route('/data/{id}', method=Method.POST)
def data(id: int, data):
    if id >= len(data_items):
        raise ValueError('invalid id {}'.format(id))
    data_items[id] = data

if __name__ == '__main__':
    app.listen(8090, address='0.0.0.0')
    loop = asyncio.get_event_loop()
    loop.run_forever()


# vim: sw=4:et:ai
