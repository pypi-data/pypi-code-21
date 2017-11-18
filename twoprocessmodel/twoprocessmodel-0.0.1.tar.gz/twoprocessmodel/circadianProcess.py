#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements the class to model the circadian process of the two process model.

    .. module:: circadianProcess
    """

import numpy as np

__author__ = "Florian Wahl"
__copyright__ = "Copyright 2017, Florian Wahl"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Florian Wahl"
__email__ = "florian.wahl@gmail.com"
__status__ = "Development"


class CircadianProcess:
    """Implements the circadian process of the two process model."""

    def __init__(self, A=0.12, tau=24.0, t0=8.6):
        """Initialises the circadian process.

        All default values were taken according to
        Borb, Alexander A., and Peter Achermann.
        "Sleep homeostasis and models of sleep regulation."
        Journal of biological rhythms 14.6 (1999): 559-570.

        :param A: Amplitude of the circadian process. Defaults to 0.12.
        :param tau: Circadian period in hours. Defaults to 24.
        :param t0: Initial circadian time of the process.
        """

        self.A = A
        self.tau = tau
        self.t0 = t0
        self.omega = (2 * np.pi) / tau

    def sample(self, t):
        """Samples circadian process value at time t.
        :param t: Time at which the circadian process should be sampled in hours.
        :return: Circadian phase at time t.
        """

        return self.A * (0.97 * np.sin(self.omega * (t - self.t0)) +
                         0.22 * np.sin(2 * self.omega * (t - self.t0)) +
                         0.07 * np.sin(3 * self.omega * (t - self.t0)) +
                         0.03 * np.sin(4 * self.omega * (t - self.t0)) +
                         0.001 * np.sin(5 * self.omega * (t - self.t0)))
