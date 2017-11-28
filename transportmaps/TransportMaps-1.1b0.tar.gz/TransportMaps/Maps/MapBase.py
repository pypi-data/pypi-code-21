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

import TransportMaps as TM

__all__ = ['Map', 'ParametricMap',
           'LinearMap', 'ConditionallyLinearMap']

nax = np.newaxis

class Map(TM.TMO):
    r""" Abstract map :math:`T:\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`

    Args:
      dim_in (int): input dimension :math:`d_x`
      dim_out (int): output dimension :math:`d_y`
    """
    def __init__(self, dim_in, dim_out):
        super(Map, self).__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.dim = None
        if self.dim_in == self.dim_out:
            self.dim = self.dim_in

    def __call__(self, x):
        r"""
        Calls :func:`evaluate`.
        """
        return self.evaluate( x )

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate the map :math:`T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate the gradient :math:`\nabla_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate the Hessian :math:`\nabla^2_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_y,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

class ParametricMap(Map):
    r""" Abstract map :math:`T:\mathbb{R}^{d_a}\times\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`

    Args:
      dim_in (int): input dimension :math:`d_x`
      dim_out (int): output dimension :math:`d_y`
    """    
    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
          (:class:`int`) -- total number :math:`N` of
              coefficients characterizing the map.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def get_n_coeffs(self):
        TM.deprecate("ParametricMap.get_n_coeffs()", "1.0b3",
                     "Use property ParametricMap.n_coeffs instead")
        return self.n_coeffs
        
    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def get_coeffs(self):
        TM.deprecate("ParametricMap.get_coeffs()", "1.0b3",
                     "Use property ParametricMap.coeffs instead")
        return self.coeffs
    
    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def set_coeffs(self, coeffs):
        TM.deprecate("ParametricMap.set_coeffs(value)", "1.0b3",
                     "Use setter ParametricMap.coeffs = value instead.")
        self.coeffs = coeffs

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla_{\bf a} T({\bf x},{\bf a})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- gradient

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla^2_{\bf a} T({\bf x},{\bf a})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- Hessian

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")
        
class LinearMap(Map):
    r""" Map :math:`T({\bf x}) = {\bf c} + {\bf T} {\bf x}`

    Args:
      c (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): constant part
      T (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_x`]): linear part (matrix)
    """
    def __init__(self, c, T):
        if c.shape[0] != T.shape[0]:
            raise ValueError("The dimensions of the constant and the " + \
                             "linear part must match")
        super(LinearMap, self).__init__(T.shape[1], T.shape[0])
        self._c = c
        self._T = T

    @property
    def c(self):
        return self._c

    @property
    def T(self):
        return self._T

    def evaluate(self, x, *args, **kwargs):
        return self.c + self.T.dot(x.T).T

    def grad_x(self, x, *args, **kwargs):
        return self.T[nax,:,:]

    def hess_x(self, x, *args, **kwargs):
        return np.zeros((1, self.dim_out, self.dim_in, self.dim_in))

class ConditionallyLinearMap(Map):
    r""" Map :math:`T:\mathbb{R}^{d_x}\times\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}` defined by :math:`T({\bf x};{\bf a}) = {\bf c}({\bf a}) + {\bf T}({\bf a}) {\bf x}`

    Args:
      c (:class:`Map`): map :math:`{\bf c}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}`
      T (:class:`Map`):
        map :math:`{\bf T}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y\times d_x}`
      coeffs (:class:`ndarray<numpy.ndarray>`): fixing the coefficients :math:`{\bf a}` defining
        :math:`{\bf c}({\bf a})` and :math:`{\bf T}({\bf a})`.
    """
    def __init__(self, c, T, coeffs=None):
        if c.dim_in != T.dim_in:
            raise ValueError("Input dimension mismatch between c and T")
        if T.dim_out % c.dim_out != 0:
            raise ValueError("Output dimension mismatch between c and T")
        self._n_coeffs = c.dim_in
        self._cMap = c
        self._TMap = T
        din = T.dim_out // c.dim_out
        dout = c.dim_out
        super(ConditionallyLinearMap,self).__init__(
            din + self.n_coeffs, dout)
        self._coeffs = None
        self.coeffs = coeffs
        
    @property
    def c(self):
        return self._c

    @property
    def T(self):
        return self._T
        
    @property
    def n_coeffs(self):
        return self._n_coeffs

    @property
    def dim_lin(self):
        return self.dim_in - self.n_coeffs

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps
        """
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            self._c = self._cMap.evaluate(coeffs[nax,:])[0,:]
            self._T = self._TMap.evaluate(coeffs[nax,:])[0,:,:]
            try:
                self._grad_a_c = self._cMap.grad_x(coeffs[nax,:])[0,:,:]
                self._grad_a_T = self._TMap.grad_x(coeffs[nax,:])[0,:,:,:]
            except NotImplementedError:
                self._grad_a_c = None
                self._grad_a_T = None
            try:
                self._hess_a_c = self._cMap.hess_x(coeffs[nax,:])[0,:,:,:]
                self._hess_a_T = self._TMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
            except NotImplementedError:
                self._hess_a_c = None
                self._hess_a_T = None
            self._coeffs = coeffs

    @property
    def grad_a_c(self):
        return self._grad_a_c

    @property
    def grad_a_T(self):
        return self._grad_a_T

    @property
    def hess_a_c(self):
        return self._hess_a_c

    @property
    def hess_a_T(self):
        return self._hess_a_T

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate the map :math:`T` at the points :math:`{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points
        """
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                c = self._cMap.evaluate(cf)[0,:]
                T = self._TMap.evaluate(cf)[0,:,:]
                out[i,:] = c + np.dot(T, xx)
        else:
            xx = x[:,:self.dim_lin]
            out = self.c + np.dot(self.T, xx.T).T
        return out

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out, self.dim_in))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                T = self._TMap.evaluate(cf)[0,:,:]
                gac = self._cMap.grad_x(cf)[0,:,:]
                gaT = self._TMap.grad_x(cf)[0,:,:,:]
                out[i,:,:self.dim_lin] = T
                out[i,:,self.dim_lin:] = gac + np.einsum('ijk,j->ik', gaT, xx)
        else:
            raise NotImplementedError("To be done")
        return out
        
class ConstantMap(Map):
    r""" Map :math:`T({\bf x})={\bf c}`

    Args:
       dim_in (int): input dimension :math:`d_x`
       const (:class:`ndarray<numpy.ndarray>`): constant :math:`{\bf c}`
    """
    def __init__(self, dim_in, const):
        self._const = const
        super(ConstantMap, self).__init__(dim_in, const.size)

    @property
    def const(self):
        return self._const
        
    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tpl = tuple([nax] + [slice(None)] * self._const.ndim)
        return self._const[tpl]

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        shp = (1,) + self._const.shape + (self.dim_in,)
        return np.zeros(shp)

    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        shp = (1,) + self._const.shape + (self.dim_in,self.dim_in)
        return np.zeros(shp)