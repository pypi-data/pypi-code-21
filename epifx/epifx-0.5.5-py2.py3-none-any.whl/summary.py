from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

from functools import reduce
import logging
import numpy as np

import pypfilt
import pypfilt.check as check
import pypfilt.stats as stats
import pypfilt.summary
from pypfilt.summary import Table, Monitor
import pypfilt.text

from . import obs


class PrOutbreak(Table):
    """
    Record the daily outbreak probability, defined as the sum of the weights
    of all particles in which an outbreak has been seeded.

    :param name: the name of the table in the output file.
    """

    def __init__(self, name='pr_epi'):
        Table.__init__(self, name)

    def dtype(self, params, obs_list):
        self.__model = params['model']
        self.__time = params['time']
        return [params['time'].dtype('date'), ('pr', np.float64)]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        return n_days

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        for date, ix, hist_ix in dates:
            mask = self.__model.is_seeded(hist[hist_ix])
            seeded_weights = weights[ix, :] * mask
            date_enc = self.__time.to_dtype(date)
            insert_fn((date_enc, np.sum(seeded_weights)))


def obs_types(params, obs_list, obs_reqd=False):
    """
    Return a sorted list of ``(unit, period)`` tuples that define the unique
    combinations of observation unit and observation period in the provided
    list of observations. If this list is empty, the observation models will
    instead be queried.

    :param params: The simulation parameters.
    :param obs_list: The list of observations for the simulation.
    :param obs_reqd: Whether a non-empty list of observations is required; if
        ``True``, an empty list will be return when no observations are
        provided.
    """
    if len(obs_list) > 0:
        return sorted(set((o['unit'], o['period']) for o in obs_list))
    elif obs_reqd:
        # Observations are required, return an empty list.
        return []
    else:
        # Query each observation model to determine the observation types.
        return sorted({(u, om['obs_model'].period)
                       for u, om in params['obs'].items()})


def obs_units(params, obs_list, obs_reqd=False):
    """
    Return a dictionary that maps observation units (represented as Unicode
    strings) to their byte string encodings, for the provided list of
    observations. If this list is empty, the observation models will instead
    be queried.

    :param params: The simulation parameters.
    :param obs_list: The list of observations for the simulation.
    :param obs_reqd: Whether a non-empty list of observations is required; if
        ``True``, an empty dictionary will be return when no observations are
        provided.
    """
    if len(obs_list) > 0:
        return {o['unit']: pypfilt.text.to_bytes(o['unit']) for o in obs_list}
    elif obs_reqd:
        # Observations are required, return an empty dictionary.
        return {}
    else:
        return {unit: pypfilt.text.to_bytes(unit) for unit in params['obs']}


