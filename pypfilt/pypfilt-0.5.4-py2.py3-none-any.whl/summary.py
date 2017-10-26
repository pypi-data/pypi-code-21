"""Calculation of simulation summary statistics."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import abc
import h5py
import locale
import logging
import numpy as np
import subprocess
import sys

from . import check
from . import text
from . import version


def dtype_unit(obs_list, name='unit'):
    """The dtype for columns that store observation units."""
    return (name, 'S{}'.format(max(len(o['unit']) for o in obs_list)))


def dtype_period(name='period'):
    """The dtype for columns that store observation periods."""
    return (name, np.int8)


def dtype_value(value, name='value'):
    """The dtype for columns that store observation values."""
    if hasattr(value, 'dtype'):
        value_dtype = value.dtype
    elif isinstance(value, int):
        value_dtype = np.dtype(int)
    elif isinstance(value, float):
        value_dtype = np.dtype(float)
    else:
        raise ValueError("no dtype for observed value {}".format(value))

    return (name, value_dtype)


def dtype_names_to_str(dtypes, encoding='utf-8'):
    """
    Ensure that dtype field names are native strings, as
    `required <https://github.com/numpy/numpy/issues/2407>`__ by NumPy.
    Unicode strings are not valid field names in Python 2, and this can cause
    problems when using Unicode string literals.

    :param dtypes: A list of fields where each field is either a string, or a
        tuple of length 2 or 3 (see the NumPy
        `docs <http://docs.scipy.org/doc/numpy-1.8.0/reference/arrays.dtypes.html#index-9>`__
        for details).
    :param encoding: The encoding for converting Unicode strings to native
        strings in Python 2.
    :return: A list of fields, where each field name is a native string
        (``str`` type).
    :raises ValueError: If a name cannot be converted to a native string.
    """

    PY2 = sys.version_info[0] == 2

    def str_name(value):
        if isinstance(value, str):
            return value
        elif PY2 and isinstance(value, unicode):
            return value.encode(encoding)
        elif not PY2 and isinstance(value, bytes):
            return value.decode(encoding)
        else:
            raise ValueError("Invalid column name '{!r}'".format(value))

    # Inspect the first element to see if we have a list of strings or tuples.
    if isinstance(dtypes[0], tuple):
        return [(str_name(dtype[0]),) + dtype[1:] for dtype in dtypes]
    else:
        return [str_name(dtype) for dtype in dtypes]


# Create a new metaclass for abstract base classes (ABCs), so that subclasses
# can only be instantiated if they implement all of the abstract methods.
# The metaclass syntax differs between Python 2 and 3, the following line is
# the simplest way to sidestep this issue without relying on ``six``.
ABC = abc.ABCMeta(str('ABC'), (object,), {})


class Table(ABC):
    """
    The base class for summary statistic tables.

    Tables are used to record rows of summary statistics as a simulation
    progresses.

    :param name: the name of the table in the output file.
    """

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def dtype(self, params, obs_list):
        """
        Return the column names and data types, represented as a list of
        ``(name, data type)`` tuples. See the NumPy documentation for details.

        :param params: The simulation parameters.
        :param obs_list: A list of all observations.
        """
        pass

    @abc.abstractmethod
    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        """
        Return the number of rows required for a single simulation.

        :param start_date: The date at which the simulation starts.
        :param end_date: The date at which the simulation ends.
        :param n_days: The number of days for which the simulation runs.
        :param n_sys: The number of observation systems (i.e., data sources).
        :param forecasting: ``True`` if this is a forecasting simulation,
            otherwise ``False``.
        """
        pass

    @abc.abstractmethod
    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        """
        Record rows of summary statistics for some portion of a simulation.

        :param hist: The particle history matrix.
        :param weights: The weight of each particle at each date in the
            simulation window; it has dimensions ``(d, p)`` for ``d`` days and
            ``p`` particles.
        :param fs_date: The forecasting date; if this is not a forecasting
            simulation, this is the date at which the simulation ends.
        :param dates: A list of ``(datetime, ix, hist_ix)`` tuples that
            identify each day in the simulation window, the index of that day
            in the simulation window, and the index of that day in the
            particle history matrix.
        :param obs_types: A set of ``(unit, period)`` tuples that identify
            each observation system from which observations have been taken.
        :param insert_fn: A function that inserts one or more rows into the
            underlying data table; see the examples below.

        The row insertion function can be used as follows:

        .. code-block:: python

           # Insert a single row, represented as a tuple.
           insert_fn((x, y, z))
           # Insert multiple rows, represented as a list of tuples.
           insert_fn([(x0, y0, z0), (x1, y1, z1)], n=2)
        """
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        """
        Record rows of summary statistics at the end of a simulation.

        The parameters are as per :meth:`.add_rows`.

        Derived classes should only implement this method if rows must be
        recorded by this method; the provided method does nothing.
        """
        pass

    def monitors(self):
        """
        Return a list of monitors required by this Table.

        Derived classes should implement this method if they require one or
        more monitors; the provided method returns an empty list.
        """
        return []


class Monitor(ABC):
    """
    The base class for simulation monitors.

    Monitors are used to calculate quantities that:

    * Are used by multiple Tables (i.e., avoiding repeated computation); or
    * Require a complete simulation for calculation (as distinct from Tables,
      which incrementally record rows as a simulation progresses).

    The quantities calculated by a Monitor can then be recorded by
    :meth:`.Table.add_rows` and/or :meth:`.Table.finished`.
    """

    def prepare(self, params, obs_list):
        """
        Perform any required preparation prior to a set of simulations.

        :param params: The simulation parameters.
        :param obs_list: A list of all observations.
        """
        pass

    def begin_sim(self, start_date, end_date, n_days, n_sys, forecasting):
        """
        Perform any required preparation at the start of a simulation.

        :param start_date: The date at which the simulation starts.
        :param end_date: The date at which the simulation ends.
        :param n_days: The number of days for which the simulation runs.
        :param n_sys: The number of observation systems (i.e., data sources).
        :param forecasting: ``True`` if this is a forecasting simulation,
            otherwise ``False``.
        """
        pass

    @abc.abstractmethod
    def monitor(self, hist, weights, fs_date, dates, obs_types):
        """
        Monitor the simulation progress.

        :param hist: The particle history matrix.
        :param weights: The weight of each particle at each date in the
            simulation window; it has dimensions ``(d, p)`` for ``d`` days and
            ``p`` particles.
        :param fs_date: The forecasting date; if this is not a forecasting
            simulation, this is the date at which the simulation ends.
        :param dates: A list of ``(datetime, ix, hist_ix)`` tuples that
            identify each day in the simulation window, the index of that day
            in the simulation window, and the index of that day in the
            particle history matrix.
        :param obs_types: A set of ``(unit, period)`` tuples that identify
            each observation system from which observations have been taken.
        """
        pass

    def end_sim(self, hist, weights, fs_date, dates, obs_types):
        """
        Finalise the data as required for the relevant summary statistics.

        The parameters are as per :meth:`.monitor`.

        Derived classes should only implement this method if finalisation of
        the monitored data is required; the provided method does nothing.
        """
        pass

    @abc.abstractmethod
    def load_state(self, grp):
        """
        Load the monitor state from a cache file.

        :param grp: The h5py Group object from which to load the state.
        """
        pass

    @abc.abstractmethod
    def save_state(self, grp):
        """
        Save the monitor state to a cache file.

        :param grp: The h5py Group object in which to save the state.
        """
        pass


class ParamCovar(Table):
    """
    Calculate the covariance between all pairs of model parameters during each
    simulation.

    :param name: the name of the table in the output file.
    """

    def __init__(self, name='param_covar'):
        Table.__init__(self, name)

    def dtype(self, params, obs_list):
        self.__params = params
        # Only calculate covariances between model parameters that admit
        # continuous kernels.
        details = params['model'].describe()
        self.__param_info = [(n, ix)
                             for (ix, (n, smooth, _, _)) in enumerate(details)
                             if smooth]
        self.__param_names = [text.to_bytes(info[0])
                              for info in self.__param_info]
        self.__num_params = len(self.__param_info)
        nlen = max(len(info[0]) for info in self.__param_info)

        fs_date = params['time'].dtype('fs_date')
        date = params['time'].dtype('date')
        param1 = ('param1', 'S{}'.format(nlen))
        param2 = ('param2', 'S{}'.format(nlen))
        covar = ('covar', np.float64)
        return [fs_date, date, param1, param2, covar]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        num_params = len(self.__param_info)
        return n_days * num_params * (num_params - 1) // 2

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        from . import stats

        num_params = len(self.__param_info)
        fs_date_enc = self.__params['time'].to_dtype(fs_date)

        for date, ix, hist_ix in dates:
            date_enc = self.__params['time'].to_dtype(date)
            min_ix = min(info[1] for info in self.__param_info)
            max_ix = max(info[1] for info in self.__param_info)
            x = hist[hist_ix, :, min_ix:max_ix + 1]
            covars = stats.cov_wt(x, weights[ix, :])
            for ix1 in range(num_params):
                name1 = self.__param_names[ix1]
                for ix2 in range(ix1 + 1, num_params):
                    name2 = self.__param_names[ix2]
                    row = (fs_date_enc, date_enc, name1, name2,
                           covars[ix1, ix2])
                    insert_fn(row)


class ModelCIs(Table):
    """
    Calculate fixed-probability central credible intervals for all state
    variables and model parameters.

    :param probs: an array of probabilities that define the size of each
        central credible interval.
        The default value is ``numpy.uint8([0, 50, 90, 95, 99, 100])``.
    :param name: the name of the table in the output file.
    """

    def __init__(self, probs=None, name='model_cints'):
        Table.__init__(self, name)
        if probs is None:
            probs = np.uint8([0, 50, 90, 95, 99, 100])
        self.__probs = probs

    def dtype(self, params, obs_list):
        self.__params = params
        details = params['model'].describe()
        self.__sv_info = [(info[0], ix) for (ix, info) in enumerate(details)]
        self.__stat_info = params['model'].stat_info()
        self.__num_stats = len(self.__sv_info) + len(self.__stat_info)

        # Determine the length (in *bytes*) of the longest name.
        all_info = self.__sv_info + self.__stat_info
        self.__name_bytes = {info[0]: text.to_bytes(info[0])
                             for info in all_info}
        nlen = max(len(bs) for n, bs in self.__name_bytes.items())

        fs_date = params['time'].dtype('fs_date')
        date = params['time'].dtype('date')
        prob = ('prob', np.int8)
        ymin = ('ymin', np.float64)
        ymax = ('ymax', np.float64)
        # State variables/parameters ('model') or statistics ('stat').
        value_type = ('type', 'S5')
        name = ('name', 'S{}'.format(nlen))
        return [fs_date, date, prob, ymin, ymax, value_type, name]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        # Need a row for each interval, for each day, for each parameter,
        # variable and statistic.
        return len(self.__probs) * n_days * self.__num_stats

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        from . import stats

        fs_date_enc = self.__params['time'].to_dtype(fs_date)
        for date, ix, hist_ix in dates:
            date_enc = self.__params['time'].to_dtype(date)

            # Identify which state vectors to examine.
            valid = self.__params['model'].is_valid(hist[hist_ix])
            # Note that np.where() returns a *tuple*  of arrays (one for
            # each dimension) and we're only scanning a 1D array.
            mask = np.where(valid)[0]

            if np.count_nonzero(mask):
                ws = weights[ix, mask]
                for (lbl, vix) in self.__sv_info:
                    val = self.__name_bytes[lbl]
                    sub_hist = hist[hist_ix, mask, vix]
                    cred_ints = stats.cred_wt(sub_hist, ws, self.__probs)
                    for cix, pctl in enumerate(self.__probs):
                        row = (fs_date_enc, date_enc, pctl,
                               cred_ints[pctl][0], cred_ints[pctl][1],
                               'model', val)
                        insert_fn(row)
                for (lbl, stat_fn) in self.__stat_info:
                    val = self.__name_bytes[lbl]
                    stat_vec = stat_fn(hist[hist_ix, mask])
                    cred_ints = stats.cred_wt(stat_vec, ws, self.__probs)
                    for cix, pctl in enumerate(self.__probs):
                        row = (fs_date_enc, date_enc, pctl,
                               cred_ints[pctl][0], cred_ints[pctl][1],
                               'stat', val)
                        insert_fn(row)
            else:
                for pctl in self.__probs:
                    for (lbl, _) in self.__sv_info:
                        val = self.__name_bytes[lbl]
                        row = (fs_date_enc, date_enc, pctl, 0, 0,
                               'model', val)
                        insert_fn(row)
                    for (lbl, _) in self.__stat_info:
                        val = self.__name_bytes[lbl]
                        row = (fs_date_enc, date_enc, pctl, 0, 0, 'stat', val)
                        insert_fn(row)


class Obs(Table):
    """
    Record the basic details of each observation; the columns are: ``'unit',
    'period', 'source', 'date', 'value', 'incomplete', 'upper_bound'``.
    """

    def __init__(self, name='obs'):
        Table.__init__(self, name)

    def dtype(self, params, obs_list):
        self.__written = False
        self.__obs_list = obs_list
        self.__params = params
        obs_srcs = {o['source'] for o in obs_list}
        obs_units = {o['unit'] for o in obs_list}
        self.__obs_src_bs = {k: text.to_bytes(k) for k in obs_srcs}
        self.__obs_unit_bs = {k: text.to_bytes(k) for k in obs_units}
        slen = max(len(bs) for __, bs in self.__obs_src_bs.items())
        ulen = max(len(bs) for __, bs in self.__obs_unit_bs.items())
        obs_val = self.__obs_list[0]['value']
        dtype = [('unit', 'S{}'.format(ulen)), ('source', 'S{}'.format(slen)),
                 ('period', np.int8), params['time'].dtype('date'),
                 dtype_value(obs_val),
                 ('incomplete', np.bool),
                 dtype_value(obs_val, name='upper_bound')]
        return dtype

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if self.__written:
            return 0
        else:
            return len(self.__obs_list)

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        # Add all of the rows in finished(), below.
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        for o in self.__obs_list:
            unit = self.__obs_unit_bs[o['unit']]
            src = self.__obs_src_bs[o['source']]
            date = self.__params['time'].to_dtype(o['date'])
            inc = o.get('incomplete', False)
            upr = o.get('upper_bound', 0)
            row = (unit, src, o['period'], date, o['value'], inc, upr)
            insert_fn(row)
        self.__written = True


class HDF5(object):
    """
    Save tables of summary statistics to an HDF5 file.

    :param params: The simulation parameters.
    :param obs_list: A list of all observations.
    :param meta: The simulation metadata; by default the output of
        :func:`Metadata.build` is used.
    :param first_day: If ``False`` (the default) statistics are calculated
       from the date of the first *observation*. If ``True``, statistics are
       calculated from the very beginning of the simulation period.
    :param only_fs: If ``False`` (the default) statistics are calculated for
       the initial estimation simulation and for forecasting simulations. If
       ``True``, statistics are only calculated for forecasting simulations.
    """

    def __init__(self, params, obs_list, meta=None, first_day=False,
                 only_fs=False):
        # Store simulation metadata.
        if meta is None:
            meta = Metadata()
            self.__metadata = meta.build(params)
        else:
            self.__metadata = meta

        # Store the observations and simulation parameters.
        self.__all_obs = obs_list
        self.__params = params

        # Allocate variables to store the details of each summary table.
        self.__tbl_dict = {}
        self.__dtypes = {}
        # When a simulation commences, this will be a dictionary that maps
        # table names to NumPy structured arrays; the value of ``None``
        # indicates that no tables have been allocated.
        self.__df = None

        self.__monitors = set()

        self.__data_group = 'data'

        # If True, start statistics at the beginning of the simulation period,
        # otherwise start statistics at the date of the first observation.
        self.__first_day = first_day

        # Determine whether simulation states are being stored persistently.
        using_cache = False
        if 'cache_file' in params['hist']:
            if params['hist']['cache_file'] is not None:
                using_cache = True

        # When a cache file is used, the initial estimation run will stop at
        # the last of the forecasting dates, rather than at the end of the
        # forecasting simulation period (e.g., the end of the season).
        # This means that the forecasting date used to identify the estimation
        # run --- the end date --- will *also* be used to identify a
        # forecasting simulation, and we should prevent this from occurring.
        if using_cache and not only_fs:
            logger = logging.getLogger(__name__)
            logger.warning('A cache file is being used, but only_fs=False')
            logger.warning('Setting only_fs=True, correct this in your code')
            only_fs = True

        # If True, only calculate statistics for forecasting simulations.
        self.__only_fs = only_fs
        # If True when self.__only_fs is True, the current simulation is not a
        # forecasting simulation, and tables should be ignored.
        # Note that monitors are *never* ignored.
        self.__ignore = False

        # Identify all combinations for observation periods and units.
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in self.__all_obs))

    def add_tables(self, *tables):
        """
        Add summary statistic tables that will be included in the output file.
        """
        for tbl in tables:
            if tbl.name in self.__tbl_dict:
                raise ValueError("Table '{}' already exists".format(tbl.name))
            # Add the table to the relevant internal variables.
            self.__tbl_dict[tbl.name] = tbl
            self.__dtypes[tbl.name] = dtype_names_to_str(
                tbl.dtype(self.__params, self.__all_obs))

            # Add the required monitors for this table, if any.
            for mon in tbl.monitors():
                if mon not in self.__monitors:
                    self.__monitors.add(mon)
                    mon.prepare(self.__params, self.__all_obs)

    def load_state(self, grp):
        """
        Load the internal state of each monitor from a cache file.

        :param grp: The h5py Group object from which to load the state.
        """
        grp_names = set()
        for mon in self.__monitors:
            grp_name = mon.__class__.__name__
            if grp_name in grp_names:
                msg = "Multiple {} monitors".format(grp_name)
                raise ValueError(msg)
            else:
                grp_names.add(grp_name)
            mon_grp = grp.require_group(grp_name)
            mon.load_state(mon_grp)

    def save_state(self, grp):
        """
        Save the internal state of each monitor to a cache file.

        :param grp: The h5py Group object in which to save the state.
        """
        grp_names = set()
        for mon in self.__monitors:
            grp_name = mon.__class__.__name__
            if grp_name in grp_names:
                msg = "Multiple {} monitors".format(grp_name)
                raise ValueError(msg)
            else:
                grp_names.add(grp_name)
            mon_grp = grp.require_group(grp_name)
            mon.save_state(mon_grp)

    def allocate(self, start_date, end_date, forecasting=False):
        """Allocate space for the simulation statistics."""
        if self.__df is not None:
            raise ValueError("Tables have already been allocated")

        if self.__only_fs and not forecasting:
            # Flag this simulation as being ignored.
            self.__ignore = True
        else:
            self.__ignore = False

        logger = logging.getLogger(__name__)

        self.__start_date = start_date
        self.__end_date = end_date
        if forecasting:
            # Forecasting from the start of the simulation period.
            self.__fs_date = start_date
        else:
            # Not forecasting, so all observations are included.
            self.__fs_date = end_date

        # Retain only observations that occur during the simulation period.
        def include_obs(d):
            try:
                return start_date <= d <= end_date
            except TypeError:
                raise ValueError("invalid observation date '{}'".format(d))

        fs_obs = [o for o in self.__all_obs if include_obs(o['date'])]

        # Calculate the number of days from the first observation date to the
        # end of the simulation
        obs_dates = sorted(set(o['date'] for o in fs_obs))
        # Either use observation times *or* each time unit.
        steps_per_unit = self.__params['steps_per_unit']
        if self.__first_day:
            t0 = start_date
        else:
            t0 = min(obs_dates)
        self.__all_dates = [t0]
        for (step, time) in self.__params['time'].steps():
            if step % steps_per_unit == 0 and time > t0:
                self.__all_dates.append(time)
        n_days = len(self.__all_dates)
        n_sys = len(self.__obs_types)

        # Notify each monitor, regardless of whether tables are ignored.
        for mon in self.__monitors:
            mon.begin_sim(start_date, end_date, n_days, n_sys, forecasting)

        if self.__ignore:
            logger.debug("Summary.allocate({}, {}): {} points".format(
                start_date, end_date, n_days))
            return

        # Determine the number of rows to allocate for each table.
        # Note: the items() method returns a list in Python 2 and a view
        # object in Python 3; since the number of tables will always be small
        # (on the order of 10) the overhead of using items() in Python 2 and
        # not iteritems() --- which returns an interator --- is negligible.
        n_rows = {n: t.n_rows(start_date, end_date, n_days, n_sys,
                              forecasting)
                  for (n, t) in self.__tbl_dict.items()}
        # Allocate tables that require at least one row.
        self.__df = {tbl: np.empty(n_rows[tbl], dtype=self.__dtypes[tbl])
                     for tbl in n_rows if n_rows[tbl] > 0}
        # Initialise a row counter for each allocated table.
        self.__ix = {tbl: 0 for tbl in self.__df}
        # Create a row insertion function for each allocated table.
        self.__insert = {tbl: self.__insert_row_fn(tbl) for tbl in self.__df}

        logger.debug("Summary.allocate({}, {}): {} points".format(
            start_date, end_date, n_days))

    def __insert_row_fn(self, tbl):
        def insert(fields, n=1):
            row_ix = self.__ix[tbl]
            self.__df[tbl][row_ix:row_ix + n] = fields
            self.__ix[tbl] += n
        return insert

    def summarise(self, hist, sim_time, start_date, end_date, offset):
        """
        Calculate statistics for some portion of the simulation period.

        :param hist: The particle history matrix.
        :param sim_time: The entire simulation period.
        :param start_date: The start of the period to be summarised.
        :param end_date: The end of the period to be summarised.
        :param offset: The history matrix time-step offset.
        """
        if self.__df is None and not self.__ignore:
            raise ValueError("Tables have not been allocated")

        if self.__start_date > start_date or self.__end_date < end_date:
            raise ValueError("Summary.summarise() called for invalid period")

        # Ensure we have received the entire particle history matrix.
        check.is_entire_matrix(self.__params, hist)

        logger = logging.getLogger(__name__)

        dates = [(d, ix, sim_time.step_of(d) + offset)
                 for (ix, d) in enumerate(d for d in self.__all_dates
                                          if start_date <= d <= end_date)]
        num_dates = len(dates)

        logger.debug("Summary.summarise({}, {}): {} dates".format(
            start_date, end_date, num_dates))

        # Record the particle weights.
        weights = np.zeros((num_dates, hist.shape[1]))
        for date, ix, hist_ix in dates:
            weights[ix, :] = hist[hist_ix, :, -2]

        fs_date = self.__fs_date
        obs_types = self.__obs_types

        for mon in self.__monitors:
            mon.monitor(hist, weights, fs_date, dates, obs_types)

        tables = self.__df if self.__df is not None else []

        for tbl in tables:
            insert_fn = self.__insert[tbl]
            self.__tbl_dict[tbl].add_rows(
                hist, weights, fs_date, dates, obs_types, insert_fn)

        if end_date == self.__end_date:
            for mon in self.__monitors:
                mon.end_sim(hist, weights, fs_date, dates, obs_types)

            for tbl in tables:
                insert_fn = self.__insert[tbl]
                self.__tbl_dict[tbl].finished(
                    hist, weights, fs_date, dates, obs_types, insert_fn)

    def get_stats(self):
        """Return the calculated statistics for a single simulation."""
        if self.__df is None:
            if self.__ignore:
                return {}
            else:
                raise ValueError("Tables have not been created")

        logger = logging.getLogger(__name__)
        logger.debug("Summary.get()")

        # Check all table rows are filled (and no further).
        for tbl in self.__df:
            alloc = self.__df[tbl].shape[0]
            used = self.__ix[tbl]
            if alloc != used:
                msg = "Table '{}' allocated {} rows but filled {}"
                raise ValueError(msg.format(tbl, alloc, used))

        # Return the summary tables and remove them from this class instance.
        stats = self.__df
        self.__df = None
        return stats

    def save_forecasts(self, fs, filename):
        """
        Save forecast summaries to disk in the HDF5 binary data format.

        This function creates the following datasets that summarise the
        estimation and forecasting outputs:

        - ``'data/TABLE'`` for each table.

        The provided metadata will be recorded under ``'meta/'``.

        If dataset creation timestamps are enabled, two simulations that
        produce identical outputs will not result in identical files.
        Timestamps will be disabled where possible (requires h5py >= 2.2):

        - ``'hdf5_track_times'``: Presence of creation timestamps.

        :param fs: Simulation outputs, as returned by ``pypfilt.forecast()``.
        :param filename: The filename to which the data will be written.
        """
        fs_dates = [d for d in fs.keys() if d not in ['obs', 'complete']]
        fs_compl = fs_dates[:]
        fs_compl.append('complete')

        # Construct aggregate data tables.
        # Note that some tables may not exist for every simulation.
        tbl_dict = {}
        tbl_names = set(ns for fd in fs_compl for ns in fs[fd]['summary'])
        for n in tbl_names:
            in_fs = [fdate for fdate in fs_compl
                     if n in fs[fdate]['summary']]
            tbl_dict[n] = np.concatenate([fs[fdate]['summary'][n]
                                          for fdate in in_fs])

        # Attempt to avoid tracking times (not supported by h5py < 2.2).
        kwargs = {'track_times': False}

        def save_data(g, key, value):
            name = text.to_bytes(key)
            if isinstance(value, dict):
                sub_g = g.create_group(name)
                for sub_key, sub_value in sorted(value.items()):
                    save_data(sub_g, sub_key, sub_value)
            else:
                g.create_dataset(name, data=value, **kwargs)

        with h5py.File(filename, 'w') as f:
            # Record whether tracking times have been disabled.
            try:
                f.create_dataset('hdf5_track_times', data=False, **kwargs)
            except TypeError:
                # Cannot disable tracking times (h5py < 2.2).
                kwargs = {}
                f.create_dataset('hdf5_track_times', data=True, **kwargs)

            # Save the associated metadata, if any.
            if self.__metadata:
                meta_grp = f.create_group('meta')
                for k, v in sorted(self.__metadata.items()):
                    save_data(meta_grp, k, v)

            # Compress and checksum the data tables.
            kwargs['compression'] = 'gzip'
            kwargs['shuffle'] = True
            kwargs['fletcher32'] = True

            # Save the data tables.
            df_grp = f.create_group(self.__data_group)
            for tbl in tbl_dict:
                df_grp.create_dataset(tbl, data=tbl_dict[tbl], **kwargs)


class FakeVal(object):
    """A fake value that converts basic arithmetic operations into strings."""

    def __init__(self, value):
        self.value = value

    def __rtruediv__(self, x):
        return FakeVal("({} / {})".format(x, self.value))

    def __str__(self):
        if text.PY2:
            return text.to_bytes(self.value)
        else:
            return text.to_unicode(self.value)

    def __repr__(self):
        return repr(self.value)


class FakeRNG(object):
    """
    A fake random number generator whose methods return strings that describe
    each method call.
    """

    def __init__(self, prefix="random."):
        self.__prefix = prefix

    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        name = self.__prefix + name

        def log_call(*args, **kwargs):
            """Return a string representation of a method call."""
            # Ignore the 'size' keyword argument if its value is None.
            kw_iter = [(k, v) for (k, v) in kwargs.items()
                       if k != 'size' or v is not None]
            return FakeVal("{}({})".format(
                name,
                ", ".join(
                    [repr(a) for a in args] +
                    ["{}={}".format(k, repr(v)) for k, v in kw_iter]
                )))

        return log_call


class Metadata(object):
    """
    Document the simulation parameters and system environment for a set of
    simulations. A black-list (``ignore_dict``) defines which members of
    the parameters dictionary will be excluded from this metadata, see
    :func:`~Metadata.filter` for details.
    """

    def __init__(self):
        # Ignore the following parameters; some will be replaced by better
        # descriptions (e.g., 'prior') and some should always be ignored
        # because they have no meaningful representation.
        self.ignore_dict = {
            'prior': None,
            'log_llhd_fn': None,
            'px_range': None,
            'resample': {'rnd': None},
        }

    def build(self, params, pkgs=None):
        """
        Construct a metadata dictionary that documents the simulation
        parameters and system environment. Note that this should be generated
        at the **start** of the simulation, and that the git metadata will
        only be valid if the working directory is located within a git
        repository.

        :param params: The simulation parameters.
        :param pkgs: A dictionary that maps package names to modules that
            define appropriate ``__version__`` attributes, used to record the
            versions of additional relevant packages (see the example below).

        By default, the versions of ``pypfilt``, ``h5py``, ``numpy`` and
        ``scipy`` are recorded. The following example demonstrates how to also
        record the installed version of the ``epifx`` package:

        .. code-block:: python

           import epifx
           import pypfilt.summary
           params = ...
           meta = pypfilt.summary.Metadata()
           metadata = meta.build(params, {'epifx': epifx})
        """

        # Import modules for extracting system-specific details.
        import platform
        # Import modules for extracting package versions.
        import scipy

        # Record the command line used to launch this simulation.
        # Note that sys.argv is a list of native strings.
        argv = [text.to_unicode(arg) for arg in sys.argv]
        cmdline = " ".join(argv)

        meta = {
            'package': {
                'python': text.to_bytes(platform.python_version()),
                'h5py': self.pkg_version(h5py),
                'pypfilt': self.pkg_version(version),
                'numpy': self.pkg_version(np),
                'scipy': self.pkg_version(scipy),
            },
            'sim': {
                'cmdline': cmdline.encode("utf-8"),
            },
            'git': self.git_data(),
            'param': self.filter(params, self.ignore_dict, self.encode),
            'prior': self.priors(params),
        }

        # Record the versions of user-specified packages (if any).
        if pkgs:
            for pkg in pkgs:
                meta['package'][pkg] = self.pkg_version(pkgs[pkg])

        # Record the name of the system model.
        meta['param']['model'] = self.object_name(params['model'])

        # Record the simulation time scale.
        meta['param']['time'] = self.object_name(params['time'])

        return meta

    def filter(self, values, ignore, encode_fn):
        """
        Recursively filter items from a dictionary, used to remove parameters
        from the metadata dictionary that, e.g., have no meaningful
        representation.

        :param values: The original dictionary.
        :param ignore: A dictionary that specifies which values to ignore.
        :param encode_fn: A function that encodes the remaining values (see
            :func:`.encode_value`).

        For example, to ignore ``['px_range']``,  ``['resample']['rnd']``, and
        ``'expect_fn'`` and ``'log_llhd_fn'`` for *every* observation system
        when using ``epifx``:

        .. code-block:: python

           m = pypfilt.summary.Metadata()
           ignore = {
               'px_range': None,
               'resample': {'rnd': None},
               # Note the use of ``None`` to match any key under 'obs'.
               'obs': {None: {'expect_fn': None, 'log_llhd_fn': None}}
           }
           m.filter(params, ignore, m.encode)
        """
        retval = {}
        for k, v in values.items():
            if k in ignore and ignore[k] is None:
                # Ignore this parameter.
                continue
            elif k in ignore and isinstance(v, dict):
                # Recursively encode this dictionary, maybe ignoring values.
                retval[k] = self.filter(v, ignore[k], encode_fn)
            elif None in ignore and isinstance(v, dict):
                # Recursively encode this dictionary, maybe ignoring values.
                retval[k] = self.filter(v, ignore[None], encode_fn)
            elif isinstance(v, dict):
                # Recursively encode this dictionary without ignoring values.
                retval[k] = self.filter(v, {}, encode_fn)
            else:
                retval[k] = encode_fn(v)
        return retval

    def encode(self, value):
        """
        Encode values in a form suitable for serialisation in HDF5 files.

        * Integer values are converted to ``numpy.int32`` values.
        * Floating-point values and arrays retain their data type.
        * All other (i.e., non-numerical) values are converted to UTF-8
          strings.
        """
        if isinstance(value, (int, np.int64)):
            # Avoid storing 64-bit integers since R doesn't support them.
            return np.int32(value)
        elif isinstance(value, (float, np.ndarray)):
            # Ensure that numerical values retain their data type.
            return value
        else:
            # Convert non-numerical values to UTF-8 strings.
            return text.to_bytes(value)

    def object_name(self, obj):
        """
        Return the fully qualified name of the object as a byte string.
        """
        if hasattr(obj, '__name__'):
            # The object is a class.
            obj_name = obj.__name__
            obj_mod = obj.__module__
        elif hasattr(obj, '__class__'):
            # The object is a class instance.
            obj_name = obj.__class__.__name__
            obj_mod = obj.__class__.__module__
        else:
            # The object doesn't appear to be a class or a class instance.
            obj_name = str(obj)
            obj_mod = None

        if obj_mod is not None:
            descr = "{}.{}".format(obj.__module__, obj_name)
        else:
            descr = obj_name

        return text.to_bytes(descr)

    def priors(self, params):
        """
        Return a dictionary that describes the model parameter priors.

        Each key identifies a parameter (by name); the corresponding value is
        a byte string representation of the prior distribution, which is
        typically a ``numpy.random.RandomState`` method call.

        For example:

        .. code-block:: python

           {'R0': b'random.uniform(1.0, 2.0)',
            'gamma': b'(1 / random.uniform(1.0, 3.0))'}
        """
        logger = logging.getLogger(__name__)
        priors = params['prior'].items()
        rng = FakeRNG()
        descr = {}
        for k, v in priors:
            try:
                descr[k] = text.to_bytes(v(rng))
            except TypeError:
                # Can occur when performing arbitrary operations.
                logger.debug("Can not describe the prior for '{}'".format(k))
                descr[k] = text.to_bytes("unknown")
        return descr

    def pkg_version(self, module):
        """Attempt to obtain the version of a Python module."""
        try:
            return text.to_bytes(module.__version__)
        except AttributeError:
            try:
                # Older versions of h5py store the version number here.
                return text.to_bytes(module.version.version)
            except AttributeError:
                return "unknown".encode("utf-8")

    def git_data(self):
        """
        Record the status of the git repository within which the working
        directory is located (if such a repository exists).
        """
        # Determine the encoding for the default locale.
        default_encoding = locale.getdefaultlocale()[1]
        logger = logging.getLogger(__name__)
        enc_msg = "Extracting git metadata using locale encoding '{}'"
        logger.debug(enc_msg.format(default_encoding))

        git_head = self.run_cmd(['git', 'rev-parse', 'HEAD'])
        git_branch = self.run_cmd(['git', 'symbolic-ref', '--short', 'HEAD'])
        git_mod_files = self.run_cmd(['git', 'ls-files', '--modified'],
                                     all_lines=True, err_val=[])
        git_mod_files.sort()
        git_mod = len(git_mod_files) > 0
        return {
            'HEAD': git_head.encode("utf-8"),
            'branch': git_branch.encode("utf-8"),
            'modified': git_mod,
            'modified_files': [f.encode("utf-8") for f in git_mod_files],
        }

    def run_cmd(self, args, all_lines=False, err_val=''):
        """
        Run a command and return the (Unicode) output. By default, only the
        first line is returned; set ``all_lines=True`` to receive all of the
        output as a list of Unicode strings. If the command returns a non-zero
        exit status, return ``err_val`` instead.
        """
        try:
            # Return the output as a single byte string.
            lines = subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return err_val
        # Decode and break into lines according to Unicode boundaries.
        # For details see:
        # * https://docs.python.org/2/library/stdtypes.html#unicode.splitlines
        # * https://docs.python.org/3/library/stdtypes.html#str.splitlines
        default_encoding = locale.getdefaultlocale()[1]
        lines = lines.decode(default_encoding).splitlines()
        if all_lines:
            return lines
        else:
            return lines[0]


def obs_table(params, all_obs):
    """
    Create a structured array that contains the details of each observation.
    The columns are: ``'unit', 'period', 'source', 'date', 'value',
    'incomplete', 'upper_bound'``.

    :param params: The simulation parameters.
    :param all_obs: A list of all observations.
    """
    # Encode units into bytes, for HDF5 storage.
    obs_units = {o['unit']: text.to_bytes(o['unit'])
                 for o in all_obs}
    ulen = max(len(bs) for unit, bs in obs_units.items())
    # Encode source into bytes, for HDF5 storage.
    obs_srcs = {o['source']: text.to_bytes(o['source'])
                for o in all_obs}
    slen = max(len(bs) for source, bs in obs_srcs.items())
    unit = ('unit', 'S{}'.format(ulen))
    period = ('period', np.int8)
    source = ('source', 'S{}'.format(slen))
    date = params['time'].dtype('date')
    obs_val = all_obs[0]['value']
    value = dtype_value(obs_val)
    incomplete = ('incomplete', np.bool)
    upper = dtype_value(obs_val, name='upper_bound')
    dtype = dtype_names_to_str([unit, period, source, date, value, incomplete,
                                upper])
    obs_df = np.empty(len(all_obs), dtype=dtype)
    for ix, o in enumerate(all_obs):
        unit_bs = obs_units[o['unit']]
        src_bs = obs_srcs[o['source']]
        date_enc = params['time'].to_dtype(o['date'])
        inc = o.get('incomplete', False)
        upr = o.get('upper_bound', 0)
        obs_df[ix] = (unit_bs, o['period'], src_bs, date_enc, o['value'],
                      inc, upr)
    return obs_df


def convert_cols(data, converters):
    """
    Convert columns in a structured array from one type to another.

    :param data: The input structured array.
    :param converters: A dictionary that maps (unicode) column names to
        ``(convert_fn, new_dtype)`` tuples, which contain a conversion
        function and define the output dtype.
    :returns: A new structured array.
    """
    dt = data.dtype
    col_names = dtype_names_to_str(dt.names)
    conv_names = dtype_names_to_str([n for n in converters.keys()])
    conv_fns = {}
    new_dtype = []
    for col in col_names:
        if col in conv_names:
            convert_fn, convert_dt = converters[col]
            conv_fns[col] = convert_fn
            new_dtype.append((col, convert_dt))
        else:
            new_dtype.append((col, dt.fields[col][0]))
    # Create and fill the new array.
    data_out = np.zeros(data.shape, dtype=new_dtype)
    for col in col_names:
        if col in conv_names:
            data_out[col] = conv_fns[col](data[col])
        else:
            data_out[col] = data[col]
    return data_out


def default_converters(time_scale):
    """
    Return a dictionary for converting the ``'fs_date'`` and ``'date'``
    columns from (see :func:`~convert_cols`).
    """
    def convert_fn(np_col):
        return np.array([time_scale.from_dtype(val) for val in np_col])
    return {
        'fs_date': (convert_fn, time_scale.native_dtype()),
        'date': (convert_fn, time_scale.native_dtype()),
    }
