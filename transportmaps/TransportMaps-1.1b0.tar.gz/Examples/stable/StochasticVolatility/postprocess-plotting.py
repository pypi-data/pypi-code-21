#!/usr/bin/env python

#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2016 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# E-mail: tmteam@mit.edu
#

import sys, getopt
import os.path
import time, datetime
import dill
import h5py
import numpy as np
import numpy.random as npr
import scipy.stats as scistat
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import codecs
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

import TransportMaps as TM
import TransportMaps.Diagnostics as DIAG
import TransportMaps.Densities as DENS

def usage():
    print("postprocess-plotting.py --data=<file_name> " + \
          "--postprocess-data=<fname> " + \
          "[--exchanges=<fname> --events=<fname> " + \
          "--do-smooth --do-unb-smooth --do-filt " + \
          "--do-hyper-smooth --do-hyper-filt --do-hyper-unb-filt --trim-ts=TIMES " + \
          "--do-post-pred --do-unb-post-pred " + \
          "--mcmc-skip=SKIP --mcmc-burnin=BURNIN --ntraj=4 --perc=90,50,20 " + \
          "--do-trim-var-diag --chunk-size=SIZE" + \
          "--store-fig-dir=None]")

def full_usage():
    usage()

def bytespdate2num(fmt, encoding='us-ascii'):
    strconverter = mdates.strpdate2num(fmt)
    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)
    return bytesconverter

FSIZE = (12,4.5)
LW = 1
TITLES = False
STATE_VAR = "Z_t"
YLIM = [-3.,2.]
    
argv = sys.argv[1:]
DATA = None
POST_DATA = None
EXCHANGES_DATA = None
EVENTS_DATA = None
DO_SMOOTH = False
DO_UNBIASED_SMOOTH = False
DO_FILT = False
DO_HYPER_SMOOTH = False
DO_HYPER_FILT = False
DO_HYPER_UNB_FILT = False
TRIM_TS = None
DO_POST_PRED = False
DO_UNB_POST_PRED = False
DO_TRIM_VAR_DIAG = False
CHUNK_SIZE = None
MCMC_SKIP = 0
MCMC_BURNIN = 0
NTRAJ = 4
PERC_LIST = [90, 50, 20]
PERC_STYLES = [':', '-.', '--']
STORE_FIG_DIR = None
STORE_FIG_FMATS = ['svg', 'pdf']
try:
    opts, args = getopt.getopt(argv,"h",["data=", "postprocess-data=",
                                         "exchanges=", "events=",
                                         "do-smooth", "do-unb-smooth", "do-filt",
                                         "do-hyper-smooth",
                                         "do-hyper-filt", "do-hyper-unb-filt",
                                         "trim-ts=",
                                         "mcmc-skip=", "mcmc-burnin=",
                                         "ntraj=", "perc=",
                                         'do-post-pred', "do-unb-post-pred",
                                         "do-trim-var-diag", "chunk-size=",
                                         "store-fig-dir="])
except getopt.GetoptError:
    full_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt == "--data":
        DATA = arg
    elif opt == "--postprocess-data":
        POST_DATA = arg
    elif opt == "--exchanges":
        EXCHANGES_DATA = arg
    elif opt == "--events":
        EVENTS_DATA = arg
    elif opt == "--do-smooth":
        DO_SMOOTH = True
    elif opt == "--do-unb-smooth":
        DO_UNBIASED_SMOOTH = True
    elif opt == "--do-filt":
        DO_FILT = True
    elif opt == "--do-hyper-smooth":
        DO_HYPER_SMOOTH = True
    elif opt == "--do-hyper-filt":
        DO_HYPER_FILT = True
    elif opt == "--do-hyper-unb-filt":
        DO_HYPER_UNB_FILT = True
    elif opt == "--trim-ts":
        TRIM_TS = [ int(t) for t in arg.split(',') ]
    elif opt == "--mcmc-skip":
        MCMC_SKIP = int(arg)
        if MCMC_SKIP < 1:
            raise ValueError("SKIP must be >0 in --mcmc-skip=SKIP")
    elif opt == "--ntraj":
        NTRAJ = int(arg)
    elif opt == "--perc":
        PERC_LIST = [int(p) for p in arg.split(',')]
    elif opt == '--do-post-pred':
        DO_POST_PRED = True
    elif opt == '--do-unb-post-pred':
        DO_UNB_POST_PRED = True
    elif opt == '--do-trim-var-diag':
        DO_TRIM_VAR_DIAG = True
    elif opt == '--chunk-size':
        CHUNK_SIZE = int(arg)
    elif opt == "--store-fig-dir":
        STORE_FIG_DIR = arg

def tstamp_print(msg, *args, **kwargs):
    tstamp = datetime.datetime.fromtimestamp(
        time.time()
    ).strftime('%Y-%m-%d %H:%M:%S')
    print(tstamp + " " + msg, *args, **kwargs)

def filter_tstamp_print(msg, *args, **kwargs):
    if VERBOSE:
        tstamp_print(msg, *args, **kwargs)

