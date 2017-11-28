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

from .SequentialInferenceDistributions import AR1TransitionDistribution
from TransportMaps.Distributions.FrozenDistributions import \
    GaussianDistribution
from TransportMaps.Distributions.ConditionalDistributions import \
    ConditionallyGaussianDistribution
from TransportMaps.Maps.MapBase import \
    Map, LinearMap, ConstantMap, ConditionallyLinearMap

__all__ = ['LinearGaussianAR1TransitionDistribution',
           'ConditionallyLinearGaussianAR1TransitionDistribution']

class LinearGaussianAR1TransitionDistribution(AR1TransitionDistribution):
    r""" Transition probability distribution :math:`g({\bf x}_{k-1},{\bf x}_k) = \pi_{{\bf X}_k \vert {\bf X}_{k-1}={\bf x}_{k-1}}({\bf x}_k) = \pi({\bf x}_k - F_k {\bf x}_{k-1} - {\bf c}_k)` where :math:`\pi \sim \mathcal{N}(\mu_k,Q_k)`.

    This represents the following Markov transition model:

    .. math::

       {\bf x}_k = c_k + F_k {\bf x}_{k-1} + {\bf w}_k \\
       {\bf w}_k \sim \mathcal{N}(\mu,Q_k)

    where the control :math:`{\bf c}_k := B_k {\bf u}_k` can be used for control purposes
    
    Args:
      ck (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): constant part or map returning the constant part given some parameters
      Fk (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): state transition matrix (dynamics) or map returning the linear part given some parametrs
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): mean :math:`\mu_k` or parametric map for :math:`\mu_k(\theta)`
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): covariance :math:`Q_k` or parametric map for :math:`Q_k(\theta)`
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): precision :math:`Q_k^{-1}` or parametric map for :math:`Q_k^{-1}(\theta)`
    """
    def __init__(self, ck, Fk, mu, sigma=None, precision=None,
                 coeffs=None):
        Fmap = LinearMap(ck, Fk)
        pi = GaussianDistribution(mu, sigma=sigma, precision=precision)
        super(LinearGaussianAR1TransitionDistribution, self).__init__(
            pi, Fmap)

class ConditionallyLinearGaussianAR1TransitionDistribution(AR1TransitionDistribution):
    r""" Transition probability distribution :math:`g(\theta,{\bf x}_{k-1},{\bf x}_k) = \pi_{{\bf X}_k \vert {\bf X}_{k-1}={\bf x}_{k-1}}({\bf x}_k, \Theta=\theta) = \pi({\bf x}_k - F_k(\theta) {\bf x}_{k-1} - {\bf c}_k(\theta))` where :math:`\pi \sim \mathcal{N}(\mu_k(\theta),Q_k(\theta))`.

    This represents the following Markov transition model:

    .. math::

       {\bf x}_k = c_k + F_k {\bf x}_{k-1} + {\bf w}_k \\
       {\bf w}_k \sim \mathcal{N}(\mu,Q_k)

    where the control :math:`{\bf c}_k := B_k {\bf u}_k` can be used for control purposes
    
    Args:
      ck (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): constant part or map returning the constant part given some parameters
      Fk (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): state transition matrix (dynamics) or map returning the linear part given some parametrs
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`] or :class:`Map<TransportMaps.Maps.Map>`): mean :math:`\mu_k` or parametric map for :math:`\mu_k(\theta)`
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): covariance :math:`Q_k` or parametric map for :math:`Q_k(\theta)`
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`] or :class:`Map<TransportMaps.Maps.Map>`): precision :math:`Q_k^{-1}` or parametric map for :math:`Q_k^{-1}(\theta)`
      coeffs (:class:`ndarray<numpy.ndarray>`): fixing the coefficients :math:`\theta`
    """
    def __init__(self, ck, Fk, mu, sigma=None, precision=None, coeffs=None):
        # DISTRIBUTION
        if isinstance(mu, np.ndarray) and (
                (sigma is not None and isinstance(sigma, np.ndarray)) or
                (precision is not None and isinstance(precision, np.ndarray)) ):
            pi = GaussianDistribution(mu, sigma=sigma, precision=precision)
        else:
            pi = ConditionallyGaussianDistribution(mu, sigma=sigma, precision=precision)
        Fmap = ConditionallyLinearMap(ck, Fk)
        super(ConditionallyLinearGaussianAR1TransitionDistribution, self).__init__(
            pi, Fmap)
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