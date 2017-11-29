"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""

from time import sleep


class JemuSudo(object):
    _id = None
    _jemu_connection = None
    _peripheral_type = None
    _stopped_packet_rec = True

    _STOP_AFTER_COMMAND = "stop_after"
    _START_COMMAND = "resume_running"
    _COMMAND = "command"
    _NANO_SECONDS = "nanoseconds"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _STOPPED = "stopped"

    def __init__(self, jemu_connection, id, peripheral_type):
        self._id = id
        self._peripheral_type = peripheral_type
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)

    def _send_json_command(self, command):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: command,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def set_stopped_packet_rec(self, state):
        self._stopped_packet_rec = state

    def stop_after_ns(self, nanoseconds):
        json_command = self._send_json_command(self._STOP_AFTER_COMMAND)
        json_command[self._NANO_SECONDS] = nanoseconds
        self._jemu_connection.send_json(json_command)
    
    def run_for_ns(self, nanoseconds):
        self._stopped_packet_rec = False
        self.stop_after_ns(nanoseconds)
        sleep(0.001)
        self.resume()
        self.wait_until_stopped()

    def resume(self):
        self._jemu_connection.send_json(self._send_json_command(self._START_COMMAND))

    def wait_until_stopped(self):
        while not self._stopped_packet_rec:
            sleep(0.01)

    def receive_packet(self, jemu_packet):
        if not self._stopped_packet_rec and jemu_packet[self._TYPE_STRING] == self._STOPPED:
            self._stopped_packet_rec = True