class PeakMonitor(Monitor):
    """Record epidemic peak forecasts, for use with other statistics."""

    peak_size = None
    """
    A dictionary that maps observation systems to the size of each particle's
    peak with respect to that system: ``peak_size[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_date = None
    """
    A dictionary that maps observation systems to the date of each particle's
    peak with respect to that system: ``peak_date[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_time = None
    """
    A dictionary that maps observation systems to the time of each particle's
    peak with respect to that system, measured in (fractional) days from the
    start of the forecasting period: ``peak_time[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_weight = None
    """
    A dictionary that maps observation systems to the weight of each
    particle at the time that its peak occurs:
    ``peak_weight[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    expected_obs = None
    """
    The expected observation for each particle for the duration of the
    **current simulation window**.

    Note that this is **only** valid for tables to inspect in each call to
    ``add_rows()``, and **not** in a call to ``finished()``.
    """

    def __init__(self):
        self.__run = None
        self.__loaded_from_cache = False

    def prepare(self, params, obs_list):
        self.__params = params
        self.__obs_types = obs_types(params, obs_list, obs_reqd=True)
        self.peak_obs = {u_p: (0, None) for u_p in self.__obs_types}
        for o in obs_list:
            key = (o['unit'], o['period'])
            if o['value'] > self.peak_obs[key][0]:
                self.peak_obs[key] = (o['value'], o['date'])

    def begin_sim(self, start_date, end_date, n_days, n_sys, forecasting):
        logger = logging.getLogger(__name__)
        time_scale = self.__params['time']
        if self.__run is None or self.__run != (start_date, end_date):
            # For each particle, record the weight and peak time.
            num_px = self.__params['size']
            self.__run = (start_date, end_date)
            if self.__loaded_from_cache:
                logger.debug("Using cached monitor state")
                self.__loaded_from_cache = False
                # Adjust the cached peak_time data now that the simulation
                # start date is known.
                dt = (time_scale.to_scalar(start_date)
                      - time_scale.to_scalar(self.__loaded_from_date))
                logger.debug("Adjusting peak_time by {} days".format(dt))
                for k, v in self.peak_time.items():
                    self.peak_time[k] = v - dt
                return
            logger.debug("Initialising monitor state")
            self.peak_size = {k: np.zeros(num_px) for k in self.__obs_types}
            self.peak_time = {k: np.zeros(num_px) for k in self.__obs_types}
            self.peak_date = {k: np.empty(num_px, dtype='O')
                              for k in self.__obs_types}
            self.peak_weight = {k: np.zeros(num_px) for k in self.__obs_types}
        elif self.__run is not None and self.__run == (start_date, end_date):
            logger.debug("Ignoring monitor state")
        else:
            logger.debug("Deleting monitor state")
            self.__run = None
            self.peak_size = None
            self.peak_time = None
            self.peak_date = None
            self.peak_weight = None

    def days_to(self, date):
        """
        Convert a date to the (fractional) number of days from the start of
        the forecasting period.
        """
        time_scale = self.__params['time']
        return time_scale.to_scalar(date)

    def monitor(self, hist, weights, fs_date, dates, obs_types):
        """Record the peak for each particle during a forecasting run."""
        self.expected_obs = {}

        # Do nothing more if there are no dates to summarise.
        num_dates = len(dates)
        if num_dates == 0:
            # Ensure an empty data structure exists, at least.
            for (u, p) in obs_types:
                self.expected_obs[u, p] = np.array([])
            return

        # Calculate the infection probabilities at every date, for every
        # observation period.
        pr_inf = {}
        pr_inf_fn = self.__params['model'].pr_inf
        periods = set([p for (_, p) in obs_types])

        times = [date for (date, ix, hist_ix) in dates]
        exp_shape = (len(times), self.__params['size'])
        for (u, p) in obs_types:
            self.expected_obs[u, p] = np.zeros(exp_shape)

        # Resampling can change the particle order, so we need to iterate over
        # the particle chronologically, and reorder the arrays whenever
        # resampling occurs.
        date_ix = 0
        for date, ix, hist_ix in dates:
            curr = hist[hist_ix]
            prev_ixs = curr[:, -1].astype(int)
            resampled = not np.all(np.diff(prev_ixs) == 1)
            if resampled:
                # Particles were resampled on this date.
                # Adjust the arrays to reflect the new particle ordering.
                for k in self.__obs_types:
                    self.peak_weight[k] = self.peak_weight[k][prev_ixs]
                    self.peak_size[k] = self.peak_size[k][prev_ixs]
                    self.peak_date[k] = self.peak_date[k][prev_ixs]
                    self.peak_time[k] = self.peak_time[k][prev_ixs]

            # Record the expected observations.
            for p in periods:
                n_back = self.__params['steps_per_unit'] * p
                prev = pypfilt.earlier_states(hist, hist_ix, n_back)
                pr_inf = pr_inf_fn(prev, curr)

                valid_types = [(u, pd) for (u, pd) in obs_types if p == pd]
                for (u, p) in valid_types:
                    values = obs.expect(self.__params, date, u, p,
                                        pr_inf, prev, curr)
                    self.expected_obs[u, p][date_ix] = values
                    # Update the recorded peaks where appropriate.
                    mask = values > self.peak_size[u, p]
                    self.peak_size[u, p][mask] = values[mask]
                    self.peak_date[u, p][mask] = date
                    self.peak_time[u, p][mask] = self.days_to(date)

            date_ix += 1

        # Record the *final* weights.
        for k in self.__obs_types:
            self.peak_weight[k] = weights[-1]

    def __obs_type_seq(self):
        """Return a generator that returns ``(obs_type, str_name)`` tuples."""
        for u, p in self.__obs_types:
            yield ((u, p), "{}/{}".format(u, p))

    def load_state(self, grp):
        """Load the monitor state for disk."""
        logger = logging.getLogger(__name__)
        logger.debug("{}.load_state('{}')".format(self.__class__.__name__,
                                                  grp.name))
        # Record the start date used in the cached simulation, as this defines
        # the origin for the peak_time values.
        time_scale = self.__params['time']
        start_date_enc = grp['start_date'][()]
        self.__loaded_from_date = time_scale.from_dtype(start_date_enc[0])
        # Initialise the data structures.
        self.peak_weight = {}
        self.peak_size = {}
        self.peak_time = {}
        self.peak_date = {}
        # Load the cached state for each observation type.
        for (k, name) in self.__obs_type_seq():
            logger.debug("Loading sub-group '{}'".format(name))
            sub_grp = grp[name]
            self.peak_weight[k] = sub_grp['peak_weight'][()]
            self.peak_size[k] = sub_grp['peak_size'][()]
            self.peak_time[k] = sub_grp['peak_time'][()]
            peak_date = sub_grp['peak_date'][()]
            self.peak_date[k] = np.array([time_scale.from_dtype(d)
                                          for d in peak_date])
        # Indicate that the monitor state has been loaded from a cache file,
        # and that the peak_time data needs to be adjusted once the simulation
        # start date is known.
        self.__loaded_from_cache = True

    def save_state(self, grp):
        """Save the monitor state to disk."""
        logger = logging.getLogger(__name__)
        logger.debug("{}.save_state('{}')".format(self.__class__.__name__,
                                                  grp.name))
        # Save the start date, as this is the origin for the peak_time values.
        time_scale = self.__params['time']
        start_date_enc = np.array([time_scale.to_dtype(self.__run[0])])
        if 'start_date' in grp:
            # Delete existing data sets, in case they differ in size or type.
            del grp['start_date']
        grp.create_dataset('start_date', data=start_date_enc)
        data_sets = ['peak_weight', 'peak_size', 'peak_time', 'peak_date']
        for (k, name) in self.__obs_type_seq():
            logger.debug("Saving sub-group '{}'".format(name))
            sub_grp = grp.require_group(name)
            # Delete existing data sets, in case they differ in size or type.
            for ds in data_sets:
                if ds in sub_grp:
                    del sub_grp[ds]
            peak_date = np.array([time_scale.to_dtype(d)
                                  for d in self.peak_date[k]])
            sub_grp.create_dataset('peak_weight', data=self.peak_weight[k])
            sub_grp.create_dataset('peak_size', data=self.peak_size[k])
            sub_grp.create_dataset('peak_time', data=self.peak_time[k])
            sub_grp.create_dataset('peak_date', data=peak_date)


class ThresholdMonitor(Monitor):
    """Record when expected observations exceed a specific threshold."""

    exceed_date = None
    """
    A dictionary that maps observation systems to the date when each particle
    exceeded the specific threshold: ``exceed_date[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    exceed_weight = None
    """
    A dictionary that maps observation systems to the **final** weight of each
    particle: ``exceed_weight``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    exceed_mask = None
    """
    A dictionary that maps observation systems to Boolean arrays that indicate
    which particles have exceeded the threshold:
    ``exceed_mask[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    def __init__(self, threshold):
        """:param threshold: The threshold observation value."""
        self.__threshold = threshold
        self.__run = None
        self.__loaded_from_cache = False

    def prepare(self, params, obs_list):
        self.__params = params
        self.__obs_types = obs_types(params, obs_list, obs_reqd=True)

    def begin_sim(self, start_date, end_date, n_days, n_sys, forecasting):
        logger = logging.getLogger(__name__)
        if self.__run is None or self.__run != (start_date, end_date):
            # For each particle, record the weight, whether it exceeded the
            # threshold and, if so, when that occurred .
            num_px = self.__params['size']
            self.__run = (start_date, end_date)
            if self.__loaded_from_cache:
                logger.debug("Using cached monitor state")
                self.__loaded_from_cache = False
                return
            logger.debug("Initialising monitor state")
            # Note: ensure that exceed_date always contains values that can be
            # successfully (de)serialised by the appropriate time scale.
            native = self.__params['time'].native_dtype()
            self.exceed_date = {k: np.full(num_px, start_date, dtype=native)
                                for k in self.__obs_types}
            self.exceed_weight = np.zeros(num_px)
            self.exceed_mask = {k: np.zeros(num_px, dtype=bool)
                                for k in self.__obs_types}
        elif self.__run is not None and self.__run == (start_date, end_date):
            logger.debug("Ignoring monitor state")
        else:
            logger.debug("Deleting monitor state")
            self.__run = None
            self.exceed_date = None
            self.exceed_weight = None
            self.exceed_mask = None

    def monitor(self, hist, weights, fs_date, dates, obs_types):
        """Record the peak for each particle during a forecasting run."""
        # Do nothing more if there are no dates to summarise.
        num_dates = len(dates)
        if num_dates == 0:
            return

        # Calculate the infection probabilities at every date, for every
        # observation period.
        pr_inf = {}
        pr_inf_fn = self.__params['model'].pr_inf
        periods = set([p for (_, p) in obs_types])

        # Resampling can change the particle order, so we need to iterate over
        # the particles chronologically, and reorder the arrays whenever
        # resampling occurs.
        for date, ix, hist_ix in dates:
            curr = hist[hist_ix]
            prev_ixs = curr[:, -1].astype(int)
            resampled = not np.all(np.diff(prev_ixs) == 1)
            if resampled:
                # Particles were resampled on this date.
                # Adjust the arrays to reflect the new particle ordering.
                self.exceed_weight = self.exceed_weight[prev_ixs]
                for k in self.__obs_types:
                    self.exceed_date[k] = self.exceed_date[k][prev_ixs]
                    self.exceed_mask[k] = self.exceed_mask[k][prev_ixs]

            # Calculate the expected observations for each particle.
            for p in periods:
                n_back = self.__params['steps_per_unit'] * p
                prev = pypfilt.earlier_states(hist, hist_ix, n_back)
                pr_inf = pr_inf_fn(prev, curr)

                valid_types = [(u, pd) for (u, pd) in obs_types if p == pd]
                for (u, p) in valid_types:
                    values = obs.expect(self.__params, date, u, p,
                                        pr_inf, prev, curr)
                    # Identify where the threshold has been exceeded for the
                    # first time.
                    mask = np.logical_and(
                        values > self.__threshold,
                        ~ self.exceed_mask[u, p])
                    self.exceed_date[u, p][mask] = date
                    self.exceed_mask[u, p][mask] = True

        # Record the *final* weights.
        self.exceed_weight[:] = weights[-1]

    def __obs_type_seq(self):
        """Return a generator that returns ``(obs_type, str_name)`` tuples."""
        for u, p in self.__obs_types:
            yield ((u, p), "{}/{}".format(u, p))

    def load_state(self, grp):
        """Load the monitor state for disk."""
        logger = logging.getLogger(__name__)
        logger.debug("{}.load_state('{}')".format(self.__class__.__name__,
                                                  grp.name))
        time_scale = self.__params['time']
        # Initialise the data structures.
        self.exceed_weight = grp['exceed_weight'][()]
        self.exceed_date = {}
        self.exceed_mask = {}
        native = self.__params['time'].native_dtype()
        # Load the cached state for each observation type.
        for (k, name) in self.__obs_type_seq():
            logger.debug("Loading sub-group '{}'".format(name))
            sub_grp = grp[name]
            exceed_date = sub_grp['exceed_date'][()]
            self.exceed_date[k] = np.array([time_scale.from_dtype(d)
                                            for d in exceed_date],
                                           dtype=native)
            self.exceed_mask[k] = sub_grp['exceed_mask'][()]
        # Indicate that the monitor state has been loaded from a cache file,
        # and that the peak_time data needs to be adjusted once the simulation
        # start date is known.
        self.__loaded_from_cache = True

    def save_state(self, grp):
        """Save the monitor state to disk."""
        logger = logging.getLogger(__name__)
        logger.debug("{}.save_state('{}')".format(self.__class__.__name__,
                                                  grp.name))
        time_scale = self.__params['time']
        if 'exceed_weight' in grp:
            del grp['exceed_weight']
        grp.create_dataset('exceed_weight', data=self.exceed_weight)
        data_sets = ['exceed_date', 'exceed_mask']
        # Note that time.dtype(...) returns a ``(name, type)`` tuple.
        time_dtype = self.__params['time'].dtype('ignored')[1]
        for (k, name) in self.__obs_type_seq():
            logger.debug("Saving sub-group '{}'".format(name))
            sub_grp = grp.require_group(name)
            # Delete existing data sets, in case they differ in size or type.
            for ds in data_sets:
                if ds in sub_grp:
                    del sub_grp[ds]
            exceed_date = np.array([time_scale.to_dtype(d)
                                    for d in self.exceed_date[k]],
                                   dtype=time_dtype)
            sub_grp.create_dataset('exceed_date', data=exceed_date)
            sub_grp.create_dataset('exceed_mask', data=self.exceed_mask[k])


class ExceedThreshold(Table):
    """
    Record when expected observations exceed a specific threshold.

    :param thresh_monitor: an instance of :class:`.ThresholdMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, thresh_monitor, name='exceed_threshold', fs_only=True):
        super(ExceedThreshold, self).__init__(name)
        self.__monitor = thresh_monitor
        self.__fs_only = fs_only
        self.__bins = None

    def monitors(self):
        return [self.__monitor]

    def define_bins(self, params, start, end, bin_width):
        """
        Divide the time scale into a finite number of bins.

        This table will record the (weighted) proportion of particles that
        first exceeded the threshold in each of these bins.
        Note that the bins **must** be defined before this table can be used.

        :param params: The simulation parameters.
        :param start: The time that marks the start of the first bin.
        :param end: The time that marks the end of the last bin.
        :param bin_width: The **scalar** bin width.
        """
        self.__bins = []
        time_scale = params['time']
        bin_start = start
        while bin_start < end:
            bin_end = time_scale.add_scalar(bin_start, bin_width)
            self.__bins.append((bin_start, bin_end))
            bin_start = bin_end

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        # Encode units into bytes, for HDF5 storage.
        self.__obs_units = {o['unit']: pypfilt.text.to_bytes(o['unit'])
                            for o in obs_list}
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        week_start = params['time'].dtype('week_start')
        prob = ('prob', np.float64)
        return [unit, period, fs_date, week_start, prob]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if self.__bins is None:
            raise ValueError('The week bins have not been defined')
        if forecasting or not self.__fs_only:
            self.__end_date = end_date
            return len(self.__bins) * n_sys
        else:
            self.__end_date = None
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_enc = self.__params['time'].to_dtype(fs_date)
        for (u, p) in obs_types:
            u_bs = self.__obs_units[u]
            dates = self.__monitor.exceed_date[u, p]
            exceed_mask = self.__monitor.exceed_mask[u, p]
            dates[~ exceed_mask] = self.__end_date
            weights = self.__monitor.exceed_weight
            for (wk_start, wk_end) in self.__bins:
                mask = (dates >= wk_start) & (dates < wk_end) & exceed_mask
                prob = np.sum(weights[mask])
                wk_start_enc = self.__params['time'].to_dtype(wk_start)
                row = (u_bs, p, fs_date_enc, wk_start_enc, prob)
                insert_fn(row)


class PeakForecastEnsembles(Table):
    """
    Record the weighted ensemble of peak size and time predictions for each
    forecasting simulation.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, name='peak_ensemble', fs_only=True):
        Table.__init__(self, name)
        self.__monitor = peak_monitor
        self.__fs_only = fs_only

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = obs_types(params, obs_list)
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        weight = ('weight', np.float64)
        date = params['time'].dtype('date')
        value = ('value', np.float64)
        return [unit, period, fs_date, weight, date, value]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return self.__params['size'] * n_sys
        elif self.__fs_only:
            return 0
        else:
            return self.__params['size'] * n_sys

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_bs = pypfilt.text.to_bytes(fs_date)

        for (u, p) in obs_types:
            # Save the peak time and size ensembles.
            u_bs = self.__obs_units[u]
            for ix in range(self.__params['size']):
                pk_date = self.__monitor.peak_date[u, p][ix]
                row = (u_bs, p, fs_date_bs,
                       self.__monitor.peak_weight[u, p][ix],
                       self.__params['time'].to_dtype(pk_date),
                       self.__monitor.peak_size[u, p][ix])
                insert_fn(row)


class PeakForecastCIs(Table):
    """
    Record fixed-probability central credible intervals for the peak size and
    time predictions.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param probs: an array of probabilities that define the size of each
        central credible interval.
        The default value is ``numpy.uint8([0, 50, 90, 95, 99, 100])``.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, probs=None, name='peak_cints'):
        Table.__init__(self, name)
        if probs is None:
            probs = np.uint8([0, 50, 90, 95, 99, 100])
        self.__probs = probs
        self.__monitor = peak_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = obs_types(params, obs_list)
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        prob = ('prob', np.int8)
        s_min = ('sizemin', np.float64)
        s_max = ('sizemax', np.float64)
        t_min = params['time'].dtype('timemin')
        t_max = params['time'].dtype('timemax')
        return [unit, period, fs_date, prob, s_min, s_max, t_min, t_max]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            # Need a row for each interval, for each observation system.
            return len(self.__probs) * n_sys
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for (u, p) in obs_types:
            # Calculate the confidence intervals for peak time and size.
            sz_ints = stats.cred_wt(
                self.__monitor.peak_size[u, p],
                self.__monitor.peak_weight[u, p],
                self.__probs)
            tm_ints = stats.cred_wt(
                self.__monitor.peak_time[u, p],
                self.__monitor.peak_weight[u, p],
                self.__probs)

            # Convert from days (from the forecast date) to byte strings.
            def enc(days):
                """Convert peak times from days (as measured from the
                forecast date) to encoded NumPy values."""
                dt = self.__params['time'].add_scalar(fs_date, days)
                return self.__params['time'].to_dtype(dt)

            u_bs = self.__obs_units[u]
            for pctl in self.__probs:
                row = (u_bs, p, fs_date_enc, pctl, sz_ints[pctl][0],
                       sz_ints[pctl][1], enc(tm_ints[pctl][0]),
                       enc(tm_ints[pctl][1]))
                insert_fn(row)


class PeakSizeAccuracy(Table):
    """
    Record the accuracy of the peak size predictions against multiple accuracy
    tolerances.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    :param toln: The accuracy thresholds for peak size predictions, expressed
        as percentages of the true size.
        The default is ``np.array([10, 20, 25, 33])``.
    """

    def __init__(self, peak_monitor, name='peak_size_acc', toln=None):
        Table.__init__(self, name)
        if toln is None:
            toln = np.array([10, 20, 25, 33])
        self.__toln = toln
        self.__num_toln = len(toln)
        self.__monitor = peak_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = obs_types(params, obs_list)
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        toln = ('toln', np.float64)
        acc = ('acc', np.float64)
        var = ('var', np.float64)
        savg = ('avg', np.float64)
        return [unit, period, fs_date, toln, acc, var, savg]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return self.__num_toln * n_sys
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        obs_peaks = self.__monitor.peak_obs
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for (u, p) in obs_types:
            # Summarise the peak size distribution.
            sop_avg, sop_var = stats.avg_var_wt(
                self.__monitor.peak_size[u, p],
                self.__monitor.peak_weight[u, p])
            # Calculate the relative size of each forecast peak.
            sop_rel = self.__monitor.peak_size[u, p] / obs_peaks[(u, p)][0]

            u_bs = self.__obs_units[u]
            for pcnt in self.__toln:
                # Sum the weights of the "accurate" particles.
                sop_min, sop_max = 1 - pcnt / 100.0, 1 + pcnt / 100.0
                sop_mask = np.logical_and(sop_rel >= sop_min,
                                          sop_rel <= sop_max)
                accuracy = np.sum(self.__monitor.peak_weight[u, p][sop_mask])
                row = (u_bs, p, fs_date_enc, pcnt, accuracy, sop_var, sop_avg)
                insert_fn(row)


class PeakTimeAccuracy(Table):
    """
    Record the accuracy of the peak time predictions against multiple accuracy
    tolerances.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    :param toln: The accuracy thresholds for peak time predictions, expressed
        as numbers of days. The default is ``np.array([7, 10, 14])``.
    """

    def __init__(self, peak_monitor, name='peak_time_acc', toln=None):
        Table.__init__(self, name)
        if toln is None:
            toln = np.array([7, 10, 14])
        self.__toln = toln
        self.__num_toln = len(toln)
        self.__monitor = peak_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = obs_types(params, obs_list)
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        toln = ('toln', np.float64)
        acc = ('acc', np.float64)
        var = ('var', np.float64)
        tavg = params['time'].dtype('avg')
        return [unit, period, fs_date, toln, acc, var, tavg]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return self.__num_toln * n_sys
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        obs_peaks = self.__monitor.peak_obs
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for (u, p) in obs_types:
            top_true = obs_peaks[(u, p)][1]
            dtp_true = self.__monitor.days_to(top_true)
            # Summarise the peak size distribution.
            dtp_avg, dtp_var = stats.avg_var_wt(
                self.__monitor.peak_time[u, p],
                self.__monitor.peak_weight[u, p])
            # Convert the mean time of peak to a time value.
            top_avg = self.__params['time'].add_scalar(fs_date, dtp_avg)
            top_avg_enc = self.__params['time'].to_dtype(top_avg)

            # Calculate peak time statistics.
            u_bs = self.__obs_units[u]
            for days in self.__toln:
                # Sum the weights of the "accurate" particles.
                # Note: Shaman et al. defined accuracy as +/- one week.
                dtp_diff = dtp_true - self.__monitor.peak_time[u, p]
                dtp_mask = np.fabs(dtp_diff) <= (days + 0.5)
                accuracy = np.sum(self.__monitor.peak_weight[u, p][dtp_mask])
                row = (u_bs, p, fs_date_enc, days, accuracy, dtp_var,
                       top_avg_enc)
                insert_fn(row)


class ExpectedObs(Table):
    """
    Record fixed-probability central credible intervals for the expected
    observations.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param probs: an array of probabilities that define the size of each
        central credible interval.
        The default value is ``numpy.uint8([0, 50, 90, 95, 99, 100])``.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, probs=None, name='expected_obs'):
        Table.__init__(self, name)
        if probs is None:
            probs = np.uint8([0, 50, 90, 95, 99, 100])
        self.__probs = probs
        self.__monitor = peak_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        date = params['time'].dtype('date')
        prob = ('prob', np.int8)
        ymin = ('ymin', np.float64)
        ymax = ('ymax', np.float64)
        return [unit, period, fs_date, date, prob, ymin, ymax]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        # Need a row for each interval, for each day, for each data source.
        return len(self.__probs) * n_days * n_sys

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        exp_obs = self.__monitor.expected_obs
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for (unit, period) in obs_types:
            exp_sys = exp_obs[(unit, period)]

            unit_bs = self.__obs_units[unit]
            for date, ix, _ in dates:
                date_enc = self.__params['time'].to_dtype(date)
                cinfs = stats.cred_wt(exp_sys[ix, :], weights[ix, :],
                                      self.__probs)
                for cix, pctl in enumerate(self.__probs):
                    row = (unit_bs, period, fs_date_enc, date_enc, pctl,
                           cinfs[pctl][0], cinfs[pctl][1])
                    insert_fn(row)


class PredictiveCIs(Table):
    """
    Record fixed-probability central credible intervals for the observations.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param probs: an array of probabilities that define the size of each
        central credible interval.
        The default value is ``numpy.uint8([0, 50, 95])``.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, probs=None, name='forecasts'):
        Table.__init__(self, name)
        if probs is None:
            probs = np.uint8([0, 50, 95])
        self.__probs = np.sort(probs)
        self.__monitor = peak_monitor
        qtl_prs = self.__probs.astype(float) / 100
        qtl_lwr = 0.5 - 0.5 * qtl_prs
        qtl_upr = 0.5 + 0.5 * qtl_prs
        self.__qtls = np.sort(np.unique(np.r_[qtl_lwr, qtl_upr]))

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = params['time'].dtype('fs_date')
        date = params['time'].dtype('date')
        prob = ('prob', np.int8)
        ymin = ('ymin', np.float64)
        ymax = ('ymax', np.float64)
        return [unit, period, fs_date, date, prob, ymin, ymax]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        # Need a row for each interval, for each day, for each data source.
        return len(self.__probs) * n_days * n_sys

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        exp_obs = self.__monitor.expected_obs
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for (unit, period) in obs_types:
            exp_sys = exp_obs[(unit, period)]
            unit_bs = self.__obs_units[unit]
            op = self.__params['obs'][unit]
            obs_model = op['obs_model']

            for date, ix, _ in dates:
                date_enc = self.__params['time'].to_dtype(date)
                mu = exp_sys[ix, :]
                ws = weights[ix, :]
                # Quantiles are ordered from smallest to largest.
                qtls = obs_model.quantiles(op, date, mu, ws, self.__qtls)
                # Iterate from broadest to narrowest CI.
                for ix, pr in enumerate(self.__probs[::-1]):
                    row = (unit_bs, period, fs_date_enc, date_enc, pr,
                           qtls[ix], qtls[- (ix + 1)])
                    insert_fn(row)


class ObsLikelihood(Table):
    """
    Record the likelihood of each observation according to each particle.
    Note that this table registers its ``record_obs_llhd`` method in the
    parameter dictionary so that it can obtain the observation likelihoods.

    :param name: the name of the table in the output file.
    :param extra_obs: Observations that will **not** be used in the filtering
        process, but whose likelihoods are of interest.
    """

    def __init__(self, name='obs_llhd', extra_obs=None):
        Table.__init__(self, name)
        self.__rnd = np.random.RandomState(seed=2073010)
        self.__fs_date = None
        if extra_obs is None:
            extra_obs = []
        self.__extra_obs = extra_obs

    def install_hook(self, params):
        hook_key = 'record_log_llhd_fns'
        hook_fn = self.record_obs_llhd
        if hook_key not in params['epifx']:
            params['epifx'][hook_key] = [hook_fn]
        elif hook_fn not in params['epifx'][hook_key]:
            params['epifx'][hook_key].append(hook_fn)

    def dtype(self, params, obs_list):
        self.__params = params
        if self.__extra_obs:
            self.__all_obs = obs_list + self.__extra_obs
        else:
            self.__all_obs = obs_list
        # Build a date-indexed table of observations.
        self.__obs_tbl = {}
        for o in self.__all_obs:
            if o['date'] in self.__obs_tbl:
                self.__obs_tbl[o['date']].append(o)
            else:
                self.__obs_tbl[o['date']] = [o]
        self.__obs_dates = set(self.__obs_tbl)
        self.__obs_units = obs_units(params, obs_list)
        if not self.__obs_units:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation units could be identified")
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        # Encode source into bytes, for HDF5 storage.
        self.__obs_srcs = {o['source']: pypfilt.text.to_bytes(o['source'])
                           for o in self.__all_obs}
        if not self.__obs_srcs:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation sources could be identified")
        slen = max(len(bs) for source, bs in self.__obs_srcs.items())
        # Ensure the hook has been installed.
        self.install_hook(params)
        fs_date = params['time'].dtype('fs_date')
        date = params['time'].dtype('date')
        value = ('value', np.float64)
        llhd = ('llhd', np.float64)
        std_err = ('std_err', np.float64)
        forecast = ('forecast', np.bool)
        unit = ('unit', 'S{}'.format(ulen))
        source = ('source', 'S{}'.format(slen))
        return [fs_date, unit, source, date, value, llhd, std_err, forecast]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        self.__data = []
        self.__forecasting = forecasting
        self.__start_date = start_date
        if forecasting:
            # Forecasting from the start of the simulation period.
            self.__fs_date = start_date
        else:
            # Not forecasting, so all observations are included.
            self.__fs_date = end_date
        self.__fs_date_enc = self.__params['time'].to_dtype(self.__fs_date)
        # Need a row for each observation in the simulation period.
        n_rows = len([o for o in self.__all_obs
                      if o['date'] > start_date and o['date'] <= end_date])
        return n_rows

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        # Ensure we have received the entire particle history matrix.
        check.is_entire_matrix(self.__params, hist)
        # Each observation must be considered separately, as they may or may
        # not be used in the filtering process.
        for (d, d_ix, hist_ix) in dates:
            # Important: ignore the start of the simulation period.
            if d <= self.__start_date:
                continue
            # Identify observations for this date that are not being filtered.
            obs = [o for o in self.__obs_tbl.get(d, [])
                   if self.__forecasting or o in self.__extra_obs]
            if obs:
                # This will trigger the record_obs_llhd hook.
                pypfilt.log_llhd_of(self.__params, hist, hist_ix, obs)

    def record_obs_llhd(self, obs, log_llhds, weights):
        if self.__fs_date is None:
            # A forecast may be preceded by an estimation run from the most
            # recent known-good state, and we may only be interested in
            # recording summary statistics for the forecasting simulations.
            return
        # Resample to obtain a random sample from the correct density.
        params = {'resample': {
            'method': 'basic',
            'regularisation': False,
            'rnd': self.__rnd}}
        px = np.array([weights, np.zeros(weights.shape)]).T
        pypfilt.resample(params, px)
        # Retrieve the resampled particle indices.
        sample_ixs = px[:, -1].astype(int)
        # Retrieve the weight (identical for each particle).
        wt = px[0, -2]
        # Convert from log likelihoods to likelihoods.
        probs = np.exp(log_llhds[sample_ixs])
        # Calculate the mean and standard error.
        pr_mean = np.mean(probs)
        pr_serr = np.var(probs) / wt
        # Generate a corresponding row to record later.
        unit_bs = self.__obs_units[obs['unit']]
        src_bs = self.__obs_srcs[obs['source']]
        date_enc = self.__params['time'].to_dtype(obs['date'])
        row = (self.__fs_date_enc, unit_bs, src_bs, date_enc,
               obs['value'], pr_mean, pr_serr, self.__forecasting)
        self.__data.append(row)

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        for row in self.__data:
            insert_fn(row)
        self.__fs_date = None


class Obs(Table):
    """
    Record each observation with a given observation unit.
    """

    def __init__(self, obs_units):
        self.units = obs_units
        Table.__init__(self, 'obs/{}'.format(self.units))
        self.__units_bs = pypfilt.text.to_bytes(self.units)

    def __converter_for(self, params, key, obs_list):
        """
        Return a ``(dtype, conversion_fn)`` tuple that defines the column name
        and type (``dtype``) and the conversion function from the native
        Python type to the NumPy column type (``conversion_fn``).
        """
        v = obs_list[0][key]
        if key == 'date':
            # Use the time scale to convert observation times.
            return (params['time'].dtype(key), params['time'].to_dtype)
        elif hasattr(v, 'dtype') and isinstance(v.dtype, np.dtype):
            return ((key, v.dtype), lambda x: x)
        elif isinstance(v, int):
            return ((key, np.int64), lambda x: x)
        elif isinstance(v, float):
            return ((key, np.float64), lambda x: x)
        elif pypfilt.text.is_bytes(v):
            max_len = max(len(o[key] for o in obs_list))
            return ((key, 'S{}'.format(max_len)), lambda x: x)
        elif pypfilt.text.is_unicode(v):
            max_len = max(len(pypfilt.text.to_bytes(o[key])
                              for o in obs_list))
            return ((key, 'S{}'.format(max_len)), pypfilt.text.to_bytes)
        else:
            raise ValueError('No automatic conversion for {}'.format(type(v)))

    def dtype(self, params, obs_list):
        self.__written = False
        self.__params = params
        self.__obs_list = [o for o in obs_list if o['unit'] == self.units]
        ulen = len(self.__units_bs)
        self.__obs_srcs = {o['source']: pypfilt.text.to_bytes(o['source'])
                           for o in self.__obs_list}
        if not self.__obs_srcs:
            # Provide a more meaningful message than max() complaining about
            # an empty sequence.
            raise ValueError("No observation sources could be identified")
        slen = max(len(bs) for source, bs in self.__obs_srcs.items())
        # Define the column types.
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        source = ('source', 'S{}'.format(slen))
        year = ('year', np.int)
        date = params['time'].dtype('date')
        # Observation values (and upper bounds) may already have a NumPy data
        # type (e.g., if they were read using a NumPy routine such as loadtxt)
        # but this is not guaranteed to be the case (e.g., if they were read
        # from a JSON file).
        v = self.__obs_list[0]['value']
        if hasattr(v, 'dtype') and isinstance(v.dtype, np.dtype):
            val_dtype = v.dtype
        elif type(v) in [int, float]:
            # Note that we don't support other native Python types.
            # For example, string fields require the maximum capacity to be
            # specified, so we need to know ahead of time how much space to
            # reserve (similar to the observation unit and source).
            # If insufficient capacity is allocated, strings are truncated
            # without any warning.
            val_dtype = type(v)
        else:
            raise ValueError('Cannot infer dtype for {}'.format(type(v)))
        value = ('value', val_dtype)
        upper = ('upper_bound', val_dtype)
        incomplete = ('incomplete', np.bool)
        dtype = [unit, period, source, year, date, value, incomplete, upper]
        # Identify additional fields that are defined in *all* observations.
        fields = reduce(lambda x, y: x and y,
                        ({k for k in o} for o in self.__obs_list))
        self.__extra_fields = sorted(fields - set(col[0] for col in dtype))
        self.__convert_field = {}
        # Determine the dtype and necessary conversion functions.
        for field in self.__extra_fields:
            f_type, f_conv_fn = self.__converter_for(params, field, obs_list)
            dtype += (f_type,)
            self.__convert_field[field] = f_conv_fn
        return dtype

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if self.__written:
            # Only record the observations once per simulation.
            return 0
        else:
            return len(self.__obs_list)

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        # Add all of the rows in finished(), below.
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        for o in self.__obs_list:
            unit_bs = self.__units_bs
            src_bs = self.__obs_srcs[o['source']]
            date_enc = self.__params['time'].to_dtype(o['date'])
            incomplete = 'incomplete' in o and o['incomplete']
            if 'upper_bound' in o:
                upper = o['upper_bound']
            else:
                upper = 0
            # Allow observations to identify their year (i.e., season).
            if hasattr(o['date'], 'year'):
                year = o.get('year', o['date'].year)
            else:
                try:
                    year = o['year']
                except KeyError:
                    raise ValueError("observation has no year: {}".format(o))
            row = (unit_bs, o['period'], src_bs, year, date_enc, o['value'],
                   incomplete, upper)
            # Add each additional field, converting values as required.
            for field in self.__extra_fields:
                if field in o:
                    row += (self.__convert_field[field](o[field]),)
                else:
                    msg = "Observation at {} does not define '{}'"
                    raise ValueError(msg.format(o['date'], field))
            insert_fn(row)
        self.__written = True


class Metadata(pypfilt.summary.Metadata):
    """
    Document the simulation parameters and system environment for a set of
    simulations. This extends the default ``pypfilt`` black-list to ignore
    parameters specific to ``epifx``.
    """

    def __init__(self):
        super(Metadata, self).__init__()
        self.ignore_dict['epifx'] = {
            'rnd': None,
            'record_log_llhd_fns': None,
        }
        self.ignore_dict['obs'] = {
            None: {'obs_model': None},
        }

    def build(self, params, pkgs=None):
        """
        Construct a metadata dictionary that documents the simulation
        parameters and system environment.

        :param params: The simulation parameters.
        :param pkgs: A dictionary that maps package names to modules that
            define appropriate ``__version__`` attributes, used to record the
            versions of additional relevant packages.
        """
        from . import version

        if pkgs is None:
            pkgs = {}
        pkgs['epifx'] = version

        metadata = super(Metadata, self).build(params, pkgs=pkgs)

        # Record whether temporal forcing was used, rather than storing a
        # string representation of the forcing function (if any).
        with_forcing = 'forcing' in metadata['param']['epifx']
        metadata['param']['epifx']['forcing'] = with_forcing

        return metadata


def make(params, all_obs, default=True, extra_tbls=None, pkgs=None, **kwargs):
    """
    A convenience function that collects all of the summary statistics defined
    in the ``pypfilt.summary`` and ``epifx.summary`` modules.

    :param params: The simulation parameters.
    :param all_obs: A list of all observations.
    :param default: Whether to add all of the tables defined in the
        ``pypfilt.summary`` and ``epifx.summary`` modules.
    :param extra_tbls: A list of extra summary statistic tables to include.
    :param pkgs: A dictionary of python modules whose versions should be
        recorded in the simulation metadata. By default, all of the modules
        recorded by ``pypfilt.summary.Metadata`` are included, as is the
        ``epifx`` package itself.
    :param \**kwargs: Extra arguments to pass to ``pypfilt.summary.HDF5``.

    For example:

    .. code-block:: python

       from epifx.summary import make
       params = ...
       all_obs = ...
       stats = make(params, all_obs, first_day=True, only_fs=True)
    """

    meta = Metadata()
    metadata = meta.build(params, pkgs=pkgs)
    summary = pypfilt.summary.HDF5(params, all_obs, meta=metadata, **kwargs)

    peaks = PeakMonitor()
    if default:
        tbls = [
            pypfilt.summary.ModelCIs(),
            pypfilt.summary.ParamCovar(),
            PrOutbreak(),
            PredictiveCIs(peaks),
            ObsLikelihood(),
            PeakSizeAccuracy(peaks),
            PeakTimeAccuracy(peaks),
            PeakForecastCIs(peaks),
            PeakForecastEnsembles(peaks),
        ]
    else:
        tbls = []
    for obs_unit in params['obs']:
        tbls.append(Obs(obs_unit))
    if extra_tbls:
        tbls.extend(extra_tbls)

    summary.add_tables(*tbls)
    return summary
