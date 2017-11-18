#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements the class to model the homeostatic process of the two process model.

    .. module:: homeostaticProcess
    """

import numpy as np

__author__ = "Florian Wahl"
__copyright__ = "Copyright 2017, Florian Wahl"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Florian Wahl"
__email__ = "florian.wahl@gmail.com"
__status__ = "Development"


class HomeostaticProcess:
    """Implements the homeostatic process to model sleep pressure.

    Maximum sleep pressure is 1, minimum is 0.
    """

    def __init__(self, tau_d=4.2, tau_r=18.2, d_t=0.5, S_init=0.5):
        """Initialises the homeostatic process.

        All default values were taken according to
        Borbely, Alexander A., and Peter Achermann.
        "Sleep homeostasis and models of sleep regulation."
        Journal of biological rhythms 14.6 (1999): 559-570.

        :param tau_d: Decay factor of the homeostat during wake time. Defaults to 4.2.
        :param tau_r: Decay factor of the homeostat during sleep. Defaults to 18.2.
        :param d_t: 1/sampling rate[h]. Defaults to 0.5.
        :param S_init: Initial sleep pressure at time t=0. Defaults to 0.5.
        """

        self.d = np.exp(-d_t / tau_d)
        self.r = np.exp(-d_t / tau_r)
        self.S_prev = S_init

    def sample(self, sleeping):
        """Draw the next sample from the homeostatic process.

        :param sleeping: Whether the subject is currently sleeping (1) or not (0).
        :return: S Value of homeostatic process.
        """

        if sleeping:
            S = self.d * self.S_prev
        else:
            S = 1 - self.r * (1 - self.S_prev)

        self.S_prev = S
        return S
