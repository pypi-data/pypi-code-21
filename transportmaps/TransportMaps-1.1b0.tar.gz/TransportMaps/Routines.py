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
import numpy.linalg as npla
import scipy.optimize as sciopt
import scipy.linalg as scila

from TransportMaps import mpi_eval, ExpectationReduce, TupleExpectationReduce, logger
from TransportMaps.FiniteDifference import grad_x_fd
from TransportMaps.Distributions.FrozenDistributions import GaussianDistribution

__all__ = [
    # KL divergence functions
    'kl_divergence', 'grad_a_kl_divergence',
    'hess_a_kl_divergence',
    'tuple_grad_a_kl_divergence',
    'action_hess_a_kl_divergence',
    'storage_hess_a_kl_divergence',
    # Product measures pullback KL divergence functions
    'kl_divergence_component',
    'grad_a_kl_divergence_component',
    'hess_a_kl_divergence_component',
    # L2 minimization
    'misfit_squared', 'grad_a_misfit_squared',
    'hess_a_misfit_squared',
    'L2_misfit',
    'L2squared_misfit', 'grad_a_L2squared_misfit',
    'hess_a_L2squared_misfit',
    'storage_hess_a_L2squared_misfit',
    'action_hess_a_L2squared_misfit',
    # First variations
    'grad_t_kl_divergence',
    'grad_x_grad_t_kl_divergence',
    # Laplace approximations
    'laplace_approximation','laplace_approximation_withBounds',
    # Maximum likelihood
    'maximum_likelihood']

nax = np.newaxis

