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

import numpy as np
import numpy.linalg as npla

from .AdaptivityBase import Builder
from TransportMaps.Distributions import \
    PushForwardTransportMapDistribution, PullBackTransportMapDistribution
from TransportMaps.Routines import laplace_approximation
from TransportMaps.Diagnostics.Routines import variance_approx_kl
from TransportMaps.Maps.FullTransportMaps import LinearTransportMap

__all__ = ['KullbackLeiblerBuilder',
           'SequentialKullbackLeiblerBuilder',
           'ToleranceSequentialKullbackLeiblerBuilder']

class KullbackLeiblerBuilder(Builder):
    r""" Basis builder through minimization of kl divergence

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the parametric transport map :math:`T[{\bf a}]`,
    provides the functionalities to solve the problem

    .. math::

       \arg\min_{\bf a}\mathcal{D}_{\rm KL}\left(
       T[{\bf a}]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance.

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
    """
    def __init__(self, base_distribution=None, target_distribution=None):
        self.base_distribution = base_distribution
        self.target_distribution = target_distribution
        super(KullbackLeiblerBuilder, self).__init__()

    @property
    def base_distribution(self):
        return self._base_distribution

    @base_distribution.setter
    def base_distribution(self, dstr):
        self._base_distribution = dstr

    @property
    def target_distribution(self):
        return self._target_distribution

    @target_distribution.setter
    def target_distribution(self, dstr):
        self._target_distribution = dstr

    def solve(self, transport_map, qtype, qparams,
              x0=None,
              regularization=None,
              tol=1e-4, maxit=100, ders=2,
              fungrad=False,
              batch_size=None,
              mpi_pool=None):
        if x0 is None:
            x0 = transport_map.get_default_init_values_minimize_kl_divergence()
        push_base = PushForwardTransportMapDistribution(
            transport_map, self.base_distribution)
        log = push_base.minimize_kl_divergence(
            self.target_distribution,
            qtype=qtype, qparams=qparams,
            x0=x0, regularization=regularization,
            tol=tol, maxit=maxit, ders=ders,
            fungrad=fungrad, batch_size=batch_size,
            mpi_pool=mpi_pool)
        if not log['success']:
            transport_map.coeffs = x0
        return transport_map, log

class SequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
    """        
    def solve(self, transport_map_list, solve_params_list, regression_params_list=None):
        r"""
        Args:
          transport_map_list (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            list of transport maps :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`
          solve_params_list (:class:`list` of :class:`dict`): parameters to be used for the solution
          regression_params_list (:class:`list` of :class:`dict`): parameters to be used in the regression step
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the last transport map fitted.
        """
        if regression_params_list is None:
            regression_params_list = [ {key: sp[key] for key in (
                'qtype', 'qparams', 'regularization', 'tol', 'maxit') if key in sp}
                                       for sp in solve_params_list[1:] ]
        tm, log = super(SequentialKullbackLeiblerBuilder, self).solve(
            transport_map_list[0],
            **solve_params_list[0])
        if not log['success']:
            tm.coeffs = x0
            return tm, log
        for tm_new, solve_params, regression_params in zip(
                transport_map_list[1:], solve_params_list[1:], regression_params_list):
            # fit next map to old map
            tm_old = tm
            regression_params['d'] = self.base_distribution
            tm_new.regression(tm_old, **regression_params)
            # solve for the new map using regressed starting point
            x0 = tm_new.coeffs
            tm, log = super(SequentialKullbackLeiblerBuilder, self).solve(
                tm_new, x0=x0, **solve_params)
            if not log['success']:
                return tm_old, log
        return tm, log

class ToleranceSequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one, until a target tolerance is met

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
    """        
    def solve(self, transport_map_list, solve_params_list, regression_params_list=None,
              tol=1e-2, var_diag_params=None):
        r"""
        Args:
          transport_map_list (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            list of transport maps :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`
          solve_params_list (:class:`list` of :class:`dict`): parameters to be used for the solution
          regression_params_list (:class:`list` of :class:`dict`): parameters to be used in the regression step
          tol (float): tolerance to be met by the variance diagnostic
          var_diag_params (dict): parameters to be used in the variance diagnostic approximation
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the last transport map fitted.
        """
        if regression_params_list is None:
            regression_params_list = [ {key: sp[key] for key in (
                'qtype', 'qparams', 'regularization', 'tol', 'maxit') if key in sp}
                                       for sp in solve_params_list[1:] ]
        if var_diag_params is None:
            var_diag_params = {'qtype': 0, 'qparams': 1000}
        
        # First find Laplace point and center to it
        lap = laplace_approximation(self.target_distribution)
        lap_map = LinearTransportMap.build_from_Gaussian(lap)

        # Set initial conditions to Laplace approximation
        transport_map_list[0].regression(
            lap_map, d=self.base_distribution,
            qtype=3, qparams=[3]*self.base_distribution.dim,
            regularization={'alpha': 1e-4, 'type': 'L2'})

        x0 = transport_map_list[0].coeffs
        
        # for d, t in enumerate(transport_map_list[0].approx_list):
        #     # Constant part
        #     for i, midx in enumerate(t.c.get_multi_idxs()):
        #         if sum(midx) == 0:
        #             t.c.coeffs[i] = consTerm[d]
        #         elif sum(midx) == 1:
        #             t.c.coeffs[i] = linTerm[d, midx.index(1)]
        #     # Integrated part
        #     for i, midx in enumerate(t.h.get_multi_idxs()):
        #         if sum(midx) == 0:
        #             t.h.coeffs[i] = np.sqrt(linTerm[d,d])
        
        tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve(
            transport_map_list[0],
            x0 = x0,
            **solve_params_list[0])
        if not log['success']:
            tm.coeffs = x0
            return tm, log
        pull_tar = PullBackTransportMapDistribution(tm, self.target_distribution)
        var = variance_approx_kl(self.base_distribution, pull_tar, **var_diag_params)
        if var <= tol:
            return tm, log
        for tm_new, solve_params, regression_params in zip(
                transport_map_list[1:], solve_params_list[1:], regression_params_list):
            # # fit next map to old map
            # tm_old = tm
            # regression_params['d'] = self.base_distribution
            # tm_new.regression(tm_old, **regression_params)

            tm_old = tm
            for c1, c2 in zip(tm_old.approx_list, tm_new.approx_list):
                # Constant part
                for i1, midx1 in enumerate(c1.c.get_multi_idxs()):
                    for i2, midx2 in enumerate(c2.c.get_multi_idxs()):
                        if midx1 == midx2:
                            break
                    c2.c.coeffs[i2] = c1.c.coeffs[i1]
                # Integrated part
                for i1, midx1 in enumerate(c1.h.get_multi_idxs()):
                    for i2, midx2 in enumerate(c2.h.get_multi_idxs()):
                        if midx1 == midx2:
                            break
                    c2.h.coeffs[i2] = c1.h.coeffs[i1]
            
            # solve for the new map using regressed starting point
            x0 = tm_new.coeffs
            tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve(
                tm_new, x0=x0, **solve_params)
            if not log['success']:
                return tm_old, log
            pull_tar = PullBackTransportMapDistribution(tm, self.target_distribution)
            var = variance_approx_kl(self.base_distribution, pull_tar, **var_diag_params)
            if var <= tol:
                return tm, log
        # Variance was not met
        log['success'] = False
        log['msg'] = "Desired tolerance was no met by the map adaptivity. " + \
                     "Target variance: %e - Variance: %e " % (tol, var)
        return tm, log