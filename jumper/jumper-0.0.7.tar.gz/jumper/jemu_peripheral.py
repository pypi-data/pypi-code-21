"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from queue import Queue

class FieldDescriptor:
    _RESPONSE_TIMEOUT = 10

    _TYPE_STRING = "type"
    _VALUE = "value"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _FIELD_NAME = "field_name"
    _COMMAND = "command"
    _COMMAND_SET_VALUE = "set_value"
    _COMMAND_GET_VALUE = "get_value"

    def __init__(self, jemu_connection, id, field_name, peripheral_type):
        self._id = id
        self._jemu_connection = jemu_connection
        self._field_name = field_name
        self._peripheral_type = peripheral_type
        self._queue = Queue()
        self._jemu_connection.register(self._peripheral_receive_callback)

    def set(self, val):
        self._jemu_connection.send_json(self._set_value_json(val))

    def get(self):
        self._jemu_connection.send_json(self._get_value_json())
        return self._queue.get(timeout=self._RESPONSE_TIMEOUT)

    def _set_value_json(self, value):
        return {
            self._FIELD_NAME: self._field_name,
            self._TYPE_STRING: self._COMMAND,
            self._VALUE: value,
            self._PERIPHERAL_TYPE: self._peripheral_type,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_SET_VALUE
        }

    def _get_value_json(self):
        return {
            self._FIELD_NAME: self._field_name,
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_TYPE: self._peripheral_type,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_GET_VALUE
        }

    def _peripheral_receive_callback(self, jemu_packet):
        if 'type' in jemu_packet and jemu_packet["type"] == "get_value_response":
            self._got_message = True
            self._queue.put(jemu_packet["value"])

    
class JemuPeripheral:

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        self._peripheral_type = peripheral_type
        self._id = id
        self._jemu_connection = jemu_connection
        
        if generators != None:
            for field in generators:
                descriptor = FieldDescriptor(jemu_connection, id, field, peripheral_type)
                setattr(self, field, descriptor)
