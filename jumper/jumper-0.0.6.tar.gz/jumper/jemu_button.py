"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""


class JemuButton(object):
    _id = None
    _jemu_connection = None
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0

    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _PIN_LEVEL = "pin_level"
    _COMMAND = "command"
    _COMMAND_PIN_LOGIC_LEVEL = "set_pin_level"
    _EXTERNAL_PERIPHERAL = "External"

    def _button_gpio_json(self, id, level):
        return {
            self._PIN_LEVEL: level,
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: id,
            self._COMMAND: self._COMMAND_PIN_LOGIC_LEVEL,
            self._PERIPHERAL_TYPE: self._EXTERNAL_PERIPHERAL
        }

    def __init__(self, jemu_connection, id):
        self._id = id
        self._jemu_connection = jemu_connection

    def on(self):
        self._jemu_connection.send_json(self._button_gpio_json(self._id, self._LEVEL_LOW))

    def off(self):
        self._jemu_connection.send_json(self._button_gpio_json(self._id, self._LEVEL_HIGH))

    def status(self):
        return self._jemu_connection.recv_json()
