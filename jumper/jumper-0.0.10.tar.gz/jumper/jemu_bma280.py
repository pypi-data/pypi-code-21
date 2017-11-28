from jemu_mem_peripheral import JemuMemPeripheral


class JemuBMA280(JemuMemPeripheral):
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0
    _RESPONSE_TIMEOUT = 10

    _TYPE_STRING = "type"
    _VALUE = "value"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _INTERRUPT = "interrupts"
    _COMMAND = "command"
    _COMMAND_SET_INTERRUPT = "set_interrupt"
    _COMMAND_UNSET_INTERRUPT = "unset_interrupt"
    _COMMAND_RESET_INTERRUPT = "reset_interrupts"

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, generators)

    def _set_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._INTERRUPT: interrupt,
            self._COMMAND: self._COMMAND_SET_INTERRUPT,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _unset_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_UNSET_INTERRUPT,
            self._INTERRUPT: interrupt,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _reset_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_RESET_INTERRUPT,
            self._INTERRUPT: interrupt,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def set_interrupt(self, interrupt):
        self._jemu_connection.send_json(self._set_interrupt_json(interrupt))

    def unset_interrupt(self, interrupt):
        self._jemu_connection.send_json(self._unset_interrupt_json(interrupt))

    def reset_interrupt(self, interrupt):
        self._jemu_connection.send_json(self._redset_interrupt_json(interrupt))

