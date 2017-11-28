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

import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt
import scipy.linalg as scila
from  TransportMaps.Distributions import *
import sys
import scipy.sparse as scisp
import copy as cp


from TransportMaps.Maps.TransportMapBase import *

__all__ = ['LinearTransportMap']

class LinearTransportMap(TransportMap):
    r""" Linear map :math:`T({\bf x})={\bf c} + {\bf L}{\bf x}`

    Args:
      constantTerm (:class:`ndarray<numpy.ndarray>` [:math:`d`]): term :math:`{\bf c}`
      linearTerm (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): term :math:`{\bf L}`
      log_det (float): :math:`\log\det{\bf L}`, only required if
        :math:`{\bf L}` is in the sparse format
        :module:`scipy.sparse<scipy.sparse>`.
    """
    def __init__(self, constantTerm, linearTerm, log_det = None):
        if len(constantTerm) != linearTerm.shape[0]:
            raise ValueError("Inconsistent dimensions")
        if linearTerm.shape[0] != linearTerm.shape[1]:
            raise ValueError("Inconsistent dimensions")

        if scisp.issparse(linearTerm):
            if log_det is None:
                raise ValueError("We did not implement the log-determinant of sparse matrices yet")
        else:
            #Make sure it is monotone increasing and invertible
            p,l,u  = scila.lu(linearTerm)
            diagu = np.nonzero( abs(np.diag(u))<1e-12 )
            if len(diagu[0])>0:
                raise ValueError("The map might not be increasing")
            sign_log_det , log_det =  np.linalg.slogdet(linearTerm)


        # if sign_log_det<0:
        #   raise ValueError("The map should be monotone increasing")
        self.dim = self.dim_in = self.dim_out = len(constantTerm)
        self.constantTerm = cp.deepcopy(constantTerm)
        self.linearTerm = cp.deepcopy(linearTerm) #Make sure the copy is valid even when the matrices are sparse
        self.log_det_linearTerm = log_det

    @property
    def c(self):
        r""" The constant term :math:`{\bf c}`
        """
        return self.constantTerm

    @c.setter
    def c(self, value):
        if len(value) != self.dim_out:
            raise ValueError("Inconsistent dimensions")
        self.constantTerm = value
        
    @property
    def L(self):
        r""" The linear term :math:`{\bf L}`
        """
        return self.linearTerm

    @L.setter
    def L(self, value):
        if self.dim != value.shape[0]:
            raise ValueError("Inconsistent dimensions")
        if value.shape[0] != value.shape[1]:
            raise ValueError("Inconsistent dimensions")
        #Make sure it is monotone increasing and invertible
        p,l,u  = scila.lu(value)
        diagu = np.nonzero( abs(np.diag(u))<1e-12 )
        if len(diagu[0])>0:
          raise ValueError("The map might not be increasing")
        sign_log_det , log_det =  np.linalg.slogdet(value)
        if sign_log_det<0:
          raise ValueError("The map should be monotone increasing")
        self.linearTerm = value
        self.log_det_linearTerm = log_det
        
    @staticmethod
    def build_from_Gaussian(pi , typeMap = "Sym"):
        r""" Build a linear transport map from a
        standard normal to a Gaussian distribution pi

        Args:
           pi (:class:`GaussianDistribution`):
              constant term of the linear map
        Raises:
           ValueError: if the shape of linear and constant term are inconsistent.
        """
        if not isinstance(pi, GaussianDistribution):
          raise ValueError("The input distribution should be a Gaussian")
        if typeMap == "Sym":
          try:
              U, s, V = np.linalg.svd(pi.sigma)
              s_sr = np.sqrt(s)
              linearTerm_sr = np.dot( U , np.diag( np.sqrt(s_sr) ) )
              linearTerm = np.dot( linearTerm_sr, linearTerm_sr.transpose() )
          except AttributeError:
              U, s, V = np.linalg.svd(pi.inv_sigma)
              s_inv_sr = np.sqrt(1./s)
              linearTerm_sr = np.dot( U , np.diag( np.sqrt(s_inv_sr) ) )
              linearTerm = np.dot( linearTerm_sr, linearTerm_sr.transpose() )
        elif typeMap == "Tri":
          try:
              linearTerm = np.linalg.cholesky(pi.sigma)
          except AttributeError:
              sigma = np.linalg.inv(pi.inv_sigma)
              linearTerm = np.linalg.cholesky(sigma)
        else:
           raise ValueError("Type of the map not supported yet")
        constantTerm = pi.mu
        return LinearTransportMap(constantTerm, linearTerm)

    @property
    def coeffs(self):
        r""" Returns the constant and linear term of the linear map.

        Returns:
           (:class:`ndarray<numpy.ndarray>`, :class:`ndarray<numpy.ndarray>`) --
           tuple (constant term, linear term)
        """
        return self.constantTerm, self.linearTerm

    @coeffs.setter
    def set_coeffs(self, constantTerm, linearTerm):
        r""" Set the constant and linear term of the linear map.

        Args:
           constantTerm (:class:`ndarray<numpy.ndarray>`):
              constant term of the linear map
           linearTerm (:class:`ndarray<numpy.ndarray>`):
              linear term of the linear map
        Raises:
           ValueError: if the shape of linear and constant term are inconsistent.
        """
        if len(constantTerm) != linearTerm.shape[0]:
            raise ValueError("Inconsistent dimensions")
        if linearTerm.shape[0] != linearTerm.shape[1]:
            raise ValueError("Inconsistent dimensions")
        #Make sure it is monotone increasing and invertible
        p,l,u  = scila.lu(linearTerm)
        diagu = np.nonzero( abs(np.diag(u))<1e-12 )
        if len(diagu[0])>0:
          raise ValueError("The map might not be increasing")
        sign_log_det , log_det =  np.linalg.slogdet(linearTerm)
        if sign_log_det<0:
          raise ValueError("The map should be monotone increasing")
        self.constantTerm = np.copy(constantTerm)
        self.linearTerm = np.copy(linearTerm)
        self.log_det_linearTerm = log_det

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate the transport map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        #Implementation valid also for sparse linear terms
        out = np.transpose( self.linearTerm.dot( x.transpose() ) ) + self.constantTerm 
        #out =  np.dot( x,self.linearTerm.transpose() ) + self.constantTerm
        return out

    def grad_x(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} \hat{T}({\bf x},{\bf a})`.

         .. math::
            :nowrap:

            \nabla_{\bf x} \hat{T}({\bf x},{\bf a}) =
                 \begin{bmatrix}
                 \nabla_{\bf x}  \hat{T}_1({\bf x},{\bf a})  \\
                 \nabla_{\bf x}  \hat{T}_2({\bf x},{\bf a})  \\
                 \vdots \\
                 \nabla_{\bf x}  \hat{T}_d({\bf x},{\bf a})
                 \end{bmatrix}

         for every evaluation point.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]) --
           gradient matrix (constant at every evaluation point).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """

        if scisp.issparse(self.linearTerm):
            grad = self.linearTerm.toarray()
        else:
            grad = self.linearTerm

        return grad[np.newaxis,:]

    def hess_x(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} \hat{T}({\bf x},{\bf a})`.

            Args:
            x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

            Returns:
            (:class:`ndarray<numpy.ndarray>` [:math:`d,d,d`]) --
            Hessian matrix (zero everywhere).

            Raises:
            ValueError: if :math:`d` does not match the dimension of the transport map.
            """
        return np.zeros((self.dim, self.dim, self.dim))

    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} \hat{T}^{-1}({\bf x},{\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]) --
           gradient matrix (constant at every evaluation point).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if np.allclose(self.linearTerm, np.tril(self.linearTerm)):
            return scila.solve_triangular(self.linearTerm, np.eye(self.dim),
                                          lower=True)
        else:
            raise NotImplementedError("Not implemented at this time...")

    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} \hat{T}^{-1}({\bf x},{\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`d,d,d`]) --
           Hessian matrix (zero everywhere).

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.zeros((self.dim, self.dim, self.dim))

    def log_det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`float`) --
           :math:`\log \det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`
           (constant at every evaluation point)

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return self.log_det_linearTerm

    def det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`float`) --
           :math:`\det \nabla_{\bf x} \hat{T}({\bf x}, {\bf a})`
           (constant at every evaluation point)

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.exp(self.log_det_linearTerm)

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        return np.zeros((x.shape[0],self.dim))

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (float) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           (constant at every evaluation point)
        """
        return - self.log_det_linearTerm

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim))

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim,self.dim))

    def inverse(self, y, *args, **kwargs):
        r""" Compute: :math:`\hat{T}^{-1}({\bf y},{\bf a})`

        Args:
           y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\hat{T}^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        if y.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = npla.solve(self.linearTerm, (y - self.constantTerm).T).T
        return out

    def grad_x_log_pullback(self, pi, x, params_t=None, params_pi=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\nabla_{\bf x}\left[ \log \pi \circ \hat{T}({\bf x,a}) + \log \vert\det \nabla_{\bf x}\hat{T}({\bf x,a})\vert \right]`

        Args:
           pi (:class:`Distributions.Distribution`): distribution to be pulled back
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x}\left[ \log \pi \circ \hat{T}({\bf x,a}) + \log \vert\det \nabla_{\bf x}\hat{T}({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_pullback`, :func:`grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.einsum( '...i,...ij->...j',
                         pi.grad_x_log_pdf(self.evaluate(x, params_t, idxs_slice), params_pi),
                         self.grad_x(x, params_t, idxs_slice) )
        return  out

    def hess_x_log_pullback(self, pi, x, params_t=None, params_pi=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla^2_{\bf x}\left[ \log \pi \circ \hat{T}({\bf x,a}) + \log \vert\det \nabla_{\bf x}\hat{T}({\bf x,a})\vert \right]`.

        Args:
           pi (:class:`Distributions.Distribution`): distribution to be pulled back
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x}\left[ \log \pi \circ \hat{T}({\bf x,a}) + \log \vert\det \nabla_{\bf x}\hat{T}({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_x_log_pullback`, :func:`log_pullback`, :func:`grad_x`, :func:`hess_x` and :func:`hess_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        dx2logpi = pi.hess_x_log_pdf(
            self.evaluate(x, params_t, idxs_slice), params_pi )
        dxT = self.grad_x(x, params_t, idxs_slice)
        A = np.einsum('...kl,...lj->...kj',dx2logpi, dxT) #Hess logpi * grad_T
        out = np.einsum('...lk,...lj->...kj', dxT,A)
        return out
