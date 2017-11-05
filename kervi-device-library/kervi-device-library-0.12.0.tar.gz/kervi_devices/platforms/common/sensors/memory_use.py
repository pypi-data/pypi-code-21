# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

from kervi.hal import SensorDeviceDriver
import psutil

class MemUseSensorDeviceDriver(SensorDeviceDriver):
    """ Sensor that mesures memory use """
    def __init__(self):
        try:
            percent = psutil.virtual_memory().percent
        except:
            percent = psutil.phymem_usage().percent

    def read_value(self):
        try:
            percent = psutil.virtual_memory().percent
        except:
            percent = psutil.phymem_usage().percent
        return percent

    @property
    def type(self):
        return "memory_use"

    @property
    def unit(self):
        return "%"

    @property
    def max(self):
        return 100

    @property
    def min(self):
        return 0
