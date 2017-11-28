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

import logging
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from tabulate import tabulate

import TransportMaps as TM
import TransportMaps.Distributions as DIST
import TransportMaps.Maps as MAPS

import xun   # The Python wrapper to the C++ sampler/samples

# logging.basicConfig(level=logging.INFO)

PLOTTING = True
ORDER = 3
TOL = 1e-5

# REGULARIZATION
# None: No regularization
# L2: L2 regularization
REG = None
# REG = {'type': 'L2',
#        'alpha': 1e-3}

# L2 error estimation
# 0: Monte Carlo quadrature with n point (the samples)
qtype = 0

# Gradient information
# 0: derivative free
# 1: gradient information
# 2: Hessian information
ders = 2

# MC samples
N_samp = 1000

# Define target distribution pi (the one we have samples for)
# We just need to define the rvs and quadrature functions, which will
# both return random samples.
# For further documentation check out the class TransportMap.Densities.Distribution
class WeirdDistribution(DIST.Distribution):
    def __init__(self):
        self.dim = 1
    def rvs(self, n):
        return xun.weird_samples(n)
    def quadrature(self, qtype, qparams):
        if qtype == 0:
            x = self.rvs(qparams)
            w = np.ones(qparams)/float(qparams)
        else: raise ValueError("Quadrature type not recognized")
        return (x,w)
    # For the interest of the example, we actually know the pdf and log_pdf
    # but they are in general not needed in the construction from samples
    def pdf(self, x, params=None):
        a = 2.
        b = 4.
        return a/b * (x/b)**(a-1.) * np.exp(-(x/b)**a)
    # def log_pdf(self, x, params=None): # We really don't need this here.
    #     a = 2.
    #     b = 4.
    #     return np.log(a) - np.log(b) + (a-1.) * (np.log(x)-np.log(b)) - (x/b)**a

pi = WeirdDistribution()

# Generate samples from the distribution and visualize
tar_samp = pi.rvs(N_samp)
xx = np.linspace(np.min(tar_samp), np.max(tar_samp), 100)
plt.figure()
plt.hist(tar_samp, bins=20, normed=True, histtype='step')
plt.plot(xx, pi.pdf(xx))
plt.show(False)

# Define the base distribution \rho (standard normal)
rho = DIST.StandardNormalDistribution(pi.dim)

# Define the support map L, i.e. the object that maps samples in the
# real line (reference support) to samples in the half-line (target support).
# For further documentation check out the file
# TransportMaps/Maps/FrozenTriangularTransportMaps.py
support_map = MAPS.FrozenExponentialDiagonalTransportMap(1)

# Plot the generated samples on the real line
supp_samp = support_map.inverse( tar_samp )
supp_xx = np.linspace(np.min(supp_samp), np.max(supp_samp), 100)
plt.figure()
plt.hist(supp_samp, bins=20, normed=True, histtype='step')
plt.show(False)

# Build the transport map (isotropic for each entry)
# See documentation of the constructor for more information.
active_vars = [ [0] ]
tm_approx = TM.Default_IsotropicIntegratedExponentialTriangularTransportMap(
    1, ORDER, 'total', active_vars=active_vars)
print("Number of coefficients: %d" % tm_approx.get_n_coeffs())

# Set up the arguments of D_KL(T_\sharp L^\sharp \pi || \rho)
L_pull_pi = DIST.PullBackTransportMapDistribution(support_map, pi)
T_push_L_pull_pi = DIST.PushForwardTransportMapDistribution(tm_approx, L_pull_pi)

# SOLVE
log_entry_solve = T_push_L_pull_pi.minimize_kl_divergence(
    rho, qtype=qtype, qparams=N_samp, regularization=REG,
    tol=TOL, ders=ders, batch_size=[None,None,None])

# Construct approximate distribution T^\sharp \pi
T_push_rho = DIST.PullBackTransportMapDistribution(tm_approx, rho)
# Construct approximate distribution L_\sharp T^\sharp \pi
L_pull_T_push_rho = DIST.PushForwardTransportMapDistribution(
    support_map, T_push_rho)

# Visualize approximated pdf
plt.figure()
plt.plot(xx, pi.pdf(xx), label='Exact')
plt.plot(xx, L_pull_T_push_rho.pdf(xx[:,np.newaxis]), label='Approximation')
plt.legend()
plt.show(False)

