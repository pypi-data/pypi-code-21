#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .Battery import Battery
from .LedStateEnum import ledStateEnum
from .Led import Led
from .USBPowerSource import USBPowerSource
from .TouchStateEnum import touchStateEnum
from .WakeTimer import WakeTimer
from .Touch import Touch
from .Reader import Reader

__author__ = "Frederick Lussier <frederick.lussier@hotmail.com>"
__status__ = "dev"
__version__ = "0.1.1"
__date__ = "september 10th 2017"

__all__ = [
    "Battery",
    "USBPowerSource",
    "Led", "ledStateEnum",
    "Touch", "touchStateEnum"
]

battery = Battery()
led = Led()
touch = Touch()
wakeTimer = WakeTimer()
usbPowerSource = USBPowerSource()

__reader = Reader()
__reader.add(battery._diffuseChanges)
__reader.add(usbPowerSource._diffuseChanges)
__reader.add(touch._diffuseChanges)
__reader.startPeriodicallyReading()


def getPeriodicInterval():
    """
    Get the interval between read data from power supply board
    """
    return __reader.interval


def setPeriodicInterval(interval):
    """
    Set the interval between read data from power supply board

    :param number interval: delay in second
    """
    __reader.interval = interval


def ceaseReading():
    """
    Cease reading periodically the data from power supply board.

    This is important when you close your application.
    """
    __reader.stop()


def restartReading():
    """
    Restart reading periodically the data from power supply board.

    """
    __reader.restart()
