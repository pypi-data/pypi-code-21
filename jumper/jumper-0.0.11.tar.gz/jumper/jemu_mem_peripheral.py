"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from queue import Queue
from jemu_peripheral import JemuPeripheral


class JemuMemPeripheral(JemuPeripheral):
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0
    _RESPONSE_TIMEOUT = 10

    _TYPE_STRING = "type"
    _VALUE = "value"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _REG_ADDRESS = "address"
    _COMMAND = "command"
    _COMMAND_SET_REG = "set_reg_value"
    _COMMAND_GET_REG = "get_reg_value"

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        JemuPeripheral.__init__(self, jemu_connection, id, peripheral_type, generators)
        self._queue = Queue()
        self._jemu_connection.register(self._receive_callback)

    def _set_reg_json(self, register, value):
        return {
            self._REG_ADDRESS: register,
            self._TYPE_STRING: self._COMMAND,
            self._VALUE: value,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_SET_REG,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _get_reg_json(self, register):
        return {
            self._REG_ADDRESS: register,
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_GET_REG,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _receive_callback(self, jemu_packet):
        if 'type' in jemu_packet and jemu_packet["type"] == "value_response":
            self._got_message = True
            self._queue.put(jemu_packet["value"])

    def set_register_value(self, register, value):
        self._jemu_connection.send_json(self._set_reg_json(register, value))

    def get_register_value(self, register):
        self._jemu_connection.send_json(self._get_reg_json(register))
        return self._queue.get(timeout=self._RESPONSE_TIMEOUT)

    def status(self):
        return self._jemu_connection.recv_json()
