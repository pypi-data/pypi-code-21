"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        constant.py -- Dummy sensor which returns only a constant value

    FIRST RELEASE
        2017-07-07  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import logging

from messgeraet_anzapfen.sensor import Sensor

_logger = logging.getLogger(__name__)

__all__ = ['Constant']


class Constant(Sensor):
    """Dummy sensor which returns a configurable constant value

    Can be used to send a ping signal to the logserver"""

    config_keys = ['value']

    def measure(self):
        self.data = {'constant': self.config.get('value')}

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
