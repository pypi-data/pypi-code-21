# Copyright 2016 Matthew Treinish
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


class Device(object):
    """PyMochad Device class

    This class represents an X1 device connected to your controller

    :param PyMochad controller: A PyMochad controller object for the device to
                                use
    :param str address: The device address
    :param str comm_type: The communication type to use for the device. This is
                          either pl (for power line) or rf (for radio
                          frequency)
    """
    def __init__(self, controller, address, comm_type='pl'):
        self.controller = controller
        self.address = address
        if comm_type not in ['pl', 'rf']:
            msg = 'Mochad only supports a comm_type of pl or rf'
            raise TypeError(msg)
        self.comm_type = comm_type

    def send_cmd(self, cmd):
        """Send a raw command to device.

        :param str cmd: The command to send to the device
        """
        cmd_str = ' '.join([self.comm_type, self.address, cmd])
        self.controller.send_cmd(cmd_str + '\n')

    def get_status(self):
        """Get the on/off status for the devices

        :returns: Device status
        :rtype: str
        """
        cmd_str = 'getstatus ' + self.address + '\n'
        self.controller.send_cmd(cmd_str)
        return self.controller.read_data().lower()

    def get_statussec(self):
        """Get the on/off status for the X10 Security devices

        :returns: Device status
        :rtype: str
        """
        cmd_str = 'getstatussec ' + self.address + '\n'
        self.controller.send_cmd(cmd_str)
        return self.controller.read_data().lower()
