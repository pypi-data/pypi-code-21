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

import warnings
import numpy as np
import scipy.linalg as scila

from TransportMaps.Functionals.FrozenMonotonicFunctions import \
    FrozenLinear, FrozenExponential, FrozenGaussianToUniform

from TransportMaps.Maps.TriangularTransportMapBase import *

__all__ = ['FrozenLinearDiagonalTransportMap',
           'FrozenExponentialDiagonalTransportMap',
           'FrozenGaussianToUniformDiagonalTransportMap',
           'FrozenBananaTransportMap']

nax = np.newaxis

class FrozenLinearDiagonalTransportMap(MonotonicTriangularTransportMap):
    r""" Linear diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (a_1+b_1 x_1, \ldots, a_d + b_d x_d)`

    Args:
       a (:class:`ndarray<numpy.ndarray>` [:math:`d`]): coefficients
       b (:class:`ndarray<numpy.ndarray>` [:math:`d`]): coefficients

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and :class:`FunctionalApproximations.FrozenLinear`
       for a description of the linear approximation used for each component.
    """

    def __init__(self, a, b):
        if len(a) != len(b):
            raise ValueError("Dimension mismatch")
        dim = len(a)
        self.a = a
        self.b = b
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append( FrozenLinear(1, a[d], b[d]) )
            active_vars.append( [d] )
        super(FrozenLinearDiagonalTransportMap, self).__init__(active_vars, approx_list)

    @property
    def n_coeffs(self):
        return len(self.a)*2

    def set_coeffs(self, a, b):
        raise NotImplementedError("This is a frozen transport map")

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = self.a[nax,:] + self.b[nax,:] * x
        return xout

    def grad_x(self, x, *args, **kwargs):
        r""" This is a diagonal map """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        out += np.diag(self.b)[nax,:,:]
        return out

    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.prod( self.b )

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.sum( np.log(self.b) )

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((x.shape[0], self.dim))

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((x.shape[0], self.dim, self.dim))

    def regression(self, x, w, F, REG, tol):
        r"""
        Raises:
           NotImplementedError: this is a frozen transport map.
        """
        raise NotImplementedError("This is a frozen transport map.")

