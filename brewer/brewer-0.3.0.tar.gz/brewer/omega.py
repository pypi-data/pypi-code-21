from omegacn7500 import OmegaCN7500
import minimalmodbus
from . import settings

"""
I know this is messy, but I've been having problems with minimalmodbus for weeks and the author has abandoned it.
This is my best option
"""

class Omega():
    def __init__(self, port, address, baudrate=None, timeout=None):
        self.instrument = OmegaCN7500(port, address)
        self.instrument.serial.baudrate = baudrate if baudrate else settings.baudRate
        self.instrument.serial.timeout = timeout if timeout else settings.timeout
        return None

    def safeguard(self, item, types):
        for type in types:
            if isinstance(item, type):
                return True
        raise ValueError("Safeguard failed, %s does not match given types of %s" % (item, types))

    def pv(self):
        while True:
            try:
                return float(self.instrument.get_pv())
            except IOError: # pragma: no cover - This is hard to force
                continue

    def sv(self):
        while True:
            try:
                return float(self.instrument.get_setpoint())
            except IOError: # pragma: no cover - This is hard to force
                continue

    def set_sv(self, temp):
        while True:
            try:
                self.safeguard(temp, [int, float])
                self.instrument.set_setpoint(temp)
                return True
            except IOError: # pragma: no cover - This is hard to force
                continue

    def is_running(self):
        while True:
            try:
                return self.instrument.is_running()
            except IOError: # pragma: no cover - This is hard to force
                continue

    def run(self):
        while True:
            try:
                self.instrument.run()
                return True
            except IOError: # pragma: no cover - This is hard to force
                continue

    def stop(self):
        while True:
            try:
                self.instrument.stop()
                return True
            except IOError: # pragma: no cover - This is hard to force
                continue
