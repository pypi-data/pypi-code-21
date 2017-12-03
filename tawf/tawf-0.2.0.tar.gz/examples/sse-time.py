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

import asyncio
import logging
from datetime import datetime
from tornado.web import StaticFileHandler

from tawf import Application, Method

logging.basicConfig(level=logging.DEBUG)

app = Application([
    ('^/(.*)$', StaticFileHandler, {'path': 'examples'}),
])

@app.sse('/server-time/{sleep}')
async def time(sleep: int, callback):
    while True:
        callback(datetime.now())
        await asyncio.sleep(sleep)


@app.route('/server-time/{sleep}', Method.OPTIONS)
def time(sleep: int):
    return 'updated every {}s'.format(sleep)


if __name__ == '__main__':
    app.listen(8090, address='0.0.0.0')
    loop = asyncio.get_event_loop()
    loop.run_forever()


# vim: sw=4:et:ai