def kl_divergence(d1, d2, params1=None, params2=None,
                  qtype=None, qparams=None, x=None, w=None,
                  batch_size=None, mpi_pool_tuple=(None,None),
                  d1_entropy=True):
    r""" Compute :math:`\mathcal{D}_{KL}(\pi_1 | \pi_2)`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``
      d1_entropy (bool): whether to include the entropy term
        :math:`\mathbb{E}_{\pi_1}[\log \pi_1]` in the KL divergence

    Returns:
      (:class:`float<float>`) -- :math:`\mathcal{D}_{KL}(\pi_1 | \pi_2)`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ( (qtype is not None) and (qparams is not None)
         and (x is None) and (w is None) ):
        (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ( (qtype is None) and (qparams is None)
           and (x is not None) and (w is not None) ):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    # d1.log_pdf
    mean_log_d1 = 0.
    if d1_entropy:
        try:
            mean_log_d1 = d1.mean_log_pdf()
        except NotImplementedError as e:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            dmem_key_in_list = ['params1']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params1]
            mean_log_d1 = mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                                   dmem_key_in_list=dmem_key_in_list,
                                   dmem_arg_in_list=dmem_arg_in_list,
                                   dmem_val_in_list=dmem_val_in_list,
                                   obj=d1, reduce_obj=reduce_obj,
                                   reduce_tuple=reduce_tuple,
                                   mpi_pool=mpi_pool_tuple[0])
    # d2.log_pdf
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        mean_log_d2 = mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                               dmem_key_in_list=dmem_key_in_list,
                               dmem_arg_in_list=dmem_arg_in_list,
                               dmem_val_in_list=dmem_val_in_list,
                               obj=d2, reduce_obj=reduce_obj,
                               reduce_tuple=reduce_tuple,
                               mpi_pool=mpi_pool_tuple[1])
    else:
        mean_log_d2 = 0.
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mean_log_d2 += mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                                    dmem_key_in_list=dmem_key_in_list,
                                    dmem_arg_in_list=dmem_arg_in_list,
                                    dmem_val_in_list=dmem_val_in_list,
                                    obj=d2, reduce_obj=reduce_obj,
                                    reduce_tuple=reduce_tuple,
                                    mpi_pool=mpi_pool_tuple[1], splitted=True)
    out = mean_log_d1 - mean_log_d2
    return out

def grad_a_kl_divergence(d1, d2, params1=None, params2=None,
                         qtype=None, qparams=None, x=None, w=None,
                         batch_size=None, mpi_pool_tuple=(None,None)):
    r""" Compute :math:`\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`] --
        :math:`\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ( (qtype is not None) and (qparams is not None)
         and (x is None) and (w is None) ):
        (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ( (qtype is None) and (qparams is None)
           and (x is not None) and (w is not None) ):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        out = - mpi_eval("grad_a_log_pdf", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=d2, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool_tuple[1])
    else:
        out = np.zeros( d2.n_coeffs )
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            out -= mpi_eval("grad_a_log_pdf", scatter_tuple=scatter_tuple,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            dmem_val_in_list=dmem_val_in_list,
                            obj=d2, reduce_obj=reduce_obj,
                            reduce_tuple=reduce_tuple,
                            mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out

def tuple_grad_a_kl_divergence(d1, d2, params1=None, params2=None,
                               qtype=None, qparams=None, x=None, w=None,
                               batch_size=None, mpi_pool_tuple=(None,None),
                               d1_entropy=True):
    r""" Compute :math:`\left(\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})\right)`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`tuple`) --
        :math:`\left(\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),\nabla_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})\right)`
    
    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ( (qtype is not None) and (qparams is not None)
         and (x is None) and (w is None) ):
        (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ( (qtype is None) and (qparams is None)
           and (x is not None) and (w is not None) ):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = TupleExpectationReduce()
    # d1.log_pdf
    mean_log_d1 = 0.
    if d1_entropy:
        try:
            mean_log_d1 = d1.mean_log_pdf()
        except NotImplementedError as e:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            dmem_key_in_list = ['params1']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params1]
            mean_log_d1 = mpi_eval("log_pdf", scatter_tuple=scatter_tuple,
                                   dmem_key_in_list=dmem_key_in_list,
                                   dmem_arg_in_list=dmem_arg_in_list,
                                   dmem_val_in_list=dmem_val_in_list,
                                   obj=d1, reduce_obj=reduce_obj,
                                   reduce_tuple=reduce_tuple,
                                   mpi_pool=mpi_pool_tuple[0])
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        o1, o2 = mpi_eval("tuple_grad_a_log_pdf", scatter_tuple=scatter_tuple,
                                   dmem_key_in_list=dmem_key_in_list,
                                   dmem_arg_in_list=dmem_arg_in_list,
                                   dmem_val_in_list=dmem_val_in_list,
                                   obj=d2, reduce_obj=reduce_obj,
                                   reduce_tuple=reduce_tuple,
                                   mpi_pool=mpi_pool_tuple[1])
        mean_log_d2 = o1
        ga = -o2
    else:
        mean_log_d2 = 0.
        ga = np.zeros( d2.n_coeffs )
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            o1, o2 = mpi_eval("tuple_grad_a_log_pdf", scatter_tuple=scatter_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              obj=d2, reduce_obj=reduce_obj,
                              reduce_tuple=reduce_tuple,
                              mpi_pool=mpi_pool_tuple[1], splitted=True)
            mean_log_d2 += o1
            ga -= o2
    ev = mean_log_d1 - mean_log_d2
    return ev, ga

def hess_a_kl_divergence(d1, d2, params1=None, params2=None,
                         qtype=None, qparams=None, x=None, w=None,
                         batch_size=None, mpi_pool_tuple=(None,None)):
    r""" Compute :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N,N`] --
        :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ( (qtype is not None) and (qparams is not None)
         and (x is None) and (w is None) ):
        (x,w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool_tuple[0])
    elif ( (qtype is None) and (qparams is None)
           and (x is not None) and (w is not None) ):
        pass
    else:
        raise ValueError("Parameters (qtype,qparams) and (x,w) are mutually " +
                         "exclusive, but one pair of them is necessary.")
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        out = - mpi_eval("hess_a_log_pdf", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=d2, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool_tuple[1])
    else:
        nc = d2.n_coeffs
        out = np.zeros((nc,nc))
        # Split data and get maximum length of chunk
        if mpi_pool_tuple[1] is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool_tuple[1].split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            out -= mpi_eval("hess_a_log_pdf", scatter_tuple=scatter_tuple,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            dmem_val_in_list=dmem_val_in_list,
                            obj=d2, reduce_obj=reduce_obj,
                            reduce_tuple=reduce_tuple,
                            mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out

def storage_hess_a_kl_divergence(d1, d2, params1=None, params2=None,
                                 qtype=None, qparams=None, x=None, w=None,
                                 batch_size=None, mpi_pool_tuple=(None,None)):
    r""" Assemble :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`.

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one.
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2`

    Returns:
      (None) -- the result is stored in ``params2['hess_a_kl_divergence']``
    
    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.

    .. note:: the dictionary ``params2`` must be provided
    """
    # assemble/fetch Hessian
    H = hess_a_kl_divergence(
        d1, d2, params1=params1, params2=params2,
        qtype=qtype, qparams=qparams, x=x, w=w,
        batch_size=batch_size,
        mpi_pool_tuple=mpi_pool_tuple)
    return (None, H)

def action_hess_a_kl_divergence(H, v):
    r""" Evaluate action of :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})` on vector :math:`v`.

    Args:
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector :math:`v`
      H (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]): Hessian
        :math:`\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}})`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --
        :math:`\langle\nabla^2_{\bf a}\mathcal{D}_{KL}(\pi_1 | \pi_{2,{\bf a}}),v\rangle`    
    """
    return np.dot(H, v)

def kl_divergence_component(f, params=None,
                            x=None, w=None,
                            batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m f(x_i) = -\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f` 
      params (dict): parameters for function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params]
        out = - mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=f, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool)
    else:
        out = 0.
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params]
            out += - mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              obj=d2, reduce_obj=reduce_obj,
                              reduce_tuple=reduce_tuple,
                              mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out

def grad_a_kl_divergence_component(f, params=None,
                                   x=None, w=None,
                                   batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m \nabla_{\bf a}f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla_{\bf a} \left(\log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f` 
      params (dict): parameters for function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params]
        out = - mpi_eval("grad_a", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=f, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool)
    else:
        out = 0.
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params]
            out += - mpi_eval("grad_a", scatter_tuple=scatter_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              obj=d2, reduce_obj=reduce_obj,
                              reduce_tuple=reduce_tuple,
                              mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out

def hess_a_kl_divergence_component(f, params=None,
                                   x=None, w=None,
                                   batch_size=None, mpi_pool=None):
    r""" Compute :math:`-\sum_{i=0}^m \nabla^2_{\bf a}f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla^2_{\bf a} \left(\log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

    Args:
      f (ProductDistributionParametricPullbackComponentFunction): function :math:`f` 
      params (dict): parameters for function :math:`f`
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi_1}`
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f``

    Returns:
      (:class:`float<float>`) -- value
    """
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        dmem_key_in_list = ['params']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params]
        out = - mpi_eval("hess_a", scatter_tuple=scatter_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         obj=f, reduce_obj=reduce_obj,
                         reduce_tuple=reduce_tuple,
                         mpi_pool=mpi_pool)
    else:
        out = 0.
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:] for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice] for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            dmem_key_in_list = ['params']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params]
            out += - mpi_eval("hess_a", scatter_tuple=scatter_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              obj=d2, reduce_obj=reduce_obj,
                              reduce_tuple=reduce_tuple,
                              mpi_pool=mpi_pool_tuple[1], splitted=True)
    return out
    
def misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\vert f_1 - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be 
    
    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit :math:`\vert f_1 - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    if isinstance(f1, np.ndarray):
        F1 = f1[idxs_slice]
    else:
        F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)
    if F1.ndim == 2:
        mf = np.sum((F1 - F2)**2, axis=1)
    else:
        mf = ( F1 - F2 )**2.
    return mf

def grad_a_misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\nabla_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be 
    
    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit
         :math:`\nabla_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    # Evaluate f2
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)
    # Evaluate f1 and grad_a f1
    F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)
    ga_F1 = f1.grad_a(x, precomp=params1, idxs_slice=idxs_slice)
    mf2 = F1 - F2
    ga_mf2 = 2. * mf2[:,np.newaxis] * ga_F1
    return ga_mf2

def hess_a_misfit_squared(f1, f2, x, params1=None, params2=None, idxs_slice=None):
    r""" Compute :math:`\nabla^2_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      idxs_slice (:class:`slice<slice>`): slice of points to be 
    
    Returns:
      (:class:`ndarray<numpy.ndarray>`) --  misfit
         :math:`\nabla^2_{\bf a}\vert f_{1,{\bf a}} - f_2 \vert^2`
    """
    if idxs_slice is None:
        idxs_slice = slice(None)
    # Evaluate f2
    if isinstance(f2, np.ndarray):
        F2 = f2[idxs_slice]
    else:
        F2 = f2.evaluate(x, precomp=params2, idxs_slice=idxs_slice)
    # Evaluate f1, grad_a f1 and hess_a f1
    F1 = f1.evaluate(x, precomp=params1, idxs_slice=idxs_slice)
    ga_F1 = f1.grad_a(x, precomp=params1, idxs_slice=idxs_slice)
    ha_F1 = f1.hess_a(x, precomp=params1, idxs_slice=idxs_slice)
    mf2 = F1 - F2
    ha_mf2 = 2. * ( mf2[:,np.newaxis,np.newaxis] * ha_F1 + \
                    ga_F1[:,:,np.newaxis] * ga_F1[:,np.newaxis,:] )
    return ha_mf2

