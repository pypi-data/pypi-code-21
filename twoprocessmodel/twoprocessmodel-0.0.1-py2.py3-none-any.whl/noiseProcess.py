#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements tests for the noise process.

    .. module:: noiseProcess
"""

import numpy as np

__author__ = "Florian Wahl"
__copyright__ = "Copyright 2017, Florian Wahl"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Florian Wahl"
__email__ = "florian.wahl@gmail.com"
__status__ = "Development"


class NoiseProcess:
    """
    Implements the noise process of the two process model.
    """

    def __init__(self, N=0.022):
        """
        Initialises the noise process.
        :param N: Amplitude of the noise process. Defaults to 0.022.
        """

        self.N = N
        self.noise_prev = self.N * np.random.normal()

    def sample(self):
        """
        Sample random noise from Gaussian distribution with 0 mean and std of 1.
        :return: Noise sample.
        """

        noise_now = 0.5 * (self.noise_prev + (self.N * np.random.normal()))
        self.noise_prev = noise_now
        return noise_now
