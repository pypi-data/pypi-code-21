"""Random sampling utilities.
"""
import numpy as np

from km3astro.time import np_to_astrotime


def random_azimuth(n=1, unit='rad'):
    """Draw azimuth, uniformly distributed."""
    n = int(n)  # the method does not cast floats
    azi = (2 * np.pi * np.random.random_sample(size=n))
    if unit == 'rad':
        return azi
    elif unit == 'deg':
        return azi / np.pi * 180
    else:
        raise KeyError("Unknown unit '{}'".format(unit))


def random_zenith(n=1, unit='rad'):
    """Draw zenith, uniformly distributed in cos(zen)."""
    n = int(n)  # the method does not cast floats
    coszen = (2 * np.random.random_sample(size=n) - 1)
    zen = np.arccos(coszen)
    if unit == 'rad':
        return zen
    elif unit == 'deg':
        return zen / np.pi * 180
    else:
        raise KeyError("Unknown unit '{}'".format(unit))


def second_from_interval(start, stop, n=1, **randargs):
    """Sample random times from an interval (in seconds)."""
    n = int(n)
    sec = np.timedelta64(1, 's')
    n_seconds = (stop - start) / sec
    samples = np.random.randint(low=0, high=n_seconds, size=n, **randargs) * sec
    return start + samples


def equidistant_from_interval(start, stop, step=np.timedelta64(2, 'm')):
    """Draw equidistant samples (fixed stepsize) from interval."""
    start = np.datetime64(start)
    stop = np.datetime64(stop)
    duration = stop - start
    n_steps = np.ceil(duration / step)
    samples = np.arange(n_steps) * step
    return start + samples


def random_date(n=1, year=2015, astropy_time=False, **randargs):
    """Create random dates in the given year.

    Parameters
    ----------
    year: int, default: 2015
    n: int, default: 1
    """
    start = np.datetime64('{}-01-01'.format(year))
    stop = np.datetime64('{}-01-01'.format(year + 1))
    sample = second_from_interval(start, stop, n=n, **randargs)
    if astropy_time:
        return np_to_astrotime(sample)
    else:
        return sample
