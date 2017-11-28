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

import TransportMaps.Distributions.Decomposable as DECDIST
import TransportMaps.Distributions.Examples.StochasticVolatility as SV

# Generate data
mu = -.5
phi = .95
sigma = 0.25
nsteps = 4
yB, ZA = SV.generate_data(nsteps, mu, sigma, phi)
yB[2] = None # Missing data y2

# Define distribution
is_mu_h = True
is_sigma_h = False
is_phi_h = True
pi_hyper = SV.PriorHyperParameters(is_mu_h, is_sigma_h, is_phi_h, 1)
mu_h = SV.IdentityFunction()
phi_h = SV.F_phi(3.,1.)
sigma_h = SV.ConstantFunction(0.25)
pi_ic = SV.PriorDynamicsInitialConditions(
    is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)
pi_trans = SV.PriorDynamicsTransition(
    is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)
pi = DECDIST.SequentialHiddenMarkovChainDistribution([], [], pi_hyper)
for n, yt in enumerate(yB):
    if yt is None:
        ll = None
    else:
        ll = SV.LogLikelihood(yt, is_mu_h, is_sigma_h, is_phi_h)
    if n == 0: pin = pi_ic
    else: pin = pi_trans
    pi.append(pin, ll)

# Store Distribution
pi.store("Distribution.dill")