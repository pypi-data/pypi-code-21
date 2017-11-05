# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Module that defines core cpu sensors """

from kervi.hal import SensorDeviceDriver, HAL_DRIVER_ID

class CPUTempSensorDeviceDriver(SensorDeviceDriver):
    """ Sensor that mesures cpu temp on host """
    def __init__(self):
        SensorDeviceDriver.__init__(self)

    def read_value(self):
        if HAL_DRIVER_ID == "kervi_hal_rpi":
            return int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
        return 0

    @property
    def max(self):
        return 150

    @property
    def min(self):
        return 0

    @property
    def type(self):
        return "temperature"

    @property
    def unit(self):
        return "C"
