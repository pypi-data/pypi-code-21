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

from TransportMaps.Maps.TransportMapBase import TransportMap

__all__ = ['IdentityTransportMap', 'PermutationTransportMap']

class IdentityTransportMap(TransportMap):
    r""" Map :math:`T({\bf x})={\bf x}`.
    """
    def __init__(self, dim):
        self.dim = self.dim_in = self.dim_out = dim

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x

    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.eye(self.dim)
        return gx[np.newaxis,:,:]

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,1,1,1))

    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.eye(self.dim)
        return gx[np.newaxis,:,:]
        
    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,1,1,1))

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros(1)

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim))

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim, self.dim))

    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones(1)

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros(1)

    def det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones(1)

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim))

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim, self.dim))

class PermutationTransportMap(TransportMap):
    r""" Map :math:`T({\bf x}) = [x_{p(0)}, \ldots, x_{p(d)}]^T`

    Args:
      p (list): permutation list :math:`p`
    """
    def __init__(self, p):
        if any([ i != pi for i,pi in enumerate(sorted(p))]):
            raise ValueError("The permutation is not complete or valid")
        self.p = np.asarray(p)
        self.inv_p = np.argsort(self.p)
        self.dim = self.dim_in = self.dim_out = len(p)

    @property
    def coeffs(self):
        return self.p

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x[:,self.p]

    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.zeros((1,self.dim, self.dim))
        for i in range(self.dim):
            gx[0,i,self.p[i]] = 1.
        return gx

    def hess_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,1,1,1))

    def inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return x[:, self.inv_p]

    def grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        gx = np.zeros((1,self.dim, self.dim))
        for i in range(self.dim):
            gx[0,i,self.inv_p[i]] = 1.
        return gx

    def hess_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,1,1,1))

    def log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros(1)

    def grad_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim))

    def hess_x_log_det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim, self.dim))

    def det_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones(1)

    def log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros(1)

    def det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.ones(1)

    def grad_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim))

    def hess_x_log_det_grad_x_inverse(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        return np.zeros((1,self.dim, self.dim))