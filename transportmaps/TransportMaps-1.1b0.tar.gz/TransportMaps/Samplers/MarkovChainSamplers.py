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

import itertools
import numpy as np
import scipy.stats as stats

from TransportMaps.External import PYHMC_SUPPORT
from TransportMaps.Misc import mpi_eval
from TransportMaps.Distributions.DistributionBase import ConditionalDistribution
from TransportMaps.Samplers.SamplerBase import *

if PYHMC_SUPPORT:
    import pyhmc

nax = np.newaxis

__all__ = ['MetropolisHastingsIndependentProposalsSampler',
           'MetropolisHastingsSampler',
           'MetropolisHastingsWithinGibbsSampler',
           'HamiltonianMonteCarloSampler']

class MetropolisHastingsIndependentProposalsSampler(Sampler):
    r""" Metropolis-Hastings with independent proposal sampler of distribution ``d``, with proposal distribution ``d_prop``

    Args:
      d (Distributions.Distribution): distribution to sample from
      d_prop (Distributions.Distribution): proposal distribution
    """
    def __init__(self, d, d_prop):
        if d.dim != d_prop.dim:
            raise ValueError("Dimension of the densities ``d`` and ``d_prop`` must " + \
                             "be the same")
        super(MetropolisHastingsIndependentProposalsSampler, self).__init__(d)
        self.prop_distribution = d_prop

    def rvs(self, m, x0=None, mpi_pool_tuple=(None,None)):
        r""" Generate a Markov Chain of :math:`m` equally weighted samples from the distribution ``d``

        Args:
          m (int): number of samples to generate
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`1,d`]): initial chain value
          mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
            pool of processes to be used for the evaluation of ``d`` and ``prop_d``

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        # Logging vars
        log_time_span = max(m//100, 1)
        last_log = 0
        nrej_tot = 0
        lg_str = "Sample %%%ii/%%i - Acceptance rate %%3.1f%%%%" % int(
            np.floor(np.log10(m))+1)
        # Init
        samps = self.prop_distribution.rvs(m+1, mpi_pool=mpi_pool_tuple[1])
        if x0 is not None:
            samps[0,:] = x0
        scatter_tuple = (['x'], [samps])
        d_log_pdf_Y = mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                               obj=self.distribution, mpi_pool=mpi_pool_tuple[0])
        prop_d_log_pdf_Y = mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                                    obj=self.prop_distribution,
                                    mpi_pool=mpi_pool_tuple[1])
        xt_idx = 0
        nrej = 0
        ar_samp = stats.uniform().rvs(m)
        for i in range(1,m+1):
            log_rho = min( d_log_pdf_Y[i] + prop_d_log_pdf_Y[xt_idx] - \
                           (d_log_pdf_Y[xt_idx] + prop_d_log_pdf_Y[i]) , 0 )
            if ar_samp[i-1] < np.exp(log_rho): #stats.bernoulli(np.exp(log_rho)).rvs(1): # Accept
                xt_idx = i
            else:
                nrej += 1
                samps[i,:] = samps[xt_idx,:]
            # Logging
            if i == last_log + log_time_span or i == m:
                rate = float(i-last_log-nrej)/float(i-last_log)*100.
                self.logger.info(lg_str % (i,m,rate))
                last_log = i
                nrej_tot += nrej
                nrej = 0
        rate = float(m-nrej_tot)/float(m)*100
        self.logger.info("Overall acceptance rate %3.1f%%" % rate)
        return (samps[1:,:], np.ones(m)/float(m))

class MetropolisHastingsSampler(Sampler):
    r""" Metropolis-Hastings sampler of distribution ``d``, with proposal ``d_prop``

    Args:
      d (Distributions.Distribution): distribution :math:`\pi({\bf x})` to sample from
      d_prop (Distributions.ConditionalDistribution): conditional distribution :math:`\pi({\bf y}\vert{\bf x})`
        to use as a proposal
    """
    def __init__(self, d, d_prop):
        if d.dim != d_prop.dim:
            raise ValueError("Dimension of the densities ``d`` and ``d_prop`` must " + \
                             "be the same")
        if not issubclass(type(d_prop), ConditionalDistribution):
            raise ValueError("The proposal distribution must be a conditional distribution")
        if d_prop.dim_y != d.dim:
            raise ValueError("The conditioning dimension of the proposal distribution must be d.dim")
        super(MetropolisHastingsSampler, self).__init__(d)
        self.prop_distribution = d_prop

    def rvs(self, m, x0=None, mpi_pool_tuple=(None,None)):
        r""" Generate a Markov Chain of :math:`m` equally weighted samples from the distribution ``d``

        Args:
          m (int): number of samples to generate
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`1,d`]): initial chain value
          mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
            pool of processes to be used for the evaluation of ``d`` and ``prop_d``

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        # Logging vars
        log_time_span = max(m//100, 1)
        last_log = 0
        nrej_tot = 0
        lg_str = "Sample %%%ii/%%i - Acceptance rate %%3.1f%%%%" % int(
            np.floor(np.log10(m))+1)
        # Init
        nrej = 0
        dim = self.distribution.dim
        samps = np.zeros((m+1, dim))
        ar_samps = stats.uniform().rvs(m)
        samps[0,:] = self.prop_distribution.rvs(1, np.zeros(dim)) if x0 is None else x0
        d_last_log_pdf = self.distribution.log_pdf(samps[[0],:])[0]
        for i in range(1,m+1):
            yt = self.prop_distribution.rvs(1, samps[i-1,:])
            d_new_log_pdf = self.distribution.log_pdf(yt)
            log_rho = min( d_new_log_pdf - d_last_log_pdf +
                           self.prop_distribution.log_pdf(samps[[0],:], yt) -
                           self.prop_distribution.log_pdf(yt, samps[[0],:]),
                           0 )
            if ar_samps[i-1] < np.exp(log_rho):
                samps[i,:] = yt
                d_last_log_pdf = d_new_log_pdf
            else:
                nrej += 1
                samps[i,:] = samps[i-1,:]
            # Logging
            if i == last_log + log_time_span or i == m:
                rate = float(i-last_log-nrej)/float(i-last_log)*100.
                self.logger.info(lg_str % (i,m,rate))
                last_log = i
                nrej_tot += nrej
                nrej = 0
        rate = float(m-nrej_tot)/float(m)*100
        self.logger.info("Overall acceptance rate %3.1f%%" % rate)
        return (samps[1:,:], np.ones(m)/float(m))

class MetropolisHastingsWithinGibbsSampler(Sampler):
    r""" Metropolis-Hastings within Gibbs sampler of distribution ``d``, with proposal ``d_prop`` and Gibbs block sampling ``blocks``

    Args:
      d (Distributions.Distribution): distribution :math:`\pi({\bf x})` to sample from
      d_prop (:class:`list` of :class:`Distributions.ConditionalDistribution`):
        conditional distribution :math:`\pi({\bf y}\vert{\bf x})` to use as a proposal
      block_list (:class:`list` of :class:`list`): list of blocks of variables
    """
    def __init__(self, d, d_prop_list, block_list=None):
        if block_list is None:
            block_list = [ [i] for i in range(d.dim) ]
        else:
            all_vars = sorted(itertools.chain(*block_list))
            if any([ v != i for i,v in enumerate(all_vars)]) or len(all_vars) != d.dim:
                raise ValueError("The blocks are not covering all the variables")
        if len(d_prop_list) != len(block_list):
            raise ValueError("The number of proposal distributions must be equal to " + \
                             "the number of blocks")
        for block, d_prop in zip(block_list, d_prop_list):
            if not issubclass(type(d_prop), ConditionalDistribution):
                raise ValueError(
                    "The proposal distribution must be a conditional distribution")
            if len(block) != d_prop.dim:
                raise ValueError("Dimension of the densities ``d`` and " + \
                                 "``d_prop`` must be the same")
            if d_prop.dim_y != d.dim:
                raise ValueError(
                    "The conditioning dimension of the proposal distribution must be d.dim")
        super(MetropolisHastingsWithinGibbsSampler, self).__init__(d)
        self.prop_distribution_list = d_prop_list
        self.block_list = block_list

    def rvs(self, m, x0=None, mpi_pool_tuple=(None,None)):
        r""" Generate a Markov Chain of :math:`m` equally weighted samples from the distribution ``d``

        Args:
          m (int): number of samples to generate
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`1,d`]): initial chain value
          mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
            pool of processes to be used for the evaluation of ``d`` and ``prop_d``

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        # Logging vars
        log_time_span = max(m//100, 1)
        last_log = 0
        nrej_tot = 0
        lg_str = "Sample %%%ii/%%i - Acceptance rate %%3.1f%%%%" % int(
            np.floor(np.log10(m))+1)
        # Init
        nblocks = len(self.block_list)
        nrej_list = [0 for i in range(nblocks)]
        nrej_tot_list = [0 for i in range(nblocks)]
        dim = self.distribution.dim
        samps = np.zeros((m+1, dim))
        ar_samps = stats.uniform().rvs(m*nblocks)
        if x0 is None:
            for block, d_prop in zip(self.block_list, self.prop_distribution_list):
                samps[0,block] = d_prop.rvs(1, np.zeros(dim))[0,:]
        else:
            samps[0,:] = x0
        d_last_log_pdf = self.distribution.log_pdf(samps[[0],:])[0]
        for i in range(1,m+1):
            samps[i,:] = samps[i-1,:]
            for j, (block, d_prop) in enumerate(
                    zip(self.block_list, self.prop_distribution_list)):
                yt = samps[[i],:]
                yt[0,block] = d_prop.rvs(1, samps[i-1,:])[0,:]
                d_new_log_pdf = self.distribution.log_pdf(yt)
                log_rho = min( d_new_log_pdf - d_last_log_pdf +
                               d_prop.log_pdf(samps[[i],:][:,block], yt) -
                               d_prop.log_pdf(yt[[0],:][:,block], samps[[i],:]),
                               0 )
                if ar_samps[(i-1)*nblocks+j] < np.exp(log_rho):
                    samps[i,:] = yt
                    d_last_log_pdf = d_new_log_pdf
                else:
                    nrej_list[j] += 1
                    nrej_tot_list[j] += 1
            # Logging
            if i == last_log + log_time_span or i == m:
                rate_list = [ float(i-last_log-nrej)/float(i-last_log)*100.
                              for nrej in nrej_list ]
                rate = sum([ rate/float(dim)*len(block)
                             for rate, block in zip(rate_list, self.block_list) ])
                self.logger.info(lg_str % (i,m,rate))
                last_log = i
                nrej_list = [0 for i in range(nblocks)]
        rate_list = [ float(m-nrej_tot)/float(m)*100
                      for nrej_tot in nrej_tot_list ]
        rate = sum([ rate/float(dim)*len(block)
                     for rate, block in zip(rate_list, self.block_list) ])
        self.logger.info("Overall acceptance rate %3.1f%%" % rate)
        return (samps[1:,:], np.ones(m)/float(m))
        
class HamiltonianMonteCarloSampler(Sampler):
    r""" Hamiltonian Monte Carlo sampler of distribution ``d``, with proposal distribution ``d_prop``

    This sampler requires the package `pyhmc <http://pythonhosted.org/pyhmc/>`_.

    Args:
      d (Distributions.Distribution): distribution to sample from
    """
    def __init__(self, d):
        if not PYHMC_SUPPORT:
            raise ImportError("HamiltonianMonteCarlo is not supported because " + \
                              "pyhmc is not installed")
        super(HamiltonianMonteCarloSampler, self).__init__(d)

    def rvs(self, m, x0=None,
            display=False, n_steps=1,
            persistence=False, decay=0.9, epsilon=0.2, window=1,
            return_logp=False, return_diagnostics=False, random_state=None):
        r""" Generate a Markov Chain of :math:`m` equally weighted samples from the distribution ``d``

        .. seealso:: `pyhmc <http://pythonhosted.org/pyhmc/>`_ for arguments
        """
        def fun(x, d):
            return d.log_pdf(x[nax,:])[0], d.grad_x_log_pdf(x[nax,:])[0,:]

        if x0 is None:
            x0 = stats.norm().rvs(self.distribution.dim)

        nsamp = 0
        step = min(100, m)
        x = np.zeros((m,self.distribution.dim))
        nrej = 0
        lg_str = "Sample %%%ii/%%i - Acceptance rate %%3.1f%%%%" % int(
            np.floor(np.log10(m))+1)
        while nsamp < m:
            x[nsamp:nsamp+step,:], diag = pyhmc.hmc(
                fun, x0=x0, n_samples=step, args=(self.distribution,),
                display=display, n_steps=n_steps, n_burn=0,
                persistence=persistence, decay=decay, epsilon=epsilon, window=window,
                return_logp=return_logp, return_diagnostics=True,
                random_state=random_state)
            # Update samples and starting point
            nsamp += step
            nrej += diag['rej']*step
            x0 = x[nsamp-1,:]
            self.logger.info(lg_str % (nsamp, m, (1-diag['rej'])*100.))
            step = min(100, m-nsamp)
        rate = float(nsamp-nrej)/float(nsamp) * 100.
        self.logger.info("Overall acceptance rate %3.1f%%" % rate)
        return (x, np.ones(m)/float(m))