def L2_misfit(*args, **kwargs):
    r""" Compute :math:`\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not. 
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`
    
    Returns:
      (:class:`float<float>`) --  misfit :math:`\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    l2squared = L2squared_misfit(*args, **kwargs)
    return np.sqrt(l2squared)
    
def L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
              qtype=None, qparams=None, x=None, w=None,
              batch_size=None, mpi_pool=None):
    r""" Compute :math:`\Vert f_1 - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]):
        function :math:`f_1` or its functions values
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not. 
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`
    
    Returns:
      (:class:`float<float>`) --  misfit :math:`\Vert f_1 - f_2 \Vert^2_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if ( isinstance(f1, np.ndarray) and isinstance(f2, np.ndarray)
         and isinstance(w, np.ndarray) ):
        F1 = f1
        F2 = f2
        err = np.abs( F1 - F2 )
        L2err = np.dot( err**2., w )
    else:
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
        reduce_obj = ExpectationReduce()
        if batch_size is None:
            scatter_tuple = (['x'], [x])
            reduce_tuple = (['w'], [w])
            bcast_tuple = (['f1','f2'], [f1,f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            L2err = mpi_eval(misfit_squared, scatter_tuple=scatter_tuple,
                             bcast_tuple=bcast_tuple,
                             reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_val_in_list=dmem_val_in_list,
                             mpi_pool=mpi_pool)
        else: # Batching
            L2err = 0.
            # Split data and get maximum length of chunk
            if mpi_pool is None:
                x_list, ns = ([x], [0,len(x)])
                w_list = [w]
            else:
                split_dict = mpi_pool.split_data([x,w],['x','w'])
                x_list = [sd['x'] for sd in split_dict]
                w_list = [sd['w'] for sd in split_dict]
                ns = [0] + [ len(xi) for xi in x_list ]
                ns = list(np.cumsum(ns))
            max_len = x_list[0].shape[0]
            # Compute the number of iterations necessary for batching
            niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
            # Iterate
            idx0_list = [ 0 ] * len(x_list)
            for it in range(niter):
                # Prepare batch-slicing for each chunk
                idxs_slice_list = []
                for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                    incr = min(batch_size, xs.shape[0] - idx0)
                    idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                    idx0_list[i] += incr
                # Prepare input x and w
                x_in = [ xs[idxs_slice,:]
                         for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
                w_in = [ ws[idxs_slice]
                         for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
                # Evaluate
                scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
                reduce_tuple = (['w'], [w_in])
                bcast_tuple = (['f1','f2'], [f1,f2])
                dmem_key_in_list = ['params1', 'params2']
                dmem_arg_in_list = ['params1', 'params2']
                dmem_val_in_list = [params1, params2]
                L2err += mpi_eval( misfit_squared, scatter_tuple=scatter_tuple,
                                   bcast_tuple=bcast_tuple,
                                   dmem_key_in_list=dmem_key_in_list,
                                   dmem_arg_in_list=dmem_arg_in_list,
                                   dmem_val_in_list=dmem_val_in_list,
                                   reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                                   mpi_pool=mpi_pool, splitted=True )
    return L2err

def grad_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                     qtype=None, qparams=None, x=None, w=None,
                     batch_size=None, mpi_pool=None):
    r""" Compute :math:`\nabla_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not. 
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --  misfit gradient
        :math:`\nabla_{\bf a}\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if (x is None) and (w is None):
        (x,w) = d.quadrature(qtype, qparams)
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        bcast_tuple = (['f1','f2'], [f1,f2])
        dmem_key_in_list = ['params1', 'params2']
        dmem_arg_in_list = ['params1', 'params2']
        dmem_val_in_list = [params1, params2]
        ga_L2err = mpi_eval(grad_a_misfit_squared, scatter_tuple=scatter_tuple,
                            bcast_tuple=bcast_tuple,
                            reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            dmem_val_in_list=dmem_val_in_list,
                            mpi_pool=mpi_pool)
    else: # Batching
        ga_L2err = np.zeros( f1.n_coeffs )
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:]
                     for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice]
                     for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            bcast_tuple = (['f1','f2'], [f1,f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            ga_L2err += mpi_eval( grad_a_misfit_squared,
                                  scatter_tuple=scatter_tuple,
                                  bcast_tuple=bcast_tuple,
                                  dmem_key_in_list=dmem_key_in_list,
                                  dmem_arg_in_list=dmem_arg_in_list,
                                  dmem_val_in_list=dmem_val_in_list,
                                  reduce_obj=reduce_obj,
                                  reduce_tuple=reduce_tuple,
                                  mpi_pool=mpi_pool, splitted=True )
    return ga_L2err

def hess_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                     qtype=None, qparams=None, x=None, w=None,
                     batch_size=None, mpi_pool=None):
    r""" Compute :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not. 
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]) --  misfit Hessian
        :math:`\nabla^2_{\bf a}\Vert f_1 - f_2 \Vert_{L^2_\pi}`

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    if (x is None) and (w is None):
        (x,w) = d.quadrature(qtype, qparams)
    reduce_obj = ExpectationReduce()
    if batch_size is None:
        scatter_tuple = (['x'], [x])
        reduce_tuple = (['w'], [w])
        bcast_tuple = (['f1','f2'], [f1,f2])
        dmem_key_in_list = ['params1', 'params2']
        dmem_arg_in_list = ['params1', 'params2']
        dmem_val_in_list = [params1, params2]
        ha_L2err = mpi_eval(hess_a_misfit_squared, scatter_tuple=scatter_tuple,
                            bcast_tuple=bcast_tuple,
                            reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            dmem_val_in_list=dmem_val_in_list,
                            mpi_pool=mpi_pool)
    else: # Batching
        nc = f1.n_coeffs
        ha_L2err = np.zeros((nc,nc))
        # Split data and get maximum length of chunk
        if mpi_pool is None:
            x_list, ns = ([x], [0,len(x)])
            w_list = [w]
        else:
            split_dict = mpi_pool.split_data([x,w],['x','w'])
            x_list = [sd['x'] for sd in split_dict]
            w_list = [sd['w'] for sd in split_dict]
            ns = [0] + [ len(xi) for xi in x_list ]
            ns = list(np.cumsum(ns))
        max_len = x_list[0].shape[0]
        # Compute the number of iterations necessary for batching
        niter = max_len // batch_size + (1 if max_len % batch_size > 0 else 0)
        # Iterate
        idx0_list = [ 0 ] * len(x_list)
        for it in range(niter):
            # Prepare batch-slicing for each chunk
            idxs_slice_list = []
            for i, (xs, idx0) in enumerate(zip(x_list, idx0_list)):
                incr = min(batch_size, xs.shape[0] - idx0)
                idxs_slice_list.append( slice(idx0, idx0+incr, None) )
                idx0_list[i] += incr
            # Prepare input x and w
            x_in = [ xs[idxs_slice,:]
                     for xs, idxs_slice in zip(x_list, idxs_slice_list) ]
            w_in = [ ws[idxs_slice]
                     for ws, idxs_slice in zip(w_list, idxs_slice_list) ]
            # Evaluate
            scatter_tuple = (['x','idxs_slice'],[x_in, idxs_slice_list])
            reduce_tuple = (['w'], [w_in])
            bcast_tuple = (['f1','f2'], [f1,f2])
            dmem_key_in_list = ['params1', 'params2']
            dmem_arg_in_list = ['params1', 'params2']
            dmem_val_in_list = [params1, params2]
            ha_L2err += mpi_eval( hess_a_misfit_squared,
                                  scatter_tuple=scatter_tuple,
                                  bcast_tuple=bcast_tuple,
                                  dmem_key_in_list=dmem_key_in_list,
                                  dmem_arg_in_list=dmem_arg_in_list,
                                  dmem_val_in_list=dmem_val_in_list,
                                  reduce_obj=reduce_obj,
                                  reduce_tuple=reduce_tuple,
                                  mpi_pool=mpi_pool, splitted=True )
    return ha_L2err

def storage_hess_a_L2squared_misfit(f1, f2, d=None, params1=None, params2=None,
                             qtype=None, qparams=None, x=None, w=None,
                             batch_size=None, mpi_pool=None):
    r""" Assemble :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`.

    Args:
      f1 (:class:`ParametricFunctionApproximation`): function
        :math:`f_1`
      f2 (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
        :math:`f_2` or its functions values
      d (Distribution): distribution :math:`\pi`
      params1 (dict): parameters for function :math:`f_1`
      params2 (dict): parameters for function :math:`f_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
        used for the approximation of :math:`\mathbb{E}_{\pi}`
      batch_size (int): this defines whether to evaluate in batches or not. 
        A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``f1`` and ``f2`

    Returns:
      (None) -- the result is stored in ``params1['hess_a_L2_misfit']``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.

    .. note:: the dictionary ``params1`` must be provided
    """
    H = hess_a_L2squared_misfit(
        f1, f2, d=d, params1=params1, params2=params2,
        qtype=qtype, qparams=qparams, x=x, w=w,
        batch_size=batch_size, mpi_pool=mpi_pool)
    return (None, H)

def action_hess_a_L2squared_misfit(H, v):
    r""" Evaluate the action of :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}` on :math:`v`.

    Args:
      v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector :math:`v`
      v (:class:`ndarray<numpy.ndarray>` [:math:`N,N`]): Hessian
        :math:`\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi}`

    Returns:
      (:class:`ndarray<numpy.ndarray>` [:math:`N`]) --
        :math:`\langle\nabla^2_{\bf a}\Vert f_{1,{\bf a}} - f_2 \Vert^2_{L^2_\pi},v\rangle`
    """
    return np.dot(H, v)

def grad_t_kl_divergence(x, d1, d2, params=None, params2=None,
                         qtype=None, qparams=None, 
                         batch_size=None, mpi_pool_tuple=(None,None)):
    r""" Compute :math:`\nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))`.

    This corresponds to:

    .. math:

       \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) = (\nabla_x T)^{-\top} \left[ \nabla_x \log \frac{\pi_1}{\pi_2(T)} \right]

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``
    
    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    # Note: this is a naive implementation. We should be able to reuse
    # T.grad_x in pbdistribution.grad_x_log_pdf and implement parallelization
    scatter_tuple = (['x'], [x])
    grad_x_tm = mpi_eval("grad_x", obj=d2.transport_map,
                         scatter_tuple=scatter_tuple, mpi_pool=mpi_pool_tuple[1])
    grad_t = mpi_eval("grad_x_log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[0]) - \
             mpi_eval("grad_x_log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[1])
    for i in range(x.shape[0]):
        scila.solve_triangular(grad_x_tm[i,:,:], grad_t[i,:],
                               lower=True, trans='T', overwrite_b=True)
    return grad_t

def grad_x_grad_t_kl_divergence(x, d1, d2, params1=None, params2=None, 
                                qtype=None, qparams=None, 
                                batch_size=None, mpi_pool_tuple=(None,None)):
    r""" Compute :math:`\nabla_x \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T))`.

    This corresponds to:

    .. math:

       \nabla_x \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) = (\nabla_x T)^{-\top} \left[ \nabla^2_x \log \frac{\pi_1}{\pi_2(T)} - \sum_{i=1}^d \left( \nabla_T \mathcal{D}_{KL}(\pi_1, \pi_2(T)) \right)_i \nabla^2_x T^{(i)} \right]

    Args:
      d1 (Distribution): distribution :math:`\pi_1`
      d2 (Distribution): distribution :math:`\pi_2`
      params1 (dict): parameters for distribution :math:`\pi_1`
      params2 (dict): parameters for distribution :math:`\pi_2`
      qtype (int): quadrature type to be used for the approximation of
        :math:`\mathbb{E}_{\pi_1}`
      qparams (object): parameters necessary for the construction of the
        quadrature
      batch_size (int): this is the size of the batch to
        evaluated for each iteration. A size ``1`` correspond to a completely
        non-vectorized evaluation. A size ``None`` correspond to a
        completely vectorized one. (Note: if ``nprocs > 1``, then the batch
        size defines the size of the batch for each process)
      mpi_pool_tuple (:class:`tuple` [2] of :class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`):
        pool of processes to be used for the evaluation of ``d1`` and ``d2``

    .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
      exclusive, but one pair of them is necessary.
    """
    # Note: this is a naive implementation. We should be able to reuse
    # T.grad_x in pbdistribution.grad_x_log_pdf and implement parallelization
    dim = d2.dim
    scatter_tuple = (['x'], [x])
    grad_x_tm = mpi_eval("grad_x", obj=d2.transport_map, scatter_tuple=scatter_tuple,
                         mpi_pool=mpi_pool_tuple[1])
    grad_t = mpi_eval("grad_x_log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[0]) - \
             mpi_eval("grad_x_log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                      mpi_pool=mpi_pool_tuple[1])
    for i in range(x.shape[0]):
        scila.solve_triangular(grad_x_tm[i,:,:], grad_t[i,:],
                               lower=True, trans='T', overwrite_b=True)
    hess_log_d1_d2 = mpi_eval("hess_x_log_pdf", obj=d1, scatter_tuple=scatter_tuple,
                              mpi_pool=mpi_pool_tuple[0]) - \
                     mpi_eval("hess_x_log_pdf", obj=d2, scatter_tuple=scatter_tuple,
                              mpi_pool=mpi_pool_tuple[1])
    hess_fv_comp = np.zeros( (x.shape[0], dim, dim) ) # Last term in brakets
    for k,(a,avar) in enumerate(zip(d2.transport_map.approx_list,
                                    d2.transport_map.active_vars)):
        # numpy advanced indexing
        nvar = len(avar)
        rr,cc = np.meshgrid(avar,avar)
        rr = list( rr.flatten() )
        cc = list( cc.flatten() )
        idxs = (slice(None), rr, cc)
        # Compute Hessian component
        hess_fv_comp[idxs] = (grad_t[:,k][:,nax,nax] * \
                              a.hess_x(x[:,avar])).reshape((x.shape[0],nvar**2))
    # Assemble term in the brakets
    grad_x_grad_t = hess_log_d1_d2 - hess_fv_comp
    # Solve in place
    for i in range(x.shape[0]):
        scila.solve_triangular(grad_x_tm[i,:,:], grad_x_grad_t[i,:,:],
                               lower=True, trans='T', overwrite_b=True)
    return (grad_t, grad_x_grad_t)

def laplace_approximation(pi, params=None, x0=None, tol=1e-5, ders=2, fungrad=False):
    r""" Compute the Laplace approximation of the distribution :math:`\pi`.

    Args:
      pi (Distribution): distribution :math:`\pi`
      params (dict): parameters for distribution :math:`\pi`
      tol (float): tolerance to be used to solve the maximization problem.
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``.
    

    Returns:
      (:class:`GaussianDistribution`) -- Laplace approximation
    """
    # Minimize :math:`-\log \pi`
    if params is None:
        params = {}
    params['nobj'] = 0
    params['gx_nobj'] = 0
    params['hx_nobj'] = 0
    def objective(x, params):
        params['nobj'] += 1
        out = - pi.log_pdf(x[nax,:], params)[0]
        logger.debug("Lap. Obj. Eval. %d - f val. = %.10e" % (params['nobj'], out))
        return out
    def dx_objective(x, params):
        params['gx_nobj'] += 1
        out = - pi.grad_x_log_pdf(x[nax,:], params)[0,:]
        logger.debug(
            "Lap. Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(out))
        return out
    def tuple_dx_objective(x, params):
        params['nobj'] += 1
        params['gx_nobj'] += 1
        ev, gx = pi.tuple_grad_x_log_pdf(x[nax,:], params)
        ev = -ev[0]
        gx = -gx[0,:]
        logger.debug("Lap. Obj. Eval. %d - f val. = %.10e" % (params['nobj'], ev))
        logger.debug(
            "Lap. Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(gx))
        return ev, gx
    def dx2_objective(x, params):
        params['hx_nobj'] += 1
        out = - pi.hess_x_log_pdf(x[nax,:], params)[0,:,:]
        logger.debug(
            "Lap. Hess. Obj. Eval. %d " % params['hx_nobj'])
        return out
    if x0 is None:
        x0 = np.zeros(pi.dim) # Random or zero starting point? Or input argument?
    options = {'maxiter': 10000,
               'disp': False}
    if ders == 0:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              method='BFGS',
                              tol=tol,
                              options=options)
    elif ders == 1:
        if not fungrad:
            res = sciopt.minimize(objective, args=params,
                                  x0=x0,
                                  jac=dx_objective,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
        else:
            res = sciopt.minimize(tuple_dx_objective, args=params,
                                  x0=x0,
                                  jac=True,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
    elif ders == 2:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              hess=dx2_objective,
                              method='newton-cg',
                              tol=tol,
                              options=options)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    # Log
    if res['success']:
        logger.info("Optimization terminated successfully")
    else:
        logger.info("Optimization failed.")
        logger.info("Message: %s" % res['message'])
    logger.info("  Function value:          %6f" % res['fun'])
    if ders >= 1:
        logger.info("  Norm of the Jacobian:    %6f" % npla.norm(res['jac']))
    logger.info("  Number of iterations:    %6d" % res['nit'])
    logger.info("  N. function evaluations: %6d" % res['nfev'])
    if ders >= 1:
        logger.info("  N. Jacobian evaluations: %6d" % res['njev'])
    if ders >= 2:
        logger.info("  N. Hessian evaluations:  %6d" % res['nhev'])
    # Set MAP point
    x_map = res['x']
    # Compute the Hessian at the maximizer
    if ders == 2:
        hess_map = - pi.hess_x_log_pdf( x_map[nax,:] )[0,:,:]
    elif ders == 1: # Finite difference
        dx = 1e-6
        hess_map = - grad_x_fd(pi.grad_x_log_pdf, x_map[nax,:], dx)[0,:,:]
    elif ders == 0:
        raise NotImplementedError("The finite difference Hessian is not implemented " + \
                                  "for ders==0.")
    # Define the Gaussian distribution/Laplace approximation
    d_laplace = GaussianDistribution(x_map, precision=hess_map)
    return d_laplace


def laplace_approximation_withBounds(pi, params=None, tol=1e-5, ders=2, disp=True, bounds = None):
    r""" Compute the Laplace approximation of the distribution :math:`\pi`.

    Args:
      pi (Distribution): distribution :math:`\pi`
      params (dict): parameters for distribution :math:`\pi`
      tol (float): tolerance to be used to solve the maximization problem.
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
      disp (bool): whether to display output from optimizer.

    Returns:
      (:class:`GaussianDistribution`) -- Laplace approximation
    """
    nax = np.newaxis
    # Minimize :math:`-\log \pi`
    def objective(x, params):
        return - pi.log_pdf(x[nax,:], params)[0]
    def dx_objective(x, params):
        return - pi.grad_x_log_pdf(x[nax,:], params)[0,:]
    def dx2_objective(x, params):
        return - pi.hess_x_log_pdf(x[nax,:], params)[0,:,:]
    x0 = np.zeros(pi.dim) # Random or zero starting point? Or input argument?
    options = {'maxiter': 10000,
               'disp': disp}
    if ders == 0:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              method='L-BFGS-B',
                              tol=tol,
                              options=options, bounds = bounds)
    elif ders == 1:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              method='L-BFGS-B',
                              tol=tol,
                              options=options, bounds = bounds)
    elif ders == 2:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              hess=dx2_objective,
                              method='TNC',
                              tol=tol,
                              options=options, bounds = bounds)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    x_map = res['x']
    # Compute the Hessian at the maximizer
    hess_map = - pi.hess_x_log_pdf( x_map[nax,:] )[0,:,:]
    # Define the Gaussian distribution/Laplace approximation
    d_laplace = GaussianDistribution(x_map, precision=hess_map)
    return d_laplace

def maximum_likelihood(logL, params=None, x0=None, tol=1e-5, ders=2, fungrad=False):
    r""" Compute the maximum likelihood of the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`.

    Args:
      logL (:class:`LogLikelihood`): log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      params (dict): parameters for the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      tol (float): tolerance to be used to solve the maximization problem
      ders (int): order of derivatives available for the solution of the
        optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian
      fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
        :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
        gradient in one step. This is used only for ``ders==1``
    

    Returns:
      (:class:`ndarray<numpy.ndarray>`) -- Maximum likelihood estimator
    """
    # Minimize - logL
    if params is None:
        params = {}
    params['nobj'] = 0
    params['gx_nobj'] = 0
    params['hx_nobj'] = 0
    def objective(x, params):
        params['nobj'] += 1
        out = - logL.evaluate(x[nax,:], params)[0]
        logger.debug("Max-lkl Obj. Eval. %d - f val. = %.10e" % (params['nobj'], out))
        return out
    def dx_objective(x, params):
        params['gx_nobj'] += 1
        out = - logL.grad_x(x[nax,:], params)[0,:]
        logger.debug(
            "Max-lkl Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(out))
        return out
    def tuple_dx_objective(x, params):
        params['nobj'] += 1
        params['gx_nobj'] += 1
        ev, gx = logL.tuple_grad_x(x[nax,:], params)
        ev = -ev[0]
        gx = -gx[0,:]
        logger.debug("Max-lkl Obj. Eval. %d - f val. = %.10e" % (params['nobj'], ev))
        logger.debug(
            "Max-lkl Grad. Obj. Eval. %d " % params['nobj'] + \
            "- ||grad f|| = %.10e" % npla.norm(gx))
        return ev, gx
    def dx2_objective(x, params):
        params['hx_nobj'] += 1
        out = - logL.hess_x(x[nax,:], params)[0,:,:]
        logger.debug(
            "Max-lkl Hess. Obj. Eval. %d " % params['hx_nobj'])
        return out
    # Solve
    if x0 is None:
        x0 = np.zeros(logL.dim)
    options = {'maxiter': 10000,
               'disp': False}
    if ders == 0:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              method='BFGS',
                              tol=tol,
                              options=options)
    elif ders == 1:
        if not fungrad:
            res = sciopt.minimize(objective, args=params,
                                  x0=x0,
                                  jac=dx_objective,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
        else:
            res = sciopt.minimize(tuple_dx_objective, args=params,
                                  x0=x0,
                                  jac=True,
                                  method='BFGS',
                                  tol=tol,
                                  options=options)
    elif ders == 2:
        res = sciopt.minimize(objective, args=params,
                              x0=x0,
                              jac=dx_objective,
                              hess=dx2_objective,
                              method='newton-cg',
                              tol=tol,
                              options=options)
    else:
        raise ValueError("ders parameter not valid. Chose between 0,1,2.")
    # Log
    if res['success']:
        logger.info("Optimization terminated successfully")
    else:
        logger.info("Optimization failed.")
        logger.info("Message: %s" % res['message'])
    logger.info("  Function value:          %6f" % res['fun'])
    if ders >= 1:
        logger.info("  Norm of the Jacobian:    %6f" % npla.norm(res['jac']))
    logger.info("  Number of iterations:    %6d" % res['nit'])
    logger.info("  N. function evaluations: %6d" % res['nfev'])
    if ders >= 1:
        logger.info("  N. Jacobian evaluations: %6d" % res['njev'])
    if ders >= 2:
        logger.info("  N. Hessian evaluations:  %6d" % res['nhev'])
    # Set MAP point
    return res['x']