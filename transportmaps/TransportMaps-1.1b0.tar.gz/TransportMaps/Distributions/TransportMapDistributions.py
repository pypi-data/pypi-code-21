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

import warnings
import numpy as np

from TransportMaps import mpi_eval
from TransportMaps.Distributions.ParametricDistributionBase import *

__all__ = ['TransportMapDistribution',
           'PushForwardTransportMapDistribution',
           'PullBackTransportMapDistribution']

class TransportMapDistribution(ParametricDistribution):
    r""" Abstract class for densities of the transport map type (:math:`T^\sharp \pi` or :math:`T_\sharp \pi`)

    Args:
      transport_map (Maps.TriangularTransportMap): transport map :math:`T`
      base_distribution (Distributions.Distribution): distribution :math:`\pi`

    .. seealso:: :class:`PushForwardTransportMapDistribution` and :class:`PullBackTransportMapDistribution`.
    """

    def __init__(self, transport_map, base_distribution):
        if transport_map.dim != base_distribution.dim:
            raise ValueError("The transport_map and the base_distribution should have " +
                             "the same dimension")
        super(TransportMapDistribution,self).__init__(transport_map.dim)
        self.transport_map = transport_map
        self.base_distribution = base_distribution

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricDistribution.coeffs`
        """
        return self.transport_map.coeffs

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients
        
        .. seealso:: :func:`ParametricDistribution.n_coeffs`
        """
        return self.transport_map.n_coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}` of the distribution

        .. seealso:: :func:`ParametricDistribution.coeffs`
        """
        self.transport_map.coeffs = coeffs

    def rvs(self, m, mpi_pool=None, batch_size=None):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes
          batch_size (int): whether to generate samples in batches

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples
        """
        if batch_size is None:
            batch_size = m
        samples = np.zeros((m, self.dim))
        niter = m // batch_size + (1 if m % batch_size > 0 else 0)
        for it in range(niter):
            nnew = min(m-it*batch_size, batch_size)
            samp_start = it * batch_size
            samp_stop = samp_start + nnew
            # Sample
            base_samples = self.base_distribution.rvs(nnew, mpi_pool=mpi_pool)
            samples[samp_start:samp_stop,:] = self.map_samples_base_to_target(
                base_samples, mpi_pool=mpi_pool)
        return samples

    def quadrature(self, qtype, qparams, mpi_pool=None):
        r""" Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Return:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`],
            :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of quadrature
            points and weights
        """
        (base_x,w) = self.base_distribution.quadrature(qtype, qparams, mpi_pool=mpi_pool)
        x = self.map_samples_base_to_target(base_x, mpi_pool=mpi_pool)
        return (x,w)

    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" [Abstract] Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T^\sharp \pi` or :math:`T_\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        raise NotImplementedError("Abstract method. Implement in sub-class.")

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" [Abstract] Map input samples (assumed to be from :math:`T^\sharp \pi` or :math:`T_\sharp \pi`) to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        raise NotImplementedError("Abstract method. Implement in sub-class.")


