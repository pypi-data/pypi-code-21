from . import str116
from . import settings
from .slack import BrewerBot
import time
from .omega import Omega
from terminaltables import AsciiTable

class Controller:
    def __init__(self):
        self.omega = Omega(
            settings.port,
            settings.rimsAddress,
            settings.baudRate,
            settings.timeout
        )

        self.settings = settings

        self.slack = BrewerBot()

    def relay_status(self, relay_num):
        return str116.get_relay(relay_num)

    def set_relay(self, relay_num, state):
        str116.set_relay(relay_num, state)

    def pid_running(self):
        return self.omega.is_running()

    def pid_status(self):
        return {
            "pid_running": bool(self.pid_running()),
            "sv": self.sv(),
            "pv": self.pv()
        }

    def pid(self, state):
        self._safegaurd_state(state)
        if state == 1:
            self.omega.run()
        else:
            self.omega.stop()
        return True

    def hlt(self, state):
        self._safegaurd_state(state)
        self.set_relay(self.settings.relays["hlt"], state)
        return True

    def hlt_to(self, location):
        if location == "mash":
            self.set_relay(self.settings.relays["hltToMash"], 1)
            return True
        elif location  == "boil":
            self.set_relay(self.settings.relays["hltToMash"], 0)
            return True
        else:
            raise ValueError("Location unknown: valid locations are 'mash' and 'boil'")


    def rims_to(self, location):
        if location == "mash":
            self.set_relay(self.settings.relays["rimsToMash"], 1)
            return True
        elif location == "boil":
            self.set_relay(self.settings.relays["rimsToMash"], 0)
            return True
        else:
            raise ValueError("Location unknown: valid locations are 'mash' and 'boil'")

    def pump_status(self):
        return self.relay_status(self.settings.relays["pump"])

    def pump(self, state):
        self._safegaurd_state(state)
        self.set_relay(self.settings.relays['pump'], state)
        return True

    def _safegaurd_state(self, state):
        if not isinstance(state, int):
            raise ValueError("Relay State needs to be an integer, " + str(type(state)) + " given.")
        if state < 0 or state > 1:
            raise ValueError("State needs to be integer 0 or 1, " + str(state) + " given.")
        return True

    def sv(self):
        return float(self.omega.sv())

    def set_sv(self, temp):
        self.omega.safeguard(temp, [int, float])
        self.omega.set_sv(temp)
        return self.omega.sv()

    def pv(self):
        return float(self.omega.pv())

    def watch(self):
        while self.pv() <= self.sv():
            time.sleep(2) # :nocov:

        self.slack.send("PV is now at " + str(self.pv()) + " f")
        return True

    def status_table(self):
        status = AsciiTable([
            ["Setting", "Value"],
            ["PID on?", str(self.pid_status()['pid_running'])],
            ["Pump on?", str(self.pump_status())],
            ["pv", str(self.pv())],
            ["sv", str(self.sv())]
        ])
        return status
