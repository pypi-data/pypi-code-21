####################################################################################################
# pimms/test/normal.py
#
# This source-code file is part of the pimms library.
#
# The pimms library is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program.  If
# not, see <http://www.gnu.org/licenses/>.

import pimms
import numpy as np
import scipy.special as sps

@pimms.immutable
class NormalDistribution(object):
    '''
    The NormalDistribution class contains data about a normal distribution.
    '''

    def __init__(self, mean=0.0, standard_deviation=1.0):
        self.mean = mean
        self.standard_deviation = standard_deviation
    
    # The parameters:
    @pimms.param
    def mean(val):
        return float(val)
    @pimms.option(1.0)
    def standard_deviation(val):
        return float(val)

    # The checks:
    @pimms.require
    def standard_deviation_is_positive(standard_deviation):
        if standard_deviation <= 0: raise ValueError('standard_deviation must be positive')
        return True
    
    # The values:
    @pimms.value
    def variance(standard_deviation):
        return standard_deviation * standard_deviation
    @pimms.value
    def outer_scalar(standard_deviation):
        return 1.0/(standard_deviation * np.sqrt(2*np.pi))
    @pimms.value
    def inner_scalar(variance):
        return -0.5 / variance

    # A method:
    def pdf(self, x):
        return self.outer_scalar * np.exp(self.inner_scalar * (x - self.mean)**2)
    def cdf(self, x):
        return 0.5 * (1 + sps.erf((x - self.mean) / (np.sqrt(2.0) * self.standard_deviation)))

        
