"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""


class JemuInterrupt:
    _TYPE_STRING = "type"
    _INT = "interrupt"
    RESET = "reset"

    def __init__(self, jemu_connection):
        self._pin_interrupt_callbacks = []
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)

    def on_interrupt(self, callback):
        self._pin_interrupt_callbacks += callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._TYPE_STRING] == self._INT:
            for callback in self._pin_interrupt_callbacks:
                callback(jemu_packet)
