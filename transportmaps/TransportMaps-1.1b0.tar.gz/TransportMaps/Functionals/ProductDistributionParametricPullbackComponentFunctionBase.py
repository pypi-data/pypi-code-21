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

import logging
import numpy as np
import numpy.linalg as npla

from .ParametricFunctionApproximationBase import \
    ParametricFunctionApproximation
from TransportMaps.Distributions.DistributionBase import Distribution

__all__ = ['ProductDistributionParametricPullbackComponentFunction']

nax = np.newaxis

class ProductDistributionParametricPullbackComponentFunction(
        ParametricFunctionApproximation):
    r""" Parametric function :math:`f[{\bf a}](x_{1:k}) = \log\pi\circ T_k[{\bf a}](x_{1:k}) + \log\partial_{x_k}T_k[{\bf a}](x_{1:k})`

    Args:
      transport_map_component (MonotonicFunctionApproximation): component :math:`T_k`
        of monotone map :math:`T`
      base_distribution (Distribution): distribution :math:`\pi`
    """
    def __init__(self, transport_map_component, base_distribution):
        if base_distribution.dim != 1:
            raise AttributeError("The dimension of the distribution must be 1")
        super(ParametricFunctionApproximation, self).__init__(transport_map_component.dim)
        self.tmap_component = transport_map_component
        self.base_distribution = base_distribution

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}` of the function

        .. seealso:: :func:`ParametricFunctionApproximation.coeffs`
        """
        return self.tmap_component.coeffs

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients
        
        .. seealso:: :func:`ParametricFunctionApproximation.n_coeffs`
        """
        return self.tmap_component.n_coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricFunctionApproximation.coeffs`
        """
        self.tmap_component.coeffs = coeffs

    def evaluate(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        params_pi = params['params_pi']
        params_ti = params['params_t']
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)
        lpdf = self.base_distribution.log_pdf(ev[:,nax], params_pi)
        lgxd = np.log( self.tmap_component.partial_xd(x, params_ti, idxs_slice) )
        return lpdf + lgxd

    def grad_a(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,n`]) -- evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        params_pi = params['params_pi']
        params_ti = params['params_t']
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)
        gxlpdf = self.base_distribution.grad_x_log_pdf(ev[:,nax], params_pi)[:,0]
        ga = self.tmap_component.grad_a(x, params_ti, idxs_slice)
        gxd = self.tmap_component.partial_xd(x, params_ti, idxs_slice)
        gagxd = self.tmap_component.grad_a_partial_xd(x, params_ti, idxs_slice)
        out = gxlpdf[:,nax] * ga + gagxd / gxd[:,nax]
        return out

    def hess_a(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a}f[{\bf a}](x_{1:k})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,n`]) -- evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        params_pi = params['params_pi']
        params_ti = params['params_t']
        # First term
        ev = self.tmap_component.evaluate(x, params_ti, idxs_slice)
        hxlpdf = self.base_distribution.hess_x_log_pdf(ev[:,nax], params_pi)[:,0,0]
        ga = self.tmap_component.grad_a(x, params_ti, idxs_slice)
        t1 = ga[:,nax,:] * ga[:,:,nax]
        t1 *= hxlpdf[:,nax,nax]
        # Second term
        gxlpdf = self.base_distribution.grad_x_log_pdf(ev[:,nax], params_pi)[:,0]
        ha = self.tmap_component.hess_a(x, params_ti, idxs_slice)
        t2 = gxlpdf[:,nax,nax] * ha
        # Third term
        gxd = self.tmap_component.partial_xd(x, params_ti, idxs_slice)
        hagxd = self.tmap_component.hess_a_partial_xd(x, params_ti, idxs_slice)
        t3 = hagxd / gxd[:,nax,nax]
        # Fourth term
        gagxd = self.tmap_component.grad_a_partial_xd(x, params_ti, idxs_slice)
        t4 = (gagxd[:,nax,:] * gagxd[:,:,nax]) / gxd[:,nax,nax]**2
        # Output
        out = t1 + t2 + t3 - t4
        return out
        
        