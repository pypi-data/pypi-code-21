"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
class JemuSudo:
    __id = None
    __jemu_connection = None
    __peripheral_type = None

    _STOP_AFTER_COMMAND = "stop_after"
    _START_COMMAND = "start"
    _COMMAND = "command"
    _MILLI_SECONDS = "milliseconds"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"

    def __SendJsonCommand(self, command):
        return {self._TYPE_STRING: self._COMMAND,
                        self._PERIPHERAL_ID: self.__id,
                        self._COMMAND: command,
                        self._PERIPHERAL_TYPE: self.__peripheral_type} 

    def __init__(self, jemu_connection, id, peripheral_type):
        self.__id = id
        self.__peripheral_type = peripheral_type
        self.__jemu_connection = jemu_connection

    def stop_after(self, milliseconds):
        json_command = self.__SendJsonCommand(self._STOP_AFTER_COMMAND)
        json_command[self._MILLI_SECONDS] = milliseconds
        self.__jemu_connection.send_json(json_command)

    def start(self):
        self.__jemu_connection.send_json(self.__SendJsonCommand(self._START_COMMAND))
