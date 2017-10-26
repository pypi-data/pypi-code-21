"""Observation models: expected values and log likelihoods."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import abc
import codecs
import datetime
import numpy as np
import pypfilt.summary
import pypfilt.text
import scipy.stats

from scipy.special import betaln, gammaln


def from_model(params, when, unit, period, pr_inf):
    """Determine the expected observation for a given infection probability.

    :param params: The observation model parameters.
    :param when: The end of the observation period.
    :type when: datetime.datetime
    :param unit: The observation units (see classes in :py:module`data`).
    :type unit: str
    :param period: The duration of the observation period (in days).
    :type period: int
    :param pr_inf: The probability of an individual becoming infected during
        the observation period.
    :type pr_inf: float
    """
    return {'date': when,
            'value': expect(params, unit, period, pr_inf),
            'unit': unit,
            'period': period,
            'source': "synthetic-observation"}


def expect(params, time, unit, period, pr_inf, prev, curr):
    """
    Return the expected observation value :math:`\mathbb{E}[y_t]` for every
    every particle :math:`x_t`, at one or more times :math:`t`.

    :param params: The observation model parameters.
    :param time: The simulation time(s).
    :param unit: The observation units (see classes in :py:module`data`).
    :type unit: str
    :param period: The duration of the observation period (in days).
    :type period: int
    :param pr_inf: The probability of an individual becoming infected during
        the observation period(s).
    :type pr_inf: float
    :param prev: The state vectors at the start of the observation period(s).
    :type prev: numpy.ndarray
    :param curr: The state vectors at the end of the observation period(s).
    :type curr: numpy.ndarray
    """
    if unit in params['obs']:
        op = params['obs'][unit]
        obs_model = op['obs_model']
        return obs_model.expect(params, op, time, period, pr_inf, prev, curr)
    else:
        raise ValueError("Unknown observation type '{}'".format(unit))


def log_llhd(params, obs, curr, hist, weights):
    """
    Return the log-likelihood :math:`\mathcal{l}(y_t \mid x_t)` for the
    observation :math:`y_t` and every particle :math:`x_t`.

    :param params: The observation model parameters.
    :param obs: The list of observations for the current time-step.
    :param curr: The particle state vectors.
    :param hist: The particle state histories, indexed by observation period.
    """
    log_llhd = np.zeros(curr.shape[:-1])
    pr_inf = params['model'].pr_inf

    hook_key = 'record_log_llhd_fns'
    hook_fns = params['epifx'][hook_key]

    for o in obs:
        # Extract the observation period and the infection probability.
        days = o['period']
        unit = o['unit']
        time = o['date']
        p_inf = np.maximum(pr_inf(hist[days], curr), 0)
        cpt_indiv = np.array([1 - p_inf, p_inf])

        if unit in params['obs']:
            op = params['obs'][unit]
            obs_model = op['obs_model']
            l = obs_model.log_llhd(params, op, time, o, cpt_indiv, curr, hist)
            for hook_fn in hook_fns:
                hook_fn(o, l, weights)
            log_llhd += l
        else:
            raise ValueError("Unknown observation type '{}'".format(unit))

    return log_llhd


def datetime_conv(text, fmt='%Y-%m-%d', encoding='utf-8'):
    """
    Convert date strings to datetime.datetime instances. This is a
    convenience function intended for use with, e.g., ``numpy.loadtxt``.

    :param text: A string (bytes or Unicode) containing a date or date-time.
    :param fmt: A format string that defines the textual representation.
        See the Python ``strptime`` documentation for details.
    :param encoding: The byte string encoding (default is UTF-8).
    """
    # Note: text will always be read in as a byte string.
    text = pypfilt.text.to_unicode(text, encoding)
    return datetime.datetime.strptime(text, fmt)


def read_table(filename, columns, date_fmt=None, comment='#'):
    """
    Load data from a space-delimited **ASCII** text file with column headers
    defined in the first *non-comment* line.

    :param filename: The file to read.
    :param columns: The columns to read, represented as a list of
        ``(name, type)`` tuples; ``type`` should either be a built-in NumPy
        `scalar type <http://docs.scipy.org/doc/numpy-1.9.2/reference/arrays.scalars.html#arrays-scalars-built-in>`__,
        or ``datetime.date`` or ``datetime.datetime`` (in which case
        string values will be automatically converted to ``datetime.datetime``
        objects by :func:`~epifx.obs.datetime_conv`).
    :param date_fmt: A format string for parsing date columns; see
        :func:`datetime_conv` for details and the default format string.
    :param comment: Prefix string(s) that identify comment lines; either a
        single Unicode string or a *tuple* of Unicode strings.
    :return: A NumPy structured array.
    :raises ValueError: If the data file contains non-ASCII text (i.e., bytes
        greater than 127), because ``numpy.loadtxt`` cannot process non-ASCII
        data (e.g., see NumPy issues
        `#3184 <https://github.com/numpy/numpy/issues/3184>`__,
        `#4543 <https://github.com/numpy/numpy/issues/4543>`__,
        `#4600 <https://github.com/numpy/numpy/issues/4600>`__,
        `#4939 <https://github.com/numpy/numpy/issues/4939>`__).

    :Example:

    The code below demonstrates how to read observations from a file that
    includes columns for the year, the observation date, the observed value,
    and free-text metadata (up to 20 characters in length).

    ::

       import datetime
       import numpy as np
       import epifx.obs
       columns = [('year', np.int32), ('date', datetime.datetime),
                  ('count', np.int32), ('metadata', 'S20')]
       df = epifx.obs.read_table('my-data-file.ssv', columns,
                                 date_fmt='%Y-%m-%d')
    """
    if comment is None:
        comment = '#'
    skip_lines = 1
    with codecs.open(filename, encoding='ascii') as f:
        cols = f.readline().strip().split()
        while len(cols) == 0 or cols[0].startswith(comment):
            cols = f.readline().strip().split()
            skip_lines += 1

    req_cols = [col[0] for col in columns]
    for req in req_cols:
        if req not in cols:
            raise ValueError("Column '{}' not found in {}".format(
                req, filename))

    col_convs = {}
    col_types = pypfilt.summary.dtype_names_to_str(columns)
    for ix, col in enumerate(col_types):
        # Ensure that all column names are valid ASCII strings.
        try:
            pypfilt.text.to_bytes(col[0], encoding='ascii')
        except UnicodeEncodeError as e:
            raise ValueError("Column '{}' is not valid ASCII".format(col[0]))
        if isinstance(col[1], type) and issubclass(col[1], datetime.date):
            # Dates and datetimes must be converted from strings to objects.
            # Note: the opposite is true when *writing* tables!
            # This has implications for making the time units arbitrary, as
            # the time class will need to define both conversion operations.
            col_types[ix] = (col[0], 'O')
            col_ix = cols.index(col[0])
            if date_fmt is None:
                col_convs[col_ix] = lambda s: datetime_conv(s,
                                                            encoding='ascii')
            else:
                col_convs[col_ix] = lambda s: datetime_conv(s, date_fmt,
                                                            'ascii')
    col_read = [cols.index(name) for name in req_cols]

    with codecs.open(filename, encoding='ascii') as f:
        try:
            return np.loadtxt(f, skiprows=skip_lines, dtype=col_types,
                              converters=col_convs, usecols=col_read)
        except (TypeError, UnicodeDecodeError) as e:
            msg = "File '{}' contains non-ASCII text".format(filename)
            print(e)
            raise ValueError(msg)


# Create a new metaclass for abstract base classes (ABCs), so that subclasses
# can only be instantiated if they implement all of the abstract methods.
# The metaclass syntax differs between Python 2 and 3, the following line is
# the simplest way to sidestep this issue without relying on ``six``.
ABC = abc.ABCMeta(str('ABC'), (object,), {})


class Obs(ABC):
    """
    The base class of observation models, which defines the minimal set of
    methods that are required.
    """

    @abc.abstractmethod
    def expect(self, params, op, time, period, pr_inf, prev, curr):
        """
        Return the expected observation value :math:`\mathbb{E}[y_t]` for
        every particle :math:`x_t`, at one or more times :math:`t`.

        :param params: The observation model parameters.
        :param op: The observation model parameters dictionary.
        :param time: The simulation time(s), :math:`t`.
        :param period: The duration of the observation period (in days).
        :param pr_inf: The probability of an individual becoming infected
            during the observation period(s), :math:`p_\mathrm{inf}`.
        :param prev: The state vectors at the start of the observation
            period(s), :math:`x_t`.
        :param curr: The state vectors at the end of the observation
            period(s).
        """
        pass

    @abc.abstractmethod
    def log_llhd(self, params, op, time, obs, pr_indiv, curr, hist):
        """
        Return the log-likelihood :math:`\mathcal{l}(y_t \mid x_t)` for the
        observation :math:`y_t` and every particle :math:`x_t`.

        :param params: The observation model parameters.
        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param obs: An observation for the current time-step, :math:`y_t`.
        :param pr_indiv: The probabilities of an individual not being infected
            and being infected during the observation period,
            :math:`[1 - p_\mathrm{inf}, p_\mathrm{inf}]`.
        :param curr: The particle state vectors, :math:`x_t`.
        :param hist: The particle state histories, indexed by observation
            period.
        """
        pass

    @abc.abstractmethod
    def llhd_in(self, op, time, mu, wt, y0, y1):
        """
        Return the weighted likelihood that :math:`y_t \in [y_0, y_1)`:

        .. math::

           \sum_i w_i \cdot \mathcal{L}(y_0 \le y_t < y_1 \mid x_t^i)

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected case fraction for each particle,
            :math:`\mathbb{E}(y_t)`.
        :param wt: The weight associated with each particle, :math:`w_i`.
        :param y0: The (inclusive) minimum fraction of cases, :math:`y_0`.
        :param y1: The (exclusive) maximum fraction of cases, :math:`y_1`.
        """
        pass

    @abc.abstractmethod
    def quantiles(self, op, time, mu, wt, probs):
        r"""
        Return the observations :math:`y_i` that satisfy:

        .. math::

           y_i = \inf\left\{ y \in \mathbb{N} : p_i \le
               \sum_i w_i \cdot \mathcal{L}(y_t \le y \mid x_t^i)\right\}

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected case fraction for each particle,
            :math:`\mathbb{E}(y_t)`.
        :param wt: The weight associated with each particle, :math:`w_i`.
        :param probs: The probabilities :math:`p_i`, which **must** be sorted
            in **ascending order**.
        """
        pass


class SampleCounts(Obs):
    """
    Generic observation model for relating disease incidence to count data
    where the denominator is reported.
    """

    def __init__(self, obs_unit, obs_period, denom, k_obs_ix=None):
        """
        :param obs_unit: A descriptive name for the data.
        :param obs_period: The observation period (in days).
        :param denom: The denominator to use when calculating likelihoods and
            quantiles in the absence of an actual observation.
        :param k_obs_ix: The index of the model parameter that defines the
            disease-related increase in observation rate
            (:math:`\kappa_\mathrm{obs}`). By default, the value in the
            parameters dictionary is used.
        """
        self.unit = obs_unit
        self.period = obs_period
        self.denom = denom
        self.k_obs_ix = k_obs_ix

    @staticmethod
    def logpmf(x, prob, size, disp):
        """
        Return the log of the probability mass at :math:`x`.

        :param x: The number of cases (observed numerator :math:`x`).
        :param prob: The expected fraction of all patients that are cases.
        :param size: The number of patients (observed denominator).
        :param disp: The dispersion parameter (:math:`k`).
        """
        return (gammaln(size + 1) - gammaln(x + 1) - gammaln(size - x + 1) -
                betaln(disp * (1 - prob), disp * prob) +
                betaln(size - x + disp * (1 - prob), x + disp * prob))

    @classmethod
    def interval_pmf(cls, x0, x1, prob, size, disp, log=True):
        """
        Return the (log of the) probability mass over the interval
        :math:`(x_0, x1]`.

        :param x0: The (exclusive) minimum number of cases (:math:`x_0`).
        :param x1: The (inclusive) maximum number of cases (:math:`x_1`).
        :param prob: The expected fraction of all patients that are cases.
        :param size: The number of patients (observed denominator).
        :param disp: The dispersion parameter (:math:`k`).
        :param log: Whether to return the log of the probability mass.
        """
        total = np.zeros(np.shape(prob))
        for x in range(x0 + 1, x1 + 1):
            total += np.exp(cls.logpmf(x, prob, size, disp))
        if log:
            # Handle particles with zero mass in this interval.
            total[total <= 0.0] = np.finfo(total.dtype).tiny
            return np.log(total)
        return total

    def expect(self, params, op, time, period, pr_inf, prev, curr):
        """
        Calculate the expected observation value :math:`\mathbb{E}[y_t]` for
        every particle :math:`x_t`.
        """
        if self.k_obs_ix is None:
            k_obs = op['k_obs']
        else:
            # Each particle has its own observation probability.
            k_obs = curr[..., self.k_obs_ix]
        return op['bg_obs'] + pr_inf * k_obs

    def log_llhd(self, params, op, time, obs, pr_indiv, curr, hist):
        """
        Calculate the log-likelihood :math:`\mathcal{l}(y_t \mid x_t)` for the
        observation :math:`y_t` (``obs``) and every particle :math:`x_t`.

        If it is known (or suspected) that the observed value will increase in
        the future --- when ``obs['incomplete'] == True`` --- then the
        log-likehood :math:`\mathcal{l}(y > y_t \mid x_t)` is calculated
        instead (i.e., the log of the *survival function*).

        If an upper bound to this increase is also known (or estimated) ---
        when ``obs['upper_bound']`` is defined --- then the log-likelihood
        :math:`\mathcal{l}(y_u \ge y > y_t \mid x_t)` is calculated instead.
        """
        period = obs['period']
        pr_inf = pr_indiv[1]
        pr = self.expect(params, op, time, period, pr_inf, hist[period], curr)
        num = obs['numerator']
        denom = obs['denominator']
        disp = self.effective_disp(pr, op)

        if 'incomplete' in obs and obs['incomplete']:
            if 'upper_bound' in obs:
                # Calculate the log-likelihood over the interval from the
                # observed value to this upper bound.
                num_max = obs['upper_bound']
                return self.interval_pmf(num, num_max, pr, denom, disp)
            else:
                # Calculate the log-likelihood of observing a strictly greater
                # value than reported by this incomplete observation.
                return self.logsf(num, pr, denom, disp)
        # Calculate the log-likehood of the observed value.
        return self.logpmf(num, pr, denom, disp)

    def trapz_qtls(self, mu, wt, disp, probs, trapz_w):
        """
        Approximate the quantile function using trapezoidal integration.

        :param mu: The expected case fraction for each particle.
        :param wt: The weight associated with each particle.
        :param disp: The dispersion parameter for each particle.
        :param probs: The cumulative probabilities that define the credible
            interval boundaries (must lie in the interval :math:`(0, 1)` and
            must be sorted in *ascending order*).
        :param trapz_w: The trapezoid width; quantiles will be approximated by
            linear interpolation between trapezoid boundaries.
        """
        denom = self.denom
        if not np.array_equal(probs, np.sort(probs)):
            raise ValueError("unsorted intervals: {}".format(probs))
        cints = np.zeros(probs.shape)
        # Record point and cumulative probabilities for a subset of [0, Nt].
        csums = np.zeros((denom + 1,))
        pmass = np.zeros((denom + 1,))

        # Calculate the probability mass for a specific number of cases.
        def pm_at(x):
            return np.dot(wt, np.exp(self.logpmf(x, mu, denom, disp)))

        # Calculate cumulative probabilities at the boundaries.
        pmass[0] = pm_at(0)
        csums[0] = pmass[0]
        pmass[-1] = pm_at(denom)
        csums[-1] = 1.0
        # Calculate cumulative probabilities for each trapezoid in turn.
        x_lwr = 0
        x_upr = 0
        # Trapezoids span intervals (x_lwr, x_upr], weight accordingly.
        w_lwr = (trapz_w - 1) / 2
        w_upr = (trapz_w + 1) / 2
        for pix, pr in enumerate(probs):
            while csums[x_upr] < pr:
                x_lwr = x_upr
                x_upr += trapz_w
                if x_upr > denom:
                    x_upr = denom
                    break
                pmass[x_upr] = pm_at(x_upr)
                csums[x_upr] = (csums[x_lwr] + w_lwr * pmass[x_lwr] +
                                w_upr * pmass[x_upr])
            # Have found bounds on x for the given probability.
            if x_lwr == x_upr:
                x_est = x_lwr
            else:
                # Use linear interpolation to estimate the value of x.
                slope = (csums[x_upr] - csums[x_lwr]) / (x_upr - x_lwr)
                diff = pr - csums[x_lwr]
                x_est = np.rint(x_lwr + diff / slope).astype(int)
            cints[pix] = x_est / denom
        return cints

    def trapz_approx(self, mu, wt, disp, x0, x1, n_samp):
        """
        Approximate the probability mass over the interval :math:`[x_0, x_1)`
        using a trapezoidal integration scheme.

        :param mu: The expected case fraction for each particle.
        :param wt: The weight associated with each particle.
        :param disp: The dispersion parameter for each particle.
        :param x0: The (inclusive) minimum number of cases (:math:`x_0`).
        :param x1: The (exclusive) maximum number of cases (:math:`x_1`).
        :param n_samp: The number of samples over the :math:`[x_0, x_1)`
            interval (i.e., set to :math:`t + 1` for :math:`t` trapezoids).
        """
        x = np.linspace(x0, x1 - 1, num=n_samp, dtype=int)
        grid_x, grid_mu = np.meshgrid(x, mu, copy=False)
        # Note: we use self.denom as the denominator here; this must be
        # consistent with the denominator used to calculate x0 and x1.
        probs = np.exp(self.logpmf(grid_x, grid_mu, self.denom, disp))
        widths = 0.5 * np.ediff1d(x)
        # Note: the end-points need to be scaled by (w + 1)/2 for intervals of
        # width w (x is discrete, so they both have *unit* width).
        traps = np.r_[0.5, widths] + np.r_[widths, 0.5]
        trap_probs = probs * traps[None, :]
        trap_sums = np.dot(wt, np.sum(trap_probs, axis=1))
        return trap_sums

    def effective_disp(self, mu, op, expand_dim=False):
        """
        Return the dispersion parameter for each particle, subject to an
        optional lower bound imposed on the variance.
        """
        disp = op['disp']

        if 'bg_var' in op and op['bg_var'] > 0:
            # Ensure the variance is not smaller than the variance in the
            # background signal.
            disp = op['disp'] * np.ones(mu.shape)
            min_var = op['bg_var']
            frac_var = (mu * (1 - mu) * (1 + (self.denom - 1) / (disp + 1))
                        / self.denom)
            mask_v = frac_var < min_var
            if np.any(mask_v):
                c = mu[mask_v] * (1 - mu[mask_v]) / self.denom
                disp[mask_v] = (self.denom * c - min_var) / (min_var - c)
            else:
                return op['disp']
            if expand_dim:
                disp = disp[:, None]

        return disp

    def llhd_in(self, op, time, mu, wt, y0, y1):
        """
        Return the probability mass over the interval :math:`[y_0, y1)`.

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected fraction of all patients that are cases.
        :param wt: The weight associated with each value of ``mu``.
        :param y0: The (inclusive) minimum fraction of cases (:math:`y_0`).
        :param y1: The (exclusive) maximum fraction of cases (:math:`y_0`).
        """
        x0 = np.ceil(y0 * self.denom).astype(int)
        x1 = np.ceil(y1 * self.denom).astype(int)
        disp = self.effective_disp(mu, op, expand_dim=True)
        diff = x1 - x0
        if diff <= 20:
            # Sufficiently small interval, calculate the mass at every x.
            x = np.linspace(x0, x1 - 1, num=diff, dtype=int)
            grid_x, grid_mu = np.meshgrid(x, mu, copy=False)
            probs = np.exp(self.logpmf(grid_x, grid_mu, self.denom, disp))
            return np.dot(wt, np.sum(probs, axis=1))
        elif diff <= 50:
            n_samp = 6
        else:
            # Maximum relative error < 0.1% on CDC national data.
            n_samp = 9
        return self.trapz_approx(mu, wt, disp, x0, x1, n_samp)

    def quantiles(self, op, time, mu, wt, probs):
        r"""
        Return the observations :math:`y_i` that satisfy:

        .. math::

           y_i = \inf\left\{ y \in \mathbb{N} : p_i \le
               \sum_i w_i \cdot \mathcal{L}(y_t \le y \mid x_t^i)\right\}

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected case fraction for each particle,
            :math:`\mathbb{E}(y_t)`.
        :param wt: The weight associated with each particle, :math:`w_i`.
        :param probs: The probabilities :math:`p_i`, which **must** be sorted
            in **ascending order**.
        """
        disp = self.effective_disp(mu, op)
        # Determine the trapezoid width by setting an upper limit on the
        # number of trapezoids that can be used to span the interval [0, 1],
        # and defining a minimum trapezoid width.
        denom = self.denom
        max_traps = 10000
        min_width = 10
        trapz_w = max(min_width, np.ceil(denom / max_traps).astype(int))
        return self.trapz_qtls(mu, wt, disp, probs, trapz_w)

    @classmethod
    def logsf(cls, x, prob, size, disp):
        """
        Return the log of the survival function :math:`(1 - \mathrm{CDF}(x))`.

        :param x: The number of cases (observed numerator :math:`x`).
        :param prob: The expected fraction of all patients that are cases.
        :param size: The number of patients (observed denominator).
        :param disp: The dispersion parameter (:math:`k`).
        """
        total = np.ones(np.size(prob))
        for x in range(x + 1):
            total -= np.exp(cls.logpmf(x, prob, size, disp))
        # Handle particles with zero mass in this interval.
        total[total == 0.0] = np.finfo(total.dtype).tiny
        return np.log(total)

    def define_params(self, params, bg_obs, k_obs, disp, bg_var=None):
        """
        Add observation model parameters to the simulation parameters.

        :param bg_obs: The background signal in the data
            (:math:`bg_\mathrm{obs}`).
        :param k_obs: The increase in observation rate due to infected
            individuals (:math:`\kappa_\mathrm{obs}`).
        :param disp: The dispersion parameter (:math:`k`).
        :param bg_var: The variance of the background signal
            (:math:`bg_\mathrm{var}`).
        """
        params['obs'][self.unit] = {
            'obs_model': self,
            'bg_obs': bg_obs,
            'k_obs': k_obs,
            'disp': disp,
        }
        if bg_var is not None:
            params['obs'][self.unit]['bg_var'] = bg_var

    def from_file(self, filename, year=None, date_col='to', value_col='cases',
                  denom_col='patients'):
        """
        Load count data from a space-delimited text file with column headers
        defined in the first line.

        Note that returned observation *values* represent the *fraction* of
        patients that were counted as cases, **not** the *absolute number* of
        cases.
        The number of cases and the number of patients are recorded under the
        ``'numerator'`` and ``'denominator'`` keys, respectively.

        :param filename: The file to read.
        :param year: Only returns observations for a specific year.
            The default behaviour is to return all recorded observations.
        :param date_col: The name of the observation date column.
        :param value_col: The name of the observation value column (reported
            as absolute values, **not** fractions).
        :param denom_col: The name of the observation denominator column.
        :return: A list of observations, ordered as per the original file.

        :raises ValueError: If a denominator or value is negative, or if the
            value exceeds the denominator.
        """
        year_col = 'year'
        cols = [(year_col, np.int32), (date_col, datetime.date),
                (value_col, np.int32), (denom_col, np.int32)]
        df = read_table(filename, cols)

        if year is not None:
            df = df[df[year_col] == year]

        # Perform some basic validation checks.
        if np.any(df[denom_col] < 0):
            raise ValueError("Observation denominator is negative")
        elif np.any(df[value_col] < 0):
            raise ValueError("Observed value is negative")
        elif np.any(df[value_col] > df[denom_col]):
            raise ValueError("Observed value exceeds denominator")

        # Return observations with non-zero denominators.
        nrows = df.shape[0]
        return [{'date': df[date_col][i],
                 'value': df[value_col][i] / df[denom_col][i],
                 'numerator': df[value_col][i],
                 'denominator': df[denom_col][i],
                 'unit': self.unit,
                 'period': self.period,
                 'source': filename}
                for i in range(nrows) if df[denom_col][i] > 0 and
                df[value_col][i] > 0]


class PopnCounts(Obs):
    """
    Generic observation model for relating disease incidence to count data
    where the denominator is assumed or known to be the population size.
    """

    def __init__(self, obs_unit, obs_period, pr_obs_ix=None):
        """
        :param obs_unit: A descriptive name for the data.
        :param obs_period: The observation period (in days).
        :param pr_obs_ix: The index of the model parameter that defines the
            observation probability (:math:`p_\mathrm{obs}`). By default, the
            value in the parameters dictionary is used.
        """
        self.unit = obs_unit
        self.period = obs_period
        self.pr_obs_ix = pr_obs_ix

    def expect(self, params, op, time, period, pr_inf, prev, curr):
        """
        Calculate the expected observation value :math:`\mathbb{E}[y_t]` for
        every particle :math:`x_t`.
        """
        n = params['epifx']['popn_size']
        if self.pr_obs_ix is None:
            pr_obs = op['pr_obs']
        else:
            # Each particle has its own observation probability.
            pr_obs = curr[..., self.pr_obs_ix]
        return (1 - pr_inf) * op['bg_obs'] + pr_inf * pr_obs * n

    def effective_disp(self, mu, op):
        """
        Return the dispersion parameter for each particle, subject to an
        optional lower bound imposed on the variance.
        """
        nb_k = op['disp']

        # Ensure the variance is not smaller than the variance in the
        # background signal.
        if 'bg_var' in op and op['bg_var'] > 0:
            nb_k = op['disp'] * np.ones(mu.shape)
            min_var = op['bg_var']
            nb_var = mu + np.square(mu) / nb_k
            mask_v = nb_var < min_var
            if np.any(mask_v):
                nb_k[mask_v] = np.square(mu[mask_v]) / (min_var - mu[mask_v])

        return nb_k

    def log_llhd(self, params, op, time, obs, pr_indiv, curr, hist):
        """
        Calculate the log-likelihood :math:`\mathcal{l}(y_t \mid x_t)` for the
        observation :math:`y_t` (``obs``) and every particle :math:`x_t`.

        If it is known (or suspected) that the observed value will increase in
        the future --- when ``obs['incomplete'] == True`` --- then the
        log-likehood :math:`\mathcal{l}(y > y_t \mid x_t)` is calculated
        instead (i.e., the log of the *survival function*).

        If an upper bound to this increase is also known (or estimated) ---
        when ``obs['upper_bound']`` is defined --- then the log-likelihood
        :math:`\mathcal{l}(y_u \ge y > y_t \mid x_t)` is calculated instead.
        """
        period = obs['period']
        pr_inf = pr_indiv[1]
        mu = self.expect(params, op, time, period, pr_inf, hist[period], curr)
        nb_k = self.effective_disp(mu, op)
        nb_pr = nb_k / (nb_k + mu)
        nbinom = scipy.stats.nbinom(nb_k, nb_pr)
        if 'incomplete' in obs and obs['incomplete']:
            if 'upper_bound' in obs:
                # Calculate the likelihood over the interval from the observed
                # value to this upper bound, and return its logarithm.
                cdf_u = nbinom.cdf(obs['upper_bound'])
                cdf_l = nbinom.cdf(obs['value'])
                # Handle particles with zero mass in this interval.
                probs = cdf_u - cdf_l
                probs[probs <= 0] = np.finfo(probs.dtype).tiny
                return np.log(probs)
            else:
                # Return the likelihood of observing a strictly greater value
                # than the value reported by this incomplete observation.
                return nbinom.logsf(obs['value'])
        return nbinom.logpmf(obs['value'])

    def llhd_in(self, op, time, mu, wt, y0, y1):
        """
        Return the probability mass in :math:`[y_0, y1)`.

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected case fraction for each particle.
        :param wt: The weight associated with each particle.
        :param y0: The (inclusive) minimum fraction of cases (:math:`y_0`).
        :param y1: The (exclusive) maximum fraction of cases (:math:`y_0`).
        """
        nb_k = self.effective_disp(mu, op)
        nb_pr = nb_k / (nb_k + mu)
        nbinom = scipy.stats.nbinom(nb_k, nb_pr)
        return np.dot(wt, nbinom.cdf(y1 - 1) - nbinom.cdf(y0 - 1))

    def quantiles(self, op, time, mu, wt, probs):
        r"""
        Return the observations :math:`y_i` that satisfy:

        .. math::

           y_i = \inf\left\{ y \in \mathbb{N} : p_i \le
               \sum_i w_i \cdot \mathcal{L}(y_t \le y \mid x_t^i)\right\}

        :param op: The observation model parameters dictionary.
        :param time: The current simulation time, :math:`t`.
        :param mu: The expected case fraction for each particle,
            :math:`\mathbb{E}(y_t)`.
        :param wt: The weight associated with each particle, :math:`w_i`.
        :param probs: The probabilities :math:`p_i`, which **must** be sorted
            in **ascending order**.
        """
        nb_k = self.effective_disp(mu, op)
        nb_pr = nb_k / (nb_k + mu)
        nbinom = scipy.stats.nbinom(nb_k, nb_pr)

        def f(y):
            return np.dot(wt, nbinom.cdf(y))

        y_min = 0
        c_min = f(y_min)
        # Find a satisfactory upper bound for y_i.
        max_pr = np.max(probs)
        for scale in np.logspace(1, 8, base=2, num=8):
            y_max = np.max(mu) * scale
            c_max = f(y_max)
            if c_max >= max_pr:
                # We've found a satisfactory upper bound for y_i.
                break
        else:
            msg = "Could not find a satisfactory upper bound for p = {}"
            raise ValueError(msg.format(max_pr))

        lwr_bounds = {pr: y_min for pr in probs}
        upr_bounds = {pr: y_max for pr in probs}
        qtls = np.zeros(probs.shape)
        for ix, pr in enumerate(probs):
            if c_min >= pr:
                # The lower bound is the infimum, no need to search.
                qtls[ix] = pr
                continue
            rem_probs = probs[ix+1:]
            y_lwr = lwr_bounds[pr]
            y_upr = upr_bounds[pr]
            # Find the infimum using a binary search.
            while y_upr > y_lwr + 1:
                # Evaluate the CDF at the mid-point of the interval.
                y_mid = np.rint((y_lwr + y_upr) / 2).astype(int)
                c_mid = f(y_mid)
                for p in rem_probs:
                    # This is a good lower bound for a subsequent quantile.
                    if c_mid <= p and y_mid > lwr_bounds[p]:
                        lwr_bounds[p] = y_mid
                    # This is a good upper bound for a subsequent quantile.
                    if c_mid >= p and y_mid < upr_bounds[p]:
                        upr_bounds[p] = y_mid
                # Identify the half into which to descend.
                if c_mid >= pr:
                    y_upr = y_mid
                if c_mid <= pr:
                    y_lwr = y_mid
            qtls[ix] = y_upr
        return qtls

    def define_params(self, params, bg_obs, pr_obs, disp, bg_var=None):
        """
        Add observation model parameters to the simulation parameters.

        :param bg_obs: The background signal in the data
            (:math:`bg_\mathrm{obs}`).
        :param pr_obs: The probability of observing an infected individual
            (:math:`p_\mathrm{obs}`).
        :param disp: The dispersion parameter (:math:`k`).
        :param bg_var: The variance of the background signal
            (:math:`bg_\mathrm{var}`).
        """
        params['obs'][self.unit] = {
            'obs_model': self,
            'bg_obs': bg_obs,
            'pr_obs': pr_obs,
            'disp': disp,
        }
        if bg_var is not None:
            params['obs'][self.unit]['bg_var'] = bg_var

    def from_file(self, filename, year=None, date_col='to', value_col='count'):
        """
        Load count data from a space-delimited text file with column headers
        defined in the first line.

        :param filename: The file to read.
        :param year: Only returns observations for a specific year.
            The default behaviour is to return all recorded observations.
        :param date_col: The name of the observation date column.
        :param value_col: The name of the observation value column.
        :return: A list of observations, ordered as per the original file.
        """
        year_col = 'year'
        cols = [(year_col, np.int32), (date_col, datetime.date),
                (value_col, np.int32)]
        df = read_table(filename, cols)

        if year is not None:
            df = df[df[year_col] == year]

        nrows = df.shape[0]
        return [{'date': df[date_col][i],
                 'value': df[value_col][i],
                 'unit': self.unit,
                 'period': self.period,
                 'source': filename}
                for i in range(nrows)]
