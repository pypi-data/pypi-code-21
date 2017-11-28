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

import sys
import os
import os.path
import dill
import h5py
import numpy as np

from . import AvailableOptions as AO
from .PostprocessBase import Postprocess

import TransportMaps.Diagnostics as DIAG
import TransportMaps.Samplers as SAMP
import TransportMaps.Distributions as DIST

__all__ = ['SequentialPostprocess']

class SequentialPostprocess(Postprocess):
    def usage(self):
        usage_str = """
Usage: tmap-sequential-postprocess [-h -v -I]
  --input=INPUT --output=OUTPUT
  [--trim=NSTEPS
   --store-fig-dir=DIR --store-fig-fmats=FMATS
   --extra-tit=TITLE --no-plotting
   --trim=NSTEPS
   --sequential-var-diag
   --sequential-reg-diag
   --filtering-conditionals
     --filt-alc-n-points-x-ax=N --filt-alc-n-tri-plots=N
     --filt-alc-anchor=LIST --filt-alc-range=LIST
   --filtering-marginals
     --filt-alm-n-points=N --filt-alm-n-tri-plots=N
   --filtering-quadrature
     --filt-quad-qtype=QTYPE
     --filt-quad-qnum=QNUM
   --log=LOG --batch=BATCH --nprocs=NPROCS]
"""
        print(usage_str)

    def description(self):
        docs_distributions_str = \
            AO.print_avail_options(AO.AVAIL_DISTRIBUTIONS,
                                      '                        ', False)
        docs_log_str = \
            '  --log=LOG               log level (default=30). Uses package logging.\n' + \
            AO.print_avail_options(AO.AVAIL_LOGGING,'                          ')
        docs_str = """DESCRIPTION
Given a file (--input) storing the transport map pushing forward a base distribution
to a sequential Hidden Markov target distribution, 
provides a number of postrprocessing routines.
All files involved are stored and loaded using the python package dill and
an extra file OUTPUT.hdf5 is created to store big datasets in the hdf5 format.
In the following default values are shown in brackets.

All the options available for tmaps-postprocess are also available here.

OPTIONS - input/output:
  --input=INPUT         path to the file containing the target distribution,
                          the base distribution and the transport map pushing forward
                          the base to the target.
  --output=OUTPUT       path to the file storing all postprocess data.
                          The additional file OUTPUT.hdf5 will be used to store
                          the more memory consuming data.
  --trim=NSTEPS         trim the solution to NSTEPS and perform analysis
  --store-fig-dir=DIR   path to the directory where to store the figures.
  --store-fig-fmats=FMATS  figure formats - see matplotlib for supported formats (svg)
  --extra-tit=TITLE     additional title for the figures' file names.
  --no-plotting         do not plot figures, but only store their data.
                          (requires --output or --store-fig-dir)
  --trim=NSTEPS         trims the results to NSTEPS and run diagnostics on this distribution
OPTIONS - Diagnostics:
  --sequential-var-diag plot value of variance diagnostic for the sequence of maps
  --sequential-reg-diag plot value of all regression residuals
  --filtering-conditionals  plot aligned slices of the filtering distribution:
                        Optional arguments:
    --filt-alc-n-points-x-ax=N  number of discretization points per axis (30)
    --filt-alc-n-tri-plots=N    number of subplots (0)
    --filt-alc-anchor=LIST      list of floats "f1,f2,f3..." for the anchor point (0)
    --filt-alc-range=LIST       list of two floats "f1,f2" for the range (-5,5)
OPTIONS - Sampling:
  --filtering-marginals  plot aligned marginals of the filtering distribution:
                        Optional arguments:
    --filt-alm-n-points=N     number of samples to be used for the kernel density estimation
    --filt-alm-n-tri-plots=N  number of subplots (0)
  --filtering-quadrature  generate quadrature of the filtering distribution:
                        Optional arguments:
    --filt-quad-qtype=QTYPE  generate quadrature of type QTYPE (0)
    --filt-quad-qnum=QNUM    level of the quadrature (int or list)
OPTIONS - Computation:
""" + docs_log_str + """  --nprocs=NPROCS         number of processors to be used (default=1)
  --batch=BATCH           list of batch sizes for function evaluation, gradient
                          evaluation and Hessian evaluation
OPTIONS - other:
  -v                      verbose output (not affecting --log)
  -I                      enter interactive mode after finishing
  -h                      print this help
"""
        print(docs_str)

    @property
    def long_options(self):
        return super(SequentialPostprocess, self).long_options + \
            [
                "trim=",
                # Sequential diagnostics
                "sequential-var-diag", "sequential-reg-diag",
                # Aligned conditionals
                "filtering-conditionals",
                "filt-alc-n-points-x-ax=", "filt-alc-n-tri-plots=", 
                "filt-alc-anchor=", "filt-alc-range=",
                # Aligned marginals
                "filtering-marginals",
                "filt-alm-n-points=", "filt-alm-n-tri-plots=",
                # Quadrature
                "filtering-quadrature", 
                "filt-quad-qtype=", "filt-quad-qnum=",
            ]

    def load_opts(self, opts):
        super(SequentialPostprocess, self).load_opts(opts)
        for opt, arg in opts:
            if opt == "--trim":
                self.TRIM = int(arg)
            # Sequential diagnostics
            elif opt == "--sequential-var-diag":
                self.SEQUENTIAL_VAR_DIAG = True
            elif opt == "--sequential-reg-diag":
                self.SEQUENTIAL_REG_DIAG = True

            # Aligned conditionals
            elif opt in ("--filtering-conditionals"):
                self.FLT_ALIGNED_CONDITIONALS = True
            # Options
            elif opt in ("--filt-alc-n-points-x-ax"):
                self.FLT_ALC_N_POINTS_X_AX = int(arg)
            elif opt in ("--filt-alc-n-tri-plots"):
                self.FLT_ALC_N_TRI_PLOTS = list(range(int(arg)))
            elif opt in ("--filt-alc-anchor"):
                self.FLT_ALC_ANCHOR = [float(s) for s in arg.split(',')]
            elif opt in ("--filt-alc-range"):
                self.FLT_ALC_RANGE = [float(s) for s in arg.split(',')]

            # Aligned marginals
            elif opt in ("--filtering-marginals"):
                self.FLT_ALIGNED_MARGINALS = True
            # Options
            elif opt in ("--filt-alm-n-points"):
                self.FLT_ALM_N_POINTS = int(arg)
            elif opt in ("--filt-alm-n-tri-plots"):
                self.FLT_ALM_N_TRI_PLOTS = int(arg)

            # Quadrature
            elif opt in ("--filtering-quadrature"):
                self.FLT_QUADRATURE.append( True )
                self.FLT_QUAD_QTYPE.append( None )
                self.FLT_QUAD_QNUM.append( None )
            elif opt in ("--filt-quad-qtype"):
                self.FLT_QUAD_QTYPE[len(self.FLT_QUADRATURE)-1] = int(arg)
            elif opt in ("--filt-quad-qnum"):
                self.FLT_QUAD_QNUM[len(self.FLT_QUADRATURE)-1] = [int(q) for q in arg.split(',')]

    def __init__(self, argv):
        self.TRIM = None
        # Sequential diagnostics
        self.SEQUENTIAL_VAR_DIAG = False
        self.SEQUENTIAL_REG_DIAG = False
        # Filtering aligned conditionals
        self.FLT_ALIGNED_CONDITIONALS = False
        self.FLT_ALC_N_POINTS_X_AX = 30
        self.FLT_ALC_N_TRI_PLOTS = 0
        self.FLT_ALC_ANCHOR = None
        self.FLT_ALC_RANGE = [-5.,5.]
        # Filtering Aligned marginals
        self.FLT_ALIGNED_MARGINALS = False
        self.FLT_ALM_N_POINTS = 1000
        self.FLT_ALM_N_TRI_PLOTS = 0
        # Samples
        self.FLT_QUADRATURE = []
        self.FLT_QUAD_QTYPE = []
        self.FLT_QUAD_QNUM = []

        super(SequentialPostprocess, self).__init__(argv)

    def load(self):
        super(SequentialPostprocess, self).load()
        if self.TRIM is None:
            self.TRIM = self.target_distribution.nsteps
        if self.TRIM == self.target_distribution.nsteps:
            self.filt_tmap_list = self.stg.integrator.filtering_map_list
        elif self.TRIM < self.target_distribution.nsteps:
            integrator = self.stg.integrator.trim(self.TRIM)
            self.target_distribution = self.target_distribution.trim(self.TRIM)
            self.dim = self.target_distribution.dim
            self.base_distribution = DIST.StandardNormalDistribution(self.dim)
            self.tmap = integrator.smoothing_map
            self.approx_base_distribution = DIST.PullBackTransportMapDistribution(
                self.tmap, self.target_distribution)
            self.approx_target_distribution = DIST.PushForwardTransportMapDistribution(
                self.tmap, self.base_distribution)
        else:
            raise ValueError("The value --trim exceed the total number of steps.")
        # Set hdf5 root
        ROOT_NAME = "trim-%d" % self.TRIM
        if ROOT_NAME not in self.h5_file:
            self.h5_file.create_group(ROOT_NAME)
        self.h5_root = self.h5_file[ROOT_NAME]

    def sequential_variance_diagnostic(self, mpi_pool):
        if self.SEQUENTIAL_VAR_DIAG:
            self.filter_tstamp_print("[Start] Sequential variance diagnostic")
            if self.PLOTTING:
                import matplotlib.pyplot as plt
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax2 = ax.twinx()
                ax.semilogy(self.stg.integrator.var_diag_convergence)
                ax.set_xlabel("Step")
                ax.set_ylabel(r"$\mathbb{V}[\log\rho/T_i^\sharp\pi_i]$")
                n_coeffs = [ tm.n_coeffs for tm in self.stg.integrator.R_list ]
                ax2.semilogy(n_coeffs, 'k')
                ax2.set_ylabel("number of coefficients")
                if self.STORE_FIG_DIR is not None:
                    self.store_figure(
                        fig, self.STORE_FIG_DIR + "/" + self.TITLE + \
                        '-sequential-var-diag' + self.EXTRA_TIT)
                else:
                    plt.show(False)
            self.filter_tstamp_print("[Stop] Sequential variance diagnostic")

    def sequential_regression_diagnostic(self, mpi_pool):
        if self.SEQUENTIAL_REG_DIAG:
            self.filter_tstamp_print("[Start] Sequential regression diagnostic")
            if self.PLOTTING:
                import matplotlib.pyplot as plt
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.semilogy(self.stg.integrator.regression_convergence)
                ax.set_xlabel("Iteration")
                ax.set_ylabel(r"$\Vert H_i - H_{i-1}\circ\tilde{H}_i\Vert_2$")
                if self.STORE_FIG_DIR is not None:
                    self.store_figure(
                        fig, self.STORE_FIG_DIR + "/" + self.TITLE + \
                        '-sequential-reg-diag' + self.EXTRA_TIT)
                else:
                    plt.show(False)
            self.filter_tstamp_print("[Stop] Sequential regression diagnostic")

    def filtering_aligned_conditionals(self, mpi_pool):
        if self.FLT_ALIGNED_CONDITIONALS:
            self.filter_tstamp_print("[Start] Filtering conditionals")
            for n, filt_tmap in enumerate(self.filt_tmap_list):
                self.filter_tstamp_print("        Filtering conditionals " + \
                                         "- Step %d" % n)
                DATA_FIELD = 'filtering-conditionals-%d' % n
                data = self.postproc_data.get(DATA_FIELD, None)
                if data is None:
                    base_density = DIST.StandardNormalDistribution(filt_tmap.dim)
                    d = DIST.PushForwardTransportMapDistribution(
                        filt_tmap, base_density)
                    data = DIAG.computeAlignedConditionals(
                        d, dimensions_vec=self.FLT_ALC_N_TRI_PLOTS,
                        numPointsXax=self.FLT_ALC_N_POINTS_X_AX,
                        pointEval=self.FLT_ALC_ANCHOR, range_vec=self.FLT_ALC_RANGE,
                        mpi_pool=mpi_pool)
                    self.postproc_data[DATA_FIELD] = data
                    if self.OUTPUT is not None:
                        self.safe_store(self.postproc_data, self.OUTPUT)
                if self.PLOTTING:
                    fig = DIAG.plotAlignedConditionals(
                        data=data, show_flag=(self.STORE_FIG_DIR is None))
                    if self.STORE_FIG_DIR is not None:
                        self.store_figure(fig, self.STORE_FIG_DIR + '/' + \
                                          self.TITLE + \
                                          '-filtering-conditionals-%d' % n +\
                                          self.EXTRA_TIT)
            self.filter_tstamp_print("[Stop]  Filtering conditionals")

    def filtering_aligned_marginals(self, mpi_pool):
        if self.FLT_ALIGNED_MARGINALS:
            self.filter_tstamp_print("[Start] Filtering marginals")
            F_GRP_NAME = "/filtering"
            if F_GRP_NAME not in self.h5_root:
                self.h5_root.create_group(F_GRP_NAME)
            fgrp = self.h5_root[F_GRP_NAME]
            for n, filt_tmap in enumerate(self.filt_tmap_list):
                self.filter_tstamp_print("        Filtering marginals " + \
                                         "- Step %d - Sample generation" % n)
                dim = filt_tmap.dim
                # Load values if any
                S_GRP_NAME = "step-%d" % n
                if S_GRP_NAME not in fgrp:
                    fgrp.create_group(S_GRP_NAME)
                sgrp = fgrp[S_GRP_NAME]
                Q_GRP_NAME = "quadrature"
                if Q_GRP_NAME not in sgrp:
                    sgrp.create_group(Q_GRP_NAME)
                qgrp = sgrp[Q_GRP_NAME]
                DSET_NAME = '0'
                if DSET_NAME not in qgrp:
                    qgrp.create_dataset(
                        DSET_NAME, (0,dim), maxshape=(None,dim), dtype='d')
                loaded_samp = qgrp[DSET_NAME]
                if self.FLT_ALM_N_POINTS > loaded_samp.shape[0]:
                    nold = loaded_samp.shape[0]
                    new_nsamp = self.FLT_ALM_N_POINTS - nold
                    base_density = DIST.StandardNormalDistribution(dim)
                    d = DIST.PushForwardTransportMapDistribution(
                        filt_tmap, base_density)
                    x = d.rvs(new_nsamp, mpi_pool=mpi_pool)
                    loaded_samp.resize(self.FLT_ALM_N_POINTS, axis=0)
                    loaded_samp[nold:,:] = x
                self.filter_tstamp_print("        Filtering marginals " + \
                                    "- Step %d - Plotting" % n)
                if self.PLOTTING:
                    fig = DIAG.plotAlignedMarginals(
                        loaded_samp[:self.FLT_ALM_N_POINTS,:], self.FLT_ALM_N_TRI_PLOTS,
                        show_flag=(self.STORE_FIG_DIR is None))
                    if self.STORE_FIG_DIR is not None:
                        self.store_figure(
                            fig, self.STORE_FIG_DIR+'/'+self.TITLE + \
                            '-filtering-marginals-%d' % n + \
                            self.EXTRA_TIT)
            self.filter_tstamp_print("[Stop]  Filtering marginals")

    def filtering_quadratures(self, mpi_pool):
        for _, qtype, qnum in zip(
                self.FLT_QUADRATURE, self.FLT_QUAD_QTYPE, self.FLT_QUAD_QNUM):
            self.filter_tstamp_print("[Start] Quadrature " + str(qtype))
            F_GRP_NAME = "/filtering"
            if F_GRP_NAME not in self.h5_root:
                self.h5_root.create_group(F_GRP_NAME)
            fgrp = self.h5_root[F_GRP_NAME]
            for n, filt_tmap in enumerate(self.filt_tmap_list):
                self.filter_tstamp_print("        Quadrature " + str(qtype) + \
                                         "- Step %d - Sample generation" % n)
                dim = filt_tmap.dim
                # Load values if any
                S_GRP_NAME = "step-%d" % n
                if S_GRP_NAME not in fgrp:
                    fgrp.create_group(S_GRP_NAME)
                sgrp = fgrp[S_GRP_NAME]
                Q_GRP_NAME = "quadrature"
                if Q_GRP_NAME not in sgrp:
                    sgrp.create_group(Q_GRP_NAME)
                qgrp = sgrp[Q_GRP_NAME]
                if qtype == 0: # Monte-Carlo
                    DSET_NAME = str(qtype)
                    if DSET_NAME not in qgrp:
                        qgrp.create_dataset(
                            DSET_NAME, (0,dim), maxshape=(None,dim), dtype='d')
                    loaded_samp = qgrp[DSET_NAME]
                    if qnum[0] > loaded_samp.shape[0]:
                        nold = loaded_samp.shape[0]
                        new_nsamp = qnum[0] - nold
                        base_density = DIST.StandardNormalDistribution(dim)
                        d = DIST.PushForwardTransportMapDistribution(
                            filt_tmap, base_density)
                        x = d.rvs(new_nsamp, mpi_pool=mpi_pool)
                        loaded_samp.resize(qnum[0], axis=0)
                        loaded_samp[nold:,:] = x
                elif qtype == 3: # Gauss quadrature
                    QTYPE_NAME = str(qtype)
                    X_NAME = 'x'
                    W_NAME = 'w'
                    if QTYPE_NAME not in qgrp:
                        qgrp.create_group(QTYPE_NAME)
                    qtp_grp = qgrp[QTYPE_NAME]
                    QNUM_NAME = str(qnum)
                    if QNUM_NAME not in qtp_grp:
                        qtp_grp.create_group(QNUM_NAME)
                        qngrp = qtp_grp[QNUM_NAME]
                        base_density = DIST.StandardNormalDistribution(dim)
                        d = DIST.PushForwardTransportMapDistribution(
                            filt_tmap, base_density)
                        (x, w) = d.quadrature(qtype, qnum, mpi_pool=mpi_pool)
                        qngrp.create_dataset(X_NAME, data=x)
                        qngrp.create_dataset(W_NAME, data=w)
            self.filter_tstamp_print("[Stop]  Quadrature")

    def run(self, mpi_pool):
        super(SequentialPostprocess, self).run(mpi_pool)
        self.sequential_variance_diagnostic(mpi_pool)
        self.sequential_regression_diagnostic(mpi_pool)
        self.filtering_aligned_conditionals(mpi_pool)
        self.filtering_aligned_marginals(mpi_pool)
        self.filtering_quadratures(mpi_pool)