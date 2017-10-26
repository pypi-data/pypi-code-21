"""Models of disease transmission in human populations."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import numpy as np
import pypfilt


class SEIR(pypfilt.Model):
    r"""
    An SEIR compartment model for a single circulating influenza strain, under
    the assumption that recovered individuals are completely protected against
    reinfection.

    .. math::

        \frac{dS}{dt} &= - \beta S^\eta I \\[0.5em]
        \frac{dE}{dt} &= \beta S^\eta I - \sigma E \\[0.5em]
        \frac{dI}{dt} &= \sigma E - \gamma I \\[0.5em]
        \frac{dR}{dt} &= \gamma I \\[0.5em]
        \beta &= R_0 \cdot \gamma

    ==============  ================================================
    Parameter       Meaning
    ==============  ================================================
    :math:`R_0`     Basic reproduction number
    :math:`\sigma`  Inverse of the incubation period (day :sup:`-1`)
    :math:`\gamma`  Inverse of the infectious period (day :sup:`-1`)
    :math:`\eta`    Inhomogeneous social mixing coefficient
    :math:`\alpha`  Temporal forcing coefficient
    ==============  ================================================

    The force of infection can be subject to temporal forcing :math:`F(t)`, as
    mediated by :math:`\alpha`:

    .. math::

        \beta(t) = \beta \cdot \left[1 + \alpha \cdot F(t)\right]

    Note that this requires the forcing function :math:`F(t)` to be defined in
    the simulation parameters (see the `Temporal Forcing`_ documentation).
    """

    __info = [("S", False, 0, 1), ("E", False, 0, 1), ("I", False, 0, 1),
              ("R", False, 0, 1),
              ("R0", True, 1, 2), ("sigma", True, 1/3, 2),
              ("gamma", True, 1/3, 1), ("eta", True, 1, 2),
              ("alpha", True, -0.2, 0.2),
              ("t0", False, 0, 50),
              ]

    def __init__(self):
        """Initialise the model instance."""
        super(SEIR, self).__init__()
        self.sampled_vecs = None

    def init(self, params, vec):
        """Initialise a state vector.

        :param params: Simulation parameters.
        :param vec: An uninitialised state vector of correct dimensions (see
            :py:func:`~state_size`).
        """
        # Initialise the model state (fully susceptible population).
        vec[..., 0] = 1
        vec[..., 1:] = 0
        # Sample the model parameters.
        self.sample_params(params, vec)
        # Enforce invariants on model parameters.
        p_min = params['param_min']
        p_max = params['param_max']
        # Note: a memory leak arose when using the ``out`` parameter.
        vec[..., 4:] = np.clip(vec[..., 4:], p_min[4:], p_max[4:])

    def state_size(self):
        """Return the size of the state vector."""
        return len(self.__info)

    def priors(self, params):
        """
        Return a dictionary of model parameter priors.

        :param params: Simulation parameters.
        """
        # Sample R0, eta, alpha and t0 from uniform distributions.
        R0_l, l_l, i_l, eta_l, alp_l, t0_l = params['param_min'][4:]
        R0_u, l_u, i_u, eta_u, alp_u, t0_u = params['param_max'][4:]
        # Sample sigma and gamma from inverse uniform distributions.
        l_l, l_u, i_l, i_u = 1 / l_l, 1 / l_u, 1 / i_l, 1 / i_u
        priors = {
            # The basic reproduction number.
            'R0': lambda r, size=None: r.uniform(R0_l, R0_u, size=size),
            # Inverse of the incubation period (days^-1).
            'sigma': lambda r, size=None: 1 / r.uniform(l_l, l_u, size=size),
            # Inverse of the infectious period (days^-1).
            'gamma': lambda r, size=None: 1 / r.uniform(i_l, i_u, size=size),
            # Power-law scaling of (S/N), found to be ~= 2 in large US cities.
            'eta': lambda r, size=None: r.uniform(eta_l, eta_u, size=size),
            # Temporal forcing coefficient, requires a look-up function.
            'alpha': lambda r, size=None: r.uniform(alp_l, alp_u, size=size),
            # Time of the initial exposure event (relative to start time).
            't0': lambda r, size=None: r.uniform(t0_l, t0_u, size=size),
            # Relative scale of the noise in compartment flows.
            'noise_flow': lambda r: np.array(0.025),
            # Relative scale of the noise in model parameters.
            'noise_param': lambda r: np.array(5e-4),
        }
        return priors

    def sample_params(self, params, vec):
        """Sample the model parameters for every particle.

        :param params: Simulation parameters.
        :param vec: The initial particle states.
        """
        if self.sampled_vecs is not None:
            if self.sampled_vecs.shape == vec[..., 4:10].shape:
                vec[..., 4:10] = self.sampled_vecs
                return
            else:
                fmt = "Incompatible matrices: {} (vec) and {} (samples)"
                msg = fmt.format(self.sampled_vecs.shape,
                                 vec[..., 4:10].shape)
                raise ValueError(msg)

        prior = params['prior']
        rnd = params['epifx']['rnd']
        rnd_size = vec[..., 0].shape
        forcing = 'forcing' in params['epifx']
        vec[..., 4] = prior['R0'](rnd, size=rnd_size)
        vec[..., 5] = prior['sigma'](rnd, size=rnd_size)
        vec[..., 6] = prior['gamma'](rnd, size=rnd_size)
        vec[..., 7] = prior['eta'](rnd, size=rnd_size)
        if forcing:
            vec[..., 8] = prior['alpha'](rnd, size=rnd_size)
        else:
            vec[..., 8] = 0
        # Select the time of first exposure for each particle.
        vec[..., 9] = prior['t0'](rnd, size=rnd_size)

    def set_params(self, vec):
        """Read the model parameters from the provided matrix."""
        self.sampled_vecs = vec[:, 4:]

    def load_params(self, sample_file):
        """Load the model parameters from a file."""
        self.sampled_vecs = np.loadtxt(sample_file, skiprows=1)

    def save_params(self, vec, sample_file):
        """Save the model parameters to a file."""
        names = [n for (n, _, _, _) in self.describe()[4:]]
        param_vals = vec[:, 4:]
        tbl = np.core.records.fromrecords(param_vals, names=names)
        np.savetxt(sample_file, tbl, header=' '.join(names), comments='')

    def update(self, params, step_date, dt, is_fs, prev, curr):
        """Perform a single time-step.

        :param params: Simulation parameters.
        :param step_date: The date and time of the current time-step.
        :param dt: The time-step size (days).
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """
        # Use 3 masks to identify which state vectors should be (a) seeded,
        # (b) copied, and (c) stepped forward.
        #
        # This method makes extensive use of NumPy's broadcasting rules.
        # See http://docs.scipy.org/doc/numpy/user/basics.broadcasting.html
        # for details and links to tutorials/examples.
        #
        # Also note that the state vectors are assumed to be stored in a 2D
        # array (hence the use of ``axis=0`` when calculating the masks).
        # To generalise this to N dimensions, the following should be used:
        #
        #     np.all(..., axis=range(len(curr.shape) - 1)
        #
        # We ignore this for now, on the basis that we should only ever need a
        # flat array of particles at each time-step.

        rnd = params['epifx']['rnd']

        # Determine whether temporal forcing is being used.
        forcing = 'forcing' in params['epifx']

        # The lower and upper parameter bounds.
        p_min = params['param_min']
        p_max = params['param_max']

        # Determine which particles will be seeded with an exposure.
        t = params['time'].to_scalar(step_date)
        # Calculate the time to first infection, relative to the start of the
        # simulation period.
        t0 = params['time'].to_scalar(params['epoch'])
        mask_init = np.logical_and(prev[..., 0] == 1,
                                   prev[..., 9] <= (t - t0))
        if np.any(mask_init):
            seed_infs = self.initial_exposures(
                params, shape=mask_init[mask_init].shape)

        # Determine which particles remain in their current (initial) state.
        mask_copy = np.all([prev[..., 0] == 1, np.logical_not(mask_init)],
                           axis=0)
        # Determine which particles will need to step forward in time.
        mask_step = np.logical_not(np.any([mask_init, mask_copy], axis=0))

        if np.any(mask_init):
            # Seed initial infections.
            # Note: the I and R compartments remain at zero.
            curr[mask_init, 0] = 1 - seed_infs
            curr[mask_init, 1] = seed_infs
            curr[mask_init, 2:] = prev[mask_init, 2:]

        if np.any(mask_copy):
            # Nothing happening, entire population remains susceptible.
            curr[mask_copy, :] = prev[mask_copy, :]

        if np.any(mask_step):
            # Calculate flows between compartments.
            rnd_size = curr[mask_step, 0].shape
            curr[mask_step, :] = prev[mask_step, :]

            # Determine the force of infection.
            beta = curr[mask_step, 4] * curr[mask_step, 6]
            if forcing:
                # Modulate the force of infection with temporal forcing.
                force = params['epifx']['forcing'](step_date)
                force *= curr[mask_step, 8]
                # Ensure the force of infection is non-negative (can be zero).
                beta *= np.maximum(1.0 + force, 0)

            s_to_e = dt * (beta * curr[mask_step, 2] *
                           curr[mask_step, 0] ** curr[mask_step, 7])
            e_to_i = dt * (curr[mask_step, 5] * curr[mask_step, 1])
            i_to_r = dt * (curr[mask_step, 6] * curr[mask_step, 2])
            # Account for stochastic behaviour, if appropriate.
            if params['epifx']['stoch']:
                # Define the relative scales of the noise terms.
                scale = np.empty(shape=8)
                scale[:3] = params['prior']['noise_flow'](rnd)
                scale[3:] = params['prior']['noise_param'](rnd)
                n_size = rnd_size + (8,)
                noise = scale[np.newaxis, :] * dt * rnd.normal(size=n_size)
                # Scale the noise parameters in proportion to the flow rates
                # in to and out of each model compartment (i.e., S, E, I, R),
                # according to the scaling law of Gaussian fluctuations.
                # For more details see doi:10.1016/j.mbs.2012.05.010
                noise[..., 0] *= np.sqrt(s_to_e / dt)
                noise[..., 1] *= np.sqrt(e_to_i / dt)
                noise[..., 2] *= np.sqrt(i_to_r / dt)
                # Add noise to the inter-compartment flows.
                s_to_e += noise[..., 0]
                e_to_i += noise[..., 1]
                i_to_r += noise[..., 2]
                # Add noise to the model parameters *except* t0.
                curr[mask_step, 4:9] += noise[..., 3:]
                # Enforce invariants on model parameters *except t0*.
                curr[mask_step, 4:9] = np.clip(curr[mask_step, 4:9],
                                               p_min[4:9], p_max[4:9])
                if not forcing:
                    # Do not allow sigma to vary if there is no forcing.
                    curr[mask_step, 8] = 0
            # Update compartment sizes.
            curr[mask_step, 0] -= s_to_e
            curr[mask_step, 1] += s_to_e - e_to_i
            curr[mask_step, 2] += e_to_i - i_to_r
            # Enforce invariants on S, E, and I compartments.
            curr[mask_step, :3] = np.clip(curr[mask_step, :3], 0, 1)
            mask_invalid = np.sum(curr[mask_step, :3], axis=-1) > 1
            if np.any(mask_invalid):
                # Ensure we're updating the original matrix, not a copy.
                mask_sub = np.logical_and(mask_step,
                                          np.sum(curr[:, :3], axis=-1) > 1)
                sub = (np.sum(curr[mask_sub, :3], axis=-1) - 1.0)[:, None]
                curr[mask_sub, :3] = (1 - sub) * curr[mask_sub, :3]
            # Calculate the size of the R compartment and clip appropriately.
            curr[mask_step, 3] = np.clip(
                1.0 - np.sum(curr[mask_step, :3], axis=-1), 0.0, 1.0)

    def pr_inf(self, prev, curr):
        """Calculate the likelihood of an individual becoming infected, for
        any number of state vectors.

        :param prev: The model states at the start of the observation period.
        :param curr: The model states at the end of the observation period.
        """
        # Count the number of susceptible / exposed individuals at both ends
        # of the simulation period.
        prev_amt = np.sum(prev[..., 0:2], axis=-1)
        curr_amt = np.sum(curr[..., 0:2], axis=-1)
        # Avoid returning very small negative values (e.g., -1e-10).
        return np.maximum(prev_amt - curr_amt, 0)

    def can_seed(self, vec):
        """Return True if a new strain can be seeded, otherwise False."""
        return vec[..., 0] == 1

    def is_seeded(self, hist):
        """Identify state vectors where infections have occurred.

        :param hist: A matrix of arbitrary dimensions, whose final dimension
            covers the model state space (i.e., has a length no smaller than
            that returned by :py:func:`state_size`).
        :type hist: numpy.ndarray

        :returns: A matrix of one fewer dimensions than ``hist`` that contains
            ``1`` for state vectors where infections have occurred and ``0``
            for state vectors where they have not.
        :rtype: numpy.ndarray
        """
        return np.ceil(1 - hist[..., 0])

    def is_valid(self, hist):
        """Ignore state vectors where no infections have occurred, as their
        properties (such as parameter distributions) are uninformative."""
        return self.is_seeded(hist)

    def stat_info(self):
        """Return the details of each statistic that can be calculated by this
        model. Each such statistic is represented as a ``(name, stat_fn)``
        pair, where ``name`` is a string that identifies the statistic and
        ``stat_fn`` is a function that calculates the statistic (see, e.g.,
        :py:func:`stat_Reff`).
        """
        return [("Reff", self.stat_Reff)]

    def stat_Reff(self, hist):
        """Calculate the effective reproduction number :math:`R_{eff}` for
        every particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return hist[..., 0] * hist[..., 4]

    def describe(self):
        return self.__info

    def initial_exposures(self, params, shape=None):
        if shape is None:
            return 1.0 / params['epifx']['popn_size']
        else:
            xs = np.empty(shape)
            xs.fill(1.0 / params['epifx']['popn_size'])
        return xs