class PushForwardTransportMapDistribution(TransportMapDistribution):
    r""" Class for densities of the transport map type :math:`T_\sharp \pi`

    Args:
      transport_map (Maps.TriangularTransportMap): transport map :math:`T`
      base_distribution (Distributions.Distribution): distribution :math:`\pi`

    .. seealso:: :class:`TransportMapDistribution`
    """

    def pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`T_\sharp \pi`
            at the ``x`` points.
        """
        return np.exp( self.log_pdf(x, params, idxs_slice) )
        
    def log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\log T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log T_\sharp\pi`
            at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.log_pushforward(self.base_distribution, x,
                                                  params_t, params_pi, idxs_slice)

    def grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \log T_\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla_{\bf a} \log T_\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.grad_a_log_pushforward(self.base_distribution, x,
                                                         params_t, params_pi, idxs_slice)

    def tuple_grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\log T_\sharp \pi({\bf x}), \nabla_{\bf a} \log T_\sharp \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log T_\sharp \pi({\bf x}), \nabla_{\bf a} \log T_\sharp \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.tuple_grad_a_log_pushforward(self.base_distribution, x,
                                                               params_t, params_pi, idxs_slice)
        
    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.grad_x_log_pushforward(self.base_distribution, x,
                                                         params_t, params_pi, idxs_slice)

    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.tuple_grad_x_log_pushforward(self.base_distribution, x,
                                                               params_t, params_pi, idxs_slice)

    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.hess_x_log_pushforward(self.base_distribution, x,
                                                         params_t, params_pi, idxs_slice)
        
    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T_\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_eval("evaluate", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" Map input samples assumed to be from :math:`T_\sharp \pi` to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_eval("inverse", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def minimize_kl_divergence(self, tar, qtype, qparams,
                               parbase=None, partar=None,
                               x0=None,
                               regularization=None,
                               tol=1e-4, maxit=100, ders=2,
                               fungrad=False,
                               batch_size=None,
                               mpi_pool=None,
                               grad_check=False, hess_check=False):
        r""" Solve :math:`\arg \min_{\bf a}\mathcal{D}_{KL}\left((T_\sharp \pi)_{\bf a}, \pi_{\rm tar}\right)`

        The minimization is not directly done on the original problem,
        but on the equivalent problem

        .. math::

           \arg \min_{\bf a}\mathcal{D}_{KL}\left(\pi, (T^\sharp\pi_{\rm tar})_{\bf a}\right) \;.
        
        Args:
          tar (:class:`Distribution<TransportMaps.Distribution>`): target distribution
            :math:`\pi_{\rm tar}`
          qtype (int): quadrature type number provided by :math:`\pi`
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          partar (dict): parameters for the evaluation of :math:`\pi_{\rm tar}`
          parbase (dict): parameters for the evaluation of :math:`\pi`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
          fungrad (bool): whether the two distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver
        """
        pbdistribution = PullBackTransportMapDistribution(self.transport_map, tar)
        par_base = parbase
        par_pbdistribution = partar
        # par_pbdistribution = {'params_t': {},
        #                  'params_pi': partar}
        log = self.transport_map.minimize_kl_divergence(
            self.base_distribution, pbdistribution, qtype=qtype, qparams=qparams,
            params_d1=par_base, params_d2=par_pbdistribution,
            x0=x0, regularization=regularization,
            tol=tol, maxit=maxit, ders=ders, fungrad=fungrad, batch_size=batch_size, 
            mpi_pool=mpi_pool, grad_check=grad_check, hess_check=hess_check)
        return log

class PullBackTransportMapDistribution(TransportMapDistribution):
    r""" Class for densities of the transport map type :math:`T^\sharp \pi`

    Args:
      transport_map (Maps.TriangularTransportMap): transport map :math:`T`
      base_distribution (Distributions.Distribution): distribution :math:`\pi`

    .. seealso:: :class:`TransportMapDistribution`
    """

    def pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`T^\sharp \pi`
            at the ``x`` points.
        """
        return np.exp( self.log_pdf(x, params, idxs_slice))

    def log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log T^\sharp \pi`
            at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.log_pullback(self.base_distribution, x,
                                               params_t, params_pi, idxs_slice)

    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla_{\bf x} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.grad_x_log_pullback(self.base_distribution, x,
                                                      params_t, params_pi, idxs_slice)

    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf x} \log T^\sharp \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf x} \log T^\sharp \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.tuple_grad_x_log_pullback(self.base_distribution, x,
                                                            params_t, params_pi, idxs_slice)

    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla^2_{\bf x} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.hess_x_log_pullback(self.base_distribution, x,
                                                      params_t, params_pi, idxs_slice)

    def grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla_{\bf a} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.grad_a_log_pullback(self.base_distribution, x,
                                                      params_t, params_pi, idxs_slice)

    def tuple_grad_a_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf a} \log T^\sharp \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
          (:class:`tuple`) --
            :math:`\left(\log T^\sharp \pi({\bf x}), \nabla_{\bf a} \log T^\sharp \pi({\bf x})\right)`
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.tuple_grad_a_log_pullback(self.base_distribution, x,
                                                            params_t, params_pi, idxs_slice)

    def hess_a_log_pdf(self, x, params=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a} \log T^\sharp \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters with keys ``params_pi``, ``params_t``
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of
            :math:`\nabla^2_{\bf a} \log T^\sharp \pi` at the ``x`` points.
        """
        try:
            params_pi = params['params_pi']
        except (KeyError,TypeError):
            params_pi = None
        try:
            params_t = params['params_t']
        except (KeyError,TypeError):
            idxs_slice = slice(None)
            params_t = None
        return self.transport_map.hess_a_log_pullback(self.base_distribution, x,
                                                      params_t, params_pi, idxs_slice)

    def map_samples_base_to_target(self, x, mpi_pool=None):
        r""" Map input samples (assumed to be from :math:`\pi`) to the corresponding samples from :math:`T^\sharp \pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_eval("inverse", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def map_samples_target_to_base(self, x, mpi_pool=None):
        r""" Map input samples assumed to be from :math:`T^\sharp \pi` to the corresponding samples from :math:`\pi`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): input samples
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- corresponding samples
        """
        scatter_tuple = (['x'], [x])
        out = mpi_eval("evaluate", scatter_tuple=scatter_tuple, obj=self.transport_map,
                       mpi_pool=mpi_pool)
        return out

    def minimize_kl_divergence(self, tar, qtype, qparams,
                               parbase=None, partar=None,
                               x0=None,
                               regularization=None,
                               tol=1e-4, maxit=100, ders=2,
                               fungrad=False,
                               batch_size=None,
                               mpi_pool=None, 
                               grad_check=False, hess_check=False):
        r""" Solve :math:`\arg \min_{\bf a}\mathcal{D}_{KL}\left((T^\sharp \pi)_{\bf a}, \pi_{\rm tar}\right)`

        The minimization is not directly done on the original problem,
        but on the equivalent problem

        .. math::

           \arg \min_{\bf a}\mathcal{D}_{KL}\left(\pi, (T_\sharp\pi_{\rm tar})_{\bf a}\right) \;.
        
        Args:
          tar (:class:`Distribution<TransportMaps.Distribution>`): target distribution
            :math:`\pi_{\rm tar}`
          qtype (int): quadrature type number provided by :math:`\pi`
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          partar (dict): parameters for the evaluation of :math:`\pi_{\rm tar}`
          parbase (dict): parameters for the evaluation of :math:`\pi`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> Hessian
          fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>`): the list
            contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processes
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver
        """
        pfdistribution = PushForwardTransportMapDistribution(self.transport_map, tar)
        par_base = parbase
        par_pfdistribution = partar
        # par_pfdistribution = {'params_t': {},
        #                  'params_pi': partar}
        log = self.transport_map.minimize_kl_divergence(
            self.base_distribution, pfdistribution,
            qtype=qtype, qparams=qparams,
            params_d1=par_base, params_d2=par_pfdistribution,
            x0=x0, regularization=regularization,
            tol=tol, maxit=maxit, ders=ders,
            fungrad=fungrad,
            batch_size=batch_size, cache_level=0,
            mpi_pool=mpi_pool, 
            grad_check=grad_check, hess_check=hess_check)
        return log