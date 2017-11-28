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
import scipy.linalg as scila
import scipy.optimize as sciopt

from TransportMaps import get_mpi_pool, mpi_eval
import TransportMaps.XML as XML
from TransportMaps.Functionals.ParametricFunctionApproximationBase import \
    ParametricFunctionApproximation
from TransportMaps.Functionals.ProductDistributionParametricPullbackComponentFunctionBase \
    import ProductDistributionParametricPullbackComponentFunction
from TransportMaps.Distributions.DistributionBase import ProductDistribution
from TransportMaps.Distributions.TransportMapDistributions import \
    PullBackTransportMapDistribution, PushForwardTransportMapDistribution
from TransportMaps.Maps.TransportMapBase import *

__all__ = ['TriangularTransportMap',
           'MonotonicTriangularTransportMap',
           'TriangularListStackedTransportMap']

nax = np.newaxis

class TriangularTransportMap(TransportMap):
    r""" Generalized triangular transport map :math:`T({\bf x},{\bf a})`.

    For :math:`{\bf x} \in \mathbb{R}^d`, and parameters
    :math:`{\bf a} \in \mathbb{R}^N`, the parametric transport map is given by

    .. math::
       :nowrap:

       T({\bf x},{\bf a}) = \begin{bmatrix}
       T_1 \left({\bf x}_1, {\bf a}^{(1)}\right) \\
       T_2 \left({\bf x}_{1:2}, {\bf a}^{(2)}\right) \\
       T_3 \left({\bf x}_{1:3}, {\bf a}^{(3)}\right) \\
       \vdots \\
       T_d \left({\bf x}_{1:d}, {\bf a}^{(d)}\right)
       \end{bmatrix}

    where :math:`{\bf a}^{(i)} \in \mathbb{R}^{n_i}` and :math:`\sum_{i=1}^d n_ = N`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """

    def __init__(self, active_vars, approx_list):
        super(TriangularTransportMap,self).__init__(active_vars, approx_list)
        # Check lower triangularity
        d0 = active_vars[0][-1]
        for i, avars in enumerate(active_vars):
            if avars[-1] != d0 + i:
                raise ValueError("The map is not generalized lower triangular.")

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list,self.active_vars,precomp['components']):
            if precomp_type == 'uni':
                a.precomp_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \prod_{k=1}^d \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.exp( self.log_det_grad_x(x, precomp, idxs_slice) )

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0],self.dim_out))
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            try:
                (batch_set, vals) = p['cached_partial_xd']
            except KeyError:
                cached_flag = False
                out[:,k] = a.partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    out[:,k] = vals[idxs_slice]
                else:
                    out[:,k] = a.partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice] = out[:,k]
                    batch_set[idxs_slice] = True
        return out

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`[\nabla_{\bf a}\partial_{{\bf x}_k} T_k]_k`

        This is

        .. math::

           \left[ \begin{array}{ccccc}
             \nabla_{{\bf a}_1}\partial_{{\bf x}_1}T_1 & 0 & \cdots & & 0 \\
             0 \nabla_{{\bf a}_2}\partial_{{\bf x}_2}T_2 & 0 & \cdots & 0 \\
             \vdots & \ddots & & & \\
             0 & & \cdots & 0 & \nabla_{{\bf a}_d}\partial_{{\bf x}_d}T_d
           \end{array} \right]
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim_out, self.n_coeffs))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            try:
                (batch_set, vals) = p['cached_grad_a_partial_xd']
            except KeyError:
                cached_flag = False
                gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    gapxd = vals[idxs_slice,:]
                else:
                    gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice,:] = gapxd
                    batch_set[idxs_slice] = True
            stop = start + gapxd.shape[1]
            out[:,k,start:stop] = gapxd
            start = stop
        return out

    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.partial_xd(x, precomp=precomp, idxs_slice=idxs_slice)
        out = np.sum(np.log(pxd),axis=1)
        return out

    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T^{-1}_k({\bf y}_{1:k}, {\bf a}^{(k)})

        For :math:`{\bf x} = T^{-1}({\bf y}, {\bf a})`,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}, {\bf a}) = - \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )

    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
             :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
             at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # Load cached values
            try:
                (batch_set, vals) = p['cached_partial_xd']
            except KeyError:
                cached_flag = False
                pxd = a.partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    pxd = vals[idxs_slice]
                else:
                    pxd = a.partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice] = pxd
                    batch_set[idxs_slice] = True
            try:
                (batch_set, vals) = p['cached_grad_a_partial_xd']
            except KeyError:
                cached_flag = False
                gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    gapxd = vals[idxs_slice,:]
                else:
                    gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice,:] = gapxd
                    batch_set[idxs_slice] = True
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop] = gapxd / pxd[:,nax]
            start = stop
        return out

    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs, self.n_coeffs))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # Load cached values
            try:
                (batch_set, vals) = p['cached_partial_xd']
            except KeyError:
                cached_flag = False
                pxd = a.partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    pxd = vals[idxs_slice]
                else:
                    pxd = a.partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice] = pxd
                    batch_set[idxs_slice] = True
            try:
                (batch_set, vals) = p['cached_grad_a_partial_xd']
            except KeyError:
                cached_flag = False
                gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
            else:
                cached_flag = True
                if batch_set[idxs_slice][0]: # Checking only the first is enough..
                    gapxd = vals[idxs_slice,:]
                else:
                    gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice)
                    vals[idxs_slice,:] = gapxd
                    batch_set[idxs_slice] = True
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop,start:stop] = a.hess_a_partial_xd(x[:,avar], p, idxs_slice) \
                                           * (1./pxd)[:,nax,nax]
            pxd2 = pxd**2.
            pxd2[pxd2<=1e-14] = 1e-14
            out[:,start:stop,start:stop] -= (gapxd[:,:,nax] * gapxd[:,nax,:]) \
                                            * (1./pxd2)[:,nax,nax]
            start = stop
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_grad_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_grad_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_grad_x_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            out[:,avar] += a.grad_x_partial_xd(x[:,avar], p) / \
                           a.partial_xd(x[:,avar], p)[:,nax]
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_hess_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_hess_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.dim, self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            rr,cc = np.meshgrid(avar,avar)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Compute hess_x_partial_xd
            dxk = a.partial_xd(x[:,avar], p)
            out[idxs] += (a.hess_x_partial_xd(x[:,avar], p) / \
                          dxk[:,nax,nax]).reshape((x.shape[0],nvar**2))
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p)
            dxdxkT2 = dxdxkT[:,:,nax] * dxdxkT[:,nax,:]
            out[idxs] -= (dxdxkT2 / (dxk**2.)[:,nax,nax]).reshape((x.shape[0],nvar**2))
        return out

    def grad_a_hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim, self.dim))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):

            # Compute grad_a_hess_x_sum
            dxk = a.partial_xd(x[:,avar],p)
            dadx2dxk = a.grad_a_hess_x_partial_xd(x[:,avar],p)
            dadxk    = a.grad_a_partial_xd(x[:,avar],p)
            dadxdxk  = a.grad_a_grad_x_partial_xd(x[:,avar],p)
            dx2dxk   = a.hess_x_partial_xd(x[:,avar],p)
            dxdxkT   = a.grad_x_partial_xd(x[:,avar], p)
            dxdxkT2  = dxdxkT[:,nax,:,nax] * dxdxkT[:,nax,nax,:]
            B = dadxdxk[:,:,:,nax]*dxdxkT[:,nax,nax,:]
            grad_a_hess_x_sum = (dadx2dxk / dxk[:,nax,nax,nax]) - \
                    (dx2dxk[:,nax,:,:]*dadxk[:,:,nax,nax])/(dxk**2.)[:,nax,nax,nax] - \
                    (B + B.transpose((0,1,3,2)))/(dxk**2.)[:,nax,nax,nax] + \
                    2*(dxdxkT2*dadxk[:,:,nax,nax])/(dxk**3.)[:,nax,nax,nax]

            # 2d numpy advanced indexing
            nvar = len(avar)
            stop  = start + dadxk.shape[1]
            tmp = 0
            for coeff_idx in range(start, stop):

                rr,cc = np.meshgrid(avar, avar)
                rr = list( rr.flatten() )
                cc = list( cc.flatten() )

                # Find index for coefficients and assign to out
                idxs  = (slice(None), coeff_idx, rr, cc)
                out[idxs] += grad_a_hess_x_sum[:,tmp,:,:].reshape((x.shape[0], nvar**2))
                tmp = tmp + 1

            start = stop

        return out

    def inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`T^{-1}({\bf y},{\bf a})`

        If the map has more input than outputs :math:`d_{\rm in} > d_{\rm out}`,
        it consider the first :math:`d_{\rm in} - d_{\rm out}` values in ``x``
        to be already inverted values and feed them to the following approximations
        to find the inverse.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.


        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point

        Raises:
          ValueError: if :math:`d_{\rm in} < d_{\rm out}`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {}
        # Retrieve from cache
        try:
            (batch_set, vals) = precomp['cached_evaluate']
        except KeyError:
            cached_flag = False
        else:
            cached_flag = True
            if batch_set[idxs_slice][0]: # Checking only the first is enough..
                return vals[idxs_slice,:]
        # Evaluation
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros(x.shape)
        skip_dim = self.dim_in - self.dim_out
        if skip_dim < 0:
            raise ValueError("The map has more output than inputs")
        xout[:,:skip_dim] = x[:,:skip_dim]
        for i in range(x.shape[0]):
            for k, (a,avar) in enumerate(zip(self.approx_list,self.active_vars)):
                xout[i,skip_dim+k] = a.inverse(xout[i,avar[:-1]], x[i,skip_dim+k])
        # Store in cache
        if cached_flag:
            vals[idxs_slice,:] = xout
            batch_set[idxs_slice] = True
        return xout

    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        Differently from :func:`grad_a`,
        :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`
        is not block diagonal, but only lower block triangular
        Consequentely this function will return the full gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,N`]) --
              :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv, precomp) # Lower triangular
        ga = self.grad_a(xinv, precomp) # List of diagonal blocks
        out = np.zeros((xinv.shape[0],self.dim,self.n_coeffs))
        rhs = np.zeros((self.dim, self.n_coeffs))
        for i in range(xinv.shape[0]):
            start = 0
            for d, gad in enumerate(ga):
                rhs[d,start:start+gad.shape[1]] = gad[i,:]
                start += gad.shape[1]
            out[i,:,:] = - scila.solve_triangular(gx[i,:,:], rhs, lower=True)
        return out

    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla_{\bf x} T^{-1}({\bf x},{\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           NotImplementedError: to be implemented in subclasses
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv)
        gx_inv = np.zeros((xinv.shape[0], self.dim, self.dim))
        for i in range(xinv.shape[0]):
            gx_inv[i,:,:] = scila.solve_triangular(gx[i,:,:], np.eye(self.dim), lower=True)
        return gx_inv

    def init_mem_precomp_minimize_kl_divergence(self, params_dens=None):
        r""" Function used in order to initialize the memory for precomputed values.

        Args:
          params_dens (dict): parameters for the parent distribution
        """
        out = {'params_pi': params_dens,
               'params_t': {'components': [{} for i in range(self.dim)]} }
        return (None, out)

    def init_mem_precomp_minimize_kl_divergence_inverse(self, params_dens=None):
        r""" Function used in order to initialize the memory for precomputed values.

        Args:
          params_dens (dict): parameters for the parent distribution
        """
        out = {'params_pi': params_dens,
               'params_t': {} }
        return (None, out)
        
    def precomp_minimize_kl_divergence(self, x, params, precomp_type='uni'):
        r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence`

        Enriches the dictionaries in the ``precomp`` list if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters to be updated
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
              strucutres. The first argument is needed for consistency with 
        """
        # Fill precomputed Vandermonde matrices etc.
        self.precomp_evaluate(x, params['params_t'], precomp_type)
        self.precomp_partial_xd(x, params['params_t'], precomp_type)

    def allocate_cache_minimize_kl_divergence(self, x, params, cache_level):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): dictionary of precomputed values
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, and the gradient evaluation ``1``, or
            nothing ``-1``
        """
        precomp = params['params_t']
        tot_size = x.shape[0]
        if cache_level >= 0:
            precomp['cached_evaluate'] = ( np.zeros(tot_size,dtype=bool),
                                           np.empty((tot_size, self.dim)) )
            for a, p in zip(self.approx_list, precomp['components']):
                p['cached_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
                                           np.empty(tot_size) )
        if cache_level >= 1:
            for a, p in zip(self.approx_list, precomp['components']):
                p['cached_grad_a'] = ( np.zeros(tot_size,dtype=bool),
                                       np.empty((tot_size, a.n_coeffs)) )
                p['cached_grad_a_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
                                                  np.empty((tot_size, a.n_coeffs)) )

    def allocate_cache_minimize_kl_divergence_inverse(self, x, params, cache_level=0):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): dictionary of precomputed values
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, or nothing ``-1``
        """
        precomp = params['params_t']
        tot_size = x.shape[0]
        if cache_level >= 0:
            precomp['cached_evaluate'] = ( np.zeros(tot_size,dtype=bool),
                                           np.empty((tot_size, self.dim)) )
        if cache_level >= 1:
            raise NotImplementedError("Not implemented for inverse maps")

    def reset_cache_minimize_kl_divergence_objective(self, params):
        r""" Reset the objective part of the cache space for the KL-divergence minimization

        Args:
          params2 (dict): dictionary of precomputed values
        """
        precomp = params['params_t']
        batch_set, _ = precomp['cached_evaluate']
        batch_set[:] = False
        if 'components' in precomp:
            for p in precomp['components']:
                batch_set, _ = p['cached_partial_xd']
                batch_set[:] = False

    def reset_cache_minimize_kl_divergence_grad_a_objective(self, params):
        r""" Reset the gradient part of the cache space for the KL-divergence minimization

        Args:
          params (dict): dictionary of precomputed values
        """
        precomp = params['params_t']
        if 'components' in precomp:
            for p in precomp['components']:
                batch_set, _ = p['cached_grad_a']
                batch_set[:] = False
                batch_set, _ = p['cached_grad_a_partial_xd']
                batch_set[:] = False

    @staticmethod
    def from_xml_element(node):
        from TransportMaps import XML_NAMESPACE
        import TransportMaps.Maps as MAPS
        # Call proper type
        t = node.attrib['type']
        dim = int(node.attrib['dim'])
        # Retrieve the active variables and the approximation list
        active_vars = [None for d in range(dim)]
        approx_list = [None for d in range(dim)]
        for comp_node in node.getchildren():
            # Figure out which component are described
            id_field = comp_node.attrib['id']
            ncomp_list = []
            if id_field == '*':
                star_comp_node = comp_node
            else:
                ncomp_list = XML.id_parser(id_field, dim)
            # Iterate over components described
            for ncomp in ncomp_list:
                if active_vars[ncomp] is not None or approx_list[ncomp] is not None:
                    raise ValueError("Component %i is multiply defined" % ncomp)
                # Get the active variables of the component
                avars_node = comp_node.find(XML_NAMESPACE + 'avars')
                avars = []
                for vars_node in avars_node.getchildren():
                    vars_field = vars_node.text
                    avars += XML.vars_parser(vars_field, ncomp)
                active_vars[ncomp] = avars
                dcomp = len(avars)
                # Construct the approximation
                approx_node = comp_node.find(XML_NAMESPACE + 'approx')
                approx = ParametricFunctionApproximation.from_xml_element(
                    approx_node, dcomp)
                approx_list[ncomp] = approx
                
        # Init the star component
        # defining all the components which have not been defined yet
        ncomp_list = [i for i in range(dim) if active_vars[i] is None]
        for ncomp in ncomp_list:
            if active_vars[ncomp] is not None or approx_list[ncomp] is not None:
                raise ValueError("Component %i is multiply defined" % ncomp)
            # Get the active variables of the component
            avars_node = star_comp_node.find(XML_NAMESPACE + 'avars')
            avars = []
            for vars_node in avars_node.getchildren():
                vars_field = vars_node.text
                avars += XML.vars_parser(vars_field, ncomp)
            active_vars[ncomp] = avars
            dcomp = len(avars)
            # Construct the approximation
            approx_node = star_comp_node.find(XML_NAMESPACE + 'approx')
            approx = ParametricFunctionApproximation.from_xml_element(
                approx_node, dcomp)
            approx_list[ncomp] = approx
        
        # Instantiate and return
        if t == 'intexp':
            return MAPS.IntegratedExponentialTriangularTransportMap(
                active_vars, approx_list)
        if t == 'intsq':
            return MAPS.IntegratedSquaredTriangularTransportMap(
                active_vars, approx_list)
        elif t == 'linspan':
            return MAPS.LinearSpanTriangularTransportMap(
                active_vars, approx_list)
        elif t == 'monotlinspan':
            return MAPS.MonotonicLinearSpanTriangularTransportMap(
                active_vars, approx_list)
        else:
            raise ValueError("Triangular transport map type not recognized")

class MonotonicTriangularTransportMap(TriangularTransportMap):
    r""" [Abstract] Triangular transport map which is monotone by construction.
    """    
    def get_default_init_values_minimize_kl_divergence(self):
        raise NotImplementedError("To be implemented in sub-classes")
    
    def minimize_kl_divergence(self, d1, d2,
                               qtype=None, qparams=None,
                               x=None, w=None,
                               params_d1=None, params_d2=None,
                               x0=None,
                               regularization=None,
                               tol=1e-4, maxit=100, ders=2,
                               fungrad=False,
                               precomp_type='uni',
                               batch_size=None,
                               cache_level=1,
                               mpi_pool=None,
                               import_set=set(),
                               grad_check=False, hess_check=False):
        r""" Compute: :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`

        Args:
          d1 (Distribution): distribution :math:`\pi_1`
          d2 (Distribution): distribution :math:`\pi_2`
          qtype (int): quadrature type number provided by :math:`\pi`
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
          params_d1 (dict): parameters for distribution :math:`\pi_1`
          params_d2 (dict): parameters for distribution :math:`\pi_2`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
          fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>` or :class:`list<list>` of ``batch_size``):
            the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
            If the target distribution is a :class:`ProductDistribution`, then
            the optimization problem decouples and
            ``batch_size`` is a list of lists containing the batch sizes to be
            used for each component of the map.
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, and the gradient evaluation ``1`` or
            nothing ``-1``
          mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
            pool of processes to be used, ``None`` stands for one process.
            If the target distribution is a :class:`ProductDistribution`, then
            the minimization problem decouples and ``mpi_pool`` is a list containing
            ``mpi_pool``s for each component of the map.
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver

        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        if ders < 0:
            self.logger.warning("Value for ders too low (%d). Set to 0." % ders)
            ders = 0
        if ders > 2:
            self.logger.warning("Value for ders too high (%d). Set to 2." % ders)
            ders = 2
            
        if (x is None) and (w is None):
            (x, w) = d1.quadrature(qtype, qparams, mpi_pool=self.mpi_pool)

        if issubclass(type(d2.base_distribution), ProductDistribution) \
           and isinstance(d2, PullBackTransportMapDistribution):
            if batch_size is None:
                batch_size_list = [None] * self.dim
            else:
                batch_size_list = batch_size
            if mpi_pool is None:
                mpi_pool_list = [None] * self.dim
            else:
                mpi_pool_list = mpi_pool
            log_list = []
            start_coeffs = 0
            for i, (a, avars, batch_size, mpi_pool) in enumerate(zip(
                    self.approx_list, self.active_vars, batch_size_list, mpi_pool_list)):
                f = ProductDistributionParametricPullbackComponentFunction(
                    a, d2.base_distribution.get_component([i]) )
                stop_coeffs = start_coeffs + a.n_coeffs
                sub_x0 = None if x0 is None else x0[start_coeffs:stop_coeffs]
                start_coeffs = stop_coeffs
                log = a.minimize_kl_divergence_component(
                    f, x[:,avars], w, x0=sub_x0,
                    regularization=regularization,
                    tol=tol, maxit=maxit, ders=ders,
                    fungrad=fungrad, precomp_type=precomp_type,
                    batch_size=batch_size,
                    cache_level=cache_level,
                    mpi_pool=mpi_pool,
                    import_set=import_set)
                log_list.append( log )
            return log_list
            
        else: # Not a product distribution
            log = self.minimize_kl_divergence_complete(
                d1, d2, x=x, w=w, params_d1=params_d1, params_d2=params_d2,
                x0=x0, regularization=regularization,
                tol=tol, maxit=maxit, ders=ders,
                fungrad=fungrad, precomp_type=precomp_type,
                batch_size=batch_size, cache_level=cache_level,
                mpi_pool=mpi_pool, import_set=import_set,
                grad_check=grad_check, hess_check=hess_check)
            return log

    def minimize_kl_divergence_complete(self, d1, d2,
                                        x=None, w=None,
                                        params_d1=None, params_d2=None,
                                        x0=None,
                                        regularization=None,
                                        tol=1e-4, maxit=100, ders=2,
                                        fungrad=False,
                                        precomp_type='uni',
                                        batch_size=None,
                                        cache_level=1,
                                        mpi_pool=None,
                                        import_set=set(),
                                        grad_check=False, hess_check=False):
        r"""
        Computes :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`
        for non-product distributions.

        .. seealso:: :fun:`TriangularTransportMap.minimize_kl_divergence` for a description of the parameters
        """    
        self.logger.debug("minimize_kl_divergence(): Precomputation started")

        self.mpi_pool = mpi_pool
        if batch_size is None:
            batch_size = [None] * 3
        if isinstance(d2, PullBackTransportMapDistribution):
            # Init memory
            bcast_tuple = (['params_dens'],[params_d2])
            (_, params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                    bcast_tuple=bcast_tuple,
                                    dmem_key_out_list=['params2'],
                                    obj=d2.transport_map,
                                    mpi_pool=self.mpi_pool, concatenate=False)
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            # precomp_minimize_kl_divergence
            scatter_tuple = (['x'],[x])
            bcast_tuple = (['precomp_type'],[precomp_type])
            mpi_eval("precomp_minimize_kl_divergence",
                     scatter_tuple=scatter_tuple,
                     bcast_tuple=bcast_tuple,
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map,
                     mpi_pool=self.mpi_pool, concatenate=False)
            # allocate_cache_minimize_kl_divergence
            scatter_tuple = (['x'],[x])
            bcast_tuple = (['cache_level'],[cache_level])
            mpi_eval("allocate_cache_minimize_kl_divergence",
                     scatter_tuple=scatter_tuple,
                     bcast_tuple=bcast_tuple,
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map,
                     mpi_pool=self.mpi_pool, concatenate=False)
        elif isinstance(d2, PushForwardTransportMapDistribution):
            # Init memory
            bcast_tuple = (['params_dens'],[params_d2])
            (_, params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence_inverse",
                                    bcast_tuple=bcast_tuple,
                                    dmem_key_out_list=['params2'],
                                    obj=d2.transport_map,
                                    mpi_pool=self.mpi_pool, concatenate=False)
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            # allocate cache
            scatter_tuple = (['x'],[x])
            bcast_tuple = (['cache_level'],[cache_level])
            mpi_eval("allocate_cache_minimize_kl_divergence_inverse",
                     scatter_tuple=scatter_tuple,
                     bcast_tuple=bcast_tuple,
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map,
                     mpi_pool=self.mpi_pool, concatenate=False)
        else:
            raise AttributeError("Not recognized distribution type")
        self.logger.debug("minimize_kl_divergence(): Precomputation ended")
        params = {}
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        params['x'] = x
        params['w'] = w
        params['d1'] = d1
        params['d2'] = d2
        params['params1'] = params_d1
        params['params2'] = params2
        params['batch_size'] = batch_size
        params['cache_level'] = cache_level
        params['regularization'] = regularization
        params['grad_check'] = grad_check
        params['hess_check'] = hess_check

        if x0 is None:
            x0 = self.get_default_init_values_minimize_kl_divergence()

        if cache_level >= 0:
            params['objective_cache_coeffs'] = x0 - 1.
        if cache_level >= 1:
            params['grad_a_objective_cache_coeffs'] = x0 - 1.

        # Callback variables
        self.it_callback = 0
        self.ders_callback = ders
        self.params2_callback = params2
        self.hess_assembled = False

        # Options for optimizer
        options = {'maxiter': maxit,
                   'disp': False}

        # Solve
        if ders == 0:
            res = sciopt.minimize(self.minimize_kl_divergence_objective,
                                  args=params,
                                  x0=x0,
                                  method='BFGS',
                                  tol=tol,
                                  options=options,
                                  callback=self.minimize_kl_divergence_callback)
        elif ders == 1:
            if fungrad:
                res = sciopt.minimize(self.minimize_kl_divergence_tuple_grad_a_objective,
                                      args=params,
                                      x0=x0,
                                      jac=True,
                                      method='BFGS',
                                      tol=tol,
                                      options=options,
                                      callback=self.minimize_kl_divergence_callback)
            else:
                res = sciopt.minimize(self.minimize_kl_divergence_objective,
                                      args=params,
                                      x0=x0,
                                      jac=self.minimize_kl_divergence_grad_a_objective,
                                      method='BFGS',
                                      tol=tol,
                                      options=options,
                                      callback=self.minimize_kl_divergence_callback)
        elif ders == 2:
            res = sciopt.minimize(
                self.minimize_kl_divergence_objective, args=params, x0=x0,
                jac=self.minimize_kl_divergence_grad_a_objective,
                hessp=self.minimize_kl_divergence_action_storage_hess_a_objective,
                method='newton-cg', tol=tol, options=options,
                callback=self.minimize_kl_divergence_callback)

        # Clean up callback stuff
        del self.it_callback
        del self.ders_callback
        del self.params2_callback
        del self.hess_assembled

        # Log
        log = {}
        log['success'] = res['success']
        log['message'] = res['message']
        log['fval'] = res['fun']
        log['nit'] = res['nit']
        log['n_fun_ev'] = params['nobj']
        if ders >= 1:
            log['n_jac_ev'] = params['nda_obj']
            log['jac'] = res['jac']
        if ders >= 2:
            log['n_hess_ev'] = params['nda2_obj']
        # Display stats
        if log['success']:
            self.logger.info("Optimization terminated successfully")
        else:
            self.logger.warn("Minimization of KL-divergence failed.")
            self.logger.warn("Message: %s" % log['message'])
        self.logger.info("  Function value:          %6f" % log['fval'])
        if ders >= 1:
            self.logger.info("  Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
        self.logger.info("  Number of iterations:    %6d" % log['nit'])
        self.logger.info("  N. function evaluations: %6d" % log['n_fun_ev'])
        if ders >= 1:
            self.logger.info("  N. Jacobian evaluations: %6d" % log['n_jac_ev'])
        if ders >= 2:
            self.logger.info("  N. Hessian evaluations:  %6d" % log['n_hess_ev'])
        # Set coefficients
        self.mpi_pool = False
        d2.coeffs = res['x']
        return log

class TriangularListStackedTransportMap(ListStackedTransportMap):
    r""" Triangular transport map obtained by stacking :math:`T_1, T_2, \ldots`.

    The maps must be such that
    :math:`{\rm dim}({\rm range}(T_{i-1})) = {\rm dim}({\rm domain}(T_i))`.

    Args:
      tm_list (:class:`list` of :class:`TransportMap`): list of transport maps :math:`T_i`
    """
    def __init__(self, tm_list):
        super(TriangularListStackedTransportMap, self).__init__(tm_list)
        # Check triangularity
        dim_out = self.tm_list[0].dim_out
        for tm in self.tm_list[1:]:
            if dim_out >= tm.dim_in:
                raise ValueError("The stacked list of maps is not triangular.")
            dim_out += tm.dim_out

    def inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`T^{-1}({\bf y},{\bf a})`

        If the map has more input than outputs :math:`d_{\rm in} > d_{\rm out}`,
        it consider the first :math:`d_{\rm in} - d_{\rm out}` values in ``x``
        to be already inverted values and feed them to the following approximations
        to find the inverse.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.


        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point

        Raises:
          ValueError: if :math:`d_{\rm in} < d_{\rm out}`
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xinv = x.copy()
        start = 0
        for tm in self.tm_list:
            stop = start + tm.dim_out
            xinv[:,start:stop] = tm.inverse( xinv[:,:stop] )[:,start:stop]
            start = stop
        return xinv

    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros(x.shape[0])
        for tm in self.tm_list:
            out += tm.log_det_grad_x( x[:,:tm.dim_in] )
        return out

    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )
