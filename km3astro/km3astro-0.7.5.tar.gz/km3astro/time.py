"""Time conversion utilities.

For random time samples, goto `km3flux.random`
"""
from km3pipe.time import np_to_datetime

from astropy.time import Time


def np_to_astrotime(intime):
    return Time(np_to_datetime(intime))
