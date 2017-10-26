"""Epidemic forecasts using disease surveillance data."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import datetime
import logging
import numpy as np
import pypfilt

from . import model
from . import obs
from . import version

__package_name__ = u'epifx'
__author__ = u'Rob Moss'
__email__ = u'rgmoss@unimelb.edu.au'
__copyright__ = u'2014-2016, Rob Moss'
__license__ = u'BSD 3-Clause License'
__version__ = version.__version__


# Export classes from this module.
Obs = obs.Obs
SEIR = model.SEIR

# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def default_params(px_count, model, time, popn_size, prng_seed=None):
    """The default simulation parameters.

    :param px_count: The number of particles.
    :param model: The infection model.
    :param time: The simulation time scale.
    :param popn_size: The population size.
    :param prng_seed: The seed for both the ``epifx`` and ``pypfilt``
        pseudo-random number generators.
    """
    # Enforce a minimal history matrix.
    params = pypfilt.default_params(model, time, max_days=7,
                                    px_count=px_count)
    # The observation model.
    params['log_llhd_fn'] = obs.log_llhd

    # Override the pypfilt PRNG seed, if specified.
    if prng_seed is not None:
        params['resample']['prng_seed'] = prng_seed

    # Model-specific parameters.
    params['epifx'] = {
        # The population size.
        'popn_size': popn_size,
        # Allow stochastic variation in model parameters and state variables.
        'stoch': True,
        # Use the default pypfilt PRNG seed, whatever that might be.
        'prng_seed': params['resample']['prng_seed'],
        # Provide a hook for functions to record log-likelihoods before the
        # particles weights are adjusted and any resampling takes place.
        'record_log_llhd_fns': [],
    }

    # Construct the default PRNG object.
    params['epifx']['rnd'] = np.random.RandomState(
        params['epifx']['prng_seed'])

    # Observation model parameters.
    params['obs'] = {}

    return params


def daily_forcing(filename, date_fmt='%Y-%m-%d'):
    """Return a temporal forcing look-up function, which should be stored in
    ``params['epifx']['forcing']`` in order to enable temporal forcing.

    :param filename: A file that contains two columns separated by whitespace,
        the column first being the date and the second being the force of the
        temporal modulation.
        Note that the first line of this file is assumed to contain column
        headings and will be **ignored**.
    :param date_fmt: The format in which dates are stored.
    """

    col_types = [('Date', datetime.datetime), ('Force', np.float)]
    df = obs.read_table(filename, col_types)

    def forcing(when):
        """Return the (daily) temporal forcing factor."""
        if when.hour == when.minute == when.second == 0:
            # The time-step covered the final portion of the previous day.
            when = when - datetime.timedelta(days=1)
        else:
            when = when.replace(hour=0, minute=0, second=0)
        return df['Force'][df['Date'] == when][0]

    return forcing
