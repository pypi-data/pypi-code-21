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
import scipy.optimize as sciopt
import itertools

import TransportMaps as TM
from TransportMaps.Functionals.ParametricFunctionApproximationBase import *

__all__ = ['LinearSpanApproximation']

nax = np.newaxis

class LinearSpanApproximation(TensorizedFunctionApproximation):
    r""" Parametric function :math:`f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}`

    Args:
      basis_list (list): list of :math:`d`
        :class:`OrthogonalBasis<SpectralToolbox.OrthogonalBasis>`
      spantype (str): Span type. 'total' total order, 'full' full order,
        'midx' multi-indeces specified
      order_list (:class:`list<list>` of :class:`int<int>`): list of 
        orders :math:`\{N_i\}_{i=0}^d`
      multi_idxs (list): list of tuples containing the active multi-indices
    """

    def __init__(self, basis_list, spantype=None, order_list=None, multi_idxs=None):
        if spantype in ['total','full'] and order_list is not None:
            self.max_order_list = order_list
            self.multi_idxs = self.generate_multi_idxs(spantype)
        elif spantype == 'midx' and multi_idxs is not None:
            self.multi_idxs = multi_idxs
            self.max_order_list = list( np.max(np.asarray(self.multi_idxs), axis=0) )
        else:
            raise ValueError("""
                             Parameters mismatch: (spantype==total|full & order_list != None) |
                             (spantype==midx & multi_idxs != None)
                             """)
        super(LinearSpanApproximation,self).__init__(basis_list)

    def generate_multi_idxs(self, spantype):
        r""" Generate the list of multi-indices
        """
        if spantype == 'full':
            return list(itertools.product(*[range(o+1) for o in self.max_order_list]))
        elif spantype == 'total':
            midxs = TM.generate_total_order_midxs(self.max_order_list)
            return midxs
        raise NotImplementedError("Not implemented for the selected spantype (%s)" % spantype)

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self._coeffs = np.zeros(self.n_coeffs)

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        return len(self.multi_idxs)
        
    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        if len(coeffs) != self.n_coeffs:
            raise ValueError("The number of input coefficients does not agree " +
                             "with the number of expected coefficients.")
        self._coeffs = coeffs

    def get_multi_idxs(self):
        r""" Get the list of multi indices

        Return:
          (:class:`list` of :class:`tuple`) -- multi indices
        """
        return self.multi_idxs

    def set_multi_idxs(self, multi_idxs):
        r""" Set the list of multi indices

        Args:
          multi_idxs (:class:`list` of :class:`tuple`): multi indices
        """
        self.multi_idxs = multi_idxs

    def get_directional_orders(self):
        r""" Get the maximum orders of the univariate part of the representation.

        Returns:
          (:class:`list<list>` [d] :class:`int<int>`) -- orders
        """
        if not hasattr(self, "max_order_list"): # Backcompatibility
            self.max_order_list = list( np.max(np.asarray(self.multi_idxs), axis=0) )
        return self.max_order_list[:]

    def precomp_Vandermonde_evaluate(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V = precomp['V']
        except KeyError as e:
            try:
                V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            precomp['V'] = np.ones((V_list[0].shape[0], self.n_coeffs))
            for i,midx in enumerate(self.multi_idxs):
                for idx,V1d in zip(midx,V_list):
                    precomp['V'][:,i] *= V1d[:,idx]
        return precomp

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        # Retrieve from cache
        try:
            (batch_set, vals) = precomp['cached_evaluate']
        except (TypeError, KeyError) as e:
            cached_flag = False
        else:
            cached_flag = True
            if batch_set[idxs_slice][0]: # Checking only the first is enough..
                return vals[idxs_slice]
        # Evaluation
        try:
            V = precomp['V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_evaluate(x, precomp)
                idxs_slice = slice(None)
                V_list = precomp['V_list']
            tot_size = V_list[0].shape[0]
            out = np.zeros(x.shape[0])
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loop?
            for c, midx in zip(self._coeffs, self.multi_idxs):
                tmp[:] = 1.
                for idx,V in zip(midx,V_list):
                    tmp *= V[idxs_slice,idx]
                out += c * tmp
        else:
            tot_size = V.shape[0]
            out = np.dot(V[idxs_slice,:], self._coeffs)
        # Store in cache
        if cached_flag: 
            vals[idxs_slice] = out
            batch_set[idxs_slice] = True
        return out

    def precomp_Vandermonde_grad_x(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of multi-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: grad_x_V_list = precomp['grad_x_V_list']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            grad_x_V_list = []
            # TODO: Accelerate this loops?
            for d in range(self.dim):
                grad_x_V = np.ones((x.shape[0], self.n_coeffs))
                for i,midx in enumerate(self.multi_idxs):
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list, partial_x_V_list)):
                        if j != d:
                            grad_x_V[:,i] *= V1d[:,idx]
                        else:
                            grad_x_V[:,i] *= pxV1d[:,idx]
                grad_x_V_list.append( grad_x_V )
            precomp['grad_x_V_list'] = grad_x_V_list
        return precomp

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_V_list = precomp['grad_x_V_list']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
            except (TypeError,KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
            out = np.zeros( x.shape )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loops?
            for d in range(self.dim):
                for c, midx in zip(self._coeffs, self.multi_idxs):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j != d:
                            tmp *= V1d[idxs_slice,idx]
                        else:
                            tmp *= pxV1d[idxs_slice,idx]
                    out[:,d] += c * tmp
        else:
            out = np.zeros( x.shape )
            for i, grad_x_V in enumerate(grad_x_V_list):
                out[idxs_slice,i] = np.dot( grad_x_V[idxs_slice,:], self._coeffs )
        return out

    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_V_list = precomp['grad_x_V_list']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                precomp = self.precomp_evaluate(x)
            except TypeError as e:
                x = x[idxs_slice,:]
                precomp = self.precomp_evaluate(x)
                idxs_slice = slice(None)
            finally:
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            out = np.zeros( (x.shape[0], self.n_coeffs, x.shape[1]) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate this loops?
            for d in range(self.dim):
                cidx = 0
                for c, midx in zip(self._coeffs, self.multi_idxs):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j != d:
                            tmp *= V1d[idxs_slice,idx]
                        else:
                            tmp *= pxV1d[idxs_slice,idx]
                    out[:,cidx,d] += tmp#*(c != 0)
                    cidx = cidx + 1
        else:
            out = np.zeros( (x.shape[0], self.n_coeffs, x.shape[1]) )
            # coeff_ind = indicator function applied to coefficients in map component
            #coeff_ind = [int(x != 0) for x in self._coeffs]
            for i, grad_x_V in enumerate(grad_x_V_list):
                out[idxs_slice,:,i] = grad_x_V[idxs_slice,:]#np.dot(grad_x_V[idxs_slice,:], coeff_ind)
        return out

    def precomp_Vandermonde_hess_x(self, x, precomp=None):
        r""" Precompute the multi-variate Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>`
            [:math:`d,d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the matrix of multi-variate Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: hess_x_V_mat = precomp['hess_x_V_mat']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            hess_x_V_mat = np.empty((self.dim,self.dim), dtype=object)
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    hess_x_V = np.ones((x.shape[0],self.n_coeffs))
                    for i, midx in enumerate(self.multi_idxs):
                        for j, (idx, V1d, pxV1d, p2xV1d) in enumerate(zip(
                                midx, V_list, partial_x_V_list, partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                hess_x_V[:,i] *= p2xV1d[:,idx]
                            elif j == d1 or j == d2:
                                hess_x_V[:,i] *= pxV1d[:,idx]
                            else:
                                hess_x_V[:,i] *= V1d[:,idx]
                    hess_x_V_mat[d1,d2] = hess_x_V
            precomp['hess_x_V_mat'] = hess_x_V_mat
        return precomp

    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_V_mat = precomp['hess_x_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
            except (TypeError,KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
            out = np.zeros((x.shape[0],self.dim,self.dim))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                tmp *= p2xV1d[idxs_slice,idx]
                            elif j == d1 or j == d2:
                                tmp *= pxV1d[idxs_slice,idx]
                            else:
                                tmp *= V1d[idxs_slice,idx]
                        out[:,d1,d2] += c * tmp
        else:
            out = np.zeros((x.shape[0],self.dim,self.dim))
            for i in range(self.dim):
                for j in range(self.dim):
                    out[idxs_slice,i,j] = np.dot( hess_x_V_mat[i,j][idxs_slice,:],
                                                  self._coeffs )
        return out

    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d,d`]) --
            :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_V_mat = precomp['hess_x_V_mat']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                precomp = self.precomp_evaluate(x)
            except TypeError as e:
                x = x[idxs_slice,:]
                precomp = self.precomp_evaluate(x)
                idxs_slice = slice(None)
            finally:
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            out = np.zeros((x.shape[0], self.n_coeffs, self.dim,self.dim))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    cidx = 0
                    for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if d1 == d2 and j == d1:
                                tmp *= p2xV1d[idxs_slice,idx]
                            elif j == d1 or j == d2:
                                tmp *= pxV1d[idxs_slice,idx]
                            else:
                                tmp *= V1d[idxs_slice,idx]
                        out[:,cidx,d1,d2] += tmp#*(c != 0)
                        cidx = cidx + 1
        else:
            out = np.zeros((x.shape[0], self.n_coeffs, self.dim,self.dim))
            #coeff_ind = [int(x != 0) for x in self._coeffs]
            for i in range(self.dim):
                for j in range(self.dim):
                    out[idxs_slice,:,i,j] = hess_x_V_mat[i,j][idxs_slice,:]#np.dot(hess_x_V_mat[i,j][idxs_slice,:], coeff_ind)
        return out

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            :math:`\nabla_{\bf a} f_{\bf a}({\bf x})`
        """
        try:
            V = precomp['V']
        except KeyError as e:
            if 'V_list' not in precomp:
                idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
        except TypeError as e:
            idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
        finally:
            V = precomp['V']
        return V[idxs_slice,:]

    def grad_a_t(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\nabla_{\bf a} f_{\bf a}\right)^T` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            :math:`\left(\nabla_{\bf a} f_{\bf a}({\bf x}\right)^T)`
        """
        try:
            VT = precomp['VT']
        except (TypeError, KeyError) as e:
            try:
                V = precomp['V']
            except KeyError:
                if 'V_list' not in precomp:
                    idxs_slice = slice(None)
                precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            except TypeError:
                idxs_slice = slice(None)
                precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            finally:
                V = precomp['V']
            VT = np.transpose(V).copy()
            precomp['VT'] = VT
        return VT[:,idxs_slice]

    def precomp_VVT_evaluate(self, x, precomp=None):
        r""" Precompute the product :math:`VV^T` of the multi-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the desired product
        """
        try:
            V = precomp['V']
        except (TypeError, KeyError) as e:
            precomp = self.precomp_Vandermonde_evaluate(x, precomp)
            V = precomp['V']
        precomp['VVT'] = V[:,:,nax] * V[:,nax,:]
        return precomp

    def grad_a_squared(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\nabla_{\bf a} f_{\bf a}\right)\left(\nabla_{\bf a} f_{\bf a}\right)^T` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
            :math:`\left(\nabla_{\bf a} f_{\bf a}\right)\left(\nabla_{\bf a} f_{\bf a}\right)^T`
        """
        try:
            VVT = precomp['VVT']
        except KeyError:
            if 'V_list' not in precomp:
                idxs_slice = slice(None)
            precomp = self.precomp_VVT_evaluate(x, precomp)
        except TypeError:
            idxs_slice = slice(None)
            precomp = self.precomp_VVT_evaluate(x, precomp)
        finally:
            VVT = precomp['VVT']
        return VVT[idxs_slice,:,:]

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
            :math:`\nabla^2_{\bf a} f_{\bf a}({\bf x})`
        """
        return np.zeros((1,1,1))

    def precomp_Vandermonde_partial_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrix for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: partial_xd_V = precomp['partial_xd_V']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_xd_V_last = precomp['partial_xd_V_last']
            except KeyError as e:
                self.precomp_partial_xd(x, precomp)
                partial_xd_V_last = precomp['partial_xd_V_last']
            partial_xd_V = np.ones((V_list[0].shape[0], self.n_coeffs))
            for i, midx in enumerate(self.multi_idxs):
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    partial_xd_V[:,i] *= V1d[:,idx]
                partial_xd_V[:,i] *= partial_xd_V_last[:,midx[-1]]
            precomp['partial_xd_V'] = partial_xd_V
        return precomp

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial_{x_d} f_{\bf a}({\bf x})`
        """
        # Retrieve from cache
        try:
            (batch_set, vals) = precomp['cached_partial_xd']
        except (TypeError, KeyError) as e:
            cached_flag = False
        else:
            cached_flag = True
            if batch_set[idxs_slice][0]: # Checking only the first is enough..
                return vals[idxs_slice]
        # Evaluation
        try:
            partial_xd_V = precomp['partial_xd_V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_xd_V_last = precomp['partial_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_partial_xd(x, precomp)
                V_list = precomp['V_list']
                partial_xd_V_last = precomp['partial_xd_V_last']
            tot_size = V_list[0].shape[0]
            out = np.zeros(x.shape[0])
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                tmp[:] = 1.
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    tmp *= V1d[idxs_slice,idx]
                tmp *= partial_xd_V_last[idxs_slice,midx[-1]]
                out += c * tmp
        else:
            tot_size = partial_xd_V.shape[0]
            out = np.dot(partial_xd_V[idxs_slice,:], self._coeffs)
        # Store in cache
        if cached_flag: 
            vals[idxs_slice] = out
            batch_set[idxs_slice] = True
        return out
    
    def precomp_Vandermonde_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of multi-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except KeyError as e:
                self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            grad_x_partial_xd_V_list = []
            # TODO: Accelerate these loops?
            for d in range(self.dim):
                grad_x_partial_xd_V = np.ones((x.shape[0], self.n_coeffs))
                for i, midx in enumerate(self.multi_idxs):
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim-1):
                            grad_x_partial_xd_V[:,i] *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim-1):
                            grad_x_partial_xd_V[:,i] *= pxV1d[:,idx]
                        else:
                            grad_x_partial_xd_V[:,i] *= V1d[:,idx]
                grad_x_partial_xd_V_list.append( grad_x_partial_xd_V )
            precomp['grad_x_partial_xd_V_list'] = grad_x_partial_xd_V_list
        return precomp

    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros( x.shape )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d in range(self.dim):
                for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim-1):
                            tmp *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim-1):
                            tmp *= pxV1d[:,idx]
                        else:
                            tmp *= V1d[:,idx]
                    out[:,d] += c * tmp
        else:
            out = np.zeros( x.shape )
            for i in range( self.dim ):
                out[:,i] = np.dot(
                    grad_x_partial_xd_V_list[i][idxs_slice,:], self._coeffs )
        return out

    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla_{\bf a}\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            grad_x_partial_xd_V_list = precomp['grad_x_partial_xd_V_list']
        except (TypeError, KeyError) as e:
            try: V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                precomp = self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros((x.shape[0], self.n_coeffs, self.dim))
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d in range(self.dim):
                cidx = 0
                for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                    tmp[:] = 1.
                    for j, (idx, V1d, pxV1d) in enumerate(zip(midx, V_list,
                                                              partial_x_V_list)):
                        if j == d and d == (self.dim-1):
                            tmp *= partial2_xd_V_last[:,idx]
                        elif j == d or j == (self.dim-1):
                            tmp *= pxV1d[:,idx]
                        else:
                            tmp *= V1d[:,idx]
                    out[:,cidx,d] += tmp#*(c != 0)
                    cidx = cidx + 1
        else:
            out = np.zeros((x.shape[0], self.n_coeffs, self.dim))
            #coeff_ind = [int(x != 0) for x in self._coeffs]
            for i in range( self.dim ):
                out[:,:,i] = grad_x_partial_xd_V_list[i]#np.dot(grad_x_partial_xd_V_list[i], coeff_ind)
        return out

    def precomp_Vandermonde_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<ndarray>` [d,d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with list of Vandermonde matrices for the computation
            of the gradient.
        """
        if precomp is None: precomp = {}
        try: hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except KeyError as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial_x_V_list = precomp['partial_x_V_list']
            except KeyError as e:
                self.precomp_grad_x(x, precomp)
                partial_x_V_list = precomp['partial_x_V_list']
            try: partial2_x_V_list = precomp['partial2_x_V_list']
            except KeyError as e:
                self.precomp_hess_x(x, precomp)
                partial2_x_V_list = precomp['partial2_x_V_list']
            try: partial3_xd_V_last = precomp['partial3_xd_V_last']
            except KeyError as e:
                self.precomp_partial3_xd(x, precomp)
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            hess_x_partial_xd_V_mat = np.empty((self.dim,self.dim),dtype=object)
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    hess_x_partial_xd_V = np.ones((x.shape[0], self.n_coeffs))
                    for i, midx in enumerate(self.multi_idxs):
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim-1):
                                hess_x_partial_xd_V[:,i] *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim-1) \
                                 or j == d2 == (self.dim-1):
                                hess_x_partial_xd_V[:,i] *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim-1):
                                hess_x_partial_xd_V[:,i] *= pxV1d[:,idx]
                            else:
                                hess_x_partial_xd_V[:,i] *= V1d[:,idx]
                    hess_x_partial_xd_V_mat[d1,d2] = hess_x_partial_xd_V
            precomp['hess_x_partial_xd_V_mat'] = hess_x_partial_xd_V_mat
        return precomp

    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                precomp.pop('partial3_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                precomp = self.precomp_partial3_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            out = np.zeros( (x.shape[0], self.dim, self.dim) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim-1):
                                tmp *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim-1) \
                                 or j == d2 == (self.dim-1):
                                tmp *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim-1):
                                tmp *= pxV1d[:,idx]
                            else:
                                tmp *= V1d[:,idx]
                        out[:,d1,d2] += c * tmp
        else:
            out = np.zeros( (x.shape[0], self.dim, self.dim) )
            for i in range( self.dim ):
                for j in range(self.dim):
                    out[:,i,j] = np.dot( hess_x_partial_xd_V_mat[i,j], self._coeffs )
        return out

    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            hess_x_partial_xd_V_mat = precomp['hess_x_partial_xd_V_mat']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial_x_V_list', None)
                precomp.pop('partial2_x_V_list', None)
                precomp.pop('partial3_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_grad_x(x, precomp)
                precomp = self.precomp_hess_x(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                precomp = self.precomp_partial3_xd(x, precomp)
                V_list = precomp['V_list']
                partial_x_V_list = precomp['partial_x_V_list']
                partial2_x_V_list = precomp['partial2_x_V_list']
                partial3_xd_V_last = precomp['partial3_xd_V_last']
            out = np.zeros( (x.shape[0], self.n_coeffs, self.dim, self.dim) )
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for d1 in range(self.dim):
                for d2 in range(self.dim):
                    for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                        tmp[:] = 1.
                        for j, (idx, V1d,
                                pxV1d, p2xV1d) in enumerate(zip(midx, V_list,
                                                                partial_x_V_list,
                                                                partial2_x_V_list)):
                            if j == d1 == d2 == (self.dim-1):
                                tmp *= partial3_xd_V_last[:,idx]
                            elif j == d1 == d2 or j == d1 == (self.dim-1) \
                                 or j == d2 == (self.dim-1):
                                tmp *= p2xV1d[:,idx]
                            elif j == d1 or j == d2 or j == (self.dim-1):
                                tmp *= pxV1d[:,idx]
                            else:
                                tmp *= V1d[:,idx]
                        out[:,i,d1,d2] = tmp
        else:
            out = np.zeros( (x.shape[0], self.n_coeffs, self.dim, self.dim) )
            for i in range( self.dim ):
                for j in range(self.dim):
                    out[:,:,i,j] = hess_x_partial_xd_V_mat[i,j]
        return out

    def precomp_Vandermonde_partial2_xd(self, x, precomp=None):
        r""" Precompute multi-variate Vandermonde matrix for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: partial2_xd_V = precomp['partial2_xd_V']
        except KeyError as e:
            try: V_list = precomp['V_list']
            except (TypeError, KeyError) as e:
                self.precomp_evaluate(x, precomp)
                V_list = precomp['V_list']
            try: partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                self.precomp_partial2_xd(x, precomp)
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            partial2_xd_V = np.ones((x.shape[0], self.n_coeffs))
            # TODO: Accelerate these loops?
            for i, midx in enumerate(self.multi_idxs):
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    partial2_xd_V[:,i] *= V1d[:,idx]
                partial2_xd_V[:,i] *= partial2_xd_V_last[:,midx[-1]]
            precomp['partial2_xd_V'] = partial2_xd_V
        return precomp

    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial^2_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            partial2_xd_V = precomp['partial2_xd_V']
        except (TypeError, KeyError) as e:
            try:
                V_list = precomp['V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            except (TypeError, KeyError) as e:
                # Clean pre-existing
                precomp.pop('V_list', None)
                precomp.pop('partial2_xd_V_last', None)
                # Ignoring slice
                idxs_slice = slice(None)
                # Compute
                precomp = self.precomp_evaluate(x, precomp)
                precomp = self.precomp_partial2_xd(x, precomp)
                V_list = precomp['V_list']
                partial2_xd_V_last = precomp['partial2_xd_V_last']
            out = np.zeros(x.shape[0])
            tmp = np.ones(x.shape[0])
            # TODO: Accelerate these loops?
            for i, (c, midx) in enumerate(zip(self._coeffs,self.multi_idxs)):
                tmp[:] = 1.
                for idx, V1d in zip(midx[:-1], V_list[:-1]):
                    tmp *= V1d[:,idx]
                tmp *= partial2_xd_V_last[:,midx[-1]]
                out += c * tmp
        else:
            out = np.dot(partial2_xd_V, self._coeffs)
        return out

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try:
            partial_xd_V = precomp['partial_xd_V']
        except KeyError as e:
            if 'V_list' not in precomp or 'partial_xd_V_last' not in precomp:
                idxs_slice = slice(None)
                precomp.pop('V_list', None)
                precomp.pop('partial_xd_V_last', None)
            precomp = self.precomp_Vandermonde_partial_xd(x, precomp)
        except TypeError as e:
            idxs_slice = slice(None)
            precomp = self.precomp_Vandermonde_partial_xd(x, precomp)
        finally:
            partial_xd_V = precomp['partial_xd_V']
        return partial_xd_V[idxs_slice,:]

    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        nc = self.n_coeffs
        return np.zeros( (x.shape[0], nc, nc) )
        
    def precomp_regression(self, x, precomp=None, *args, **kwargs):
        r""" Precompute necessary structures for the speed up of :func:`regression`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary to be updated

        Returns:
           (:class:`dict<dict>`) -- dictionary of necessary strucutres
        """
        if precomp is None:
            precomp = {}
        precomp.update( self.precomp_evaluate(x) )
        return precomp

    def regression(self, f, fparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None,
                   regularization=None, tol=1e-4, maxit=100,
                   batch_size=(None,None), mpi_pool=None, import_set=set()):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

        Args:
          f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`f` or its functions values
          d (Distribution): distribution :math:`\pi`
          fparams (dict): parameters for function :math:`f`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size (:class:`list<list>` [2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)

        Returns:
          (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
          :class:`list<list>`)) -- containing the :math:`N` coefficients and
          log information from the optimizer.

        .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`coeffs` in order
           to retrieve them.
        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        self.mpi_pool = mpi_pool
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
        params = {}
        params['x'] = x
        params['w'] = w
        params['regularization'] = regularization
        params['batch_size'] = batch_size
        params['nobj'] = 0
        params['nda_obj'] = 0
        options = {'maxiter': maxit,
                   'disp': False}
        # Zero initial condition
        if x0 is None:
            x0 = np.zeros( self.n_coeffs )
        # Precomputation
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation started")
        # Prepare parameters
        if isinstance(f, np.ndarray):
            params['fvals'] = f
        else:
            scatter_tuple = (['x'], [x])
            bcast_tuple = (['precomp'], [fparams])
            params['fvals'] = TM.mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                                          bcast_tuple=bcast_tuple,
                                          obj=f, mpi_pool=self.mpi_pool)
        # Init precomputation memory
        (_, params['params1']) = TM.mpi_eval("init_mem_precomp_regression",
                                             dmem_key_out_list=['params1'],
                                             obj=self, mpi_pool=self.mpi_pool,
                                             concatenate=False)
        scatter_tuple = (['x'], [x])
        TM.mpi_eval("precomp_regression", scatter_tuple=scatter_tuple,
                    dmem_key_in_list=['params1'],
                    dmem_arg_in_list=['precomp'],
                    dmem_val_in_list=[params['params1']],
                    obj=self, mpi_pool=self.mpi_pool,
                    concatenate=False)
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation ended")
        # Solve
        res = sciopt.minimize(self.regression_objective, x0, args=params, \
                              jac=self.regression_grad_a_objective,
                              method='BFGS', options=options, tol=tol)
        if not res['success']:
            self.logger.warn("Regression failure: " + res['message'])
        coeffs = res['x']
        self.coeffs = coeffs
        self.mpi_pool = None
        return (coeffs, res)

    @staticmethod
    def from_xml_element(node, dim):
        import TransportMaps.Functionals as FUNC
        from TransportMaps import XML_NAMESPACE
        # Check span type
        multidimtype = node.attrib['multidimtype'] 
        if multidimtype == 'tensorized':
            stype = node.attrib['spantype']
            if stype == 'total' or stype == 'full':
                span_node = node.find(XML_NAMESPACE + 'spanorder')
                # Retrieve the list of orders
                order_list = LinearSpanApproximation.order_list_from_xml_element(
                    span_node, dim)
                # Retrieve the list of basis
                basis_list = LinearSpanApproximation.basis_list_from_xml_element(
                    node, dim)
                return LinearSpanApproximation(basis_list, spantype=stype, order_list=order_list)
            elif stype == 'midx':
                midxlist_node = node.find(XML_NAMESPACE + 'midxlist')
                # Retrieve the list of multi-indices
                midx_list = LinearSpanApproximation.midx_list_from_xml_element(
                    midxlist_node, dim)
                # Retrieve the list of basis
                basis_list = LinearSpanApproximation.basis_list_from_xml_element(
                    node, dim)
                return LinearSpanApproximation(basis_list, spantype=stype, midx_list=midx_list)
            raise ValueError("No recognizable spantype provided (%s)" % stype)
        raise ValueError("No recognizable multidimtype provided (%s)" % multidimtype)

    @staticmethod
    def basis_list_from_xml_element(node, dim):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps.XML as TMXML
        from TransportMaps import XML_NAMESPACE
        basis_list = [None for d in range(dim)]
        basis_nodes_list = node.findall(XML_NAMESPACE + 'spanbasis')
        for basis_node in basis_nodes_list:
            coord = basis_node.attrib['coord']
            rng = TMXML.vars_parser(coord, dim-1)
            for d in rng:
                basis_list[d] = S1D.from_xml_element(basis_node)
        # Check all basis have been provided
        if None in basis_list:
            raise ValueError("The basis for some dimensions have not been defined")
        return basis_list

    @staticmethod
    def midx_list_from_xml_element(node, dim):
        from TransportMaps import XML_NAMESPACE
        import TransportMaps.XML as TMXML
        midx_list = [TMXML.midx_parser(midx_node.text) for midx_node in
                     node.findall(XML_NAMESPACE + 'midx') ]
        return midx_list

    @staticmethod
    def order_list_from_xml_element(node, dim):
        import TransportMaps.XML as TMXML
        from TransportMaps import XML_NAMESPACE
        order_list = [None for d in range(dim)]
        maxord_nodes_list = node.findall(XML_NAMESPACE + 'maxord')
        for maxord_node in maxord_nodes_list:
            coord = maxord_node.attrib['coord']
            rng = TMXML.vars_parser(coord, dim-1)
            order = int(maxord_node.text)
            for d in rng:
                order_list[d] = order
        # Check all orders have been provided
        if None in order_list:
            raise ValueError("The orders for some dimensions have not been defined")
        return order_list