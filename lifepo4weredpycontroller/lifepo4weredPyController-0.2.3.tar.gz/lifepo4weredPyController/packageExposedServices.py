#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .Battery import Battery
from .Led import Led
from .LedStateEnum import ledStateEnum
from .Lifepo4wered import Lifepo4wered
from .Reader import Reader
from .Touch import Touch
from .TouchStateEnum import touchStateEnum
from .USBPowerSource import USBPowerSource
from .WakeTimer import WakeTimer


battery = Battery()
led = Led()
lifepo4wered = Lifepo4wered()
touch = Touch()
usbPowerSource = USBPowerSource()
wakeTimer = WakeTimer()


@battery.observeState()
def batteryChangeHandle(previous, actual):
    lifepo4wered.instanceState["batteryVoltage"] = actual["voltage"]
    lifepo4wered.instanceState["batteryRate"] = actual["rate"]


@usbPowerSource.observeState()
def usbPowerSourceChangeHandle(previous, actual):
    lifepo4wered.instanceState["usbPowerSourceVoltage"] = actual["voltage"]
    lifepo4wered.instanceState["usbPowerSourcePluggedIn"] = actual["pluggedIn"]


@touch.observeState()
def touchChangeHandle(previous, actual):
    lifepo4wered.instanceState["touchState"] = actual["state"]


__reader = Reader()
__reader.add(battery._diffuseChanges)
__reader.add(usbPowerSource._diffuseChanges)
__reader.add(touch._diffuseChanges)
__reader.addPostJob(lifepo4wered._diffuseChanges)
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
