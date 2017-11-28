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
import scipy.linalg as scila
import scipy.integrate as sciint

from TransportMaps.Distributions.FrozenDistributions import GaussianDistribution
from TransportMaps.Distributions.Decomposable.LinearGaussianSequentialInferenceDistributions import \
    LinearGaussianAR1TransitionDistribution
from TransportMaps.Likelihoods.LikelihoodBase import \
    AdditiveLinearGaussianLogLikelihood

__all__ = ['Prior', 'Transition', 'LogLikelihood', 'generate_data']

re = 6367253.
Omega = 0.2625161
dt = 0.5

class Prior(GaussianDistribution):
    def __init__(self):
        sig2_eps = (0.02 * np.pi / 180)**2
        Q0 = np.zeros((6,6))
        Q0[0,0] = Q0[1,1] = (1000./re)**2
        Q0[2,2] = (0.1 * np.pi/180)**2
        Q0[3,3] = Q0[4,4] = Q0[5,5] = sig2_eps
        # Init
        super(Prior,self).__init__(np.zeros(6), Q0)

class Transition(LinearGaussianAR1TransitionDistribution):
    def __init__(self):
        theta = np.pi / 4
        Ox = Omega * np.cos(theta)
        Oz = Omega * np.sin(theta)
        F = np.zeros((6,6))
        F[0,1] = Oz; F[1,0] = -Oz; F[1,2] = Ox; F[2,1] = -Ox;
        F[0,3] = F[1,4] = F[2,5] = 1.
        G = np.zeros((6,6))
        G[3,3] = G[4,4] = G[5,5] = 1.
        sig2_eps = (0.02 * np.pi / 180)**2
        W = np.eye(6) * sig2_eps
        # Integrate dynamics to obtain finite-difference equations
        Phi = scila.expm(F*dt)
        GWG = np.dot(G, np.dot(W,G))
        def f(q,t,F,GWG):
            Q = q.reshape((6,6))
            rhs = np.dot(F,Q) + np.dot(Q,F.T) + GWG
            return rhs.flatten()
        q0 = np.zeros(6*6)
        T = [0, dt]
        sol = sciint.odeint(f, q0, T, args=(F, GWG))
        Q = sol[1].reshape((6,6))
        # Init
        super(Transition,self).__init__(np.zeros(6), Phi, np.zeros(6), Q)

class LogLikelihood(AdditiveLinearGaussianLogLikelihood):
    def __init__(self, y):
        sig2_xy = (1000./re)**2
        sig2_z = (1./60. * np.pi/180)**2
        H = np.zeros((3,6))
        H[0,0] = H[1,1] = H[2,0] = H[2,2] = 1
        R = np.zeros((3,3))
        R[0,0] = R[1,1] = sig2_xy
        R[2,2] = sig2_z
        super(LogLikelihood,self).__init__(y, np.zeros(3), H, np.zeros(3), R)

def generate_data(nsteps):
    prior = Prior()
    trans = Transition()
    ll = LogLikelihood(np.zeros(3)) # Just use the constructor to get handle on params
    # Generate dynamics
    T = np.zeros(nsteps+1)
    Z = np.zeros((nsteps+1, 6))
    Z[0,:] = prior.rvs(1)[0,:]
    for i in range(nsteps):
        T[i+1] = T[i] + dt
        Z[i+1,:] = trans.T.evaluate(Z[[i],:])[0,:] + trans.pi.rvs(1)[0,:]
    # Generate observations
    Y = []
    for i in range(nsteps+1):
        Y.append( ll.T.evaluate(Z[[i],:])[0,:] + ll.pi.rvs(1)[0,:] )
    return (T,Z,Y)