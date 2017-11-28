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

from TransportMaps.Functionals.FunctionBase import *
from TransportMaps.Maps.MapBase import \
    Map, ConstantMap, LinearMap, ConditionallyLinearMap
from TransportMaps.Distributions.DistributionBase import \
    ConditionalDistribution
from TransportMaps.Distributions.FrozenDistributions import \
    GaussianDistribution
from TransportMaps.Distributions.ConditionalDistributions import \
    ConditionallyGaussianDistribution

__all__ = ['LogLikelihood',
           'AdditiveLogLikelihood',
           'AdditiveLinearGaussianLogLikelihood',
           'AdditiveConditionallyLinearGaussianLogLikelihood',
           'IndependentLogLikelihood']

class LogLikelihood(Function):
    r""" Abstract class for log-likelihood :math:`\log \pi({\bf y} \vert {\bf x})`

    Note that :math:`\log\pi:\mathbb{R}^d \rightarrow \mathbb{R}`
    is considered a function of :math:`{\bf x}`, while the
    data :math:`{\bf y}` is fixed.
    
    Args:
      y (:class:`ndarray<numpy.ndarray>`): data
      dim (int): input dimension $d$
    """
    def __init__(self, y, dim):
        super(LogLikelihood, self).__init__(dim)
        self._y = y

    @property
    def y(self):
        return self._y
        
    def evaluate(self, x, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x(self, x, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- gradient evaluations
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def tuple_grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\left(\log\pi({\bf y} \vert {\bf x}),\nabla_{\bf x}\log\pi({\bf y} \vert {\bf x})\right)`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log\pi({\bf y} \vert {\bf x}),\nabla_{\bf x}\log\pi({\bf y} \vert {\bf x})\right)`
        """
        return ( self.evaluate(x, *args, **kwargs),
                 self.grad_x(x, *args, **kwargs) )

    def hess_x(self, x, *args, **kwargs):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- Hessian evaluations
        """
        raise NotImplementedError("To be implemented in sub-classes")

class AdditiveLogLikelihood(LogLikelihood):
    r""" Log-likelihood :math:`\log \pi({\bf y} \vert {\bf x})=\log\pi({\bf y} - T({\bf x}))`

    Args:
      y (:class:`ndarray<numpy.ndarray>` :math:`[d_y]`): data
      pi (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
      T (:class:`Map<TransportMaps.Maps.Map>`): map :math:`T:\mathbb{R}^d\rightarrow\mathbb{R}^{d_y}`
    """
    def __init__(self, y, pi, T):
        if len(y) != pi.dim:
            raise ValueError("The dimension of the data must match the " + \
                             "dimension of the distribution pi")
        if len(y) != T.dim_out:
            raise ValueError("The dimension of the data must match the " + \
                             "dimension of the output of T")
        super(AdditiveLogLikelihood, self).__init__(y, T.dim_in)
        self.pi = pi
        self.T = T
        if issubclass(type(pi), ConditionalDistribution):
            self._isPiCond = True
        else:
            self._isPiCond = False

    @property
    def isPiCond(self):
        return self._isPiCond

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate :math:`\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations

        .. todo:: caching is not implemented
        """
        frw = self.T.evaluate(x, *args, **kwargs)
        return self.pi.log_pdf( self.y - frw )

    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- gradient evaluations

        .. todo:: caching is not implemented
        """
        frw = self.T.evaluate(x, *args, **kwargs)
        gx_frw = self.T.grad_x(x, *args, **kwargs)
        gx_lpdf = self.pi.grad_x_log_pdf( self.y - frw )
        out = - np.einsum('...i,...ij->...j',gx_lpdf, gx_frw)
        return out

    def hess_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- Hessian evaluations

        .. todo:: caching is not implemented
        """
        frw = self.T.evaluate(x, *args, **kwargs) # m x d_y
        gx_frw = self.T.grad_x(x, *args, **kwargs) # m x d_y x d_x
        hx_frw = self.T.hess_x(x, *args, **kwargs) # m x d_y x d_x x d_x
        gx_lpdf = self.pi.grad_x_log_pdf( self.y - frw ) # m x d_y
        hx_lpdf = self.pi.hess_x_log_pdf( self.y - frw ) # m x d_y x d_y
        out = np.einsum('...ij,...ik->...jk', hx_lpdf, gx_frw) # m x d_y x d_x
        out = np.einsum('...ij,...ik->...jk', out, gx_frw) # m x d_x x d_x
        out -= np.einsum('...i,...ijk->...jk', gx_lpdf, hx_frw) # m x d_x x d_x
        return out

class AdditiveLinearGaussianLogLikelihood(AdditiveLogLikelihood):
    r""" Define the log-likelihood for the additive linear Gaussian model

    The model is

    .. math::

       {\bf y} = {\bf c} + {\bf T}{\bf x} + \varepsilon \;, \quad
       \varepsilon \sim \mathcal{N}(\mu, \Sigma)

    where :math:`T \in \mathbb{R}^{d_y \times d_x}`, :math:`\mu \in \mathbb{R}^{d_y}`
    and :math:`\Sigma \in \mathbb{R}^{d_y \times d_y}` is symmetric positve
    definite

    Args:
      y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): data
      c (:class:`ndarray<numpy.ndarray>` [:math:`d_y`] or :class:`Map<TransportMaps.Maps.Map>`): system constant or parametric map returning the constant
      T (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_x`] or :class:`Map<TransportMaps.Maps.Map>`): system matrix or parametric map returning the system matrix
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d_y`] or :class:`Map<TransportMaps.Maps.Map>`): noise mean or parametric map returning the mean
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_y`] or :class:`Map<TransportMaps.Maps.Map>`):
        noise covariance or parametric map returning the covariance
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_y`] or :class:`Map<TransportMaps.Maps.Map>`):
        noise precision matrix or parametric map returning the precision matrix
    """
    def __init__(self, y, c, T, mu, sigma=None, precision=None):
        # INIT MAP AND DISTRIBUTION
        linmap = LinearMap(c, T)
        pi = GaussianDistribution(mu, sigma=sigma, precision=precision)
        super(AdditiveLinearGaussianLogLikelihood, self).__init__(y, pi, linmap)

class AdditiveConditionallyLinearGaussianLogLikelihood(AdditiveLogLikelihood):
    r""" Define the log-likelihood for the additive linear Gaussian model

    The model is

    .. math::

       {\bf y} = {\bf c}(\theta) + {\bf T}(\theta){\bf x} + \varepsilon \;, \quad
       \varepsilon \sim \mathcal{N}(\mu(\theta), \Sigma(\theta))

    where :math:`T \in \mathbb{R}^{d_y \times d_x}`, :math:`\mu \in \mathbb{R}^{d_y}`
    and :math:`\Sigma \in \mathbb{R}^{d_y \times d_y}` is symmetric positve
    definite

    Args:
      y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): data
      c (:class:`ndarray<numpy.ndarray>` [:math:`d_y`] or :class:`Map<TransportMaps.Maps.Map>`): system constant or parametric map returning the constant
      T (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_x`] or :class:`Map<TransportMaps.Maps.Map>`): system matrix or parametric map returning the system matrix
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d_y`] or :class:`Map<TransportMaps.Maps.Map>`): noise mean or parametric map returning the mean
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_y`] or :class:`Map<TransportMaps.Maps.Map>`):
        noise covariance or parametric map returning the covariance
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_y`] or :class:`Map<TransportMaps.Maps.Map>`):
        noise precision matrix or parametric map returning the precision matrix
      active_vars_system (:class:`list` of :class:`int`): active variables
        identifying the parameters for for :math:`c(\theta), T(\theta)`.
      active_vars_distribution (:class:`list` of :class:`int`): active variables
        identifying the parameters for for :math:`\mu(\theta), \Sigma(\theta)`.
      coeffs (:class:`ndarray<numpy.ndarray>`): initialization coefficients
    """
    def __init__(self, y, c, T, mu, sigma=None, precision=None,
                 active_vars_system=[], active_vars_distribution=[],
                 coeffs=None):
        # SYSTEM
        if c.dim_in != T.dim_in:
            raise ValueError("Input dimension c and T don't match")
        # DISTRIBUTION
        if isinstance(mu, np.ndarray) and (
                (sigma is not None and isinstance(sigma, np.ndarray)) or
                (precision is not None and isinstance(precision, np.ndarray)) ):
            pi = GaussianDistribution(mu, sigma=sigma, precision=precision)
        else:
            if mu.dim_in != c.dim_in:
                raise ValueError("Input dimension c and mu don't match")
            if sigma is not None and mu.dim_in != sigma.dim_in:
                raise ValueError("Input dimension mu and sigma don't match")
            if precision is not None and mu.dim_in != precision.dim_in:
                raise ValueError("Input dimension mu and precision don't match")
            pi = ConditionallyGaussianDistribution(mu, sigma=sigma, precision=precision)
        # SETUP AUXILIARY VARIABLES
        self._n_coeffs = c.dim_in
        # INIT MAP AND DISTRIBUTION
        linmap = ConditionallyLinearMap(c, T)
        super(AdditiveConditionallyLinearGaussianLogLikelihood, self).__init__(y, pi, linmap)
        self.coeffs = coeffs

    @property
    def n_coeffs(self):
        return self._n_coeffs
        
    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is not None:
            self.T.coeffs = coeffs
            if self.isPiCond:
                self.pi.coeffs = coeffs
            self._coeffs = coeffs

            
class IndependentLogLikelihood(Function):
    r""" Handling likelihoods in the form :math:`\pi({\bf y}\vert{\bf x}) = \prod_{i=1}^{n}\pi_i({\bf y}_i\vert{\bf x}_i)`

    Args:
      factors (:class:`list` of :class:`tuple`): each tuple contains a
        log-likelihood (:class:`LogLikelihood`) and the sub-set of variables
        of :math:`{\bf x}` on which it acts.

    Example
    -------
    Let :math:`\pi(y_0,y_2\vert x_0,x_1,x_2)= \pi_0(y_0\vert x_0) \pi_2(y_2,x_2)`.

    >>> factors = [(ll0, [0]),
    >>>            (ll2, [2])]
    >>> ll = IndependentLogLikelihood(factors)
    
    """
    def __init__(self, factors):
        self.factors = []
        self.input_dim = set()
        for i, (ll, xidxs) in enumerate(factors):
            # Check right number of inputs
            if ll is not None and len(set(list(xidxs))) != ll.dim:
                raise TypeError("The dimension of the %d " % i + \
                                "log-likelihood is not consistent with " + \
                                "the number of variables.")
            self.factors.append( (ll, xidxs) )
            self.input_dim |= set(xidxs)
        dim = 0 if len(self.input_dim) == 0 else max(self.input_dim)+1
        super(IndependentLogLikelihood, self).__init__(dim)

    @property
    def y(self):
        return [ ll.y for ll,_ in self.factors ]

    def append(self, factor):
        r""" Add a new factor to the likelihood

        Args:
          factors (:class:`tuple`): tuple containing a
            log-likelihood (:class:`LogLikelihood`) and the sub-set of variables
            of :math:`{\bf x}` on which it acts.

        Example
        -------
        Let :math:`\pi(y_0,y_2\vert x_0,x_1,x_2)= \pi_0(y_0\vert x_0) \pi_2(y_2,x_2)` and
        let's add the factor :math:`\pi_1(y_1\vert x_1)`, obtaining:

        .. math::

           \pi(y_0,y_1,y_2\vert x_0,x_1,x_2)= \pi_0(y_0\vert x_0) \pi_1(y_1\vert x_1) \pi_2(y_2,x_2)

        >>> factor = (ll1, [1])
        >>> ll.append(factor)
        
        """
        ll, xidxs = factor
        if ll is not None and len(set(xidxs)) != ll.dim:
            raise TypeError("The dimension of the " + \
                            "log-likelihood is not consistent with " + \
                            "the number of variables.")
        self.factors.append( (ll, xidxs) )
        self.input_dim |= set(xidxs)
        self.dim = max(self.input_dim)+1

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate :math:`\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the log-likelihood")
        out = np.zeros(x.shape[0])
        for ll, xidxs in self.factors:
            if ll is not None:
                out += ll.evaluate(x[:,xidxs], *args, **kwargs)
        return out

    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- gradient evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the log-likelihood")
        out = np.zeros(x.shape)
        for ll, xidxs in self.factors:
            if ll is not None:
                out[:,xidxs] += ll.grad_x(x[:,xidxs], *args, **kwargs)
        return out

    def hess_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\log\pi({\bf y} \vert {\bf x})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- Hessian evaluations
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the log-likelihood")
        m = x.shape[0]
        out = np.zeros( (m, self.dim, self.dim) )
        for ll, xidxs in self.factors:
            if ll is not None:
                out[np.ix_(range(m),xidxs,xidxs)] += \
                    ll.hess_x(x[:,xidxs], *args, **kwargs)
        return out