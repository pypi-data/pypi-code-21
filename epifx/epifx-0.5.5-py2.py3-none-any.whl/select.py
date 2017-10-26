"""Select particles according to desired target distributions."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import abc
import epifx.summary
import logging
import numpy as np
import pypfilt.summary
import scipy.stats

# Create a new metaclass for abstract base classes (ABCs), so that subclasses
# can only be instantiated if they implement all of the abstract methods.
# The metaclass syntax differs between Python 2 and 3, the following line is
# the simplest way to sidestep this issue without relying on ``six``.
ABC = abc.ABCMeta(str('ABC'), (object,), {})


class Target(ABC):
    """The base class for target particle distributions."""

    @abc.abstractmethod
    def prepare_summary(self, summary):
        """
        Add the necessary tables to a summary object so that required summary
        statistics are recorded.

        :param summary: The summary object to which the required tables should
            be added.
        """
        pass

    @abc.abstractmethod
    def logpdf(self, output):
        """
        Return the log of the target probability density for each particle.

        :param output: The state object returned by ``pypfilt.run``; summary
            tables are located at ``output['summary'][table_name]``.
        """
        pass


class TargetPeakMVN(Target):
    """A multivariate normal distribution for the peak timing and size."""

    def __init__(self, peak_sizes, peak_times):
        """
        :param peak_sizes: An array of previously-observed peak sizes.
        :param peak_time: An array of previously-observed peak times.
        """
        exp_size = np.mean(peak_sizes)
        std_size = np.std(peak_sizes, ddof=1)
        exp_time = np.mean(peak_times)
        std_time = np.std(peak_times, ddof=1)
        self.pdf_size = scipy.stats.norm(loc=exp_size, scale=std_size)
        self.pdf_time = scipy.stats.norm(loc=exp_time, scale=std_time)
        self.log_p_max = (self.pdf_size.logpdf(exp_size) +
                          self.pdf_time.logpdf(exp_time))

    def prepare_summary(self, summary):
        mon = epifx.summary.PeakMonitor()
        tbl = epifx.summary.PeakForecastEnsembles(mon, fs_only=False)
        summary.add_tables(tbl)

    def logpdf(self, params, output):
        t = params['time']
        tbl = output['summary']['peak_ensemble']
        size = tbl['value']
        time = np.array([t.to_scalar(t.from_dtype(bs)) for bs in tbl['date']])
        log_p_size = self.pdf_size.logpdf(size)
        log_p_time = self.pdf_time.logpdf(time)
        return log_p_size + log_p_time - self.log_p_max


class TargetAny(Target):
    """A distribution that accepts all proposals with equal likelihood."""

    def prepare_summary(self, summary):
        mon = epifx.summary.PeakMonitor()
        tbl = epifx.summary.PeakForecastEnsembles(mon, fs_only=False)
        summary.add_tables(tbl)

    def logpdf(self, params, output):
        return np.zeros(params['hist']['px_count'])


class Proposal(ABC):
    """The base class for proposal particle distributions."""

    @abc.abstractmethod
    def sample(self, params, hist, prng):
        """
        Draw particle samples from the proposal distribution.

        :param params: The simulation parameters.
        :param hist: The particle history matrix into which the samples should
            be written.
        :param prng: The PRNG instance to use for any random sampling.
        """
        pass


class DefaultProposal(Proposal):
    """
    A proposal distribution that independently samples each parameter from the
    prior distributions provided in the simulation parameters.
    """

    def sample(self, params, hist, prng):
        prev_prng = params['epifx']['rnd']
        params['epifx']['rnd'] = prng
        params['model'].sample_params(params, hist)
        params['epifx']['rnd'] = prev_prng


def select(params, start, end, proposal, target, seed, info=False):
    """
    Select particles according to a target distribution.

    :param params: The simulation parameters (note: the parameter dictionary
        will be emptied once the particles have been selected).
    :param start: The start of the simulation period.
    :param end: The end of the simulation period.
    :param proposal: The proposal distribution.
    :param target: The target distribution.
    :param seed: The PRNG seed used for sampling and accepting particles.
    :param info: Whether to return additional information about the particles.

    :returns: If ``info`` is ``False``, returns the initial state vector for
        each accepted particle. If ``info`` is ``True``, returns a tuple that
        contains the initial state vectors, a boolean array that indicates
        which of the proposed particles were accepted, and the summary tables
        for all proposed particles.
    """
    logger = logging.getLogger(__name__)

    # Initialise the parameters, history matrix, etc.
    prng = np.random.RandomState(seed)
    px_count = params['hist']['px_count']
    params['time'].set_period(start, end, params['steps_per_unit'])
    bad_ixs = np.arange(px_count)
    accepted = []
    tables = {}
    hist = pypfilt.history_matrix(params, params['time'])
    state_cols = params['hist']['state_cols']
    metadata = epifx.summary.Metadata()

    # Construct a fake date for each observation system, so that
    # pypfilt.summary.HDF5 can determine the observation types.
    fake_date = params['time'].add_scalar(end, 1)
    fake_obs = [{
        'date': fake_date,
        'value': 1,
        'unit': unit,
        'period': om['obs_model'].period,
        'source': "{}.{}".format(__name__, 'select'),
    } for unit, om in params['obs'].items()]

    # Draw samples and accept them according to the target distribution.
    while bad_ixs.shape[0] > 0:
        # Adjust the parameters accordingly.
        px_count = bad_ixs.shape[0]
        params['hist']['px_count'] = px_count
        params['px_range'] = np.arange(px_count)
        params['size'] = px_count
        # Adjust the particle history matrix, including the parent index.
        sample_hist = hist[:, bad_ixs, :]
        sample_hist[0, :, -1] = np.arange(px_count)
        # Also reset the weights.
        sample_hist[0, :, -2] = 1 / px_count
        state = {'hist': sample_hist, 'offset': 0}
        # Rebuild the metadata and initialise the summary object.
        meta = metadata.build(params)
        summary = pypfilt.summary.HDF5(params, fake_obs, meta=meta,
                                       first_day=True)
        target.prepare_summary(summary)
        # Draw samples from the proposal and run them forward.
        proposal.sample(params, sample_hist, prng)
        output = pypfilt.run(params, start, end, [fake_obs], summary,
                             state=state)
        # Decide which of the proposed samples to accept.
        log_pr = target.logpdf(params, output)
        thresh = prng.uniform(size=px_count)
        accept = np.log(thresh) < log_pr
        # Record which of the proposed particles are accepted.
        accepted.append(accept)
        msg = "Accept {:5d} of {:5d}"
        logger.debug(msg.format(np.sum(accept), px_count))
        # Keep the accepted samples.
        accept_ixs = bad_ixs[accept]
        hist[0, accept_ixs, :] = sample_hist[0, accept, :]
        # Update the accept/reject mask.
        bad_ixs = bad_ixs[np.logical_not(accept)]
        # Store the new summary tables.
        for name, tbl in output['summary'].items():
            if name in tables:
                tables[name].append(tbl)
            else:
                tables[name] = [tbl]

    # Empty the parameters dictionary so that it can't be accidentally reused.
    params.clear()

    # Aggregate and save each set of tables.
    for name, tbls in tables.items():
        tables[name] = np.concatenate(tbls)
        accepted = np.concatenate(accepted)

    # Return the initial state vector of each accepted particle.
    if info:
        return hist[0, :, :state_cols], accepted, tables
    else:
        return hist[0, :, :state_cols]
