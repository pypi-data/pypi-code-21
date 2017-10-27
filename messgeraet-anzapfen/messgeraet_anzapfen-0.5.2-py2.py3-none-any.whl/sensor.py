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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    @classmethod
    def factory(cls):
        """Return a class of this sensor"""
        return cls

    @classmethod
    def get_ini_filename(cls):
        """Returns the filename of the inifile"""
        modul = cls.__module__.split('.')[0]
        inifilename = cls.__name__.lower() + '.ini'
        return resource_filename(modul, inifilename)

    @classmethod
    def print_ini_file(cls):
        "Print the inifile for this Sensor"""
        inifile = cls.get_ini_filename()
        with open(inifile) as fil:
            print(fil.read())

    @abc.abstractmethod
    def measure(self):
        """Get measurement from sensor

        In self.config is the section of the configfile for this sensor stored

        The result of the measurement must be of type dict and stored in
        self.data

        May raise an MeasurementError if something goes wrong.
        Make sure to catch all the other exceptions and pass them through this
        Exception if necessary.
        """

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