def filter_print(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

def store_figure(fig, fname):
    for fmat in STORE_FIG_FMATS:
        fig.savefig(fname+'.'+fmat, format=fmat, bbox_inches='tight');
        
if None in [DATA, POST_DATA]:
    full_usage()
    tstamp_print("ERROR: Options --data and --postprocess-data must be specified")
    sys.exit(3)

if STORE_FIG_DIR is not None:
    DFILE = DATA.split('/')[-1]
    if not os.path.exists(STORE_FIG_DIR + '/' + DFILE):
        os.makedirs(STORE_FIG_DIR + '/' + DFILE)
    STORE_FIG_DIR += '/' + DFILE +'/'

# Load data
with open(DATA, 'rb') as in_stream:
    stg = dill.load(in_stream)

# Load postprocess data
with open(POST_DATA, 'rb') as istr:
    data = dill.load(istr)

# Load hdf5 file
h5data = h5py.File(POST_DATA + '.hdf5', 'r')

# Load exchanges data
if EXCHANGES_DATA is not None:
    with open(EXCHANGES_DATA,'r') as datafile:
        dates, exchanges, variations = \
            np.loadtxt(datafile, skiprows=2, usecols=[0,1,2], delimiter=',',
                       unpack=True, converters={0: bytespdate2num('%m/%d/%y')})

if EVENTS_DATA is not None:
    with open(EVENTS_DATA,'r') as datafile:
        events_dates = \
            np.loadtxt(datafile, skiprows=1, usecols=[0], delimiter=',',
                       unpack=True, converters={0: bytespdate2num('%m/%d/%Y')})

# Restore data
target_distribution = stg.target_distribution
base_distribution = stg.base_distribution

dim = target_distribution.dim
nsteps = target_distribution.nsteps
nhyper = dim - nsteps
dimfilt = nhyper + 1
if EXCHANGES_DATA is None:
    tvec = np.arange(nsteps)
else:
    tvec = dates[:nsteps]
if EVENTS_DATA is None:
    events_dates = []
else:
    events_dates = [d for d in events_dates if d < tvec[-1]]
obs = target_distribution.observations

if CHUNK_SIZE is None:
    CHUNK_SIZE = nsteps

if target_distribution.is_mu_hyper:
    index_mu = target_distribution.index_mu
if target_distribution.is_sigma_hyper:
    index_sigma = target_distribution.index_sigma
if target_distribution.is_phi_hyper:
    index_phi = target_distribution.index_phi

def nicePlot(ax):
    coloraxes = 'gray'
    ax.spines['right'].set_visible(False) # Remove the right axis boundary
    ax.spines['top'].set_visible(False)  # Remove the top axis boundary
    ax.xaxis.set_ticks_position('bottom') # Set the x-ticks to only the bottom
    ax.yaxis.set_ticks_position('left') # Set the y-ticks to only the left
    ax.spines['bottom'].set_position(('axes',-0.04)) # Offset the bottom scale from the axis
    ax.spines['left'].set_position(('axes',-0.04))  # Offset the left scale from the axis
    ax.spines['left'].set_linewidth(.5)
    ax.spines['bottom'].set_linewidth(.5)
    ax.spines['bottom'].set_color(coloraxes)
    ax.spines['left'].set_color(coloraxes)
    ax.xaxis.label.set_color(coloraxes)
    ax.yaxis.label.set_color(coloraxes)
    ax.tick_params(axis='x', colors=coloraxes)
    ax.tick_params(axis='y', colors=coloraxes)
    ax.yaxis.label.set_size(18)
    ax.xaxis.label.set_size(18)
    ax.title.set_color(coloraxes)
    ax.title.set_size(16)

def plot_mean_percentile_traj(tvec, data1, data2=None, edates=None, ntraj=0, 
                              ylabel=None, title=None, c1='r', c2='k'):
    fig = plt.figure(figsize=FSIZE)
    if EXCHANGES_DATA is not None:
        plt.xlabel("day")
    else:
        plt.xlabel("time")
    if ylabel is not None:
        plt.ylabel(ylabel)
    if TITLES:
        plt.title(title)
    ax = fig.add_subplot(111)
    nicePlot(ax)
    ax.set_xlim(tvec[0], tvec[-1])
    ax.set_ylim(YLIM[0], YLIM[1])
    
    # First data series
    mean1 = np.mean(data1, axis=0)
    ax.plot(tvec, mean1, '-' + c1, linewidth=LW)
    for i, perc in enumerate(PERC_LIST):
        qlow = np.percentile(data1, 50. - perc/2, axis=0)
        qhigh = np.percentile(data1, 50. + perc/2, axis=0)
        ax.plot(tvec, qlow, PERC_STYLES[i] + c1, linewidth=LW)
        ax.plot(tvec, qhigh, PERC_STYLES[i] + c1, linewidth=LW)

    # Trajectories
    for i in range(ntraj):
        ax.plot(tvec, data1[i,:], '-k', linewidth=0.5, alpha=0.6)

    if data2 is not None:
        # Comparing second data series
        mean2 = np.mean(data2, axis=0)
        ax.plot(tvec, mean2, '-' + c2, linewidth=LW)
        for i, perc in enumerate(PERC_LIST):
            qlow = np.percentile(data2, 50. - perc/2, axis=0)
            qhigh = np.percentile(data2, 50. + perc/2, axis=0)
            ax.plot(tvec, qlow, PERC_STYLES[i] + c2, linewidth=LW)
            ax.plot(tvec, qhigh, PERC_STYLES[i] + c2, linewidth=LW)

    if EXCHANGES_DATA is not None:
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        fig.autofmt_xdate()
    if EVENTS_DATA is not None:
        for dt in edates:
            ax.plot([dt,dt], YLIM, '--k', linewidth=0.5, alpha=0.6)
            
    return fig

def plot_mean_percentile_traj_3d(data1, ts, data2=None, ntraj=0,
                                 ylabel=None, zlabel=None):
    fig = plt.figure(figsize=FSIZE)
    
    mean_1 = np.mean(data1, axis=0)
    q5_1 = np.percentile(data1, 5, axis=0)
    q25_1 = np.percentile(data1, 25, axis=0)
    q40_1 = np.percentile(data1, 40, axis=0)
    q60_1 = np.percentile(data1, 60, axis=0)
    q75_1 = np.percentile(data1, 75, axis=0)
    q95_1 = np.percentile(data1, 95, axis=0)

    ax = fig.add_subplot(111, projection='3d')
    # Mean and quantiles
    ax.plot(tvec, mean_1, zs=0, zdir='z', c='k')
    verts = []
    verts.append( list(zip(tvec, q40_1)) + list(zip(tvec[::-1], q60_1[::-1])) )
    poly = PolyCollection(verts, facecolor=['red'])
    poly.set_alpha(0.5)
    ax.add_collection3d(poly, zs=[0], zdir='z')
    verts = []
    verts.append( list(zip(tvec, q25_1)) + list(zip(tvec[::-1], q75_1[::-1])) )
    poly = PolyCollection(verts, facecolor=['red'])
    poly.set_alpha(0.3)
    ax.add_collection3d(poly, zs=[0], zdir='z')
    verts = []
    verts.append( list(zip(tvec, q5_1)) + list(zip(tvec[::-1], q95_1[::-1])) )
    poly = PolyCollection(verts, facecolor=['red'])
    poly.set_alpha(0.15)
    ax.add_collection3d(poly, zs=[0], zdir='z')
    miny = np.min(q5_1)
    maxy = np.max(q95_1)
    span = maxy-miny
    miny -= 0.1 * span
    maxy += 0.1 * span
    ax.set_ylim([miny, maxy])
    # Slices
    yy = np.linspace(miny,maxy,100)
    maxz = 0.
    for ii, tt in enumerate(ts):
        # Biased
        ss = data1[:,tt-1]
        kde = scistat.gaussian_kde(ss)
        zz = kde(yy)
        maxz = max(maxz, np.max(zz))
        plt.plot(yy, zz, zs=tvec[tt-1], zdir='x', c='k')
        # Unbiased
        if data2 is not None:
            kde = scistat.gaussian_kde(data2[ii][:])
            zz = kde(yy)
            maxz = max(maxz, np.max(zz))
            plt.plot(yy, zz, '--k', zs=tvec[tt-1], zdir='x') 
    ax.set_zlim([0, maxz*1.05])
    ax.set_xlim([tvec[0], tvec[-1]])
    ax.view_init(elev=20., azim=-120.)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    plt.tight_layout()

    if EXCHANGES_DATA is not None:
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        fig.autofmt_xdate()
    else:
        ax.set_xlabel('time')
    
    return fig
            
#--1--###### Plot: smoothing/posterior marginals timesteps #############
if DO_SMOOTH:
    print("\nPlotting smoothing/posterior marginals \n")
    tar_samp_smooth = h5data['trim-%d' % nsteps]['quadrature']['approx-target']['0']
    Xt_samp_smooth = tar_samp_smooth[:,nhyper:]
    start = 0
    i = 0
    while start < nsteps:
        stop = min(start + CHUNK_SIZE, nsteps)
        smps = Xt_samp_smooth[:,start:stop]
        tt = tvec[start:stop]
        et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
        fig = plot_mean_percentile_traj(
            tt, smps, ntraj=NTRAJ, edates=et,
            ylabel="$\pi_{" + STATE_VAR + "|Y_{0:N}}$",
            title="Posterior/Smoothing marginals")
        plt.show(False)

        if STORE_FIG_DIR is not None:
            store_figure(fig, STORE_FIG_DIR+'/'+ \
                         'smoothing-marginals-timesteps-ntraj-%d-chunk-%d' % (NTRAJ, i))
        start = stop
        i += 1

if DO_UNBIASED_SMOOTH: # Fast reading from h5 file
    print("\nLoading Metropolis samples \n")
    dset = h5data['trim-%d' % nsteps]\
           ['metropolis-independent-proposal-samples']['skip-%d' % MCMC_SKIP]['x']
    tar_unb_samp_smooth = np.zeros(dset.shape)
    for d in range(dset.shape[1]):
        print("Dimension %d/%d" % (d+1,dset.shape[1]))
        tar_unb_samp_smooth[:,d] = dset[:,d]
        
if DO_SMOOTH and DO_UNBIASED_SMOOTH:
    Xt_unb_samp_smooth = tar_unb_samp_smooth[:,nhyper:]
    start = 0
    i = 0
    while start < nsteps:
        stop = min(start + CHUNK_SIZE, nsteps)
        smps = Xt_samp_smooth[:,start:stop]
        unb_smps = Xt_unb_samp_smooth[:,start:stop]
        tt = tvec[start:stop]
        et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
        fig = plot_mean_percentile_traj(
            tt, smps, unb_smps, edates=et,
            # ylabel= r"$" + STATE_VAR + "$",
            ylabel="$\pi_{" + STATE_VAR + "|Y_{0:N}}$",
            title="Posterior/Smoothing marginals - vs. unbiased")
        plt.show(False)

        if STORE_FIG_DIR is not None:
            store_figure(fig, STORE_FIG_DIR+'/' + \
                         'smoothing-marginals-vs-unbiased-timesteps-chunk-%d' % i)
        start = stop
        i += 1
        
if DO_FILT or DO_HYPER_FILT or DO_HYPER_UNB_FILT:
    fdata = h5data['trim-%d' % nsteps]['filtering']
    nsamps = np.min(
        [ fdata['step-%i/quadrature/0' %i].shape[0]
          for i in range(nsteps) ])
    samp_filt = np.zeros((nsamps,dimfilt,nsteps))
    for n in range(nsteps):
        samp_filt[:,:,n] = fdata['step-%d/quadrature/0' % n][:nsamps,:]

#--2--###### Plot: filtering marginals timesteps #############
if DO_FILT:
    print("Plotting filtering marginals \n")
    Xt_samp_filt = samp_filt[:,-1,:]
    start = 0
    i = 0
    while start < nsteps:
        stop = min(start + CHUNK_SIZE, nsteps)
        smps = Xt_samp_filt[:,start:stop]
        tt = tvec[start:stop]
        et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
        fig = plot_mean_percentile_traj(
            tt, smps, ntraj=NTRAJ, edates=et,
            # ylabel=r"$" + STATE_VAR + "$",
            ylabel=r"$\pi_{" + STATE_VAR + "|Y_{0:t}}$",
            title='Filtering marginals', c1='b')
        plt.show(False)
        
        if STORE_FIG_DIR is not None:
            store_figure(fig, STORE_FIG_DIR+'/filtering-marginals-timesteps-chunk-%d' % i)

        start = stop
        i += 1

#--3--###### Plot: smoothing+filtering marginals timesteps #############
if DO_SMOOTH and DO_FILT:
    print("Plotting smoothing + filtering marginals \n")
    start = 0
    i = 0
    while start < nsteps:
        stop = min(start + CHUNK_SIZE, nsteps)
        smps1 = Xt_samp_smooth[:,start:stop]
        smps2 = Xt_samp_filt[:,start:stop]
        tt = tvec[start:stop]
        et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
        fig = plot_mean_percentile_traj(
            tt, smps1, smps2, edates=et,
            ylabel=r"$" + STATE_VAR + "$",
            title='Smoothing and filtering marginals', c2='b')
        plt.show(False)

        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-filtering-marginals-timesteps-chunk-%d' % i)
        start = stop
        i += 1

#--4--###### Plot: filtering marginals hyper-parameters #############
if DO_HYPER_FILT and nhyper>0:
    hyper_samp_filt = samp_filt[:,:nhyper,:]
    if target_distribution.is_sigma_hyper:
        hyper_samp_filt[:,index_sigma,:] = \
            target_distribution.sigma.evaluate( hyper_samp_filt[:,index_sigma,:] )
    if target_distribution.is_phi_hyper:
        hyper_samp_filt[:,index_phi,:] = \
            target_distribution.phi.evaluate( hyper_samp_filt[:,index_phi,:] )
    
    print("Plotting hyper-parameters filtering marginals \n")
    if target_distribution.is_mu_hyper:
        #Plot filtering marginals for mu
        mu_samp_filt = hyper_samp_filt[:,index_mu,:]
        start = 0
        i = 0
        while start < nsteps:
            stop = min(start + CHUNK_SIZE, nsteps)
            smps = mu_samp_filt[:,start:stop]
            tt = tvec[start:stop]
            et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
            fig = plot_mean_percentile_traj(
                tt, smps, ntraj=0, edates=et,
                ylabel="$\pi_{\mu|Y_{0:t}}$",
                title='Filtering marginals of $\mu$')
            plt.show(False)
            if STORE_FIG_DIR is not None:
                store_figure(
                    fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_mu-chunk-%d' % i)
            start = stop
            i += 1

    if target_distribution.is_sigma_hyper:
        #Plot filtering marginals for sigma
        sigma_samp_filt = hyper_samp_filt[:,index_sigma,:]
        start = 0
        i = 0
        while start < nsteps:
            stop = min(start + CHUNK_SIZE, nsteps)
            smps = sigma_samp_filt[:,start:stop]
            tt = tvec[start:stop]
            et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
            fig = plot_mean_percentile_traj(
                tt, smps, ntraj=0, edates=et,
                ylabel=r"$\pi_{\sigma|Y_{0:t}}$",
                title=r'Filtering marginals of $\sigma$')
            plt.show(False)
            if STORE_FIG_DIR is not None:
                store_figure(
                    fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_sigma-chunk-%d' % i)
            start = stop
            i += 1

    if target_distribution.is_phi_hyper:
        #Plot filtering marginals for phi
        phi_samp_filt = hyper_samp_filt[:,index_phi,:]
        start = 0
        i = 0
        while start < nsteps:
            stop = min(start + CHUNK_SIZE, nsteps)
            smps = phi_samp_filt[:,start:stop]
            tt = tvec[start:stop]
            et = [t for t in events_dates if tt[0] <= t <= tt[-1]]
            fig = plot_mean_percentile_traj(
                tt, smps, ntraj=0, edates=et,
                ylabel=r"$\pi_{\phi|Y_{0:t}}$",
                title=r'Filtering marginals of $\sigma$')
            plt.show(False)
            if STORE_FIG_DIR is not None:
                store_figure(
                    fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_phi-chunk-%d' % i)
            start = stop
            i += 1
        
if DO_HYPER_UNB_FILT and nhyper>0:
    tar_unb_samp_smooth_trim = []
    for t in TRIM_TS:
        h5root = h5data['trim-%d' % t]
        tar_unb_samp_smooth_trim.append(
            h5root['metropolis-independent-proposal-samples/skip-%d/x/' % MCMC_SKIP]
        )
    print("Plotting hyper-parameters filtering marginals vs. unbiased \n")
    if target_distribution.is_mu_hyper:
        # Plot filtering marginals for mu (3D)
        index_mu = target_distribution.index_mu
        mu_samp_filt = hyper_samp_filt[:,index_mu,:]
        mu_unb_samp_smooth = [ samp[:,index_mu] for samp in tar_unb_samp_smooth_trim ]
        ylabel = "" # r"$\mu\vert Y_{0:t}$"
        zlabel = r"$\pi_{\mu\vert Y_{0:t}}$"
        fig = plot_mean_percentile_traj_3d(
            mu_samp_filt, TRIM_TS, mu_unb_samp_smooth,
            ylabel=ylabel, zlabel=zlabel)
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_mu-3d')
            
    if target_distribution.is_sigma_hyper:
        # Plot filtering marginals for mu (3D)
        index_sigma = target_distribution.index_sigma
        sigma_samp_filt = hyper_samp_filt[:,index_sigma,:]
        sigma_unb_samp_smooth = [
            target_distribution.sigma.evaluate( samp[:,index_sigma] )
            for samp in tar_unb_samp_smooth_trim ]
        ylabel = "" # r"$\sigma\vert Y_{0:t}$"
        zlabel = r"$\pi_{\sigma\vert Y_{0:t}}$"
        fig = plot_mean_percentile_traj_3d(
            sigma_samp_filt, TRIM_TS, sigma_unb_samp_smooth,
            ylabel=ylabel, zlabel=zlabel)
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_sigma-3d')
            
    if target_distribution.is_phi_hyper:
        # Plot filtering marginals for mu (3D)
        index_phi = target_distribution.index_phi
        phi_samp_filt = hyper_samp_filt[:,index_phi,:]
        phi_unb_samp_smooth = [
            target_distribution.phi.evaluate( samp[:,index_phi] )
            for samp in tar_unb_samp_smooth_trim ]
        ylabel = "" # r"$\phi\vert Y_{0:t}$"
        zlabel = r"$\pi_{\phi\vert Y_{0:t}}$"
        fig = plot_mean_percentile_traj_3d(
            phi_samp_filt, TRIM_TS, phi_unb_samp_smooth,
            ylabel=ylabel, zlabel=zlabel)
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/filtering-marginals-timesteps_phi-3d')
            
#--4--###### Plot: smoothing/posterior marginals hyper-parameters #############
if DO_HYPER_SMOOTH and nhyper>0:
    tar_samp_smooth = h5data['trim-%d' % nsteps]['quadrature']['approx-target']['0']
    print("Plotting hyper-parameters smoothing marginals \n")
    if target_distribution.is_mu_hyper:
        mu_samp_smooth = tar_samp_smooth[:,index_mu]
        mu_min = np.min(mu_samp_smooth)
        mu_min = mu_min - .1*np.abs(mu_min)
        mu_max = np.max(mu_samp_smooth)
        mu_max = mu_max + .1*np.abs(mu_max)
        mu_kde = scistat.gaussian_kde(mu_samp_smooth)
        mu_xx = np.linspace(mu_min, mu_max, 10000)
        pdf_mu_xx = mu_kde(mu_xx)
        fig = plt.figure()
        plt.xlabel("$\mu$")
        plt.ylabel("$\pi_{\mu|Y_{0:N}}$")
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\mu$')
        plt.xlim(mu_min,mu_max)
        plt.plot(mu_xx, pdf_mu_xx, '-k',linewidth=1.0)
        plt.show(False)

        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-mu') 

    if target_distribution.is_sigma_hyper:
        Xsigma_samp_smooth =  tar_samp_smooth[:,index_sigma]
        # Do the kde on the reference variable and then push forward through F_sigma.
        Xsigma_kde = scistat.gaussian_kde(Xsigma_samp_smooth) 
        Xsigma_min = np.min(Xsigma_samp_smooth)
        Xsigma_min = Xsigma_min - .1*np.abs(Xsigma_min)
        Xsigma_max = np.max(Xsigma_samp_smooth)
        Xsigma_max = Xsigma_max + .1*np.abs(Xsigma_max)
        Xsigma_xx = np.linspace(Xsigma_min, Xsigma_max, 10000)
        FXsigma_xx = target_distribution.sigma.evaluate( Xsigma_xx )
        grad_FXsigma_xx = target_distribution.sigma.grad_x( Xsigma_xx )
        pdf_sigma_FXsigma = Xsigma_kde(Xsigma_xx)/grad_FXsigma_xx
        fig = plt.figure()
        plt.xlabel("$\sigma$")
        plt.ylabel("$\pi_{\sigma|Y_{0:N}}$")
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\sigma$')
        sigma_max = np.max(FXsigma_xx)
        ax.set_xlim(0.,sigma_max)
        ax.plot(FXsigma_xx, pdf_sigma_FXsigma, '-k',linewidth=1.0)
        plt.show(False)

        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-sigma') 

    if target_distribution.is_phi_hyper:
        Xphi_samp_smooth =  target_distribution.phi.evaluate(
            tar_samp_smooth[:,index_phi])
        Xphi_kde = scistat.gaussian_kde(Xphi_samp_smooth)
        Xphi_min = np.min(Xphi_samp_smooth)
        Xphi_max = np.max(Xphi_samp_smooth)
        Xphi_xx = np.linspace(Xphi_min, Xphi_max, 1000)
        pdf_phi = Xphi_kde(Xphi_xx)
        fig = plt.figure()
        plt.ylabel("$\pi_{\phi|Y_{0:N}}$")
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\phi$')
        plt.plot(Xphi_xx, pdf_phi, '-k',linewidth=1.0, label='Transport Map')
        plt.legend(loc='best')
        plt.show(False)
        
        # Xphi_samp_smooth =  tar_samp_smooth[:,index_phi]
        # Xphi_kde = scistat.gaussian_kde(Xphi_samp_smooth)
        # #Do the kde on the reference variable and then push forward through F_phi.
        # Xphi_min = np.min(Xphi_samp_smooth)
        # Xphi_min = Xphi_min # - .1*np.abs(Xphi_min)
        # Xphi_max = np.max(Xphi_samp_smooth)
        # Xphi_max = Xphi_max # + .1*np.abs(Xphi_max)
        # Xphi_xx = np.linspace(Xphi_min, Xphi_max, 10000)
        # FXphi_xx = target_distribution.phi.evaluate( Xphi_xx )
        # grad_FXphi_xx = target_distribution.phi.grad_x( Xphi_xx )
        # pdf_phi_FXphi = Xphi_kde(Xphi_xx)/grad_FXphi_xx
        # fig = plt.figure()
        # plt.xlabel("$\phi$")
        # plt.ylabel("$\pi_{\phi|Y_{0:N}}$")
        # if TITLES:
        #     plt.title('Posterior/smoothing marginals of $\phi$')
        # phi_min = np.min(FXphi_xx)
        # plt.xlim(phi_min,1.)
        # plt.plot(FXphi_xx, pdf_phi_FXphi, '-k',linewidth=1.0)
        # plt.show(False)
        # #phi_samp_smooth = target_distribution.phi.evaluate( Xphi_samp_smooth )

        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-phi')

    print("Plotting posterior/smoothing marginals \n")
    hyper_samp_smooth = tar_samp_smooth[:,:nhyper].copy()
    if target_distribution.is_sigma_hyper:
        hyper_samp_smooth[:,index_sigma] = target_distribution.sigma.evaluate(
            hyper_samp_smooth[:,index_sigma] )
    if target_distribution.is_phi_hyper:
        hyper_samp_smooth[:,index_phi] = target_distribution.phi.evaluate(
            hyper_samp_smooth[:,index_phi] )
    (fig, handles,_,_,_) = DIAG.plotAlignedMarginals(
        hyper_samp_smooth, show_axis=True )
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/smoothing-marginals-hyper')

if DO_HYPER_SMOOTH and DO_UNBIASED_SMOOTH and nhyper > 0:
    print("Plotting hyper-parameters unbiased smoothing marginals \n")
    hyper_unb_samp_smooth = tar_unb_samp_smooth[:,:nhyper].copy()
    if target_distribution.is_sigma_hyper:
        hyper_unb_samp_smooth[:,index_sigma] = target_distribution.sigma.evaluate(
            hyper_unb_samp_smooth[:,index_sigma] )
    if target_distribution.is_phi_hyper:
        hyper_unb_samp_smooth[:,index_phi] = target_distribution.phi.evaluate(
            hyper_unb_samp_smooth[:,index_phi] )
    # (fig, handles,_,_,_) = DIAG.plotAlignedMarginals(
    #     hyper_unb_samp_smooth, show_axis=True )
    (fig, handles,_,_,_) = DIAG.plotAlignedMarginals(
        hyper_samp_smooth, hyper_unb_samp_smooth, show_axis=True )
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/unbiased-smoothing-marginals-hyper')

    
    print("Plotting hyper-parameters smoothing marginals vs. unbiased \n")
    if target_distribution.is_mu_hyper:
        mu_samp_smooth = tar_samp_smooth[:,index_mu]
        mu_unb_samp_smooth = tar_unb_samp_smooth[:,index_mu]
        mu_min = min(np.min(mu_samp_smooth), np.min(mu_unb_samp_smooth))
        mu_min = mu_min - .1*np.abs(mu_min)
        mu_max = max(np.max(mu_samp_smooth), np.max(mu_unb_samp_smooth))
        mu_max = mu_max + .1*np.abs(mu_max)
        mu_kde = scistat.gaussian_kde(mu_samp_smooth)
        mu_unb_kde = scistat.gaussian_kde(mu_unb_samp_smooth)
        mu_xx = np.linspace(mu_min, mu_max, 10000)
        pdf_mu_xx = mu_kde(mu_xx)
        pdf_mu_unb_xx = mu_unb_kde(mu_xx)
        fig = plt.figure()
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\mu$')
        plt.ylabel("$\pi_{\mu|Y_{0:N}}$")
        plt.xlim(mu_min,mu_max)
        plt.plot(mu_xx, pdf_mu_xx, '-k',linewidth=1.0, label='Transport map')
        plt.plot(mu_xx, pdf_mu_unb_xx, '--k',linewidth=1.0, label='MCMC')
        plt.legend(loc='best')
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-mu-vs-unb') 

    if target_distribution.is_sigma_hyper:
        Xsigma_samp_smooth =  tar_samp_smooth[:,index_sigma]
        Xsigma_unb_samp_smooth = tar_unb_samp_smooth[:,index_sigma]
        # Do the kde on the reference variable and then push forward through F_sigma.
        Xsigma_kde = scistat.gaussian_kde(Xsigma_samp_smooth)
        Xsigma_unb_kde = scistat.gaussian_kde(Xsigma_unb_samp_smooth) 
        Xsigma_min = min(np.min(Xsigma_samp_smooth), np.min(Xsigma_unb_samp_smooth))
        Xsigma_min = Xsigma_min - .1*np.abs(Xsigma_min)
        Xsigma_max = max(np.max(Xsigma_samp_smooth), np.max(Xsigma_unb_samp_smooth))
        Xsigma_max = Xsigma_max + .1*np.abs(Xsigma_max)
        Xsigma_xx = np.linspace(Xsigma_min, Xsigma_max, 10000)
        FXsigma_xx = target_distribution.sigma.evaluate( Xsigma_xx )
        grad_FXsigma_xx = target_distribution.sigma.grad_x( Xsigma_xx )
        pdf_sigma_FXsigma = Xsigma_kde(Xsigma_xx)/grad_FXsigma_xx
        pdf_unb_sigma_FXsigma = Xsigma_unb_kde(Xsigma_xx)/grad_FXsigma_xx
        fig = plt.figure()
        plt.ylabel("$\pi_{\sigma|Y_{0:N}}$")
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\sigma$')
        sigma_max = np.max(FXsigma_xx)
        plt.xlim(0.,sigma_max)
        plt.plot(FXsigma_xx, pdf_sigma_FXsigma, '-k',linewidth=1.0, label='Transport Map')
        plt.plot(FXsigma_xx, pdf_unb_sigma_FXsigma, '--k',
                 linewidth=1.0, label='MCMC')
        plt.legend(loc='best')
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-sigma-vs-unb') 

    if target_distribution.is_phi_hyper:
        Xphi_samp_smooth =  target_distribution.phi.evaluate(
            tar_samp_smooth[:,index_phi])
        Xphi_unb_samp_smooth =  target_distribution.phi.evaluate(
            tar_unb_samp_smooth[:,index_phi])
        Xphi_kde = scistat.gaussian_kde(Xphi_samp_smooth)
        Xphi_unb_kde = scistat.gaussian_kde(Xphi_unb_samp_smooth)
        Xphi_min = min(np.min(Xphi_samp_smooth), np.min(Xphi_unb_samp_smooth))
        Xphi_min = Xphi_min # - .1*np.abs(Xphi_min)
        Xphi_max = max(np.max(Xphi_samp_smooth), np.max(Xphi_unb_samp_smooth))
        Xphi_max = Xphi_max # + .1*np.abs(Xphi_max)
        Xphi_xx = np.linspace(Xphi_min, Xphi_max, 1000)
        pdf_phi = Xphi_kde(Xphi_xx)
        pdf_unb_phi = Xphi_unb_kde(Xphi_xx)
        fig = plt.figure()
        plt.ylabel("$\pi_{\phi|Y_{0:N}}$")
        if TITLES:
            plt.title('Posterior/smoothing marginals of $\phi$')
        plt.plot(Xphi_xx, pdf_phi, '-k',linewidth=1.0, label='Transport Map')
        plt.plot(Xphi_xx, pdf_unb_phi, '--k',linewidth=1.0, label='MCMC')
        plt.legend(loc='best')
        plt.show(False)
        if STORE_FIG_DIR is not None:
            store_figure(
                fig, STORE_FIG_DIR+ '/smoothing-marginals-phi-vs-unb')
        
        # Xphi_samp_smooth =  tar_samp_smooth[:,index_phi]
        # Xphi_unb_samp_smooth =  tar_unb_samp_smooth[:,index_phi]
        # #Do the kde on the reference variable and then push forward through F_phi.
        # Xphi_kde = scistat.gaussian_kde(Xphi_samp_smooth)
        # Xphi_unb_kde = scistat.gaussian_kde(Xphi_unb_samp_smooth) 
        # Xphi_min = min(np.min(Xphi_samp_smooth), np.min(Xphi_unb_samp_smooth))
        # Xphi_min = Xphi_min # - .1*np.abs(Xphi_min)
        # Xphi_max = max(np.max(Xphi_samp_smooth), np.max(Xphi_unb_samp_smooth))
        # Xphi_max = Xphi_max # + .1*np.abs(Xphi_max)
        # Xphi_xx = np.linspace(Xphi_min, Xphi_max, 1000)
        # FXphi_xx = target_distribution.phi.evaluate( Xphi_xx )
        # grad_FXphi_xx = target_distribution.phi.grad_x( Xphi_xx )
        # pdf_phi_FXphi = Xphi_kde(Xphi_xx)/grad_FXphi_xx
        # pdf_unb_phi_FXphi = Xphi_unb_kde(Xphi_xx)/grad_FXphi_xx
        # fig = plt.figure()
        # plt.ylabel("$\pi_{\phi|Y_{0:N}}$")
        # if TITLES:
        #     plt.title('Posterior/smoothing marginals of $\phi$')
        # phi_min = np.min(FXphi_xx)
        # plt.plot(FXphi_xx, pdf_phi_FXphi, '-k',linewidth=1.0, label='Transport Map')
        # plt.plot(FXphi_xx, pdf_unb_phi_FXphi, '--k',linewidth=1.0, label='MCMC')
        # plt.legend(loc='best')
        # plt.show(False)
        # #phi_samp_smooth = target_distribution.phi.evaluate( Xphi_samp_smooth )
        # if STORE_FIG_DIR is not None:
        #     store_figure(
        #         fig, STORE_FIG_DIR+ '/smoothing-marginals-phi-vs-unb')

#--7--###### Plot: posterior data predictive #############
def plot_post_pred(obs, data1, data2=None, edates=None, ylabel=None, title=None):
    fig = plt.figure(figsize=FSIZE)
    ax = fig.add_subplot(111)
    nicePlot(ax)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if TITLES:
        plt.title(title)
    
    q5_1 = np.percentile(data1, 5, axis=0)
    q25_1 = np.percentile(data1, 25, axis=0)
    q40_1 = np.percentile(data1, 40, axis=0)
    q60_1 = np.percentile(data1, 60, axis=0)
    q75_1 = np.percentile(data1, 75, axis=0)
    q95_1 = np.percentile(data1, 95, axis=0)
    ax.set_xlim(tvec[0],tvec[-1])
    ax.scatter(tvec,obs,s=0.5,c='k',label="data")
    ax.fill_between(tvec, q40_1, q60_1, color="r", alpha=0.6)
    ax.fill_between(tvec, q25_1, q75_1, color="r", alpha=0.3)
    ax.fill_between(tvec, q5_1, q95_1, color="r", alpha=0.1)

    if data2 is not None:
        q5_2 = np.percentile(data2, 5, axis=0)
        q25_2 = np.percentile(data2, 25, axis=0)
        q40_2 = np.percentile(data2, 40, axis=0)
        q60_2 = np.percentile(data2, 60, axis=0)
        q75_2 = np.percentile(data2, 75, axis=0)
        q95_2 = np.percentile(data2, 95, axis=0)
        ax.fill_between(tvec, q40_2, q60_2, color="b", alpha=0.6)
        ax.fill_between(tvec, q25_2, q75_2, color="b", alpha=0.3)
        ax.fill_between(tvec, q5_2, q95_2, color="b", alpha=0.1)

    if EXCHANGES_DATA is not None:
        ax.set_xlabel("day")
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
        fig.autofmt_xdate()
    else:
        ax.set_xlabel("time")
    if EVENTS_DATA is not None:
        for dt in edates:
            ax.plot([dt,dt], YLIM, '--k')
    
    ax.legend(loc='best')
    return fig

def plot_qq_post_pred(obs, data, ylabel=None, xlabel=None, title=None):
    nprc = 21
    prclst = np.linspace(0,100,nprc)

    prc = np.zeros((nprc,data.shape[1]))
    for n, p in enumerate(prclst):
        prc[n,:] = np.percentile(data, p, axis=0)

    nobs_in_prc = np.zeros(nprc)
    for n, p in enumerate(prclst):
        nobs_in_prc[n] = sum( obs < prc[n,:] )
        
    # qq-plot and identity tendency line
    fig = plt.figure()
    plt.scatter(prclst/100.,
                nobs_in_prc/float(len(obs)), s=5, c='k')
    plt.plot([0,1],[0,1],'r')
    if ylabel is not None:
        plt.ylabel(ylabel)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if TITLES:
        plt.title(title)

    # # Perform PCA
    # P = np.vstack((p1,p2)).T
    # mP = np.mean(P,axis=0)
    # plt.scatter(mP[0],mP[1], s=15, c='k', marker='s')
    # X = P - mP
    # V = np.dot(X.T,X)
    # w,v = npla.eig(V)
    # srtidxs = np.argsort(w)[::-1]
    # w = w[srtidxs]
    # v = v[:,srtidxs]
    # v0 = v[:,0]
    # v1 = v[:,1]
    # yy = mP[1] + v0[1]/v0[0] * (xx - mP[0])
    # prjv1 = np.outer(v1,v1)
    # res = np.dot(prjv1, X.T).T
    # stdres = np.std(npla.norm(res,axis=1))
    # xy = np.vstack( (xx,yy) )
    # xyp = xy + 1.96 * stdres * v1[:,np.newaxis]
    # xym = xy - 1.96 * stdres * v1[:,np.newaxis]
    # # Plot PCA and 95% confidence interval
    # plt.plot(xx, yy,'k')
    # plt.plot(xyp[0,:],xyp[1,:],'--k')
    # plt.plot(xym[0,:],xym[1,:],'--k')
    return fig
    
if DO_POST_PRED:
    tar_samp_smooth = h5data['trim-%d' % nsteps]['quadrature']['approx-target']['0']
    Xt_samp_smooth = tar_samp_smooth[:,nhyper:]
    noise_samples = npr.randn(Xt_samp_smooth.shape[0],Xt_samp_smooth.shape[1])
    Ysmooth_samples = noise_samples*np.exp(.5*Xt_samp_smooth)
    print("Plotting posterior predictive \n")
    fig = plot_post_pred(
        obs, Ysmooth_samples, ylabel="$\pi_{Y_y|Y_{0:N}}$",
        title="Data Posterior/Smoothing marginals (posterior predictive)")
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/posterior-data-predictive')

    fig = plot_qq_post_pred(obs, Ysmooth_samples,
                            xlabel='quantile', ylabel='observations',
                            title='qq-plot')
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR + '/qq-plot-posterior-data-predictive')

if DO_UNB_POST_PRED:
    Xt_samp_smooth = tar_unb_samp_smooth[:,nhyper:]
    noise_samples = npr.randn(Xt_samp_smooth.shape[0],Xt_samp_smooth.shape[1])
    unb_Ysmooth_samples = noise_samples*np.exp(.5*Xt_samp_smooth)
    print("Plotting unbiased posterior predictive \n")
    fig = plot_post_pred(
        obs, unb_Ysmooth_samples, ylabel="$\pi_{Y_y|Y_{0:N}}$",
        title="Data Posterior/Smoothing marginals (posterior predictive)")
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/posterior-data-predictive-unbiased')

    fig = plot_qq_post_pred(obs, unb_Ysmooth_samples,
                            xlabel='quantile', ylabel='observations',
                            title='qq-plot')
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR + '/unb-qq-plot-posterior-data-predictive')

if DO_POST_PRED and DO_UNB_POST_PRED:
    print("Plotting posterior predictive vs. unbiased posterior predictive\n")
    fig = plot_post_pred(
        obs, Ysmooth_samples, unb_Ysmooth_samples,
        ylabel="$\pi_{Y_y|Y_{0:N}}$",
        title="Data Posterior/Smoothing marginals (posterior predictive)")
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/posterior-data-predictive-vs-unbiased')

if DO_TRIM_VAR_DIAG:
    var_diag_list = []
    for t in TRIM_TS:
        h5root = h5data['trim-%d' % t]
        vals = h5root['vals_var_diag']['exact-base']['0']
        vals_d1 = vals['vals_d1'][:]
        vals_d2 = vals['vals_d2'][:]
        N = len(vals_d1)
        w = np.ones(N)/float(N)
        var_diag_list.append(
            DIAG.variance_approx_kl(
                None, None, vals_d1=vals_d1, vals_d2=vals_d2, w=w) )
    fig = plt.figure()
    ax = fig.add_subplot(111)
    nicePlot(ax)
    ax.semilogy(TRIM_TS, var_diag_list, '-ok')
    ax.grid(True)
    ax.set_ylabel(r"$\mathcal{D}_{\rm KL}(\rho \Vert T^\sharp \pi)$")
    ax.set_xlabel("time")
    plt.show(False)
    if STORE_FIG_DIR is not None:
        store_figure(
            fig, STORE_FIG_DIR+ '/var-diag-evolution')