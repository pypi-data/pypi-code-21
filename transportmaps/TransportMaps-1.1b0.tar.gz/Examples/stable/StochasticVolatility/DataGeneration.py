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

import sys, getopt
import numpy as np

import TransportMaps.Distributions.Examples.StochasticVolatility as SV

def usage():
    print('DataGeneration.py --output=<filename> [ ' + \
          '-n <max> --phi=.95 --sigma=.25 --mu=-0.5 --input-data=<fname>]')
    print('If no value for phi, sigma or mu are provided, they are considered ' + \
          'hyperparameters')

def full_usage():
    usage()

argv = sys.argv[1:]
nsteps = None
phi = None
sigma = None
mu = None
durbin_data = False
OUT_FNAME = None
IN_FNAME = None
try:
    opts, args = getopt.getopt(argv,"hn:",["output=", "phi=", "sigma=", "mu=",
                                           "input-data="])
except getopt.GetoptError:
    full_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt == '-n':
        nsteps = int(arg)
    elif opt == "--phi":
        phi = float(arg)
    elif opt == "--sigma":
        sigma = float(arg)
    elif opt == "--mu":
        mu = float(arg)
    elif opt == "--input-data":
        IN_FNAME = arg
    elif opt == "--output":
        OUT_FNAME = arg
if None in [OUT_FNAME]:
    full_usage()
    sys.exit(3)

#########################################
dataObs = None
if IN_FNAME is not None:
    dataObs = np.loadtxt(IN_FNAME, skiprows=2, usecols=2, delimiter=',')
    if nsteps is None:
        nsteps = len(dataObs)
    else:
        dataObs = dataObs[:nsteps]
    Xt = [None] * nsteps
else:
    dataObs, Xt = SV.generate_data(nsteps, -.5, .25, .95)
    
dens = SV.StocVolHyperDistribution(
    mu is None, sigma is None, phi is None,
    mu=mu, sigma=sigma, phi=phi,
    mu_sigma=1.,
    sigma_k=1., sigma_theta=0.1,
    phi_mean=3., phi_std=1.)

for n in range(nsteps):
    dens.assimilate(y=dataObs[n], Xt=Xt[n])

dens.store(OUT_FNAME)
