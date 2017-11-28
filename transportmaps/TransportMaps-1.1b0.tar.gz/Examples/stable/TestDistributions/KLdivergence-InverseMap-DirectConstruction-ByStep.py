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
import sys, getopt
import warnings
import time
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
import scipy.stats as stats
from tabulate import tabulate

import TransportMaps as TM
import TransportMaps.Distributions as DIST
import TransportMaps.tests.TestFunctions as TF

logging.basicConfig(level=logging.DEBUG)

# TESTS
#  0: 1D - N(mu,sigma)
#  NOT WORKING 1: 1D - Mixture X~N(-1,1), Y~N(1,0.5), p=0.3
#  2: 1D - T(x) = a + b*x + c * arctan(d + e*x)
#  3: 1D - Y = T(x) = exp(a*x) -- Corresponding to Y~logN(0,a^2)
#  4: 1D - Y~Logistic(\mu,s)
#  5: 1D - Y~Gamma(loc,scale)
#  6: 1D - Y~Beta(a,b)
#  7: 1D - Gumbel distribution
#  NOTWORKING 8: Bayesian
#  9: 2D - N(mu,sigma)
# 10: 2D - Banana
AVAIL_TESTN = {0: '1D Std. Normal',
               2: '1D ArcTan',
               3: '1D LogNormal',
               4: '1D Logistic',
               5: '1D Gamma',
               6: '1D Beta',
               7: '1D Gumbel',
               9: '2D Std. Normal',
               10: '2D Banana'}

# SPAN APPROXIMATION
# 'full': Full order approximation
# 'total': Total order approximation
AVAIL_SPAN = ['full', 'total']

# QUADRATURES
# 0: Monte Carlo
# 3: Gauss quadrature
AVAIL_QUADRATURE = {0: 'Monte Carlo',
                    3: 'Gauss quadrature'}

def usage():
    print('KLdivergence-InverseMap-DirectConstruction.py -t <test_number> -s <span_type> -q <quad_type> -n <quad_n_points> [--tol=<tolerance> --with-reg=<alpha> --ord-list=<comma_sep_order_list> --no-plotting]')

def print_avail_span():
    print('Available <span_type>: %s' % AVAIL_SPAN)

def print_avail_qtype():
    print('Available <quad_type>:')
    for qtypen, qtypename in AVAIL_QUADRATURE.items():
        print('  %d: %s' % (qtypen, qtypename))

def print_avail_testn():
    print('Available <test_number>:')
    for testn, testname in AVAIL_TESTN.items():
        print('  %d: %s' % (testn, testname))

def print_example():
    print('KLdivergence-InverseMap-DirectConstruction.py -t 2 -s total -q 3 -n 30 --tol=1e-4 --with-reg=1e-3 --ord-list=1,3,5,7,9')
        
def full_usage():
    usage()
    print_avail_testn()
    print_avail_span()
    print_avail_qtype()
    print_example()

argv = sys.argv[1:]

PLOTTING = True
TESTN = None
SPAN = None
QTYPE = None
QNUM = None
REG = None
# Orders
ORDERS = [1,3,5]
# Tolerance
TOL = 1e-5
try:
    opts, args = getopt.getopt(argv,"ht:s:q:n:",["testn=", "span_type=",
                                                 "qtype=", "qnum=",
                                                 "tol=", "with-reg=", "ord-list=",
                                                 "no-plotting"])
except getopt.GetoptError:
    full_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt in ("-t", "--testn"):
        TESTN = int(arg)
        if TESTN not in AVAIL_TESTN:
            usage()
            print_avail_testn()
            sys.exit(1)
    elif opt in ("-s", "--span_type"):
        SPAN = arg
        if SPAN not in AVAIL_SPAN:
            usage()
            print_avail_span()
            sys.exit(1)
    elif opt in ("-q", "--qtype"):
        QTYPE = int(arg)
        if QTYPE not in AVAIL_QUADRATURE:
            usage()
            print_avail_qtype()
            sys.exit(1)
    elif opt in ("-n", "--qnum"):
        QNUM = int(arg)
    elif opt in ("--tol"):
        TOL = float(arg)
    elif opt in ("--with-reg"):
        REG = {'type': 'L2',
               'alpha': float(arg)}
    elif opt in ("--ord-list"):
        ORDERS = [int(s) for s in arg.split(',')]
    elif opt in ("--no-plotting"):
        PLOTTING = False
if None in [TESTN, SPAN, QTYPE, QNUM]:
    full_usage()
    sys.exit(3)

# PLOTTING
fsize = (6,5)
discr = 101

# Get test title and parameters
title, setup, test = TF.get(TESTN)

# # REGULARIZATION
# # None: No regularization
# # L2: L2 regularization
# REG = None
# # REG = {'type': 'None',
# #        'alpha': 1e-3}
if REG is None:
    tit_reg = 'None'
elif REG['type'] == 'L2':
    tit_reg = REG['type'] + '-' + str(REG['alpha'])

# L2 error estimation
# 3: Gauss quadrature of order n
# 0: Monte Carlo quadrature with n point
qtype = QTYPE
if qtype == 0:
    qparams = QNUM
    tit_intest = "MC" + '-' + str(qparams)
