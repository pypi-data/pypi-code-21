# Copyright 2017 Matthew Treinish
#
# This file is part of pymochad
#
# pymochad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pymochad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pymochad.  If not, see <http://www.gnu.org/licenses/>.

import mock

from pymochad import controller
from pymochad.tests import base


class TestController(base.TestCase):

    @mock.patch('socket.socket')
    def test_status(self, socket_mock):
        cont = controller.PyMochad()
        with mock.patch.object(cont, 'read_data') as read_mock:
            with mock.patch.object(cont, 'send_cmd') as send_mock:
                cont.status()
                send_mock.assert_called_once_with('st\n')
                read_mock.assert_called_once_with()
