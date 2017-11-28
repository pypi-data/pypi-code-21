#!/usr/bin/env python

#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2017 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

__all__ = ['AVAIL_MONOTONE', 'AVAIL_SPAN', 'AVAIL_BTYPE',
           'AVAIL_QTYPE', 'AVAIL_DERS',
           'AVAIL_ADAPTIVITY', 'AVAIL_REGRESSION_ADAPTIVITY',
           'AVAIL_MCMC_ALGORITHMS', 'AVAIL_LOGGING',
           'AVAIL_DISTRIBUTIONS',
           'print_avail_options']

from TransportMaps.External import *

# MONOTONE APPROXIMATION
# 'intexp': Integrated Exponential
# 'linspan': Constrained Polynomial
AVAIL_MONOTONE = {'linspan': 'monotone linear span',
                  'intexp': 'integrated exponential',
                  'intsq': 'integrated square'}

# SPAN APPROXIMATION
# 'full': Full order approximation
# 'total': Total order approximation
AVAIL_SPAN = {'full': 'full span',
              'total': 'total order span'}

# BASIS TYPES
# 'poly': Hermite polynomials
# 'rbf': Radial basis functions
AVAIL_BTYPE = {'poly': 'polynomial basis',
               'rbf': 'radial basis functions (requires SPAN=full)'}

# QUADRATURES
# 0: Monte Carlo
# 3: Gauss quadrature
AVAIL_QTYPE = {0: 'Monte Carlo',
               3: 'Gauss quadrature'}

# DERS
# 1: BFGS
# 2: Newton-CG
AVAIL_DERS = {0: 'BFGS (gradient free)',
              1: 'BFGS (gradient needed)',
              2: 'Newton-CG (Hessian needed)'}

# ADAPTIVITY
# 'none': no adaptivity performed
# 'sequential': a sequence of maps of increasing order are used
AVAIL_ADAPTIVITY = {
    'none': 'no adaptivity',
    'sequential': 'a prefix sequence of maps is used',
    'tol-sequential': 'a sequence of maps is used until tolerance is met',
}

# REGRESSION ADAPTIVITY
# 'none': no adaptivity performed
# 'tol-sequential': a sequence of maps of increasing order are used
AVAIL_REGRESSION_ADAPTIVITY = {
    'none': 'no adaptivity',
    'tol-sequential': 'meet a tolerance using a prefix sequence of maps'}

# MCMC ALGORITHMS
AVAIL_MCMC_ALGORITHMS = {
    'mhind': 'Metropoli-Hastings with independent proposals',
    'hmc': "Hamiltonian Monte Carlo",
    }

# LOGGING
AVAIL_LOGGING = {10: 'debug',
                 20: 'info',
                 30: 'warning',
                 40: 'error',
                 50: 'critical'}

AVAIL_DISTRIBUTIONS = {'exact-target': 'exact target density',
                       'approx-target': 'approximate target density',
                       'exact-base': 'exact base density',
                       'approx-base': 'approximate base density'}

def print_avail_options(avail, prefix='', header=True):
    out_str = ''
    if header:
        out_str += prefix + 'Available options:\n'
    for key, val in sorted(avail.items()):
        out_str += prefix + '  ' + str(key) + ': ' + val + '\n'
    return out_str
