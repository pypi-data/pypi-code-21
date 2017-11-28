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
# Authors: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import numpy as np

from TransportMaps.Distributions.FrozenDistributions import \
    GaussianDistribution, StandardNormalDistribution
from TransportMaps.Distributions.Decomposable.LinearGaussianSequentialInferenceDistributions import \
    LinearGaussianAR1TransitionDistribution
from TransportMaps.Likelihoods.LikelihoodBase import \
    AdditiveLinearGaussianLogLikelihood

__all__ = ['Prior', 'Transition', 'LogLikelihood', 'generate_data']

dt = 0.02

class Prior(StandardNormalDistribution):
    def __init__(self):
        super(Prior,self).__init__(1)

class Transition(LinearGaussianAR1TransitionDistribution):
    def __init__(self):
        Phi = np.array([[np.exp(-0.02)]])
        Q = np.array([[ 1.-np.exp(-2*0.02) ]])
        # Init
        super(Transition,self).__init__(np.zeros(1), Phi, np.zeros(1), Q)

class LogLikelihood(AdditiveLinearGaussianLogLikelihood):
    def __init__(self, y):
        H = np.eye(1)
        R = np.eye(1)
        super(LogLikelihood,self).__init__(y, np.zeros(1), H, np.zeros(1), R)

def generate_data(nsteps):
    prior = Prior()
    trans = Transition()
    ll = LogLikelihood(np.zeros(1)) # Just use the constructor to get handle on params
    # Generate dynamics
    T = np.zeros(nsteps+1)
    Z = np.zeros((1, nsteps+1))
    Z[:,0] = prior.rvs(1)[0,:]
    for i in range(nsteps):
        T[i+1] = T[i] + dt
        Z[:,i+1] = trans.T.evaluate(Z[:,i]) + trans.pi.rvs(1)[0,:]
    # Generate observations
    Y = []
    for i in range(nsteps+1):
        Y.append( ll.T.evaluate(Z[:,i]) + ll.pi.rvs(1)[0,:] )
    return (T,Z,Y)