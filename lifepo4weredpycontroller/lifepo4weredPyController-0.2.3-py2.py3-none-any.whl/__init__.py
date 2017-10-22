#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .packageInfo import AUTHOR, VERSION, STATUS

from .packageExposedServices import (
    battery, led, lifepo4wered, touch, usbPowerSource, wakeTimer,
    ledStateEnum, touchStateEnum,
    getPeriodicInterval, setPeriodicInterval, ceaseReading, restartReading)

__author__ = AUTHOR
__status__ = STATUS
__version__ = VERSION
__date__ = "september 10th 2017"

__all__ = [
    "battery",
    "usbPowerSource",
    "led", "ledStateEnum",
    "lifepo4wered",
    "touch", "touchStateEnum",
    "wakeTimer"
]
