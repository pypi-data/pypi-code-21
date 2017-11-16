"""This is IOS XE driver implementation."""

from functools import partial
import re

from condoor.drivers.IOS import Driver as IOSDriver
from condoor import pattern_manager, TIMEOUT, EOF
from condoor.actions import a_send_line, a_send, a_disconnect, a_message_callback, a_return_and_reconnect
from condoor.fsm import FSM
from condoor.exceptions import ConnectionError


# based on IOS driver
class Driver(IOSDriver):
    """This is a Driver class implementation for IOS XR."""

    platform = 'XE'
    families = {
        "ASR-9": "ASR900",
        "ASR1": "ASR1K"
    }

    def __init__(self, device):
        """Initialize the IOS XE driver object."""
        super(Driver, self).__init__(device)

    def update_driver(self, prompt):
        """Return driver name based on prompt analysis."""
        if "-stby" in prompt:
            raise ConnectionError("Standby console detected")
        return pattern_manager.platform(prompt, ['XE'])

    def reload(self, reload_timeout=300, save_config=True):
        """Reload the device.

        CSM_DUT#reload

        System configuration has been modified. Save? [yes/no]: yes
        Building configuration...
        [OK]
        Proceed with reload? [confirm]
        """
        SAVE_CONFIG = re.compile(re.escape("System configuration has been modified. Save? [yes/no]: "))
        PROCEED = re.compile(re.escape("Proceed with reload? [confirm]"))
        IMAGE = re.compile("Passing control to the main image")
        BOOTSTRAP = re.compile("System Bootstrap")
        LOCATED = re.compile("Located .*")
        RETURN = re.compile(re.escape("Press RETURN to get started!"))

        response = "yes" if save_config else "no"

        #              0          1       2       3         4
        events = [SAVE_CONFIG, PROCEED, LOCATED, RETURN, self.username_re,
                  self.password_re, BOOTSTRAP, IMAGE, TIMEOUT, EOF]
        #              5              6          7       8      9

        transitions = [
            (SAVE_CONFIG, [0], 1, partial(a_send_line, response), 60),
            (PROCEED, [0, 1], 2, partial(a_send, "\r"), reload_timeout),
            (LOCATED, [2], 2, a_message_callback, reload_timeout),
            # if timeout try to send the reload command again
            (TIMEOUT, [0], 0, partial(a_send_line, self.reload_cmd), 10),
            (BOOTSTRAP, [2], -1, a_disconnect, reload_timeout),
            (IMAGE, [2], 3, a_message_callback, reload_timeout),
            (self.username_re, [3], -1, a_return_and_reconnect, 0),
            (self.password_re, [3], -1, a_return_and_reconnect, 0),
            (RETURN, [3], -1, a_return_and_reconnect, 0),
            (TIMEOUT, [2], -1, a_disconnect, 0),
            (EOF, [0, 1, 2, 3], -1, a_disconnect, 0)
        ]
        fsm = FSM("IOS-RELOAD", self.device, events, transitions, timeout=10)
        return fsm.run()