elif qtype == 3:
    qparams = [QNUM] * setup['dim']
    tit_intest = "Quad" + '-' + str(qparams[0])

# Gradient information
# 0: derivative free
# 1: gradient information
# 2: Hessian information
ders = 1

# MC samples
N_samp = 10000

# Generate samples of reference and target
ref_samp = test['base_distribution'].rvs(N_samp)
T_samp = test['support_map']( test['target_map'](ref_samp) )

# PLOTTING PRE-COMPUTATION
# Start plotting of the 1d map
if PLOTTING:
    pspan = setup['plotspan']
    rspan = setup['refplotspan']

    # Plot the 1d map
    X1d = np.vstack( (np.linspace(rspan[0,0],rspan[0,1],discr),
                      np.zeros((setup['dim']-1,discr))) ).T
    t1 = test['support_map']( test['target_map'](X1d) )[:,0]
    fig_map_1d = plt.figure()
    ax_map_1d = fig_map_1d.add_subplot(1,1,1)
    ax_map_1d.plot(X1d[:,0], t1, 'k--', linewidth=2, label='exact')

    # Plot the 1d distribution
    fig_kde_1d = plt.figure()
    ax_kde_1d = fig_kde_1d.add_subplot(1,1,1)
    # Exact distribution 1d
    X1d_kde = np.linspace(pspan[0,0],pspan[0,1],discr).reshape((discr,1))
    if setup['dim'] == 1:
        # Plot analytic
        pdf1d = test['target_distribution'].pdf(X1d_kde)
        ax_kde_1d.plot(X1d_kde, pdf1d, 'k--', linewidth=2, label='$\pi^1_{tar}$')
    else:
        # Gaussian KDE approximation
        T1_kde = stats.gaussian_kde(T_samp[:,0][:,np.newaxis].T)
        pdf1d = T1_kde(X1d_kde.T)
        ax_kde_1d.plot(X1d_kde, pdf1d, 'k--', linewidth=2, label='kde-$\pi^1_{tar}$')

    if setup['dim'] >= 2:
        # Plot the 2d transport map
        x = np.linspace(rspan[0,0],rspan[0,1],discr)
        y = np.linspace(rspan[1,0],rspan[1,1],discr)
        xx,yy = np.meshgrid(x,y)
        X2d = np.vstack( (xx.flatten(),yy.flatten(),np.zeros((setup['dim']-2,discr**2))) ).T
        t2 = test['support_map']( test['target_map'](X2d) )[:,1]
        fig_maps2d = []
        ax_maps = []
        levels_maps2d = np.linspace(np.min(t2),np.max(t2),20)
        for i,order in enumerate(ORDERS):
            fig_maps2d.append( plt.figure() )
            ax_map = fig_maps2d[-1].add_subplot(1,1,1)
            ax_map.contour(xx,yy,t2.reshape(xx.shape),
                           levels=levels_maps2d)
            ax_maps.append( ax_map )
            plt.title("Order %d" % order)

        # Plot PDF 2d
        fig_pdf2d = []
        axs_pdf2d = []
        x = np.linspace(pspan[0,0],pspan[0,1],discr)
        y = np.linspace(pspan[1,0],pspan[1,1],discr)
        xx2d,yy2d = np.meshgrid(x,y)
        X2d_kde = np.vstack( (xx2d.flatten(),yy2d.flatten(),
                              np.zeros((setup['dim']-2,discr**2))) ).T
        if setup['dim'] == 2:
            pdf2d = test['target_distribution'].pdf(X2d_kde)
        else:
            T2_kde = stats.gaussian_kde(T_samp[:,:1].T)
            pdf2d = T2_kde(X2d_kde.T)
        levels_pdf2d = np.linspace(np.min(pdf2d),np.max(pdf2d),20)
        for i,order in enumerate(ORDERS):
            fig_pdf2d.append( plt.figure() )
            ax_pdf2d = fig_pdf2d[-1].add_subplot(1,1,1)
            ax_pdf2d.contour(xx2d,yy2d,pdf2d.reshape(xx2d.shape),
                             levels=levels_pdf2d)
            axs_pdf2d.append( ax_pdf2d )
            plt.title("Order %d" % order)

# Define header for the output log
tit_type = 'monot'
if ders in [0,1]:
    log_header = ['Order','#F.ev.','#J.ev','$L^2$-err']
else:
    log_header = ['Order','#F.ev.','#J.ev','#H.ev','$L^2$-err']

log = [ ]