# Sample from the approximated distribution
app_samp = L_pull_T_push_rho.rvs(N_samp)
plt.figure()
plt.plot(xx, pi.pdf(xx), label='Exact')
plt.hist(app_samp, bins=20, normed=True, histtype='step')
plt.legend()
plt.show(False)


# # Push forward reference samples in two steps
# # (1) Map x from \pi to y from T^\sharp \pi
# # (2) Map y from T^\sharp \pi to z from L_\sharp T^\sharp \pi
# tmp = approx_distribution_1.map_samples_base_to_target( ref_samp )
# fapp_samp = approx_distribution.map_samples_base_to_target( tmp ) 

# # PLOT
# if PLOTTING:
#     # Map to T^\sharp \pi
#     t1_approx_tmp = approx_distribution_1.map_samples_base_to_target(X1d)
#     # Map to L_\sharp T^\sharp \pi
#     t1_approx = approx_distribution.map_samples_base_to_target(t1_approx_tmp)[:,0]
#     # Plot 1d transport map
#     ax_map_1d.plot(X1d[:,0], t1_approx, label='ord %d' % order)

#     # Plot the 1d distribution
#     if setup['dim'] == 1:
#         pdf1d_approx = approx_distribution.pdf(X1d_kde)
#     else:
#         t1_kde_approx = stats.gaussian_kde(fapp_samp[:,0][:,np.newaxis].T)
#         pdf1d_approx = t1_kde_approx(X1d_kde.T)
#     ax_kde_1d.plot(X1d_kde, pdf1d_approx, label='ord %d' % order)

#     if setup['dim'] >= 2:
#         # Map to T_\sharp \pi
#         t2_approx_tmp = approx_distribution_1.map_samples_base_to_target(X2d)
#         # Map to L_\sharp T_\sharp \pi
#         t2_approx = approx_distribution.map_samples_base_to_target(t2_approx_tmp)[:,1]
#         # Plot 2d transport map
#         ax_maps[i_ord].contour(xx2d, yy2d, t2_approx.reshape(xx2d.shape),
#                                linestyles='dashed', levels=levels_maps2d)

#         # Plot the 2d distribution
#         if setup['dim'] == 2:
#             pdf2d_approx = approx_distribution.pdf(X2d_kde)
#         else:
#             t2_kde_approx = stats.gaussian_kde(fapp_samp[:,:1].T)
#             pdf2d_approx = t2_kde_approx(X2d_kde.T)
#         axs_pdf2d[i_ord].contour(xx2d,yy2d,pdf2d_approx.reshape(xx2d.shape),
#                                  linestyles='dashed', levels=levels_pdf2d)
#         axs_pdf2d[i_ord].scatter(fapp_samp[:nscatter,0],fapp_samp[:nscatter,1],color='r')

# # Compute L2 error
# dist = np.sqrt( np.sum((T_samp - fapp_samp)**2., axis=1) )
# log_entry.append( np.sqrt( np.sum( dist**2. ) / float(N_samp) ) )

# log.append( log_entry )

# if PLOTTING:
#     fig_map_1d.gca().legend()
#     fig_kde_1d.gca().legend()
#     plt.show(False)

# # # Decorate map plotting
# # # ax_map.set_ylim([f(X[0]), f(X[-1])])
# # ax_map.scatter(x, np.zeros(x.shape))
# # ax_map.set_xlabel('x')
# # ax_map.set_ylabel('$T(x)$')
# # # ax_map.set_ylabel('$ (F^{-1} \circ F_{ref})x $')
# # # ax_map.set_ylim([np.min(exact_tm),np.max(exact_tm)])
# # ax_map.legend(loc='best')
# # ax_map.grid(True)

# # # fig_map.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-Approximation.pdf' % \
# # #                 (title, tit_type, tit_reg, tit_intest))
# # # fig_map.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-Approximation.eps' % \
# # #                 (title, tit_type, tit_reg, tit_intest))

# # # Decorate kde plotting
# # ax_kde.set_xlabel('x')
# # ax_kde.set_ylabel('PDF')
# # ax_kde.legend(loc='best')

# # # fig_kde.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-DistributionApproximation.pdf' % \
# # #                 (title, tit_type, tit_reg, tit_intest))
# # # fig_kde.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-DistributionApproximation.eps' % \
# # #                 (title, tit_type, tit_reg, tit_intest))

# # plt.show(False)

# print(" ")
# print(tabulate(log, headers=log_header))
# print(" ")

# print(tabulate(log, headers=log_header, tablefmt="latex", floatfmt=".2e"))