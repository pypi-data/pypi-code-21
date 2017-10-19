#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''signals.py - Waqas Bhatti (wbhatti@astro.princeton.edu) - Jan 2017

Contains functions to deal with masking and removing periodic signals in light
curves.

'''


import logging
from datetime import datetime
from traceback import format_exc
from time import time as unixtime
import os.path

from numpy import nan as npnan, sum as npsum, abs as npabs, \
    roll as nproll, isfinite as npisfinite, std as npstd, \
    sign as npsign, sqrt as npsqrt, median as npmedian, \
    array as nparray, percentile as nppercentile, \
    polyfit as nppolyfit, var as npvar, max as npmax, min as npmin, \
    log10 as nplog10, arange as nparange, pi as MPI, floor as npfloor, \
    argsort as npargsort, cos as npcos, sin as npsin, tan as nptan, \
    where as npwhere, linspace as nplinspace, \
    zeros_like as npzeros_like, full_like as npfull_like, all as npall, \
    correlate as npcorrelate

import os
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

try:
    from cStringIO import StringIO as strio
except:
    from io import BytesIO as strio


###################
## LOCAL IMPORTS ##
###################

from ..periodbase.zgls import pgen_lsp
from .lcfit import _fourier_func, fourier_fit_magseries, spline_fit_magseries
from ..lcmath import sigclip_magseries


#############
## LOGGING ##
#############

# setup a logger
LOGGER = None

def set_logger_parent(parent_name):
    globals()['LOGGER'] = logging.getLogger('%s.varbase.signals' % parent_name)

def LOGDEBUG(message):
    if LOGGER:
        LOGGER.debug(message)
    elif DEBUG:
        print('%sZ [DBUG]: %s' % (datetime.utcnow().isoformat(), message))

def LOGINFO(message):
    if LOGGER:
        LOGGER.info(message)
    else:
        print('%sZ [INFO]: %s' % (datetime.utcnow().isoformat(), message))

def LOGERROR(message):
    if LOGGER:
        LOGGER.error(message)
    else:
        print('%sZ [ERR!]: %s' % (datetime.utcnow().isoformat(), message))

def LOGWARNING(message):
    if LOGGER:
        LOGGER.warning(message)
    else:
        print('%sZ [WRN!]: %s' % (datetime.utcnow().isoformat(), message))

def LOGEXCEPTION(message):
    if LOGGER:
        LOGGER.exception(message)
    else:
        print(
            '%sZ [EXC!]: %s\nexception was: %s' % (
                datetime.utcnow().isoformat(),
                message, format_exc()
                )
            )


################################################
## REMOVING SIGNALS FROM MAGNITUDE TIMESERIES ##
################################################

def prewhiten_magseries(times, mags, errs,
                        whitenperiod,
                        whitenparams,
                        sigclip=3.0,
                        magsarefluxes=False,
                        plotfit=None,
                        plotfitphasedlconly=True,
                        rescaletomedian=True):
    '''Removes a periodic sinusoidal signal generated using whitenparams from
    the input magnitude time series.

    whitenparams are the Fourier amplitude and phase coefficients:

    [ampl_1, ampl_2, ampl_3, ..., ampl_X,
     pha_1, pha_2, pha_3, ..., pha_X]

    where X is the Fourier order. These are usually the output of a previous
    Fourier fit to the light curve (from varbase.lcfit.fourier_fit_magseries for
    example).

    if rescaletomedian is True, then we add back the constant median term of the
    magnitudes to the final pre-whitened mag series.

    '''

    stimes, smags, serrs = sigclip_magseries(times, mags, errs,
                                             sigclip=sigclip,
                                             magsarefluxes=magsarefluxes)

    median_mag = npmedian(smags)


    # phase the mag series using the given period and epoch = min(stimes)
    mintime = npmin(stimes)

    # calculate the unsorted phase, then sort it
    iphase = (
        (stimes - mintime)/whitenperiod -
        npfloor((stimes - mintime)/whitenperiod)
    )
    phasesortind = npargsort(iphase)

    # these are the final quantities to use for the Fourier fits
    phase = iphase[phasesortind]
    pmags = smags[phasesortind]
    perrs = serrs[phasesortind]

    # get the times sorted in phase order (useful to get the fit mag minimum
    # with respect to phase -- the light curve minimum)
    ptimes = stimes[phasesortind]

    # get the Fourier order
    fourierorder = int(len(whitenparams)/2)

    # now subtract the harmonic series from the phased LC
    # these are still in phase order
    wmags = pmags - _fourier_func(whitenparams, phase, pmags)

    # resort everything by time order
    wtimeorder = npargsort(ptimes)
    wtimes = ptimes[wtimeorder]
    wphase = phase[wtimeorder]
    wmags = wmags[wtimeorder]
    werrs = perrs[wtimeorder]

    if rescaletomedian:
        wmags = wmags + median_mag

    # prepare the returndict
    returndict = {'wtimes':wtimes, # these are in phase order
                  'wphase':wphase,
                  'wmags':wmags,
                  'werrs':werrs,
                  'whitenparams':whitenparams,
                  'whitenperiod':whitenperiod}


    # make the fit plot if required
    if plotfit and isinstance(plotfit, str) or isinstance(plotfit, strio):

        if plotfitphasedlconly:
            plt.figure(figsize=(10,4.8))
        else:
            plt.figure(figsize=(16,9.6))

        if plotfitphasedlconly:

            # phased series before whitening
            plt.subplot(121)
            plt.plot(phase,pmags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC before pre-whitening')

            # phased series after whitening
            plt.subplot(122)
            plt.plot(wphase,wmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC after pre-whitening')

        else:

            # time series before whitening
            plt.subplot(221)
            plt.plot(stimes,smags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('JD')
            plt.title('LC before pre-whitening')

            # time series after whitening
            plt.subplot(222)
            plt.plot(wtimes,wmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('JD')
            plt.title('LC after pre-whitening with period: %.6f' % whitenperiod)

            # phased series before whitening
            plt.subplot(223)
            plt.plot(phase,pmags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC before pre-whitening')

            # phased series after whitening
            plt.subplot(224)
            plt.plot(wphase,wmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC after pre-whitening')

        plt.tight_layout()
        plt.savefig(plotfit, format='png', pad_inches=0.0)
        plt.close()

        if isinstance(plotfit, str) or isinstance(plotfit, strio):
            returndict['fitplotfile'] = plotfit

    return returndict



def gls_prewhiten(times, mags, errs,
                  startp=None, endp=None,
                  autofreq=True,
                  sigclip=30.0,
                  magsarefluxes=False,
                  stepsize=1.0e-4,
                  fourierorder=3, # 3rd order series to start with
                  initfparams=None,
                  nbestpeaks=5,
                  nworkers=4,
                  plotfits=None):
    '''Iterative pre-whitening of a magnitude series using the L-S periodogram.

    This finds the best period, fits a fourier series with the best period, then
    whitens the time series with the best period, and repeats until nbestpeaks
    are done.

    '''
    stimes, smags, errs = sigclip_magseries(times, mags, errs,
                                            sigclip=sigclip,
                                            magsarefluxes=magsarefluxes)


    # now start the cycle by doing an LSP on the initial timeseries
    lsp = pgen_lsp(stimes, smags, serrs,
                   magsarefluxes=magsarefluxes,
                   startp=startp, endp=endp,
                   autofreq=autofreq,
                   sigclip=sigclip,
                   stepsize=stepsize,
                   nworkers=nworkers)
    wperiod = lsp['bestperiod']
    fseries = fourier_fit_magseries(stimes, smags, serrs, wperiod,
                                    fourierorder=fourierorder,
                                    fourierparams=initfparams,
                                    sigclip=sigclip,
                                    magsarefluxes=magsarefluxes)
    ffitparams = fseries['fitinfo']['finalparams']

    # this is the initial whitened series using the initial fourier fit and
    # initial found best period
    wseries = prewhiten_magseries(stimes,
                                  smags,
                                  serrs,
                                  wperiod,
                                  ffitparams,
                                  sigclip=sigclip,
                                  magsarefluxes=magsarefluxes)

    LOGINFO('round %s: period = %.6f' % (1, wperiod))
    bestperiods = [wperiod]

    if plotfits and isinstance(plotfits, str):

        plt.figure(figsize=(8,6*nbestpeaks))

        nplots = nbestpeaks + 1

        plt.subplot(nplots,1,1)
        plt.errorbar(stimes,smags,fmt='bo',yerr=serrs,
                     markersize=2.0,capsize=0)
        ymin, ymax = plt.ylim()

        if not magsarefluxes:
            plt.ylim(ymax,ymin)
            plt.ylabel('magnitude')
        else:
            plt.ylim(ymin,ymax)
            plt.ylabel('magnitude')

        plt.xlabel('JD')
        plt.title('LC before whitening')

        plt.subplot(nplots,1,2)
        plt.errorbar(wseries['wtimes'],wseries['wmags'],
                     fmt='bo',yerr=wseries['werrs'],
                     markersize=2.0,capsize=0)
        ymin, ymax = plt.ylim()
        if not magsarefluxes:
            plt.ylim(ymax,ymin)
            plt.ylabel('magnitude')
        else:
            plt.ylim(ymin,ymax)
            plt.ylabel('magnitude')
        plt.xlabel('JD')
        plt.title('LC after whitening with period: %.6f' % wperiod)

    # now go through the rest of the cycles
    for fitind in range(nbestpeaks-1):

        wtimes, wmags, werrs = (wseries['wtimes'],
                                wseries['wmags'],
                                wseries['werrs'])

        wlsp = pgen_lsp(wtimes, wmags, werrs,
                        magsarefluxes=magsarefluxes,
                        startp=startp,
                        endp=endp,
                        autofreq=autofreq,
                        sigclip=sigclip,
                        stepsize=stepsize,
                        nworkers=nworkers)
        wperiod = wlsp['bestperiod']
        wfseries = fourier_fit_magseries(wtimes, wmags, werrs, wperiod,
                                         fourierorder=fourierorder,
                                         fourierparams=initfparams,
                                         magsarefluxes=magsarefluxes,
                                         sigclip=sigclip)
        wffitparams = wfseries['fitinfo']['finalparams']
        wseries = prewhiten_magseries(wtimes, wmags, werrs,
                                      wperiod,
                                      wffitparams,
                                      magsarefluxes=magsarefluxes,
                                      sigclip=sigclip)

        LOGINFO('round %s: period = %.6f' % (fitind+2, wperiod))
        bestperiods.append(wperiod)

        if plotfits and isinstance(plotfits, str):

            plt.subplot(nplots,1,fitind+3)
            plt.errorbar(wtimes,wmags,fmt='bo',yerr=werrs,
                         markersize=2.0,capsize=0)
            ymin, ymax = plt.ylim()
            if not magsarefluxes:
                plt.ylim(ymax,ymin)
                plt.ylabel('magnitude')
            else:
                plt.ylim(ymin,ymax)
                plt.ylabel('magnitude')
            plt.xlabel('JD')
            plt.title('LC after whitening with period: %.6f' % wperiod)


    if plotfits and isinstance(plotfits, str):

        plt.subplots_adjust(hspace=0.3,top=0.9)
        plt.savefig(plotfits, bbox_inches='tight')
        plt.close()
        return bestperiods, os.path.abspath(plotfits)

    else:

        return bestperiods



def mask_signal(times, mags, errs,
                signalperiod,
                signalepoch,
                magsarefluxes=False,
                maskphases=[0,0,0.5,1.0],
                maskphaselength=0.1,
                plotfit=None,
                plotfitphasedlconly=True,
                sigclip=30.0):
    '''This removes repeating signals in the magnitude time series.

    Useful for masking transit signals in light curves to search for other
    variability.

    '''

    stimes, smags, serrs = sigclip_magseries(times, mags, errs,
                                             sigclip=sigclip,
                                             magsarefluxes=magsarefluxes)


    # now phase the light curve using the period and epoch provided
    phases = (
        (stimes - signalepoch)/signalperiod -
        npfloor((stimes - signalepoch)/signalperiod)
    )

    # mask the requested phases using the mask length (in phase units)
    # this gets all the masks into one array
    masks = nparray([(npabs(phases - x) > maskphaselength)
                     for x in maskphases])
    # this flattens the masks to a single array for all combinations
    masks = npall(masks,axis=0)

    # apply the mask to the times, mags, and errs
    mphases = phases[masks]
    mtimes = stimes[masks]
    mmags = smags[masks]
    merrs = serrs[masks]

    returndict = {'mphases':mphases,
                  'mtimes':mtimes,
                  'mmags':mmags,
                  'merrs':merrs}

    # make the fit plot if required
    if plotfit and isinstance(plotfit, str) or isinstance(plotfit, strio):

        if plotfitphasedlconly:
            plt.figure(figsize=(10,4.8))
        else:
            plt.figure(figsize=(16,9.6))

        if plotfitphasedlconly:

            # phased series before whitening
            plt.subplot(121)
            plt.plot(phases,smags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC before signal masking')

            # phased series after whitening
            plt.subplot(122)
            plt.plot(mphases,mmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC after signal masking')

        else:

            # time series before whitening
            plt.subplot(221)
            plt.plot(stimes,smags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('JD')
            plt.title('LC before signal masking')

            # time series after whitening
            plt.subplot(222)
            plt.plot(mtimes,mmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('JD')
            plt.title('LC after signal masking')

            # phased series before whitening
            plt.subplot(223)
            plt.plot(phases,smags,
                     marker='.',
                     color='k',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC before signal masking')

            # phased series after whitening
            plt.subplot(224)
            plt.plot(mphases,mmags,
                     marker='.',
                     color='g',
                     linestyle='None',
                     markersize=2.0,
                     markeredgewidth=0)

            if not magsarefluxes:
                plt.gca().invert_yaxis()
                plt.ylabel('magnitude')
            else:
                plt.ylabel('fluxes')

            plt.xlabel('phase')
            plt.title('phased LC after signal masking')

        plt.tight_layout()
        plt.savefig(plotfit, format='png', pad_inches=0.0)
        plt.close()

        if isinstance(plotfit, str) or isinstance(plotfit, strio):
            returndict['fitplotfile'] = plotfit


    return returndict
