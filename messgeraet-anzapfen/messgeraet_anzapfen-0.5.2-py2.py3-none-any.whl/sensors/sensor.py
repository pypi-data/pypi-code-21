"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        sensor.py -- Abstract base class for a sensor

    FIRST RELEASE
        2017-07-04  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import abc
import logging

from pkg_resources import resource_filename

from messgeraet_anzapfen.configurable import Configurable
_logger = logging.getLogger(__name__)

__all__ = ['MeasurementError', 'Sensor']


class MeasurementError(Exception):
    """Error to indicate something gone wrong while measuring

       As a consequence the main programm will swich an error led will on"""


class Sensor(abc.ABC, Configurable):
    """Baseclass for the sensors"""

    @classmethod
    def factory(cls):
        """Return a class of this sensor"""
        return cls

    @classmethod
    def print_ini_file(cls):
        "Print the inifile for this Sensor"""
        modul = cls.__module__.split('.')[0]
        inifilename = cls.__name__.lower() + '.ini'
        inifile = resource_filename(modul, inifilename)
        with open(inifile) as fil:
            print(fil.read())
        print()

    @abc.abstractmethod
    def measure(self):
        """Reads the sensor an returns a dict with the sensor values

        May raise an MeasurementError if something goes wrong.
        Make sure to catch all the other exceptions and pass them through this
        Exception if necessary.
        """

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
