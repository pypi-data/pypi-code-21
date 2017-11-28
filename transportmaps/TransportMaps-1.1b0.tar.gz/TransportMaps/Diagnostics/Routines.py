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

import time
import numpy as np

from TransportMaps import mpi_eval

__all__ = ['compute_vals_variance_approx_kl', 'variance_approx_kl']

def compute_vals_variance_approx_kl( d1, d2, params1=None, params2=None, x=None,
                                     mpi_pool_tuple=(None,None), import_set=set() ):
    r""" Compute values necessary for the evaluation of the variance diagnostic :func:`variance_approx_kl`

    Returns:
      (:class:`tuple` [2] :class:`ndarray<numpy.ndarray>` [:math:`m`]) --
        computed values of :math:`\log\pi_1` and :math:`\log\pi_2`

    .. seealso:: :func:`variance_approx_kl`
    """
    # d1
    scatter_tuple = (['x'], [x])
    vals_d1 = mpi_eval("log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                       mpi_pool=mpi_pool_tuple[0])
    # d2
    vals_d2 = mpi_eval("log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                       mpi_pool=mpi_pool_tuple[1])
    return (vals_d1, vals_d2)

def variance_approx_kl( d1, d2, params1=None, params2=None, vals_d1=None, vals_d2=None,
                        qtype=None, qparams=None, x=None, w=None,
                        mpi_pool_tuple=(None,None), import_set=set() ):
    r""" Variance diagnositc

    Statistical analysis of the variance diagnostic

    .. math::

       \mathcal{D}_{KL}(\pi_1 \Vert \pi_2) \approx \frac{1}{2} \mathbb{V}_{\pi_1} \left( \log \frac{\pi_1}{\pi_2}\right)

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      vals_d1 (:class:`ndarray<numpy.ndarray>` [:math:`m`]):
        computed values of :math:`\log\pi_1`
      vals_d2 (:class:`ndarray<numpy.ndarray>` [:math:`m`]):
        computed values of:math:`\log\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field`` (for MPI purposes)

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if vals_d1 is None or vals_d2 is None:
        if x is None and w is None:
            (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
        elif x is None or w is None:
            raise ValueError("Provide quadrature points and weights or quadrature " + \
                             "type and parameters")
    if vals_d1 is None or vals_d2 is None:
        vals_d1, vals_d2 = compute_vals_variance_approx_kl(
            d1, d2, params1, params2, x=x,
            mpi_pool_tuple=mpi_pool_tuple, import_set=import_set)
    vals = vals_d1 - vals_d2
    expect = np.dot( vals, w )
    var = .5 * np.dot( (vals - expect)**2., w )
    return var
