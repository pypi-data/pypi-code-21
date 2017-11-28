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

from .AdaptivityBase import Builder
from TransportMaps.Routines import L2_misfit

__all__ = ['L2RegressionBuilder',
           'ToleranceSequentialL2RegressionBuilder']

class L2RegressionBuilder(Builder):
    r""" Basis builder through :math:`\mathcal{L}^2` regression

    Given a map :math:`M`, fit a supplied parametric transport map :math:`T`
    through the solution of the :math:`\mathcal{L}^2` regression problem

    .. math::

       \arg\min_{\bf a}\left\Vert M - T \right\Vert_{\mathcal{L}^2} + \alpha \Vert {\bf a} \Vert_x

    where :math:`\alpha\Vert{\bf a}\Vert_x` is a regularization term, with
    respect to one of the available norms.

    Args:
      target_map (:class:`Map<TransportMaps.Maps.Map>`): map :math:`M`
    """
    def __init__(self, target_map=None):
        self.target_map = target_map
        super(L2RegressionBuilder, self).__init__()

    @property
    def target_map(self):
        return self._target_map

    @target_map.setter
    def target_map(self, m):
        self._target_map = m

    def solve(self, transport_map, d=None, qtype=None, qparams=None,
              x=None, w=None, x0=None, regularization=None,
              tol=1e-4, maxit=100, batch_size_list=None,
              mpi_pool_list=None, import_set=set()):
        log_list = transport_map.regression(
            self.target_map, d=d, qtype=qtype, qparams=qparams,
            x=x, w=w, x0=x0, regularization=regularization,
            tol=tol, maxit=maxit, batch_size_list=batch_size_list,
            mpi_pool_list=mpi_pool_list, import_set=import_set)
        return transport_map, log_list

class ToleranceSequentialL2RegressionBuilder(L2RegressionBuilder):
    def solve(self, transport_map_list, eps, regression_params_list, monitor_params):
        tm = None
        x0 = None
        for tm_new, regression_params in zip(
                transport_map_list, regression_params_list):
            if tm is not None:
                for c1, c2 in zip(tm.approx_list, tm_new.approx_list):
                    # Constant part
                    for i1, midx1 in enumerate(c1.c.get_multi_idxs()):
                        for i2, midx2 in enumerate(c2.c.get_multi_idxs()):
                            if midx1 == midx2:
                                break
                        c2.c.coeffs[i2] = c1.c.coeffs[i1]
                    # Integrated part
                    for i1, midx1 in enumerate(c1.h.get_multi_idxs()):
                        for i2, midx2 in enumerate(c2.h.get_multi_idxs()):
                            if midx1 == midx2:
                                break
                        c2.h.coeffs[i2] = c1.h.coeffs[i1]
                x0 = tm_new.coeffs
            tm_new, log_list = super(ToleranceSequentialL2RegressionBuilder, self).solve(
                tm_new, x0=x0, **regression_params)
            if not log_list[-1]['success']:
                if tm is None: # If no map is available return the target map
                    return self.target_map, log_list
                else:
                    break
            else:
                tm = tm_new
            # Check error
            err = L2_misfit(self.target_map, tm, **monitor_params)
            if err < eps:
                break
        return tm, log_list
            