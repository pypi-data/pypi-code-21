"""A bootstrap particle filter for epidemic forecasting."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import atexit
import datetime
import h5py
import logging
import numpy as np
import os
import os.path
import signal
import tempfile

from . import check
from . import model
from . import summary
from . import text
from . import time
from . import version

__package_name__ = u'pypfilt'
__author__ = u'Rob Moss'
__email__ = u'rgmoss@unimelb.edu.au'
__copyright__ = u'2014-2016, Rob Moss'
__license__ = u'BSD 3-Clause License'
__version__ = version.__version__


# Export abstract base classes from this module.
Model = model.Model
Monitor = summary.Monitor
Table = summary.Table
Datetime = time.Datetime
Scalar = time.Scalar

# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def post_regularise(params, px, new_px):
    """
    Sample model parameter values from a continuous approximation of the
    optimal filter, assuming that it has a smooth density.

    This is the post-regularised particle filter (post-RPF). For details, see
    chapter 12 of Doucet et al., Sequential Monte Carlo Methods in Practice,
    Springer, 2001.

    :param params: The simulation parameters.
    :param px: The particles, prior to resampling.
    :param new_px: The particles after resampling directly from the discrete
        distribution (``px``). This matrix will be **destructively updated**
        with model parameter values samples from the regularisation kernel.
    """

    from . import stats

    logger = logging.getLogger(__name__)

    rnd = params['resample']['rnd']
    count = px.shape[0]
    # Only resample parameters that can be sampled continuously.
    details = params['model'].describe()
    p_info = [(ix, vmin, vmax, name)
              for ix, (name, smooth, vmin, vmax) in enumerate(details)
              if smooth]
    p_ixs = np.array([info[0] for info in p_info])

    if len(p_ixs) == 0:
        logger.debug("Post-RPF: no parameters to resample")
        return

    # Check for parameters that are constant (or nearly so) for all particles.
    # These parameters must be ignored or the covariance matrix will not be
    # positive definite, and the Cholesky decomposition will fail.
    p_range = np.ptp(px[:, p_ixs], axis=0)
    toln = params['resample']['reg_toln']
    good = p_range >= toln
    if not np.all(good):
        bad = np.logical_not(good)
        msg = "Post-RPF found {} constant parameter(s) at {}".format(
            sum(bad), p_ixs[np.where(bad)])
        logger.debug(msg)
        p_ixs = p_ixs[good]
        if len(p_ixs) == 0:
            logger.debug("Post-RPF: no non-constant parameters to resample")
            return

    # Use a bandwidth that is half that of the optimal bandwidth for a
    # Gaussian kernel (when the underlying density is Gaussian with unit
    # covariance), to handle multi-model densities.
    npar = len(p_ixs)
    h = 0.5 * (4 / (count * (npar + 2))) ** (1 / (npar + 4))

    # Calculate the Cholesky decomposition of the parameter covariance
    # matrix V, which is used to transform independent normal samples
    # into multivariate normal samples with covariance matrix V.
    try:
        cov_mat = stats.cov_wt(px[:, p_ixs], px[:, -2])
        a_mat = np.linalg.cholesky(cov_mat)
    except np.linalg.LinAlgError as e:
        # When the covariance matrix is not positive definite, print the name
        # and range of each parameter, and the covariance matrix itself.
        names = [name for (ix, vmin, vmax, name) in p_info
                 if ix in p_ixs]
        mins = np.min(px[:, p_ixs], axis=0)
        maxs = np.max(px[:, p_ixs], axis=0)
        means = np.mean(px[:, p_ixs], axis=0)
        mat_lines = str(cov_mat).splitlines()
        mat_sep = "\n      "
        mat_disp = mat_sep.join(["Covariance matrix:"] + mat_lines)
        logger = logging.getLogger(__name__)
        logger.warn("Post-RPF Cholesky decomposition: {}".format(e))
        logger.warn("Post-RPF parameters: {}".format(", ".join(names)))
        logger.warn("Minimum values: {}".format(mins))
        logger.warn("Maximum values: {}".format(maxs))
        logger.warn("Mean values:    {}".format(means))
        logger.warn(mat_disp)
        if params['resample']['regularise_or_fail']:
            raise
        else:
            return

    # Sample the multivariate normal with covariance V and mean of zero.
    std_samples = rnd.normal(size=(npar, count))
    scaled_samples = np.transpose(np.dot(a_mat, h * std_samples))
    # Add the sampled noise and clip to respect parameter bounds.
    new_px[:, p_ixs] = np.clip(new_px[:, p_ixs] + scaled_samples,
                               params['param_min'][None, p_ixs],
                               params['param_max'][None, p_ixs])


def resample(params, px):
    """Resample a particle population.

    :param params: The simulation parameters.
    :param px: An array of particle state vectors.

    The supported resampling methods are:

    - ``'basic'``:         uniform random numbers from [0, 1].
    - ``'stratified'``:    uniform random numbers from [j / m, (j + 1) / m).
    - ``'deterministic'``: select (j - a) / m for some fixed a.

    Where m is the number of particles and j = 0, ..., m - 1.

    These algorithms are described in G Kitagawa, J Comp Graph Stat
    5(1):1-25, 1996.
    `doi:10.2307/1390750 <http://dx.doi.org/10.2307/1390750>`_
    """
    # Sort the particle indices according to weight (in descending order), so
    # that we can determine the original index of each resampled particle.
    # Use the merge sort algorithm because it is stable (thus preserving the
    # behaviour of Python's built-in `sorted` function).
    sorted_ix = np.argsort(- px[:, -2], kind='mergesort')
    # Sort the weights in descending order.
    sorted_ws = px[sorted_ix, -2]
    # Calculate the upper bounds for each interval.
    bounds = np.cumsum(sorted_ws)
    # Generate the random samples using the specified resampling method.
    count = px.shape[0]
    method = params['resample']['method']
    rnd = params['resample']['rnd']
    if method == 'basic':
        choices = np.sort(rnd.uniform(size=count))
    elif method == 'stratified':
        choices = (rnd.uniform(size=count) + np.arange(count)) / count
    elif method == 'deterministic':
        choices = (rnd.uniform() + np.arange(count)) / count
    else:
        # This is an error.
        raise ValueError("Invalid resampling method '{}'".format(method))
    # Resample the particles.
    new_px = np.copy(px)
    # Since the intervals and random samples are both monotonic increasing, we
    # only need step through the samples and record the current interval.
    bix = 0
    for (j, rand_val) in enumerate(choices):
        while bounds[bix] < rand_val:
            bix += 1
        new_px[j, 0:-2] = px[sorted_ix[bix]][0:-2]
        new_px[j, -1] = sorted_ix[bix]
    # Renormalise the weights.
    new_px[:, -2] = 1.0 / count
    # Sample model parameter values from a regularised kernel, if requested.
    if params['resample']['regularisation']:
        post_regularise(params, px, new_px)
    # Copy the resampled particles back into the original array.
    px[:, :] = new_px[:, :]


def log_llhd_of(params, hist, hist_ix, obs, max_back=None):
    """Return the log-likelihood of obtaining observations from each particle.

    :param params: The simulation parameters.
    :param hist: The particle history matrix.
    :param hist_ix: The index of the current time-step in the history matrix.
    :param obs: The observation(s) that have been made.
    :param max_back: The number of time-steps into the past when the most
        recent resampling occurred (i.e., how far back the current particle
        ordering is guaranteed to persist; default is ``None``, no limit).

    :returns: An array containing the log-likelihood for each particle.
    """
    # Ensure we have received the entire particle history matrix.
    check.is_entire_matrix(params, hist)
    if 'last_n_periods' in params and params['last_n_periods'] > 1:
        # The model requires the last N observation periods.
        rng_n = range(1, params['last_n_periods'] + 1)
        periods = set(o['period'] * n for o in obs for n in rng_n)
    else:
        periods = set(o['period'] for o in obs)
    steps_per_unit = params['steps_per_unit']
    log_llhd = params['log_llhd_fn']

    # Extract the particle histories at every relevant prior step.
    # It may or may not be necessary to use earlier_states().
    def hist_for(period):
        """Return past state vectors in the appropriate order."""
        steps_back = steps_per_unit * period
        same_ixs = max_back is None or max_back >= steps_back
        if same_ixs:
            if steps_back > hist_ix:
                # If the observation period starts before the beginning of the
                # the simulation period, the initial state should be returned.
                return hist[0]
            else:
                return hist[hist_ix - steps_back]
        else:
            return earlier_states(hist, hist_ix, steps_back)
    period_hists = {period: hist_for(period) for period in periods}

    # Calculate the log-likelihood of obtaining the given observation, for
    # each particle.
    sc = params['hist']['state_cols']
    logs = log_llhd(params, obs, hist[hist_ix, :, 0:sc], period_hists,
                    hist[hist_ix, :, -2])

    return logs


def reweight(params, hist, hist_ix, obs, max_back=None):
    """Adjust particle weights in response to some observation(s).

    :param params: The simulation parameters.
    :param hist: The particle history matrix.
    :param hist_ix: The index of the current time-step in the history matrix.
    :param obs: The observation(s) that have been made.
    :param max_back: The number of time-steps into the past when the most
        recent resampling occurred (i.e., how far back the current particle
        ordering is guaranteed to persist; default is ``None``, no limit).

    :returns: A tuple; the first element (*bool*) indicates whether resampling
        is required, the second element (*float*) is the **effective** number
        of particles (i.e., accounting for weights).
    """
    # Calculate the log-likelihood of obtaining the given observation, for
    # each particle.
    logs = log_llhd_of(params, hist, hist_ix, obs, max_back)

    # Scale the log-likelihoods so that the maximum is 0 (i.e., has a
    # likelihood of 1) to increase the chance of smaller likelihoods
    # being within the range of double-precision floating-point.
    logs = logs - np.max(logs)
    # Calculate the effective number of particles, prior to reweighting.
    prev_eff = 1.0 / sum(w * w for w in hist[hist_ix, :, -2])
    # Update the current weights.
    hist[hist_ix, :, -2] *= np.exp(logs)
    ws_sum = np.sum(sorted(hist[hist_ix, :, -2]))
    # Renormalise the weights.
    hist[hist_ix, :, -2] /= ws_sum
    if np.any(np.isnan(hist[hist_ix, :, -2])):
        # Either the new weights were all zero, or every new non-zero weight
        # is associated with a particle whose previous weight was zero.
        nans = np.sum(np.isnan(hist[hist_ix, :, -2]))
        raise ValueError("{} NaN weights; ws_sum = {}".format(nans, ws_sum))
    # Determine whether resampling is required.
    num_eff = 1.0 / sum(w * w for w in hist[hist_ix, :, -2])
    req_resample = num_eff / params['size'] < params['resample']['threshold']

    # Detect when the effective number of particles has greatly decreased.
    eff_decr = num_eff / prev_eff
    if (eff_decr < 0.1):
        # Note: this could be mitigated by replacing the weights with their
        # square roots (for example) until the decrease is sufficiently small.
        logger = logging.getLogger(__name__)
        logger.debug("Effective particles decreased by {}".format(eff_decr))

    return (req_resample, num_eff)


def __log_step(params, when, do_resample, num_eff=None):
    """Log the state of the particle filter when an observation is made or
    when particles have been resampled.

    :param when: The current simulation time.
    :param do_resample: Whether particles were resampled at this time-step.
    :type do_resample: bool
    :param num_eff: The effective number of particles (default is ``None``).
    :type num_eff: float
    """
    logger = logging.getLogger(__name__)
    resp = {True: 'Y', False: 'N'}
    if num_eff is not None:
        logger.debug('{} RS: {}, #px: {:7.1f}'.format(
            params['time'].to_unicode(when), resp[do_resample], num_eff))
    elif do_resample:
        logger.debug('{} RS: {}'.format(
            params['time'].to_unicode(when), resp[do_resample]))


def step(params, hist, hist_ix, step_num, when, step_obs, max_back, is_fs):
    """Perform a single time-step for every particle.

    :param params: The simulation parameters.
    :param hist: The particle history matrix.
    :param hist_ix: The index of the current time-step in the history matrix.
    :param step_num: The time-step number.
    :param when: The current simulation time.
    :param step_obs: The list of observations for this time-step.
    :param max_back: The number of time-steps into the past when the most
        recent resampling occurred; must be either a positive integer or
        ``None`` (no limit).
    :param is_fs: Indicate whether this is a forecasting simulation (i.e., no
        observations).
        For deterministic models it is useful to add some random noise when
        estimating, to allow identical particles to differ in their behaviour,
        but this is not desirable when forecasting.

    :return: ``True`` if resampling was performed, otherwise ``False``.
    """
    # Ensure we have received the entire particle history matrix.
    check.is_entire_matrix(params, hist)

    d_t = params['dt']

    # Allocate an array that enumerates the particles, if it isn't present.
    if params['px_range'] is None:
        params['px_range'] = np.arange(params['size'])

    # Matrices of previous and current state vectors.
    sc = params['hist']['state_cols']
    prev = hist[hist_ix - 1, :, 0:sc]
    curr = hist[hist_ix, :, 0:sc]

    # Step each particle forward by one time-step.
    params['model'].update(params, when, d_t, is_fs, prev, curr)

    # Copy the particle weights from the previous time-step.
    # These will be updated by ``reweight`` as necessary.
    hist[hist_ix, :, -2] = hist[hist_ix - 1, :, -2]

    # The particle ordering is (as yet) unchanged.
    # This will be updated by ``resample`` as necessary.
    hist[hist_ix, :, -1] = params['px_range']

    # Account for observations, if any.
    num_eff = None
    do_resample = False
    if step_obs:
        do_resample, num_eff = reweight(params, hist, hist_ix, step_obs,
                                        max_back)

    __log_step(params, when, do_resample, num_eff)

    # Perform resampling when required.
    if do_resample:
        resample(params, hist[hist_ix])
        __log_step(params, when, True, params['size'])
    # Indicate whether resampling occurred at this time-step.
    return do_resample


def run(params, start, end, streams, summary, state=None,
        save_when=None, save_to=None):
    """Run the particle filter against any number of data streams.

    :param params: The simulation parameters.
    :type params: dict
    :param start: The start of the simulation period.
    :param end: The (**exclusive**) end of the simulation period.
    :param streams: A list of observation streams.
    :param summary: An object that generates summaries of each simulation.
    :param state: A previous simulation state as returned by, e.g., this
        function.
    :param save_when: Times at which to save the particle history matrix.
    :param save_to: The filename for saving the particle history matrix.

    :returns: The resulting simulation state: a dictionary that contains the
        simulation parameters (``'params'``), the particle history matrix
        (``'hist'``), and the summary statistics (``'summary'``).
    """
    # Construct the time-step generator.
    params['dt'] = 1.0 / params['steps_per_unit']
    seed = params['resample']['prng_seed']
    params['resample']['rnd'] = np.random.RandomState(seed)
    sim_time = params['time']
    sim_time.set_period(start, end, params['steps_per_unit'])
    steps = sim_time.with_observations(*streams)
    # Determine whether this is a forecasting run, by checking whether there
    # are any observation streams.
    is_fs = not streams
    # We allow the history matrix to be provided in order to allow, e.g., for
    # forecasting from any point in a completed simulation.
    if state is None:
        hist = history_matrix(params, sim_time)
        offset = 0
    else:
        hist = state['hist']
        offset = state['offset']
        # Ensure that the number of particles is recorded as a parameter.
        params['size'] = hist.shape[1]
        # Ensure the history matrix structure is appropriate.
        state_size = params['model'].state_size()
        extra = hist.shape[-1] - state_size
        if extra < 2:
            raise ValueError("Too few extra columns: {} < 2".format(extra))
        else:
            params['hist']['state_cols'] = state_size
            params['hist']['extra_cols'] = extra
            # Ensure we have received the entire particle history matrix.
            check.is_entire_matrix(params, hist)

    # Allocate space for the summary statistics.
    summary.allocate(start, end, forecasting=is_fs)
    win_start = start
    most_recent = None
    last_rs = None
    # Simulate each time-step.
    for (step_num, when, obs) in steps:
        hist_ix = step_num + offset
        # Checking for a "truthy" value is insufficient, since zero is a valid
        # scalar time!
        if win_start is None:
            win_start = most_recent
        # Check whether the end of the history matrix has been reached.
        # If so, shift the sliding window forward in time.
        if hist_ix == hist.shape[0]:
            # Calculate summary statistics in blocks.
            if most_recent is not None:
                # The current simulation has covered a well-defined block of
                # the history matrix.
                summary.summarise(hist, sim_time, win_start, most_recent,
                                  offset)
            else:
                # If most_recent is None, no time-steps have been simulated.
                # This means, e.g., a forecasting simulation has begun at the
                # final time-step in the matrix; the correct response is to
                # calculate summary statistics only for this one time-step.
                summary.summarise(hist, sim_time, win_start, win_start,
                                  offset)
            win_start = None
            shift = params['hist']['wind_shift'] * params['steps_per_unit']
            offset -= shift
            hist_ix = step_num + offset
            # Shift the sliding window forward.
            hist[:-shift, :, :] = hist[shift:, :, :]
            hist[hist_ix, :, :-2] = 0
        if last_rs is None:
            max_back = None
        else:
            max_back = (step_num - last_rs)
        resampled = step(params, hist, hist_ix, step_num, when, obs,
                         max_back, is_fs)
        if resampled:
            last_rs = step_num
        most_recent = when
        # Check whether to save the particle history matrix to disk.
        if save_when is not None and save_to is not None:
            if when in save_when:
                # Note: we only need to save the current matrix block!
                with h5py.File(save_to, 'a') as f:
                    when_str = params['time'].to_unicode(when)
                    grp = f.require_group(text.to_bytes(when_str))
                    # Replace any previously-saved state for this time.
                    if 'offset' in grp:
                        del grp['offset']
                    if 'hist' in grp:
                        del grp['hist']
                    grp.create_dataset('offset', data=np.int32(hist_ix))
                    grp.create_dataset('hist', data=np.float64(hist))
                    # Save the state of the summary object.
                    sum_grp = grp.require_group(text.to_bytes('summary'))
                    summary.save_state(sum_grp)

    # Calculate summary statistics for the remaining time-steps.
    if win_start is not None and most_recent is not None:
        summary.summarise(hist, sim_time, win_start, most_recent, offset)

    # Return the complete simulation state.
    return {'params': params.copy(), 'hist': hist,
            'summary': summary.get_stats()}


def __cleanup(files, dirs):
    """Delete temporary files and directories.
    This is intended for use with ``atexit.register()``.

    :param files: The list of files to delete.
    :param dirs: The list of directories to delete (*after* all of the files
        have been deleted). Note that these directories must be empty in order
        to be deleted.
    """
    logger = logging.getLogger(__name__)

    for tmp_file in files:
        if os.path.isfile(tmp_file):
            try:
                os.remove(tmp_file)
                logger.debug("Deleted '{}'".format(tmp_file))
            except OSError as e:
                msg = "Can not delete '{}': {}".format(tmp_file, e.strerror)
                logger.warning(msg)
        elif os.path.exists(tmp_file):
            logger.warning("'{}' is not a file".format(tmp_file))
        else:
            logger.debug("File '{}' already deleted".format(tmp_file))

    for tmp_dir in dirs:
        if os.path.isdir(tmp_dir):
            try:
                os.rmdir(tmp_dir)
                logger.debug("Deleted '{}'".format(tmp_dir))
            except OSError as e:
                msg = "Can not delete '{}': {}".format(tmp_dir, e.strerror)
                logger.warning(msg)
        elif os.path.exists(tmp_dir):
            logger.warning("'{}' is not a directory".format(tmp_dir))
        else:
            logger.debug("Directory '{}' already deleted".format(tmp_dir))


def resume_from_cache(params, streams, fs_dates, summary):
    """
    Load the particle history matrix from a cache file, allowing forecasting
    runs to resume at the point of the first updated/new observation.

    :param params: The simulation parameters.
    :param streams: A list of observation streams.
    :param fs_dates: The dates at which forecasts should be generated.
    :param summary: An object that generates summaries of each simulation.

    :returns: A dictionary with keys:

        - ``'state'``: Either a simulation state (see :py:func:`~pypfilt.run`)
          or ``None`` if there is no cached state from which to resume.
        - ``'start'``: Either the time from which to begin the simulation, or
          ``None`` if there is no cached state.
        - ``'end'``: Either the time at which to end the simulation, or
          ``None`` if there is no cached state.
        - ``'fs_dates'``: The dates at which forecasts should be generated.
        - ``'save_to'``: The filename for saving the particle history matrix.
        - ``'clean'``: A cleanup function to remove any temporary files, and
          which will have been registered to execute at termination.
    """
    logger = logging.getLogger(__name__)

    cache_file = None
    if 'cache_file' in params['hist']:
        if params['hist']['cache_file'] is not None:
            cache_file = os.path.join(params['out_dir'],
                                      params['hist']['cache_file'])

    def check_completeness(obs):
        """Define the 'incomplete' and 'upper_bound' observation fields."""
        if 'incomplete' not in obs:
            obs['incomplete'] = False
        if 'upper_bound' not in obs:
            obs['upper_bound'] = 0
        return obs

    def no_match(obs, obs_list):
        """Compare observations, but ignore fields such as ``'source'``."""
        semi_match = [o for o in obs_list if o['date'] == obs['date']
                      and o['value'] == obs['value']
                      and o['unit'] == obs['unit']
                      and o['period'] == obs['period']
                      and o['incomplete'] == obs['incomplete']
                      and o['upper_bound'] == obs['upper_bound']]
        return len(semi_match) == 0

    def df_to_dict(df):
        """Convert structured arrays of observations into dictionaries."""
        cols = df.dtype.names

        def convert_values(tuples):
            """Convert dates and strings into appropriate values."""
            for (name, v) in tuples:
                name = text.to_unicode(name)
                if name == 'date':
                    yield (name, params['time'].from_dtype(v))
                else:
                    if text.is_bytes(v):
                        v = text.to_unicode(v)
                    yield (name, v)

        obs_list = [dict(convert_values(zip(cols, row))) for row in df]
        return [check_completeness(o) for o in obs_list]

    if cache_file is not None:
        # The default result, should there be no suitable cached state.
        result = {'state': None, 'start': None, 'end': None,
                  'fs_dates': fs_dates,
                  'save_to': cache_file, 'clean': lambda: None}

        if not os.path.exists(cache_file):
            logger.debug("Missing cache file: '{}'".format(cache_file))
            return result

        try:
            with h5py.File(cache_file, 'r') as f:
                logger.debug("Reading cache file: '{}'".format(cache_file))
                if 'obs' in f:
                    logger.debug("Cache file has observations")
                    cached_obs = df_to_dict(f['obs'][()])
                    # Note: only consider dates up to (and including) the
                    # earliest forecasting date, even if there are later
                    # observations and later cached states consistent with
                    # these observations, because the user has *requested*
                    # forecasts for these dates (perhaps some forecasts were
                    # not generated at the time or were subsequently deleted).
                    current_obs = [check_completeness(o)
                                   for o in sum(streams, [])
                                   if o['date'] <= min(fs_dates)]
                    diff_list = [o for o in cached_obs + current_obs
                                 if no_match(o, cached_obs) or
                                 no_match(o, current_obs)]
                    if diff_list:
                        first_diff = min(o['date'] for o in diff_list)
                        logger.debug("First difference detected at {}".format(
                            first_diff))
                        cached_vals = [o['value'] for o in cached_obs
                                       if o['date'] == first_diff]
                        current_vals = [o['value'] for o in current_obs
                                        if o['date'] == first_diff]
                        if cached_vals:
                            cached_val = cached_vals[0]
                        else:
                            cached_val = 'None'
                        if current_vals:
                            current_val = current_vals[0]
                        else:
                            current_val = 'None'
                        logger.debug("Different values: was {} now {}".format(
                            cached_val, current_val))
                        # There may not be any prior observations.
                        prior_obs = [o for o in cached_obs
                                     if o['date'] < first_diff]
                        if not prior_obs:
                            logger.debug("No prior observation found")
                            return result
                        else:
                            last_good = max(o['date'] for o in prior_obs)
                            logger.debug("Prior observation at {}".format(
                                last_good))
                    else:
                        logger.debug("No differences detected")
                        last_good = max(o['date'] for o in cached_obs)

                    if last_good >= min(fs_dates):
                        logger.debug("Last known-good date may be too recent")

                    grp_str = params['time'].to_unicode(last_good)
                    grp = text.to_bytes(grp_str)
                    if grp not in f:
                        logger.debug("Last known-good date not in cache")
                        logger.debug("Looking for '{}' in:".format(grp_str))
                        for node in f.keys():
                            logger.debug("    '{}'".format(node))

                        # Search backwards for the most recent saved state.
                        try_dates = sorted((o['date'] for o in current_obs
                                            if o['date'] < last_good),
                                           reverse=True)
                        for date in try_dates:
                            grp_str = params['time'].to_unicode(date)
                            grp = text.to_bytes(grp_str)
                            if grp in f:
                                msg = "Most recent cache: {}".format(grp_str)
                                logger.debug(msg)
                                last_good = date
                                break

                        # No suitable cached state, return the default result.
                        if grp not in f:
                            return result

                    logger.debug("Loading state for {}".format(last_good))
                    result['start'] = last_good

                    # Only estimate up to the final forecasting date.
                    if len(result['fs_dates']) > 0:
                        result['end'] = max(result['fs_dates'])

                    # Load the cached state for this date.
                    result['state'] = {
                        'hist': f[grp]['hist'][()],
                        'offset': f[grp]['offset'][()]
                    }
                    # Load the cached state of the summary object.
                    sum_grp = f[grp]['summary']
                    logger.debug("Loading summary from {}".format(sum_grp))
                    summary.load_state(sum_grp)

                    return result
                else:
                    logger.debug("Cache file does not have observations")
                    return result
        except IOError:
            logger.debug("Could not read cache file: '{}'".format(cache_file))
            return result
    else:
        # No simulation state to load, use a temporary file.
        tmp_dir = tempfile.mkdtemp(dir=params['tmp_dir'])
        tmp_file = os.path.join(tmp_dir, "history.hdf5")

        # Ensure these files are always deleted upon *normal* termination.
        atexit.register(__cleanup, files=[tmp_file], dirs=[tmp_dir])

        # Ensure these files are always deleted when killed by SIGTERM.
        def clean_at_terminate(signal_num, stack_frame):
            __cleanup(files=[tmp_file], dirs=[tmp_dir])
            os._exit(0)

        signal.signal(signal.SIGTERM, clean_at_terminate)

        logger.debug("Temporary file for history matrix: '{}'".format(
            tmp_file))

        def clean():
            __cleanup(files=[tmp_file], dirs=[tmp_dir])

        return {'state': None, 'start': None, 'end': None,
                'fs_dates': fs_dates, 'save_to': tmp_file, 'clean': clean}


def forecast(params, start, end, streams, dates, summary, filename):
    """Generate forecasts from various dates during a simulation.

    :param params: The simulation parameters.
    :type params: dict
    :param start: The start of the simulation period.
    :param end: The (**exclusive**) end of the simulation period.
    :param streams: A list of observation streams.
    :param dates: The dates at which forecasts should be generated.
    :param summary: An object that generates summaries of each simulation.
    :param filename: The output file to generate (can be ``None``).

    :returns: The simulation state for each forecast date.
    """

    # Ensure that there is at least one forecasting date.
    if len(dates) < 1:
        raise ValueError("No forecasting dates specified")

    # Ensure that the forecasting dates lie within the simulation period.
    invalid_fs = [params['time'].to_unicode(d) for d in dates
                  if d < start or d >= end]
    if invalid_fs:
        raise ValueError("Invalid forecasting date(s) {}".format(invalid_fs))

    logger = logging.getLogger(__name__)

    # Record the true start of the simulation period.
    params['epoch'] = start

    # Generate forecasts in order from earliest to latest forecasting date.
    # Note that forecasting from the start date will duplicate the estimation
    # run (below) and is therefore redundant *if* sim['end'] is None.
    forecast_dates = [d for d in sorted(dates) if d >= start]

    # Load the most recently cached simulation state that is consistent with
    # the current observations.
    sim = resume_from_cache(params, streams, forecast_dates, summary)

    # Update the forecasting dates.
    if not sim['fs_dates']:
        logger.warning("All {} forecasting dates precede cached state".format(
            len(forecast_dates)))
        return
    forecast_dates = sim['fs_dates']

    # Update the simulation period.
    if sim['start'] is not None:
        start = sim['start']
    if sim['end'] is not None:
        # Only simulate as far as the final forecasting date, then forecast.
        est_end = sim['end']
    else:
        est_end = end

    # Avoid the estimation pass when possible.
    if start == est_end:
        logger.info("  {}  No estimation pass needed for {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), est_end))
    else:
        logger.info("  {}  Estimating  from {} to {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), start, est_end))

    state = run(params, start, est_end, streams, summary, state=sim['state'],
                save_when=forecast_dates, save_to=sim['save_to'])

    # Also save the (flat list of) observations to the cache file.
    from . import summary as summary_mod
    obs_list = sum(streams, [])
    obs_df = summary_mod.obs_table(params, obs_list)
    logger.debug("Saving observations to cache: '{}'".format(sim['save_to']))
    with h5py.File(sim['save_to'], 'a') as f:
        if 'obs' in f:
            del f['obs']
        f.create_dataset('obs', data=obs_df)

    # Save the complete simulation, which incorporated every observation
    # throughout the entire simulation period.
    forecasts = {'complete': state}

    # Ensure the dates are ordered from latest to earliest.
    for start_date in forecast_dates:
        logger.info("  {}  Forecasting from {} to {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"),
            params['time'].to_unicode(start_date),
            params['time'].to_unicode(end)))
        # We can reuse the history matrix for each forecast, since all of the
        # pertinent details are recorded in the summary.
        with h5py.File(sim['save_to'], 'r') as f:
            grp_str = params['time'].to_unicode(start_date)
            try:
                grp = f[text.to_bytes(grp_str)]
            except KeyError:
                msg = "State for forecast date {!r} not found in: {!r}"
                raise ValueError(msg.format(grp_str, list(f.keys())))
            state['offset'] = grp['offset'][()]
            state['hist'] = grp['hist'][:, :, :]
            # Load the cached state of the summary object.
            sum_grp = grp['summary']
            summary.load_state(sum_grp)

        fstate = run(state['params'], start_date, end, [], summary,
                     state=state)

        forecasts[start_date] = fstate

    # Save the observations (flattened into a single list).
    forecasts['obs'] = obs_list

    # Save the forecasting results to disk.
    if filename is not None:
        logger.info("  {}  Saving to:  {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), filename))
        # Save the results in the output directory.
        filepath = os.path.join(params['out_dir'], filename)
        summary.save_forecasts(forecasts, filepath)

    # Remove the temporary file and directory.
    sim['clean']()

    return forecasts


def default_params(model, time_scale, max_days=0, px_count=0):
    """The default particle filter parameters.

    Memory usage can reach extreme levels with a large number of particles,
    and so it may be necessary to keep only a sliding window of the entire
    particle history matrix in memory.

    :param model: The system model.
    :param time_scale: The simulation time scale.
    :param max_days: The number of contiguous days that must be kept in memory
        (e.g., the largest observation period).
    :param px_count: The number of particles.
    """
    details = model.describe()
    p_min = [vmin for (name, smooth, vmin, vmax) in details]
    p_max = [vmax for (name, smooth, vmin, vmax) in details]
    params = {
        'resample': {
            # Resample when the effective number of particles is 25%.
            'threshold': 0.25,
            # The deterministic method is the best resampling method, see the
            # appendix of Kitagawa 1996 (DOI:10.2307/1390750).
            'method': 'deterministic',
            # Use the default initial PRNG state, whatever that might be.
            'prng_seed': None,
            # Resample from the weighted discrete probability distribution,
            # rather than using a continuous approximation (regularisation).
            'regularisation': False,
            # By default, continue without regularisation if the parameter
            # covariance matrix is not positive definite.
            'regularise_or_fail': False,
            # The minimum range of values that a parameter must have in order
            # to be subject to the post-regularised particle filter.
            'reg_toln': 1e-8,
        },
        'hist': {
            # The sliding window size, in days.
            'wind_size': 2 * max_days,
            # The amount to shift the sliding window, in days.
            'wind_shift': max_days,
            # The number of particles.
            'px_count': px_count,
        },
        # Define the simulation time scale.
        'time': time_scale,
        # Simulate 5 time-steps per unit time.
        'steps_per_unit': 5,
        # Provide only the most recent observation period (for likelihoods).
        'last_n_periods': 1,
        # An array that enumerates the particles.
        'px_range': None,
        # The simulation model.
        'model': model,
        # The lower bounds for each model parameter.
        'param_min': np.array(p_min),
        # The upper bounds for each model parameter.
        'param_max': np.array(p_max),
        # Directory for storing output files.
        'out_dir': '.',
        # Directory for storing temporary files.
        'tmp_dir': tempfile.gettempdir(),
    }
    # Define the simulation model parameter priors.
    params['prior'] = model.priors(params)
    return params


def history_matrix(params, sim_time, extra=2):
    """Allocate a particle history matrix of sufficient size to store an
    entire particle filter simulation.

    :param params: The simulation parameters.
    :type params: dict
    :param sim_time: The simulation period.
    :type sim_time: :py:class:`~pypfilt.Time`
    :param extra: The number of additional columns.
    :type extra: int

    :returns: A particle history matrix.
    :rtype: numpy.ndarray
    """
    # Determine the size of the state vector; provide an index of -1 to
    # indicate that this is not a true model instantiation (i.e., that we
    # won't use the return value beyond checking its dimensions).
    state_size = params['model'].state_size()
    # Ensure sufficient columns to record particle weights and parents.
    if extra < 2:
        raise ValueError("Too few extra columns: {} < 2".format(extra))
    # Determine the number of particles and their initial weights.
    px_count = params['hist']['px_count']
    # Ensure there is a strictly-positive number of particles.
    if px_count < 1:
        raise ValueError("Too few particles: {}".format(px_count))
    init_weight = 1.0 / px_count
    # Record the number of particles.
    logger = logging.getLogger(__name__)
    logger.debug("Size = {}".format(px_count))
    # Determine the number of time-steps for which to allocate space.
    if params['hist']['wind_size'] > 0 and params['hist']['wind_shift'] > 0:
        num_steps = params['hist']['wind_size'] * params['steps_per_unit'] + 1
    else:
        num_steps = sim_time.step_count() + 1
    # Record the number of particles.
    params['size'] = px_count
    # Record the number of state columns and extra columns.
    params['hist']['state_cols'] = state_size
    params['hist']['extra_cols'] = extra
    # Allocate an array that enumerates the particles.
    params['px_range'] = np.arange(px_count)
    # Allocate the particle history matrix and record the initial states.
    hist = np.zeros((num_steps, px_count, state_size + extra))
    logger.debug("Hist.nbytes = {}".format(hist.nbytes))
    params['model'].init(params, hist[0, :, 0:state_size])
    hist[0, :, -2] = init_weight
    hist[0, :, -1] = params['px_range']
    # Return the allocated (and initialised) particle history matrix.
    return hist


def earlier_states(hist, ix, steps):
    """Return the particle states at a previous time-step, ordered with
    respect to their current arrangement.

    :param hist: The particle history matrix.
    :param ix: The current time-step index.
    :param steps: The number of steps back in time.
    """
    parent_ixs = np.arange(hist.shape[1])
    # Don't go too far back (negative indices jump into the future).
    steps = min(steps, ix)
    for i in range(steps):
        parent_ixs = hist[ix - i, parent_ixs, -1].astype(int)
    return hist[ix - steps, parent_ixs, :]
