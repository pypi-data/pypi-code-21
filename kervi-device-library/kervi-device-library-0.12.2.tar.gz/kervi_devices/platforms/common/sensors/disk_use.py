# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Module that defines core cpu sensors """

from kervi.hal import SensorDeviceDriver
import psutil


class DiskUseSensorDeviceDriver(SensorDeviceDriver):
    """ Sensor that mesures disk use """
    def __init__(self):
        psutil.disk_usage('/').percent

    def read_value(self):
        return psutil.disk_usage('/').percent

    @property
    def type(self):
        return "diskuse"

    @property
    def unit(self):
        return "%"

    @property
    def max(self):
        return 100

    @property
    def min(self):
        return 0