class FrozenExponentialDiagonalTransportMap(MonotonicTriangularTransportMap):
    r""" Exponential diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (\exp(x_1), \ldots, \exp(x_d))`

    Args:
       dim (int): dimension :math:`d` of the transport map

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and
       :class:`FunctionalApproximations.FrozenExponential`
       for a description of the exponential approximation used for each component.
    """
    
    def __init__(self, dim):
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append( FrozenExponential(1) )
            active_vars.append( [d] )
        super(FrozenExponentialDiagonalTransportMap,self).__init__(active_vars,
                                                                   approx_list)
    @property
    def n_coeffs(self):
        return len(self.a)*3

    def set_coeffs(self, dim):
        pass

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = np.exp(x)
        return xout

    def grad_x(self, x, *args, **kwargs):
        r""" This is a diagonal map """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        diag_out = np.einsum('...ii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.evaluate(x)
        return out

    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.prod( self.evaluate(x), axis=1 )

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.sum( x, axis=1 )

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones((x.shape[0], self.dim))

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        diag_out = np.einsum('...iii->...i', out) # Read/write from Numpy 1.10
        diag_out[:] = self.evaluate(x)
        return out

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((x.shape[0], self.dim, self.dim))

    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = np.log(x)
        return xout

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = 1/x
        return xout

    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = -1/x**2.
        return xout

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = - np.sum( np.log(x), axis=1 )
        return xout

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = - np.sum( 1./x, axis=1 )
        return xout

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xout = np.sum( 1./x**2., axis=1 )
        return xout

    def regression(self, x, w, F, REG, tol):
        r"""
        Raises:
           NotImplementedError: this is a frozen transport map.
        """
        raise NotImplementedError("This is a frozen transport map.")

class FrozenGaussianToUniformDiagonalTransportMap(MonotonicTriangularTransportMap):
    r""" Gaussian to Uniform diagonal transport map :math:`(x_1,\ldots,x_d) \rightarrow (\frac{1}{2}[1+{\rm erf}(x_1/\sqrt{2})], \ldots, \frac{1}{2}[1+{\rm erf}(x_d/\sqrt{2})])`

    Args:
       dim (int): dimension :math:`d` of the transport map

    .. note:: This map is frozen, meaning that optimizing the coefficients with
       respect to a certain cost function is not allowed.

    .. seealso:: :class:`TriangularTransportMap` for a description of the
       overridden methods and
       :class:`FunctionalApproximations.FrozenGaussianToUniform`
       for a description of the Gaussian to Uniform approximation used for
       each component.
    """
    
    def __init__(self, dim):
        approx_list = []
        active_vars = []
        for d in range(dim):
            approx_list.append( FrozenGaussianToUniform(d+1) )
            active_vars.append( [d] )
        super(FrozenGaussianToUniformDiagonalTransportMap,self).__init__(active_vars,
                                                                         approx_list)

    @property
    def n_coeffs(self):
        return len(self.a)*3

    def set_coeffs(self, dim):
        pass

    def regression(self, x, w, F, REG, tol):
        r"""
        Raises:
           NotImplementedError: this is a frozen transport map.
        """
        raise NotImplementedError("This is a frozen transport map.")

# class FrozenBananaTransportMap(TriangularTransportMap):
#     def __init__(self, a, b, mu, sigma2):
#         self.dim = 2
#         self.a = a
#         self.b = b
#         self.mu = mu
#         self.sigma2 = sigma2
#         self.chol = scila.cholesky( sigma2, lower = True )
#         self.inv_chol = scila.solve_triangular( self.chol,
#                                             np.eye(self.dim),
#                                             lower=True )
#         self.inv_sigma2 = scila.cho_solve( (self.chol,True),
#                                            np.eye(self.dim) )
#     def Tb(self, x, *args, **kwargs):
#         return self.mu + np.dot( self.chol, x.T ).T
#     def Tb_inv(self, x, *args, **kwargs):
#         return scila.solve_triangular( self.chol, (x-self.mu).T, lower=True ).T
#     def Tt(self, x, *args, **kwargs):
#         a = self.a
#         b = self.b
#         y = np.zeros(x.shape)
#         y[:,0] = a * x[:,0]
#         # y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2. + a**2.)
#         y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2.)
#         return y
#     def Tt_inv(self, y, *args, **kwargs):
#         a = self.a
#         b = self.b
#         x = np.zeros(y.shape)
#         x[:,0] = y[:,0] / a
#         # x[:,1] = a * (y[:,1] + b * (y[:,0]**2. + a**2.))
#         x[:,1] = a * (y[:,1] + b * (y[:,0]**2.))
#         return x
#     def evaluate(self, x, *args, **kwargs):
#         return self.Tt( self.Tb(x, par), par )
#     def __call__(self, x):
#         return self.evaluate(x)
#     def inverse(self, x, *args, **kwargs):
#         return self.Tb_inv( self.Tt_inv(x, par), par )
#     def log_det_grad_x(self, x, *args, **kwargs):
#         return 2. * np.log(self.a)

class FrozenBananaTransportMap(TriangularTransportMap):
    def __init__(self, a, b):
        self.dim = self.dim_in = self.dim_out = 2
        self.a = a
        self.b = b
    def evaluate(self, x, *args, **kwargs):
        a = self.a
        b = self.b
        y = np.zeros(x.shape)
        y[:,0] = a * x[:,0]
        y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2. + a**2.)
        # y[:,1] = x[:,1] / a - b * ((a*x[:,0])**2.)
        return y
    def inverse(self, y, *args, **kwargs):
        a = self.a
        b = self.b
        x = np.zeros(y.shape)
        x[:,0] = y[:,0] / a
        x[:,1] = a * (y[:,1] + b * (y[:,0]**2. + a**2.))
        # x[:,1] = a * (y[:,1] + b * (y[:,0]**2.))
        return x
    def log_det_grad_x(self, x, *args, **kwargs):
        return np.ones(x.shape[0])
    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.ones(x.shape[0])
    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros(x.shape)
    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        return np.zeros((x.shape[0],self.dim,self.dim))
    def grad_x(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        out[:,0,0] = self.a
        out[:,1,0] = - 2. * self.a**2. * self.b * x[:,0]
        out[:,1,1] = 1./self.a
        return out
    def hess_x(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        out[:,1,0,0] = - 2. * self.a**2. * self.b
        return out
    def grad_x_inverse(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim) )
        out[:,0,0] = 1./self.a
        out[:,1,0] = 2. * self.a * self.b * x[:,0]
        out[:,1,1] = self.a
        return out
    def hess_x_inverse(self, x, *args, **kwargs):
        out = np.zeros( (x.shape[0], self.dim, self.dim, self.dim) )
        out[:,1,0,0] = 2. * self.a * self.b
        return out