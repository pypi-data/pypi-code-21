"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        statusled.py -- Class for the statusleds

    FIRST RELEASE
        2017-07-07  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import logging
import time

try:
    import RPi.GPIO as GPIO
    PRINT_LINEBREAKE = False
except ImportError:
    import messgeraet_anzapfen.gpio as GPIO
    PRINT_LINEBREAKE = True
from messgeraet_anzapfen.configurable import Configurable
_logger = logging.getLogger(__name__)

__all__ = ['StatusLed']


class LED:
    """LED class wraps GPIO"""

    def __init__(self, pin):
        self.active = isinstance(pin, str) and pin.isdigit()
        if self.active:
            self.pin = int(pin)
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
        else:
            self.pin = 'N\A'

    def on(self):
        """Switch LED on"""
        _logger.debug('Switch LED({pin}) on'.format(pin=self.pin))
        if self.active:
            GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        """Switch LED off"""
        _logger.debug('Switch LED({pin}) off'.format(pin=self.pin))
        if self.active:
            GPIO.output(self.pin, GPIO.LOW)

    def blink(self, count, interval=0.6):
        """Let the LED blink

        :param count: :obj:`int` number of times to blink
        :param interval: :obj:`float` lenght of one blinking cycle in seconds
        """
        _logger.info('Blink LED({pin}) {count} times'.format(
            pin=self.pin, count=count))
        for _ in range(count):
            self.on()
            time.sleep(2 * interval / 3.)
            self.off()
            time.sleep(interval / 3.)


class StatusLed(Configurable):
    """Class wraps statusleds"""

    config_keys = ['server_pin', 'sensor_pin']

    def __init__(self, config):
        super().__init__()
        self.load_config(config)
        self.server = LED(self.config.get('server_pin'))
        self.sensor = LED(self.config.get('sensor_pin'))

    def __del__(self):
        if PRINT_LINEBREAKE:
            print()

    def blink(self, count, interval=0.6):
        """Let both LEDs blink

        :param count: :obj:`int` number of times to blink
        :param interval: :obj:`float` lenght of one blinking cycle in seconds
        """
        for _ in range(count):
            self.server.on()
            self.sensor.on()
            time.sleep(2 * interval / 3.)
            self.server.off()
            self.sensor.off()
            time.sleep(interval / 3.)
# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