for i_ord,order in enumerate(ORDERS):
    tmp_coeffs = None
    for nest_ord in range(1,order+1):
        print("\nOrder: %d" % nest_ord)
        # Build the transport map (isotropic for each entry)
        tm_approx = TM.Default_IsotropicIntegratedExponentialTriangularTransportMap(
            setup['dim'], nest_ord, SPAN)
        # Construct distribution
        # Distribution T^\sharp \pi
        tm_distribution = DIST.PullBackTransportMapDistribution(tm_approx, test['base_distribution'])
        # Target distribution to be approximated L^\sharp \pi_{\rm tar}
        target_distribution = DIST.PullBackTransportMapDistribution(test['support_map'],
                                                          test['target_distribution'])
        if tmp_coeffs is None:
            x0 = None
        else:
            x0 = tm_approx.get_coeffs()
            x0[:nest_ord] = tmp_coeffs
        # SOLVE min D_KL (T^\sharp \pi || L^\sharp \pi_{\rm tar})
        log_entry_solve = tm_distribution.minimize_kl_divergence(target_distribution, qtype=qtype,
                                                            qparams=qparams,
                                                            x0=x0,
                                                            regularization=REG,
                                                            tol=TOL, ders=ders,
                                                            batch_size=[None,None,20])
        tmp_coeffs = tm_approx.get_coeffs()

    log_entry = [order] + log_entry_solve

    # Construct approximate distribution L_\sharp T^\sharp \pi
    approx_distribution = DIST.PushForwardTransportMapDistribution(test['support_map'], tm_distribution)

    # Push forward reference samples in two steps
    # (1) Map x from \pi to y from T^\sharp \pi
    # (2) Map y from T^\sharp \pi to z from L_\sharp T^\sharp \pi
    tmp = tm_distribution.map_samples_base_to_target( ref_samp )
    fapp_samp = approx_distribution.map_samples_base_to_target( tmp ) 

    # PLOT
    if PLOTTING:
        # Map to T^\sharp \pi
        t1_approx_tmp = tm_distribution.map_samples_base_to_target(X1d)
        # Map to L_\sharp T^\sharp \pi
        t1_approx = approx_distribution.map_samples_base_to_target(t1_approx_tmp)[:,0]
        # Plot 1d transport map
        ax_map_1d.plot(X1d[:,0], t1_approx, label='ord %d' % order)

        # Plot the 1d distribution
        if setup['dim'] == 1:
            pdf1d_approx = approx_distribution.pdf(X1d_kde)
        else:
            t1_kde_approx = stats.gaussian_kde(fapp_samp[:,0][:,np.newaxis].T)
            pdf1d_approx = t1_kde_approx(X1d_kde.T)
        ax_kde_1d.plot(X1d_kde, pdf1d_approx, label='ord %d' % order)


        if setup['dim'] >= 2:
            # Map to T^\sharp \pi
            t2_approx_tmp = tm_distribution.map_samples_base_to_target(X2d)
            # Map to L_\sharp T^\sharp \pi
            t2_approx = approx_distribution.map_samples_base_to_target(t2_approx_tmp)[:,1]
            # Plot 2d transport map
            ax_maps[i_ord].contour(xx2d, yy2d, t2_approx.reshape(xx2d.shape),
                                   linestyles='dashed', levels=levels_maps2d)

            # Plot the 2d distribution
            if setup['dim'] == 2:
                pdf2d_approx = approx_distribution.pdf(X2d_kde)
            else:
                t2_kde_approx = stats.gaussian_kde(fapp_samp[:,:1].T)
                pdf2d_approx = t2_kde_approx(X2d_kde.T)
            axs_pdf2d[i_ord].contour(xx2d,yy2d,pdf2d_approx.reshape(xx2d.shape),
                                     linestyles='dashed', levels=levels_pdf2d)

    # Compute L2 error
    dist = np.sqrt( np.sum((T_samp - fapp_samp)**2., axis=1) )
    log_entry.append( np.sqrt( np.sum( dist**2. ) / float(N_samp) ) )

    log.append( log_entry )

if PLOTTING:
    fig_map_1d.gca().legend()
    fig_kde_1d.gca().legend()
    plt.show(False)

# # Decorate map plotting
# # ax_map.set_ylim([f(X[0]), f(X[-1])])
# ax_map.scatter(x, np.zeros(x.shape))
# ax_map.set_xlabel('x')
# ax_map.set_ylabel('$T(x)$')
# # ax_map.set_ylabel('$ (F^{-1} \circ F_{ref})x $')
# # ax_map.set_ylim([np.min(exact_tm),np.max(exact_tm)])
# ax_map.legend(loc='best')
# ax_map.grid(True)

# # fig_map.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-Approximation.pdf' % \
# #                 (title, tit_type, tit_reg, tit_intest))
# # fig_map.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-Approximation.eps' % \
# #                 (title, tit_type, tit_reg, tit_intest))

# # Decorate kde plotting
# ax_kde.set_xlabel('x')
# ax_kde.set_ylabel('PDF')
# ax_kde.legend(loc='best')

# # fig_kde.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-DistributionApproximation.pdf' % \
# #                 (title, tit_type, tit_reg, tit_intest))
# # fig_kde.savefig('Figs/KLdiv-%s-%s-%s-%s-MonotoneMap1d-DistributionApproximation.eps' % \
# #                 (title, tit_type, tit_reg, tit_intest))

# plt.show(False)

print(" ")
print(tabulate(log, headers=log_header))
print(" ")

print(tabulate(log, headers=log_header, tablefmt="latex", floatfmt=".2e"))