# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Module that defines core cpu sensors """

from kervi.hal import SensorDeviceDriver
import psutil

class CPULoadSensorDeviceDriver(SensorDeviceDriver):
    """ Sensor that mesures cpu load on host """
    def __init__(self):
        psutil.cpu_percent()

    def read_value(self):
        return psutil.cpu_percent()

    @property
    def max(self):
        return 100

    @property
    def min(self):
        return 0

    @property
    def type(self):
        return "cpu_use"

    @property
    def unit(self):
        return "%"
