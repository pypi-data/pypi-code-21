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
from .ScriptBase import Script

import TransportMaps.Diagnostics as DIAG
import TransportMaps.Samplers as SAMP
import TransportMaps.Distributions as DIST

__all__ = ['Postprocess']

class Postprocess(Script):

    def usage(self):
        usage_str = """
Usage: tmap-postprocess [-h -v -I]
  --input=INPUT --output=OUTPUT
  [--store-fig-dir=DIR --store-fig-fmats=FMATS
   --extra-tit=TITLE --no-plotting 
   --aligned-conditionals=DIST
     --alc-n-points-x-ax=N --alc-n-tri-plots=N
     --alc-anchor=LIST --alc-range=LIST
   --random-conditionals=DIST
     --rndc-n-points-x-ax=N --rndc-n-plots-x-ax=N
     --rndc-anchor=LIST --rndc-range=LIST
   --var-diag=DIST
     --var-diag-qtype=QTYPE --var-diag-qnum=QNUM
   --aligned-marginals=DIST
     --alm-n-points=N --alm-n-tri-plots=N
   --quadrature=DIST
     --quadrature-qtype=QTYPE
     --quadrature-qnum=QNUM
   --importance-samples=NSAMP
   --mcmc=ALG
     --mcmc-samples=NSAMP
     --mcmc-burnin=BURNIN
     --mcmc-skip=SKIP
     --mcmc-no-ess --mcmc-ess-skip=SKIP
     --mcmc-ess-q=QUANTILE
     --mcmc-ess-corr-plot
     --mcmc-ess-corr-plot-lag=LAG
     --mcmc-ess-hist-plot
     --mcmc-hmc-eps=EPS
     --mcmc-hmc-nsteps=NSTEPS
   --chunk-size=SIZE --log=LOG --nprocs=NPROCS]
"""
        print(usage_str)

    def description(self):
        docs_distributions_str = \
            AO.print_avail_options(AO.AVAIL_DISTRIBUTIONS,
                                      '                        ', False)
        docs_mcmc_str = \
            '  --mcmc=ALG              algorithm to be used to generate Markov Chain.\n' + \
            AO.print_avail_options(AO.AVAIL_MCMC_ALGORITHMS,
                                      '                          ')
        docs_log_str = \
            '  --log=LOG               log level (default=30). Uses package logging.\n' + \
            AO.print_avail_options(AO.AVAIL_LOGGING,'                          ')
        docs_str = """DESCRIPTION
Given a file (--input) storing the transport map pushing forward a base distribution
to a target distribution, provides a number of diagnositic routines.
All files involved are stored and loaded using the python package dill and
an extra file OUTPUT.hdf5 is created to store big datasets in the hdf5 format.
In the following default values are shown in brackets.

OPTIONS - input/output:
  --input=INPUT         path to the file containing the target distribution,
                          the base distribution and the transport map pushing forward
                          the base to the target.
  --output=OUTPUT       path to the file storing all postprocess data.
                          The additional file OUTPUT.hdf5 will be used to store
                          the more memory consuming data.
  --store-fig-dir=DIR   path to the directory where to store the figures.
  --store-fig-fmats=FMATS  figure formats - see matplotlib for supported formats (svg)
  --extra-tit=TITLE     additional title for the figures' file names.
  --no-plotting         do not plot figures, but only store their data.
                          (requires --output or --store-fig-dir)
OPTIONS - Diagnostics:
  --aligned-conditionals=DIST  plot aligned slices of the selected DIST:
""" + docs_distributions_str + """                        Optional arguments:
    --alc-n-points-x-ax=N  number of discretization points per axis (40)
    --alc-n-tri-plots=N    number of subplots (0)
    --alc-anchor=LIST      list of floats "f1,f2,f3..." for the anchor point (0)
    --alc-range=LIST       list of two floats "f1,f2" for the range (-5,5)
  --random-conditionals=DIST   plot randomly chosen slices of the selected DIST:
""" + docs_distributions_str + """                        Optional arguments:
    --rndc-n-points-x-ax=N   number of discretization points per axis (40)
    --rndc-n-plots-x-ax=N    number of subplots (0)
    --rndc-anchor=LIST       list of floats "f1,f2,f3..." for the anchor point (0)
    --rndc-range=LIST        list of two floats "f1,f2" for the range (-5,5)
  --var-diag=DIST       compute variance diagostic using the sampling DIST:
""" + docs_distributions_str + """                        Optional arguments:
    --var-diag-qtype=QTYPE  quadrature type to be used (0)
    --var-diag-qnum=QNUM    level of the quadrature (1000)
OPTIONS - Sampling:
  --aligned-marginals=DIST  plot aligned marginals of the selected DIST:
""" + docs_distributions_str + """                        Optional arguments:
    --alm-n-points=N         number of samples to be used for the kernel density estimation
    --alm-n-tri-plots=N      number of subplots (0)
  --quadrature=DIST     generate quadrature for the selected DIST:
""" + docs_distributions_str + """                        Optional arguments:
    --quadrature-qtype=QTYPE  generate quadrature of type QTYPE (0)
    --quadrature-qnum=QNUM  level of the quadrature (int or list)
  --importance-samples=NSAMP  number of importance samples and weights for the approximation
                        of estimators with respect to the target distribution
""" + docs_mcmc_str + \
"""    --mcmc-samples=NSAMP  length of the chain with invariant distribution the
                          target distribution using Metropolis-Hastings with independent
                          proposals
    --mcmc-burnin=BURNIN   number of samples to be considered as burn-in
    --mcmc-skip=SKIP      number of sample to be skipped (>=0) in storage (a NSAMP*SKIP chain is subsampled)
    --mcmc-no-ess         turn off the computation of the effective sample size
    --mcmc-ess-skip=SKIP  number of samples to be skipped in the effective sample size estimation
    --mcmc-ess-q=QUANTILE  quantile used for the estimation of the sample size (0.99).
                             This is estimated over the worst decaying autocorrelation rate.
    --mcmc-ess-corr-plot   whether to plot the auto correlations
    --mcmc-ess-corr-plot-lag=LAG  maximum lag to be plotted (100)
    --mcmc-ess-hist-plot   whether to plot a summary of the sample size by dimension
    --mcmc-hmc-eps=EPS     epsilon value in Hamiltonian Monte Carlo
    --mcmc-hmc-nsteps=NSTEPS number of steps per sample
OPTIONS - Computation:
  --chunk-size=SIZE       chunk size to be used in the storage of data
""" + docs_log_str + """  --nprocs=NPROCS         number of processors to be used (default=1)
OPTIONS - other:
  -v                      verbose output (not affecting --log)
  -I                      enter interactive mode after finishing
  -h                      print this help
"""
        print(docs_str)

    def store_figure(self, fig, fname):
        for fmat in STORE_FIG_FMATS:
            fig.savefig(fname+'.'+fmat, format=fmat, bbox_inches='tight');
        
    @property
    def long_options(self):
        return super(Postprocess, self).long_options + \
            [
                # I/O
                "store-fig-dir=", "store-fig-fmats=",
                "extra-tit=", "no-plotting",
                # Aligned conditionals
                "aligned-conditionals=",
                "alc-n-points-x-ax=", "alc-n-tri-plots=", "alc-anchor=", "alc-range=",
                # Random conditionals
                "random-conditionals=",
                "rndc-n-points-x-ax=", "rndc-anchor=", "rndc-range=", "rndc-n-plots-x-ax=",
                # Aligned marginals
                "aligned-marginals=",
                "alm-n-points=", "alm-n-tri-plots=",
                # Variance diagnostic
                "var-diag=", "var-diag-qtype=", "var-diag-qnum=",
                # Quadrature
                "quadrature=", "quadrature-qtype=", "quadrature-qnum=",
                # Importance sampling
                "importance-samples=",
                # Markov Chain Monte Carlo
                "mcmc=",
                "mcmc-samples=", "mcmc-burnin=", "mcmc-skip=",
                "mcmc-hmc-eps=", "mcmc-hmc-nsteps=",
                "mcmc-no-ess", "mcmc-ess-skip=",
                "mcmc-ess-q=", "mcmc-ess-xcorr",
                "mcmc-ess-corr-plot", "mcmc-ess-corr-plot-lag=",
                "mcmc-ess-hist-plot",
                # Computation
                "chunk-size="
            ]

    def load_opts(self, opts):
        super(Postprocess, self).load_opts(opts)
        for opt, arg in opts:
            # I/O
            if opt == "--store-fig-dir":
                self.STORE_FIG_DIR = arg
            elif opt == "--store-fig-fmats":
                self.STORE_FIG_FMATS = arg.split(',')
            elif opt == "--extra-tit":
                self.EXTRA_TIT = "-" + arg
            elif opt == "--no-plotting":
                self.PLOTTING = False

            # Aligned conditionals
            elif opt == "--aligned-conditionals":
                self.ALIGNED_CONDITIONALS.append(arg)
                self.ALC_N_POINTS_X_AX.append( self.DFT_N_POINTS_X_AX )
                self.ALC_N_TRI_PLOTS.append( self.DFT_N_TRI_PLOTS )
                self.ALC_ANCHOR.append( self.DFT_ANCHOR )
                self.ALC_RANGE.append( self.DFT_RANGE )
            # Options
            elif opt == "--alc-n-points-x-ax":
                self.ALC_N_POINTS_X_AX[len(self.ALIGNED_CONDITIONALS)-1] = int(arg)
            elif opt == "--alc-n-tri-plots":
                self.ALC_N_TRI_PLOTS[len(self.ALIGNED_CONDITIONALS)-1] = list(range(int(arg)))
            elif opt == "--alc-anchor":
                self.ALC_ANCHOR[len(self.ALIGNED_CONDITIONALS)-1] = [float(s) for s in arg.split(',')]
            elif opt == "--alc-range":
                self.ALC_RANGE[len(self.ALIGNED_CONDITIONALS)-1] = [float(s) for s in arg.split(',')]

            # Random conditionals
            elif opt == "--random-conditionals":
                self.RANDOM_CONDITIONALS.append(arg)
                self.RNDC_N_POINTS_X_AX.append( self.DFT_N_POINTS_X_AX )
                self.RNDC_N_PLOTS_X_AX.append( self.DFT_N_PLOTS_X_AX )
                self.RNDC_ANCHOR.append( self.DFT_ANCHOR )
                self.RNDC_RANGE.append( self.DFT_RANGE )
            # Options
            elif opt == "--rndc-n-points-x-ax":
                self.RNDC_N_POINTS_X_AX[len(self.RANDOM_CONDITIONALS)-1] = int(arg)
            elif opt == "--rndc-n-plots-x-ax":
                self.RNDC_N_PLOTS_X_AX[len(self.RANDOM_CONDITIONALS)-1] = int(arg)
            elif opt == "--rndc-anchor":
                self.RNDC_ANCHOR[len(self.RANDOM_CONDITIONALS)-1] = [float(s) for s in arg.split(',')]
            elif opt == "--rndc-range":
                self.RNDC_RANGE[len(self.RANDOM_CONDITIONALS)-1] = [float(s) for s in arg.split(',')]

            # Aligned marginals
            elif opt == "--aligned-marginals":
                self.ALIGNED_MARGINALS.append(arg)
                self.ALM_N_POINTS.append(self.DFT_N_POINTS)
                self.ALM_N_TRI_PLOTS.append(self.DFT_N_TRI_PLOTS)
            # Options
            elif opt == "--alm-n-points":
                self.ALM_N_POINTS[len(self.ALIGNED_MARGINALS)-1] = int(arg)
            elif opt == "--alm-n-tri-plots":
                self.ALM_N_TRI_PLOTS[len(self.ALIGNED_MARGINALS)-1] = int(arg)

            # Variance diagnostic
            elif opt == "--var-diag":
                self.VAR_DIAG.append(arg)
                self.VD_QTYPE.append(self.DFT_VD_QTYPE)
                self.VD_QNUM.append(self.DFT_VD_QNUM)
            elif opt == "--var-diag-qtype":
                self.VD_QTYPE[len(self.VAR_DIAG)-1] = int(arg)
            elif opt == "--var-diag-qnum":
                self.VD_QNUM[len(self.VAR_DIAG)-1] = [int(q) for q in arg.split(',')]

            # Quadrature
            elif opt == "--quadrature":
                self.QUADRATURE.append( arg )
                self.QUAD_QTYPE.append( None )
                self.QUAD_QNUM.append( None )
            elif opt == "--quadrature-qtype":
                self.QUAD_QTYPE[len(self.QUADRATURE)-1] = int(arg)
            elif opt == "--quadrature-qnum":
                self.QUAD_QNUM[len(self.QUADRATURE)-1] = [int(q) for q in arg.split(',')]

            # Importance sampling
            elif opt == "--importance-samples":
                self.IMP_SAMPLES = int(arg)

            # Metropolis Hastings
            elif opt == "--mcmc":
                self.MCMC_ALG = arg
            elif opt == "--mcmc-samples":
                self.MCMC_SAMPLES = int(arg)
            elif opt == "--mcmc-burnin":
                self.MCMC_BURNIN = int(arg)
            elif opt == "--mcmc-skip":
                self.MCMC_SKIP = max(int(arg), 0)
            elif opt == "--mcmc-hmc-eps":
                self.MCMC_HMC_EPS = float(arg)
            elif opt == "--mcmc-hmc-nsteps":
                self.MCMC_HMC_NSTEPS = int(arg)
            elif opt == "--mcmc-no-ess":
                self.MCMC_DO_ESS = False
            elif opt == "--mcmc-ess-skip":
                self.MCMC_ESS_SKIP = int(arg)
                if self.MCMC_ESS_SKIP < 1:
                    raise ValueError("SKIP must be > 0 in --mcmc-ess-skip=SKIP")
            elif opt == "--mcmc-ess-q":
                self.MCMC_ESS_Q = float(arg)
            elif opt == "--mcmc-ess-corr-plot":
                self.MCMC_ESS_CORR_PLOT = True
            elif opt == "--mcmc-ess-corr-plot-lag":
                self.MCMC_ESS_CORR_PLOT_LAG = int(arg)
            elif opt == "--mcmc-ess-hist-plot":
                self.MCMC_ESS_HIST_PLOT = True

            # Computation
            elif opt == "--chunk-size":
                self.CHUNK_SIZE = int(arg)

    def __init__(self, argv):
        # I/O
        self.STORE_FIG_DIR = None
        self.STORE_FIG_FMATS = ['svg']
        self.EXTRA_TIT = ''
        self.PLOTTING = True
        # Aligned conditionals
        self.ALIGNED_CONDITIONALS = []
        self.ALC_N_POINTS_X_AX = []
        self.ALC_N_TRI_PLOTS = []
        self.ALC_ANCHOR = []
        self.ALC_RANGE = []
        # Random conditionals
        self.RANDOM_CONDITIONALS = []
        self.RNDC_N_POINTS_X_AX = []
        self.RNDC_N_PLOTS_X_AX = []
        self.RNDC_ANCHOR = []
        self.RNDC_RANGE = []
        # Aligned marginals
        self.ALIGNED_MARGINALS = []
        self.ALM_N_POINTS = []
        self.ALM_N_TRI_PLOTS = []
        # Default plotting options
        self.DFT_N_POINTS = 1000
        self.DFT_N_POINTS_X_AX = 40
        self.DFT_N_TRI_PLOTS = 0
        self.DFT_ANCHOR = None
        self.DFT_RANGE = [-5.,5.]
        self.DFT_N_PLOTS_X_AX = 6
        # Variance diagnostic
        self.VAR_DIAG = []
        self.VD_QTYPE = []
        self.VD_QNUM  = []
        # Defaults for variance diagnostic
        self.DFT_VD_QTYPE = 0
        self.DFT_VD_QNUM = 1000
        # Samples
        self.QUADRATURE = []
        self.QUAD_QTYPE = []
        self.QUAD_QNUM = []
        # Importance samples
        self.IMP_SAMPLES = None
        # MCMC samples
        self.MCMC_ALG = None
        self.MCMC_SAMPLES = None
        self.MCMC_BURNIN = 0
        self.MCMC_SKIP = 0
        self.MCMC_DO_ESS = True
        self.MCMC_ESS_SKIP = 1
        self.MCMC_ESS_Q = 0.99
        self.MCMC_ESS_CORR_PLOT = False
        self.MCMC_ESS_CORR_PLOT_LAG = 100
        self.MCMC_ESS_HIST_PLOT = False
        self.MCMC_HMC_EPS = 0.2
        self.MCMC_HMC_NSTEPS = 1
        # hdf5 options
        self.CHUNK_SIZE = 10000

        super(Postprocess, self).__init__(argv)

        if not self.PLOTTING and self.STORE_FIG_DIR is None and self.OUTPUT is None:
            self.usage()
            self.tstamp_print(
                "ERROR: Neither --output nor --store-fig-dir were " + \
                "specified, while --no-plotting is active. " + \
                "This would result on no data shown or stored.")
            sys.exit(3)

        # Prepare storage of figures
        if self.STORE_FIG_DIR is not None:
            tit_no_path = str.split(DATA,"/")[-1]
            self.TITLE = '.'.join(str.split(tit_no_path,".")[:-1])

    def load(self):
        self.h5_file = None
        
        # Load data
        with open(self.INPUT, 'rb') as in_stream:
            self.stg = dill.load(in_stream)

        # Restore data
        self.base_distribution = self.stg.base_distribution
        self.target_distribution = self.stg.target_distribution
        self.tmap = self.stg.tmap
        self.approx_base_distribution = self.stg.approx_base_distribution
        self.approx_target_distribution = self.stg.approx_target_distribution
        self.dim = self.base_distribution.dim

        # Load output (dill file) if any
        if not os.path.exists(self.OUTPUT):
            self.postproc_data = {}
            with open(self.OUTPUT, 'wb') as out_stream:
                dill.dump(self.postproc_data, out_stream)
        with open(self.OUTPUT, 'rb') as in_stream:
            self.postproc_data = dill.load(in_stream)
        # Load output (hdf5 file) if any
        self.h5_file = h5py.File(self.OUTPUT + '.hdf5', 'a')
        self.h5_root = self.h5_file

    def aligned_conditionals(self, mpi_pool):
        for aligned, n_tri_plots, n_points_x_ax, anchor, rng in \
            zip(self.ALIGNED_CONDITIONALS, self.ALC_N_TRI_PLOTS,
                self.ALC_N_POINTS_X_AX, self.ALC_ANCHOR, self.ALC_RANGE):
            self.filter_tstamp_print("[Start] Aligned conditionals " + aligned)
            if aligned == 'exact-target':
                d = self.target_distribution
            elif aligned == 'approx-target':
                d = self.approx_target_distribution
            elif aligned == 'exact-base':
                d = self.base_distribution
            elif aligned == 'approx-base':
                d = self.approx_base_distribution
            else:
                self.full_usage()
                self.tstamp_print("ERROR: DIST %s not recognized." % aligned)
                sys.exit(3)
            DATA_FIELD = 'aligned-' + aligned
            data = self.postproc_data.get(DATA_FIELD, None)
            if data is None:
                data = DIAG.computeAlignedConditionals(
                    d, dimensions_vec=n_tri_plots,
                    numPointsXax = n_points_x_ax,
                    pointEval=anchor, range_vec=rng,
                    mpi_pool=mpi_pool)
                self.postproc_data[DATA_FIELD] = data
                if self.OUTPUT is not None:
                    self.safe_store(self.postproc_data, self.OUTPUT)
            if self.PLOTTING:
                fig = DIAG.plotAlignedConditionals(
                    data=data, show_flag=(self.STORE_FIG_DIR is None));
                if self.STORE_FIG_DIR is not None:
                    self.store_figure(fig, self.STORE_FIG_DIR+'/'+self.TITLE+ \
                                 '-aligned-conditionals-'+ aligned +\
                                 self.EXTRA_TIT)
            self.filter_tstamp_print("[Stop]  Aligned conditionals " + aligned)

    def random_conditionals(self, mpi_pool):
        for random, n_plots_x_ax, n_points_x_ax, anchor, rng in \
            zip(self.RANDOM_CONDITIONALS, self.RNDC_N_PLOTS_X_AX,
                self.RNDC_N_POINTS_X_AX,
                self.RNDC_ANCHOR, self.RNDC_RANGE):
            self.filter_tstamp_print("[Start] Random conditionals " + random)
            if random == 'exact-target':
                d = self.target_distribution
            elif random == 'approx-target':
                d = self.approx_target_distribution
            elif random == 'exact-base':
                d = self.base_distribution
            elif random == 'approx-base':
                d = self.approx_base_distribution
            else:
                self.full_usage()
                self.tstamp_print("ERROR: DIST %s not recognized." % random)
                sys.exit(3)
            DATA_FIELD = 'random-' + random
            data = self.postproc_data.get(DATA_FIELD, None)
            if data is None:
                data = DIAG.computeRandomConditionals(
                    d, num_conditionalsXax=n_plots_x_ax,
                    numPointsXax=n_points_x_ax,
                    pointEval=anchor, range_vec=rng,
                    mpi_pool=mpi_pool)
                self.postproc_data[DATA_FIELD] = data
                if self.OUTPUT is not None:
                    self.safe_store(self.postproc_data, self.OUTPUT)
            if self.PLOTTING:
                fig = DIAG.plotRandomConditionals(
                    data=data, show_flag=(self.STORE_FIG_DIR is None))
                if self.STORE_FIG_DIR is not None:
                    self.store_figure(fig, self.STORE_FIG_DIR+'/'+\
                                      self.TITLE+'-random-conditionals-' + random + \
                                      self.EXTRA_TIT)
            self.filter_tstamp_print("[Stop]  Random conditionals " + random)

    def variance_diagnostic(self, mpi_pool):
        for dstr, qtype, qnum in zip(self.VAR_DIAG, self.VD_QTYPE, self.VD_QNUM):
            self.filter_tstamp_print("[Start] Variance diagnostic " + dstr)
            if dstr == 'exact-target':
                d1 = self.target_distribution
                d2 = self.approx_target_distribution
            elif dstr == 'approx-target':
                d1 = self.approx_target_distribution
                d2 = self.target_distribution
            elif dstr == 'exact-base':
                d1 = self.base_distribution
                d2 = self.approx_base_distribution
            elif dstr == 'approx-base':
                d1 = self.approx_base_distribution
                d2 = self.base_distribution
            else:
                self.full_usage()
                self.tstamp_print("ERROR: DIST %s not recognized." % dstr)
                sys.exit(3)
            # Load values if any
            GRP_NAME = "vals_var_diag/" + dstr
            if GRP_NAME not in self.h5_root:
                self.h5_root.create_group(GRP_NAME)
            grp = self.h5_root[GRP_NAME]
            QTYPE_NAME = str(qtype)
            if QTYPE_NAME not in grp:
                grp.create_group(QTYPE_NAME)
            qtype_grp = grp[QTYPE_NAME]
            V1_NAME = 'vals_d1'
            V2_NAME = 'vals_d2'
            if qtype == 0: # Monte-Carlo
                if V1_NAME not in qtype_grp:
                    qtype_grp.create_dataset(
                        V1_NAME, (0,), maxshape=(None,), dtype='d', chunks=(self.CHUNK_SIZE,))
                if V2_NAME not in qtype_grp:
                    qtype_grp.create_dataset(
                        V2_NAME, (0,), maxshape=(None,), dtype='d', chunks=(self.CHUNK_SIZE,))
                loaded_vals_d1 = qtype_grp[V1_NAME]
                loaded_vals_d2 = qtype_grp[V2_NAME]
                if len(loaded_vals_d1) > 0 and qnum[0] <= len(loaded_vals_d1):
                    # Subselect already available data
                    vals_d1 = np.array( loaded_vals_d1[:qnum[0]] )
                    vals_d2 = np.array( loaded_vals_d2[:qnum[0]] )
                else:
                    old_len = len(loaded_vals_d1)
                    # Sample new points and evaluate
                    n_new_samps = qnum[0] - len(loaded_vals_d1)
                    x = d1.rvs(n_new_samps)
                    new_vals_d1, new_vals_d2 = DIAG.compute_vals_variance_approx_kl(
                        d1, d2, x=x, mpi_pool_tuple=(None, mpi_pool))
                    loaded_vals_d1.resize(qnum[0], axis=0)
                    loaded_vals_d2.resize(qnum[0], axis=0)
                    loaded_vals_d1[old_len:] = new_vals_d1
                    loaded_vals_d2[old_len:] = new_vals_d2
                    vals_d1 = np.array( loaded_vals_d1 )
                    vals_d2 = np.array( loaded_vals_d2 )
                w = np.ones(qnum[0])/float(qnum[0])
            elif qtype == 3: # Gauss quadrature
                QNUM_NAME = str(qnum)
                W_NAME = 'w'
                if QNUM_NAME not in qtype_grp:
                    qtype_grp.create_group(QNUM_NAME)
                    qnum_grp = qtype_grp[QNUM_NAME]
                    (x, w) = d1.quadrature(qtype, qnum, mpi_pool=mpi_pool)
                    vals_d1, vals_d2 = DIAG.compute_vals_variance_approx_kl(
                        d1, d2, x=x, mpi_pool_tuple=(None, mpi_pool))
                    csize = min(self.CHUNK_SIZE, w.shape[0])
                    qnum_grp.create_dataset(V1_NAME, data=vals_d1, chunks=(csize,))
                    qnum_grp.create_dataset(V2_NAME, data=vals_d2, chunks=(csize,))
                    qnum_grp.create_dataset(W_NAME, data=w, chunks=(csize,))
                else:
                    qnum_grp[QNUM_NAME]
                    vals_d1 = np.array( qnum_grp[V1_NAME] )
                    vals_d2 = np.array( qnum_grp[V2_NAME] )
                    w = np.array( qnum_grp[W_NAME] )
            var_diag_tm = DIAG.variance_approx_kl(d1, d2,
                                                  vals_d1=vals_d1, vals_d2=vals_d2, w=w)
            self.filter_tstamp_print("[Stop]  Variance diagnostic %s: %e" % (dstr, var_diag_tm))

    def aligned_marginals(self, mpi_pool):
        for dstr, n_points, n_tri_plots in zip(
                self.ALIGNED_MARGINALS, self.ALM_N_POINTS, self.ALM_N_TRI_PLOTS):
            self.filter_tstamp_print("[Start] Aligned marginals %s " % dstr + \
                           "- Sample generation")
            if dstr == 'exact-target':
                d = self.target_distribution
            elif dstr == 'approx-target':
                d = self.approx_target_distribution
            elif dstr == 'exact-base':
                d = self.base_distribution
            elif dstr == 'approx-base':
                d = self.approx_base_distribution
            else:
                self.full_usage()
                self.tstamp_print("ERROR: DIST %s not recognized." % dstr)
                sys.exit(3)
            # Load values if any
            Q_GRP_NAME = "quadrature"
            if Q_GRP_NAME not in self.h5_root:
                self.h5_root.create_group(Q_GRP_NAME)
            qgrp = self.h5_root[Q_GRP_NAME]
            D_GRP_NAME = dstr
            if D_GRP_NAME not in qgrp:
                qgrp.create_group(D_GRP_NAME)
            dgrp = qgrp[D_GRP_NAME]
            DSET_NAME = '0'
            if DSET_NAME not in dgrp:
                dgrp.create_dataset(
                    DSET_NAME, (0,self.dim), maxshape=(None,self.dim), dtype='d',
                    chunks=(self.CHUNK_SIZE,1))
            loaded_samp = dgrp[DSET_NAME]
            if n_points > loaded_samp.shape[0]:
                nold = loaded_samp.shape[0]
                new_nsamp = n_points - nold
                x = d.rvs(new_nsamp, mpi_pool=mpi_pool)
                loaded_samp.resize(n_points, axis=0)
                loaded_samp[nold:,:] = x
            self.filter_tstamp_print("        Aligned marginals %s " % dstr + \
                                "- Plotting")
            if self.PLOTTING:
                fig = DIAG.plotAlignedMarginals(
                    loaded_samp[:n_points,:], n_tri_plots,
                    show_flag=(self.STORE_FIG_DIR is None))
                if self.STORE_FIG_DIR is not None:
                    self.store_figure(fig, self.STORE_FIG_DIR+'/'+\
                                 self.TITLE+'-aligned-marginals-'+ dstr +\
                                 self.EXTRA_TIT)
            self.filter_tstamp_print("[Stop]  Aligned marginals %s" % dstr)

    def quadratures(self, mpi_pool):
        for dstr, qtype, qnum in zip(self.QUADRATURE, self.QUAD_QTYPE, self.QUAD_QNUM):
            self.filter_tstamp_print("[Start] Quadrature " + str(qtype))
            if dstr == 'exact-target':
                d = self.target_distribution
            elif dstr == 'approx-target':
                d = self.approx_target_distribution
            elif dstr == 'exact-base':
                d = self.base_distribution
            elif dstr == 'approx-base':
                d = self.approx_base_distribution
            else:
                self.full_usage()
                self.tstamp_print("ERROR: DIST %s not recognized." % dstr)
                sys.exit(3)
            # Load values if any
            GRP_NAME = "quadrature"
            if GRP_NAME not in self.h5_root:
                self.h5_root.create_group(GRP_NAME)
            qgrp = self.h5_root[GRP_NAME]
            D_GRP_NAME = dstr
            if D_GRP_NAME not in qgrp:
                qgrp.create_group(D_GRP_NAME)
            dgrp = qgrp[D_GRP_NAME]
            if qtype == 0: # Monte-Carlo
                DSET_NAME = str(qtype)
                if DSET_NAME not in dgrp:
                    dgrp.create_dataset(
                        DSET_NAME, (0,self.dim), maxshape=(None,self.dim), dtype='d',
                        chunks=(self.CHUNK_SIZE,1))
                loaded_samp = dgrp[DSET_NAME]
                if qnum[0] > loaded_samp.shape[0]:
                    nold = loaded_samp.shape[0]
                    new_nsamp = qnum[0] - nold
                    x = d.rvs(new_nsamp, mpi_pool=mpi_pool)
                    loaded_samp.resize(qnum[0], axis=0)
                    loaded_samp[nold:,:] = x
            elif qtype == 3: # Gauss quadrature
                QTYPE_NAME = str(qtype)
                X_NAME = 'x'
                W_NAME = 'w'
                if QTYPE_NAME not in dgrp:
                    dgrp.create_group(QTYPE_NAME)
                qtp_grp = dgrp[QTYPE_NAME]
                QNUM_NAME = str(qnum)
                if QNUM_NAME not in qtp_grp:
                    qtp_grp.create_group(QNUM_NAME)
                    qngrp = qtp_grp[QNUM_NAME]
                    (x, w) = d.quadrature(qtype, qnum, mpi_pool=mpi_pool)
                    qngrp.create_dataset(X_NAME, data=x, chunks=(self.CHUNK_SIZE,1))
                    qngrp.create_dataset(W_NAME, data=w, chunks=(self.CHUNK_SIZE,))
            self.filter_tstamp_print("[Stop]  Quadrature")

    def importance_sampling(self, mpi_pool):
        if self.IMP_SAMPLES is not None:
            self.filter_tstamp_print("[Start] Importance sampling")
            # Load values if any
            GRP_NAME = "importance-samples"
            if GRP_NAME not in self.h5_root:
                self.h5_root.create_group(GRP_NAME)
            is_grp = self.h5_root[GRP_NAME]
            X_NAME = 'x'
            W_NAME = 'w'
            if X_NAME not in is_grp:
                is_grp.create_dataset(
                    X_NAME, (0,self.dim), maxshape=(None,self.dim),
                    dtype='d', chunks=(self.CHUNK_SIZE,1))
                is_grp.create_dataset(
                    W_NAME, (0,), maxshape=(None,),
                    dtype='d', chunks=(self.CHUNK_SIZE,))
            loaded_x = is_grp[X_NAME]
            loaded_w = is_grp[W_NAME]
            if self.IMP_SAMPLES > loaded_x.shape[0]:
                nold = loaded_x.shape[0]
                new_nsamp = self.IMP_SAMPLES - nold
                sampler = SAMP.ImportanceSampler( self.approx_base_distribution, self.base_distribution )
                (x, w) = sampler.rvs(new_nsamp, mpi_pool_tuple=(mpi_pool, None))
                x = self.approx_target_distribution.map_samples_base_to_target(
                    x, mpi_pool=mpi_pool)
                loaded_x.resize(self.IMP_SAMPLES, axis=0)
                loaded_x[nold:,:] = x
                loaded_w.resize(self.IMP_SAMPLES, axis=0)
                loaded_w[nold:] = w
                loaded_w /= np.sum(loaded_w)
            self.filter_tstamp_print("[Stop]  Importance sampling")

    def mcmc(self, mpi_pool):
        if self.MCMC_ALG is not None:
            self.filter_tstamp_print("[Start] Markov Chain Monte Carlo")
            if self.MCMC_ALG == 'mhind':
                self.filter_tstamp_print("        Metropolis-Hastings with Independent Proposals")
                GRP_NAME = "metropolis-independent-proposal-samples"
                sampler = SAMP.MetropolisHastingsIndependentProposalsSampler(
                    self.approx_base_distribution, self.base_distribution )
                # Load values if any
                if GRP_NAME not in self.h5_root:
                    self.h5_root.create_group(GRP_NAME)
                is_grp = self.h5_root[GRP_NAME]
            elif self.MCMC_ALG == 'hmc':
                self.filter_tstamp_print("        Hamiltonian Monte Carlo")
                GRP_NAME = "hamiltonian-monte-carlo-samples"
                if not isinstance(self.base_distribution, DIST.StandardNormalDistribution):
                    self.logger.warn("The HMC algorithm uses a Standard Normal distribution " +\
                                     "as default proposal")
                sampler = SAMP.HamiltonianMonteCarloSampler( self.approx_base_distribution )
                # Load values if any
                if GRP_NAME not in self.h5_root:
                    self.h5_root.create_group(GRP_NAME)
                is_grp = self.h5_root[GRP_NAME]
                if str(self.MCMC_HMC_EPS) not in is_grp:
                    is_grp.create_group(str(self.MCMC_HMC_EPS))
                is_grp = is_grp[str(self.MCMC_HMC_EPS)]
                if str(self.MCMC_HMC_NSTEPS) not in is_grp:
                    is_grp.create_group(str(self.MCMC_HMC_NSTEPS))
                is_grp = is_grp[str(self.MCMC_HMC_NSTEPS)]
            else:
                self.full_usage()
                self.tstamp_print("ERROR: ALG %s not recognized." % MCMC_ALG)
                sys.exit(3)
            # Create group for each skipping value
            SKIP_NAME = "skip-%d" % self.MCMC_SKIP
            if SKIP_NAME not in is_grp:
                is_grp.create_group(SKIP_NAME)
            is_grp = is_grp[SKIP_NAME]
            X_NAME = 'x'  # Samples in pushforward space
            S_NAME = 's'  # Samples in pullback space
            if X_NAME not in is_grp:
                is_grp.create_dataset(
                    X_NAME, (0,self.dim), maxshape=(None,self.dim),
                    dtype='d', chunks=(self.CHUNK_SIZE,1))
            if S_NAME not in is_grp:
                is_grp.create_dataset(
                    S_NAME, (0,self.dim), maxshape=(None,self.dim),
                    dtype='d', chunks=(self.CHUNK_SIZE,1))
            loaded_x = is_grp[X_NAME]
            loaded_s = is_grp[S_NAME]
            if self.MCMC_SAMPLES > loaded_x.shape[0]:
                nold = loaded_x.shape[0]
                new_nsamp = self.MCMC_SAMPLES - nold
                s0 = None
                if nold > 0:
                    s0 = loaded_s[-1,:]
                    self.filter_tstamp_print("        Restarting chain from stored data (length: %d)" % nold)
                if self.MCMC_ALG == 'mhind':
                    (s, _) = sampler.rvs(new_nsamp*(self.MCMC_SKIP+1), x0=s0,
                                         mpi_pool_tuple=(mpi_pool, None))
                elif self.MCMC_ALG == 'hmc':
                    (s, _) = sampler.rvs(
                        new_nsamp*(self.MCMC_SKIP+1), x0=s0,
                        epsilon=self.MCMC_HMC_EPS, n_steps=self.MCMC_HMC_NSTEPS)
                s = s[::(self.MCMC_SKIP+1),:]
                x = self.approx_target_distribution.map_samples_base_to_target(
                    s, mpi_pool=mpi_pool)
                loaded_x.resize(self.MCMC_SAMPLES, axis=0)
                loaded_s.resize(self.MCMC_SAMPLES, axis=0)
                loaded_x[nold:,:] = x
                loaded_s[nold:,:] = s
            # Compute effective sample size
            if self.MCMC_DO_ESS:
                self.filter_tstamp_print("        Estimating ESS")
                ess_list = []
                for d in range(loaded_x.shape[1]):
                    fig = None if not (self.PLOTTING and self.MCMC_ESS_CORR_PLOT) else plt.figure()
                    ess = SAMP.ess(loaded_x[self.MCMC_BURNIN:self.MCMC_SAMPLES:self.MCMC_ESS_SKIP,[d]],
                                   quantile=self.MCMC_ESS_Q,
                                   plotting=(self.PLOTTING and self.MCMC_ESS_CORR_PLOT),
                                   plot_lag=self.MCMC_ESS_CORR_PLOT_LAG, fig=fig)
                    self.filter_tstamp_print(
                        "        ESS dimension %d: %d/%d " % (
                            d,ess,(self.MCMC_SAMPLES-self.MCMC_BURNIN)//self.MCMC_ESS_SKIP) + \
                        "(%2.3f%%)" % (
                            ess/float((self.MCMC_SAMPLES-self.MCMC_BURNIN)//self.MCMC_ESS_SKIP)*100.)
                    )
                    ess_list.append( ess )
                    if self.PLOTTING and self.MCMC_ESS_CORR_PLOT:
                        if self.STORE_FIG_DIR is None:
                            plt.show(False)
                        else:
                            self.store_figure(fig, self.STORE_FIG_DIR+'/'+\
                                              self.TITLE+'-metropolis-ess-corr-d%d' %d + \
                                              self.EXTRA_TIT)
                if self.PLOTTING and self.MCMC_ESS_HIST_PLOT:
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    ax.plot(ess, drawstyle='steps-mid')
                    ax.set_ylabel("ESS")
                    ax.set_xlable("Dimension")
                    if self.STORE_FIG_DIR is None:
                        plt.show(False)
                    else:
                        self.store_figure(fig, self.STORE_FIG_DIR+'/'+\
                                          self.TITLE+'-metropolis-ess-hist' + \
                                          self.EXTRA_TIT)
                ess = min(ess_list) # We report the worst ess
                self.filter_tstamp_print(
                    "[Stop]  Markov Chain Monte Carlo " + \
                    "- ESS: %d/%d " % (ess,(self.MCMC_SAMPLES-self.MCMC_BURNIN)//self.MCMC_ESS_SKIP) + \
                    "(%2.3f%%)" % (ess/float((self.MCMC_SAMPLES-self.MCMC_BURNIN)//self.MCMC_ESS_SKIP)*100.) )

            else:
                self.filter_tstamp_print("[Stop]  Markov Chain Monte Carlo")

    def run(self, mpi_pool):
        self.aligned_conditionals(mpi_pool)
        self.random_conditionals(mpi_pool)
        self.variance_diagnostic(mpi_pool)
        self.aligned_marginals(mpi_pool)
        self.quadratures(mpi_pool)
        self.importance_sampling(mpi_pool)
        self.mcmc(mpi_pool)