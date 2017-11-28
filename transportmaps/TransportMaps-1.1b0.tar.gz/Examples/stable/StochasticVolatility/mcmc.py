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
import dill
import h5py
import pyhmc
import matplotlib.pyplot as plt

nax = np.newaxis

argv = sys.argv[1:]
IN_FNAME = None
OUT_FNAME = None
NSAMPS = None
PLOTTING = False
NBURNIN = 0

try:
    opts, args = getopt.getopt(argv,"hn:",["output=", "dist=", "plotting","burnin="])
except getopt.GetoptError:
    full_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt == "-n":
        NSAMPS = int(arg)
    elif opt == "--dist":
        IN_FNAME = arg
    elif opt == "--output":
        OUT_FNAME = arg
    elif opt == "--plotting":
        PLOTTING = True
    elif opt == '--burnin':
        NBURNIN = int(arg)
if None in [IN_FNAME,OUT_FNAME]:
    full_usage()
    sys.exit(3)

with open(IN_FNAME,'rb') as istr:
    d = dill.load(istr)

f = h5py.File(OUT_FNAME,'a')
DSET_NAME = 'hmc'
if DSET_NAME not in f:
    f.create_dataset(DSET_NAME, (0,d.dim), maxshape=(None,d.dim), dtype='d')
loaded_samps = f[DSET_NAME]            

def logprob(x, d):
    return d.log_pdf(x[nax,:])[0], d.grad_x_log_pdf(x[nax,:])[0,:]

nold = loaded_samps.shape[0]
nnew = NSAMPS - nold
if nold == 0:
    x0 = np.random.randn(d.dim)
else:
    x0 = loaded_samps[-1,:]

if nnew > 0:
    samples = pyhmc.hmc(logprob, x0=x0, args=(d,), n_samples=nnew, display=True)
    loaded_samps.resize(NSAMPS, axis=0)
    loaded_samps[nold:,:] = samples

samples = loaded_samps[:,:]
    
f.close()

if PLOTTING:
    # MU
    mu = d.mu.evaluate(samples[NBURNIN:,0])
    plt.figure()
    plt.hist(mu, bins=50, edgecolor='k', facecolor='w', normed=True)
    plt.xlabel(r"$\mu$")
    # SIGMA
    sigma = d.sigma.evaluate(samples[NBURNIN:,1])
    tau = 1/sigma**2
    plt.figure()
    plt.hist(tau, bins=50, edgecolor='k', facecolor='w', normed=True)
    plt.xlabel(r"$\tau$")
    # PHI
    phi = d.phi.evaluate(samples[NBURNIN:,2])
    plt.figure()
    plt.hist(phi, bins=50, edgecolor='k', facecolor='w', normed=True)
    plt.xlabel(r"$\phi$")
    plt.show(False)

    # Chains
    plt.figure()
    plt.plot(mu)
    plt.xlabel(r"$\mu$")
    plt.figure()
    plt.plot(sigma)
    plt.xlabel(r"$\sigma$")
    plt.figure()
    plt.plot(phi)
    plt.xlabel(r"$\phi$")

    # ESS
    import TransportMaps.Samplers as SMPL
    ess = SMPL.ess(samples[NBURNIN:,:3], plotting=True, plot_lag=100000)
    plt.show(False)

    print("Effective sample size: %d" % ess)

# from IPython import embed
# embed()

