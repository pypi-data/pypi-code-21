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
import scipy.sparse as scisp
from TransportMaps.Functionals import FrozenLinear
from TransportMaps.Maps.TransportMapBase import *
from TransportMaps.Maps.TriangularTransportMapBase import *
from TransportMaps.Maps.FullTransportMaps import *

__all__ = ['LiftedTransportMap', 'SequentialMarkovChainTransportMap']

class LiftedTransportMap(TransportMap):
    r""" Given a map :math:`T` of dimension :math:`d_\theta + 2 d_{\bf x}`, where :math:`d_\theta` is the number of hyper-parameters and :math:`d_{\bf x}` is the state dimension, lift it to a :math:`\hat{d}` state dimensional map.

    Let

    .. math::

       T(\Theta, {\bf x}) = \begin{bmatrix}
       T^{(0)}(\Theta) \\
       T^{(1)}(\Theta, {\bf x}) \\
       \end{bmatrix}

    be the map to be lifted at index :math:`i` into a :math:`\hat{d}` dimensional map.

    .. math::

       T_{\rm lift}(\Theta, {\bf x}) = \left[ \begin{array}{c}
       T^{(0)}(\theta) \\
       x_{1} \\
       \; \vdots \\
       x_{i-1} \\
       T^{(1)}(\theta, x_{i}, \ldots, x_{i+2 d_{\bf x}}) \\
       x_{i+2d_{\bf x}+1} \\
       \; \vdots \\
       x_{\hat{d}}
       \end{array} \right]

    Args:
      idx (int): index where to lift :math:`T`
      tm (:class:`TransportMap<TransportMap>`): transport map :math:`T`
      dim (int): total dimension :math:`\hat{d}`
      hyper_dim (int): number of hyper-parameters :math:`d_\theta`
    """
    def __init__(self, idx, tm, dim, hyper_dim):
        if idx >= 0:
            self.hyper_dim = hyper_dim
            self.state_dim = (tm.dim-hyper_dim)//2
            self.tm = tm
            self.dim = self.dim_in = self.dim_out = dim
            # Instantiate index mappings
            self.hyper_idxs = np.arange(hyper_dim)
            self.state_idxs = np.arange(
                hyper_dim + idx * self.state_dim,
                hyper_dim + (idx+2) * self.state_dim)
            self.idxs = np.hstack( (self.hyper_idxs, self.state_idxs) )
        elif idx == -1: # Filtering map at first step
            self.hyper_dim = hyper_dim
            self.state_dim = tm.dim-hyper_dim
            self.tm = tm
            self.dim = self.dim_in = self.dim_out = dim
            # Instantiate index mappings
            self.hyper_idxs = np.arange(hyper_dim)
            self.state_idxs = np.arange(
                hyper_dim + (idx+1) * self.state_dim,
                hyper_dim + (idx+2) * self.state_dim)
            self.idxs = np.hstack( (self.hyper_idxs, self.state_idxs) )
        else:
            raise ValueError("idx must be >= -1")

    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
          (:class:`int`) -- total number :math:`N` of
              coefficients characterizing the map.
        """
        return self.tm.n_coeffs

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return self.tm.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps
        """
        self.tm.coeffs = coeffs

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = x.copy()
        out[:,self.idxs] = self.tm.evaluate(x[:,self.idxs], *args, **kwargs)
        return out

    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = x.copy()
        out[:,self.idxs] = self.tm.inverse(x[:,self.idxs], *args, **kwargs)
        return out

    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        m = x.shape[0]
        out = np.zeros((m, self.dim, self.dim))
        out[:,range(self.dim),range(self.dim)] = 1.
        out[np.ix_(range(m),self.idxs, self.idxs)] = self.tm.grad_x(
            x[:,self.idxs], *args, **kwargs)
        return out

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        m = x.shape[0]
        out = np.zeros((m, self.dim, self.dim, self.dim))
        out[np.ix_(range(m),self.idxs, self.idxs, self.idxs)] = \
            self.tm.hess_x(x[:,self.idxs], *args, **kwargs)
        return out

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        m = x.shape[0]
        out = np.zeros((m, self.dim, self.dim))
        out[:,range(self.dim),range(self.dim)] = 1.
        out[np.ix_(range(m),self.idxs, self.idxs)] = self.tm.grad_x_inverse(
            x[:,self.idxs], *args, **kwargs)
        return out

    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim, self.dim, self.dim))
        out[np.ix_(range(m),self.idxs, self.idxs,self.idxs)] = \
            self.tm.hess_x_inverse(
                x[:,self.idxs], *args, **kwargs)
        return out

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return self.tm.log_det_grad_x(x[:,self.idxs], *args, **kwargs)

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim))
        out[:,self.idxs] = self.tm.grad_x_log_det_grad_x(
            x[:,self.idxs], *args, **kwargs)
        return out

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim, self.dim))
        out[np.ix_(range(m),self.idxs, self.idxs)] = \
            self.tm.hess_x_log_det_grad_x(
                x[:,self.idxs], *args, **kwargs)
        return out

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return self.tm.log_det_grad_x_inverse(x[:,self.idxs], *args, **kwargs)

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim))
        out[:,self.idxs] = self.tm.grad_x_log_det_grad_x_inverse(
            x[:,self.idxs], *args, **kwargs)
        return out

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim, self.dim))
        out[np.ix_(range(m),self.idxs, self.idxs)] = \
            self.tm.hess_x_log_det_grad_x_inverse(
                x[:,self.idxs], *args, **kwargs)
        return out
        
class SequentialMarkovChainTransportMap(ListCompositeTransportMap):
    r""" Compose the lower triangular 1-lag smoothing maps into the smoothing map

    Args:
      tm_list (list): list of 1-lag smoothing lower triangular transport maps
      nhyper (int): number of hyper-parameters

    .. warning:: this works only for one dimensional states!
       It will be extended for higher dimensional states in the future.
    """
    def __init__(self, tm_list, hyper_dim):
        self.hyper_dim = hyper_dim
        if len(tm_list) == 0:
            self.state_dim = 0
        else:
            self.state_dim = (tm_list[0].dim-hyper_dim) // 2
        self.dim = self.hyper_dim + (len(tm_list)+1) * self.state_dim
        self.comp_list = tm_list
        lifted_maps = [LiftedTransportMap(d, tm, self.dim, self.hyper_dim) for \
                       d, tm in enumerate(tm_list)]
        super(SequentialMarkovChainTransportMap,self).__init__(lifted_maps)
    

