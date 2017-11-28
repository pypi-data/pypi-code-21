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

from TransportMaps.Distributions.DistributionBase import ConditionalDistribution
from TransportMaps.Distributions.FrozenDistributions import GaussianDistribution

__all__ = ['ConditionallyGaussianDistribution',
           'MeanConditionallyGaussianDistribution']

nax = np.newaxis

class ConditionallyGaussianDistribution(ConditionalDistribution):
    r""" Multivariate Gaussian distribution :math:`\pi({\bf x}\vert{\bf y}) \sim \mathcal{N}(\mu({\bf y}), \Sigma({\bf y}))`

    Args:
      mu (:class:`Map<TransportMaps.Maps.Map>`): mean vector map
      sigma (:class:`Map<TransportMaps.Maps.Map>`): covariance matrix map
      precision (:class:`Map<TransportMaps.Maps.Map>`): precision matrix map
      coeffs (:class:`ndarray<numpy.ndarray>`): fix the coefficients :math:`{\bf y}`
    """
    def __init__(self, mu, sigma=None, precision=None, coeffs=None):
        if (sigma is not None) and (precision is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        if sigma is not None and mu.dim_in != sigma.dim_in:
            raise ValueError("The number of parameters must be the same for both " + \
                             "the map mu and the map sigma")
        if precision is not None and mu.dim_in != precision.dim_in:
            raise ValueError("The number of parameters must be the same for both " + \
                             "the map mu and the map precision")
        self._muMap = mu
        self._sigmaMap = sigma
        self._precisionMap = precision
        if sigma is not None:
            self._isSigmaOn = True
        else:
            self._isSigmaOn = False
        self._mu = None
        self._sigma = None
        self._precision = None
        self._pi = GaussianDistribution(np.zeros(mu.dim_out), np.eye(mu.dim_out))
        super(ConditionallyGaussianDistribution,self).__init__(mu.dim_out, mu.dim_in)
        self._coeffs = None
        self.coeffs = coeffs

    @property
    def pi(self):
        return self._pi
        
    @property
    def mu(self):
        return self._pi.mu
        
    @property
    def sigma(self):
        return self._pi.sigma

    @property
    def precision(self):
        return self._pi.inv_sigma
        
    @property
    def muMap(self):
        return self._muMap

    @property
    def sigmaMap(self):
        return self._sigmaMap

    @property
    def precisionMap(self):
        return self._precisionMap

    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            # Set up Gaussian distribution
            mu = self._muMap.evaluate(coeffs[nax,:])[0,:]
            sigma = None
            precision = None
            if self._isSigmaOn:
                sigma = self._sigmaMap.evaluate(
                    coeffs[nax,:])[0,:,:] 
                self._precision = None
            else:
                precision = self._precisionMap.evaluate(
                    coeffs[nax,:])[0,:,:]
                self._sigma = None
            # Set up gradients
            try:
                self._grad_a_mu = self._muMap.grad_x(coeffs[nax,:])[0,:,:]
                if self._isSigmaOn:
                    self._grad_a_sigma = \
                        self._sigmaMap.grad_x(coeffs[nax,:])[0,:,:,:]
                    self._grad_a_precision = None
                else:
                    self._grad_a_precision = \
                        self._precisionMap.grad_x(coeffs[nax,:])[0,:,:,:]
                    self._grad_a_sigma = None
            except NotImplementedError:
                self._grad_a_c = None
                self._grad_a_T = None
            try:
                self._hess_a_mu = self._muMap.hess_x(
                    coeffs[nax,:])[0,:,:,:]
                if self._isSigmaOn:
                    self._hess_a_sigma = \
                        self._sigmaMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
                    self._hess_a_precision = None
                else:
                    self._hess_a_precision = \
                        self._precisionMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
                    self._hess_a_sigma = None
            except NotImplementedError:
                self._hess_a_c = None
                self._hess_a_T = None
            if self._pi is None:
                self._pi = GaussianDistribution(mu, sigma=sigma, precision=precision)
            else:
                self._pi.mu = mu
                if self._isSigmaOn:
                    self._pi.sigma = sigma
                else:
                    self._pi.precision = precision
            self._coeffs = coeffs

    @property
    def grad_a_mu(self):
        return self._grad_a_mu

    @property
    def grad_a_sigma(self):
        return self._grad_a_sigma

    @property
    def grad_a_precision(self):
        return self._grad_a_precision

    def rvs(self, m, y=None, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        if self._coeffs is None:
            self.pi.mu = self._muMap.evaluate(y[nax,:])[0,:]
            if self._isSigmaOn:
                self.pi.sigma = self._sigmaMap.evaluate(y[nax,:])[0,:,:] 
            else:
                self.pi.precision = self._precisionMap.evaluate(y[nax,:])[0,:,:]
        return self.pi.rvs(m)

    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`] or :class:`ndarray<numpy.ndarray>` [:math:`d_y`]):
            conditioning values :math:`{\bf Y}={\bf y}`. In the second case one
            conditioning value is used for all the :math:`m` points :math:`{\bf x}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        if self._coeffs is None:
            m = x.shape[0]
            mu = self._muMap.evaluate(y)
            if self._isSigmaOn:
                sigma = self._sigmaMap.evaluate(y)
            else:
                precision = self._precisionMap.Evaluate(y)
            out = np.zeros(m)
            for i in range(m):
                self.pi.mu = mu[i]
                if self._isSigmaOn:
                    self.pi.sigma = sigma[i]
                else:
                    self.pi.precision = precision[i]
                out[i] = self.pi.log_pdf(
                    x[[i],:], params=params, idxs_slice=idxs_slice)
        else:
            out = self.pi.log_pdf(x, params=params, idxs_slice=idxs_slice)
        return out

    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        if self._coeffs is None:
            m = x.shape[0]
            mu_all = self._muMap.evaluate(y)
            ga_mu_all = self._muMap.grad_x(y)
            if self._isSigmaOn:
                sigma_all = self._sigmaMap.evaluate(y)
                ga_sigma_all = self._sigmaMap.evaluate(y)
            else:
                precision_all = self._precisionMap.Evaluate(y)
                raise NotImplementedError("There are some parts missing for this gradient")
            out = np.zeros((m, x.shape[1]+y.shape[1]))
            for i in range(m):
                mu = mu_all[i]
                ga_mu = ga_mu_all[i]
                sigma = sigma_all[i]
                ga_sigma = ga_sigma_all[i]
                # Cholesky of sigma
                chol = scila.cho_factor(sigma)
                inv_sigma = scila.cho_solve(chol, np.eye(mu.shape))
                ga_inv_sigma = - np.einsum('ij,jkl,km->iml', inv_sigma, ga_sigma, inv_sigma)
                xmu = x[[i],:]-mu
                isgas = np.einsum('ij,jkl->ikl', inv_sigma, ga_inv_sigma)
                out[i,:x.shape[1]] = self.pi.grad_x_log_pdf(
                    x[[i],:], params=params, idxs_slice=idxs_slice)
                out[i,x.shape[1]:] = \
                    -.5 * ( np.einsum('ij,ik,...k->...j', -ga_mu, inv_sigma, xmu) + \
                            np.einsum('...i,ikl,...k->...l', xmu, ga_inv_sigma, xmu) + \
                            np.einsum('...i,ij,jk->...k', xmu, inv_sigma, -ga_mu) ) \
                    - .5 * np.einsum('iik->k', isgas) # Log determinant part
        else:
            raise NotImplementedError("To be done.")
        return out

class MeanConditionallyGaussianDistribution(ConditionalDistribution):
    r""" Multivariate Gaussian distribution :math:`\pi({\bf x}\vert{\bf y}) \sim \mathcal{N}(\mu({\bf y}), \Sigma)`

    Args:
      mu (:class:`Map<TransportMaps.Maps.Map>`): mean vector map
      sigma (:class:`ndarray<numpy.ndarray>`): covariance matrix map
      precision (:class:`ndarray<numpy.ndarray>`): precision matrix map
      coeffs (:class:`ndarray<numpy.ndarray>`): fix the coefficients :math:`{\bf y}`
    """
    def __init__(self, mu, sigma=None, precision=None, coeffs=None):
        if (sigma is not None) and (precision is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        self._muMap = mu
        self._mu = None
        self._pi = GaussianDistribution(np.zeros(mu.dim_out), sigma)
        super(MeanConditionallyGaussianDistribution,self).__init__(mu.dim_out, mu.dim_in)
        self._coeffs = None
        self.coeffs = coeffs

    @property
    def pi(self):
        return self._pi
        
    @property
    def mu(self):
        return self._pi.mu
        
    @property
    def sigma(self):
        return self._pi.sigma

    @property
    def precision(self):
        return self._pi.inv_sigma
        
    @property
    def muMap(self):
        return self._muMap

    @property
    def coeffs(self):
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            # Set up Gaussian distribution
            mu = self._muMap.evaluate(coeffs[nax,:])[0,:]
            self._pi.mu = mu
            self._coeffs = coeffs

    @property
    def grad_a_mu(self):
        return self._grad_a_mu

    def rvs(self, m, y=None, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        if self._coeffs is None:
            self.pi.mu = self._muMap.evaluate(y[nax,:])[0,:]
        return self.pi.rvs(m)

    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`] or :class:`ndarray<numpy.ndarray>` [:math:`d_y`]):
            conditioning values :math:`{\bf Y}={\bf y}`. In the second case one
            conditioning value is used for all the :math:`m` points :math:`{\bf x}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        if self._coeffs is None:
            m = x.shape[0]
            mu = self._muMap.evaluate(y)
            out = np.zeros(m)
            for i in range(m):
                self.pi.mu = mu[i]
                out[i] = self.pi.log_pdf(
                    x[[i],:], params=params, idxs_slice=idxs_slice)
        else:
            out = self.pi.log_pdf(x, params=params, idxs_slice=idxs_slice)
        return out

    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        raise NotImplementedError("Not implemented yet")