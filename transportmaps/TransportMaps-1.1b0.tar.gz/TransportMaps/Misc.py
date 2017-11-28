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

import sys
import logging
import warnings
import numpy as np
from TransportMaps.External import MPI_SUPPORT

if MPI_SUPPORT:
    import mpi_map

__all__ = ['LOG_LEVEL', 'logger', 'deprecate', 'setLogLevel',
  	 	   'get_mpi_pool', 'mpi_eval',
           'SumChunkReduce', 'TupleSumChunkReduce',
           'TensorDotReduce', 'ExpectationReduce', 'TupleExpectationReduce',
		   'generate_total_order_midxs']

####### LOGGING #########
LOG_LEVEL = logging.getLogger().getEffectiveLevel()

logger = logging.getLogger('TM.TransportMaps')
logger.propagate = False
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

def deprecate(name, version, msg):
    logger.warning("%s DEPRECATED since v%s. %s" % (name, version, msg))

def setLogLevel(level):
    r""" Set the log level for all existing and new objects related to the TransportMaps module

    Args:
      level (int): logging level

    .. see:: the :module:`logging` module.
    """
    import TransportMaps as TM
    TM.LOG_LEVEL = level
    for lname, logger in logging.Logger.manager.loggerDict.items():
        if "TM." in lname:
            logger.setLevel(level)

####### MPI ##########
def get_mpi_pool():
    r""" Get a pool of ``n`` processors
    
    Returns:
      (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`) -- pool of processors

    Usage example::
    
        import numpy as np
        import numpy.random as npr
        from TransportMaps import get_mpi_pool, mpi_eval

        class Operator(object):
            def __init__(self, a):
                self.a = a
            def sum(self, x, n=1):
                out = x
                for i in range(n):
                    out += self.a
                return out

        op = Operator(2.)
        x = npr.randn(100,5)
        n = 2

        pool = get_mpi_pool()
        pool.start(3)
        try:
            xsum = mpi_eval("sum", op, x, (n,), mpi_pool=pool)
        finally:
            pool.stop()
    """
    if MPI_SUPPORT:
        return mpi_map.MPI_Pool()
    else:
        raise RuntimeError("MPI is not supported")

def mpi_eval(f, scatter_tuple=None, bcast_tuple=None,
             dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
             dmem_key_out_list=None,
             obj=None, reduce_obj=None, reduce_tuple=None, import_set=None,
             mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      dmem_key_out_list (list): list of keys to be assigned to the outputs
        beside the first one
      obj (object): object where the function ``f_name`` is defined
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)   
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    # Init un-set arguments
    if scatter_tuple is None:
        scatter_tuple = ([],[])
    if bcast_tuple is None:
        bcast_tuple = ([],[])
    if dmem_key_in_list is None:
        dmem_key_in_list = []
    if dmem_arg_in_list is None:
        dmem_arg_in_list = []
    if dmem_val_in_list is None:
        dmem_val_in_list = []
    if dmem_key_out_list is None:
        dmem_key_out_list = []
    if reduce_tuple is None:
        reduce_tuple = ([],[])
    if import_set is None:
        import_set = set()

    # Start evaluation
    if mpi_pool is None:
        # Prepare arguments
        args = {}
        for key, val in zip(scatter_tuple[0], scatter_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                args[key] = val[0]
            else:
                args[key] = val
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            args[key] = val
        for key, val in zip(dmem_arg_in_list, dmem_val_in_list):
            args[key] = val
        reduce_args = {}
        for key, val in zip(reduce_tuple[0], reduce_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                reduce_args[key] = val[0]
            else:
                reduce_args[key] = val
        # Retrieve function
        if obj is not None:
            try:
                f = getattr(obj, f)
            except:
                raise NotImplementedError("Class %s " % obj.__class__.__name__ + \
                                          "does not implement method %s" % f)
        # Evaluate
        out = f(**args)
        if len(dmem_key_out_list) == 0:
            fval = out
        else:
            fval = out[0]
            pars = tuple(out[1:])
        # Reduce if necessary
        if reduce_obj is not None:
            fval = reduce_obj.outer_reduce(
                [ reduce_obj.inner_reduce(fval, **reduce_args) ], **reduce_args )
    else:
        # Prepare arguments
        obj_scatter = mpi_pool.split_data(scatter_tuple[1], scatter_tuple[0],
                                          splitted=splitted)
        obj_bcast = {}
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            obj_bcast[key] = val
        obj_args_reduce = mpi_pool.split_data(reduce_tuple[1], reduce_tuple[0],
                                              splitted=splitted)
        # Evaluate
        pars = tuple([None] * len(dmem_key_out_list))
        fval = mpi_pool.eval(f,
                             obj_scatter=obj_scatter, obj_bcast=obj_bcast,
                             dmem_key_in_list=dmem_key_in_list,
                             dmem_arg_in_list=dmem_arg_in_list,
                             dmem_key_out_list=dmem_key_out_list,
                             obj=obj,
                             reduce_obj=reduce_obj, reduce_args=obj_args_reduce,
                             import_set=import_set)
        # Put pieces together and return
        if reduce_obj is None and concatenate:
            fval = np.concatenate(fval, axis=0)
    if len(dmem_key_out_list) == 0:
        return fval
    else:
        return (fval,) + pars
    
#
# MPI REDUCE OPERATIONS
#
class SumChunkReduce(object):
    r""" Define the summation of the chunks operation.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """
    def __init__(self, axis=None):
        self.axis = axis
    def inner_reduce(self, x, *args, **kwargs):
        return x
    def outer_reduce(self, x, *args, **kwargs):
        return np.sum(x, axis=self.axis)

class TupleSumChunkReduce(SumChunkReduce):
    r""" Define the summation of the chunks operation over list of tuples.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """
    def outer_reduce(self, x, *args, **kwargs):
        out = []
        for i in range(len(x[0])):
            xin = [xx[i] for xx in x]
            out.append( super(TupleSumChunkReduce, self).outer_reduce(xin, *args, **kwargs) )
        return tuple(out)

class TensorDotReduce(object):
    r""" Define the reduce tensordot operation carried out through the mpi_eval function

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`tensordot<numpy.tensordot>` operation
    """
    def __init__(self, axis):
        self.axis = axis
    def inner_reduce(self, x, w):
        if x.shape[self.axis[0]] > 0:
            return np.tensordot(x, w, self.axis)
        else:
            return 0.
    def outer_reduce(self, x, w):
        return sum( x )

class ExpectationReduce(TensorDotReduce):
    r""" Define the expectation operation carried out through the mpi_eval function
    """
    def __init__(self):
        super(ExpectationReduce, self).__init__((0,0))

class TupleExpectationReduce(ExpectationReduce):
    r""" Define the expectation operation applied on a tuple

    If we are given a tuple :math:`(x_1,x_2)`, the inner reduce
    returns :math:`(\langle x_1,w\rangle , \langle x_2, w\rangle)`.

    Given a list of tuples :math:`\{(x_i,y_i\}_{i=0}^n`, the outer reduce
    gives :math:`(\sum x_i, \sum y_i)`.
    """
    def inner_reduce(self, x, w):
        out = []
        for xx in x:
            out.append( super(TupleExpectationReduce, self).inner_reduce(xx, w) )
        return tuple(out)
    def outer_reduce(self, x, w):
        out = []
        tdim = len(x[0])
        for i in range(tdim):
            xin = [xx[i] for xx in x]
            out.append( super(TupleExpectationReduce, self).outer_reduce(xin, w) )
        return tuple(out)

#
# Total order multi index generation
#
def generate_total_order_midxs(max_order_list):
    r""" Generate a total order multi-index

    Given the list of maximums :math:`{\bf m}`, the returned set of
    multi-index :math:`I` is such that :math:`\sum_j^d {\bf_i}_j <= max {\bf m}`
    and :math:`{\bf i}_j <= {\bf m}_j`.
    """
    # Improve performances by writing it in cython.
    dim = len(max_order_list)
    max_order = max(max_order_list)
    # Zeros multi-index
    midxs_set = set()
    midx_new = tuple([0]*dim)
    if sum(midx_new) < max_order:
        midxs_old_set = set([ midx_new ]) # Containing increasable multi-indices
    else:
        midxs_old_set = set()
    midxs_set.add(midx_new)
    # Higher order multi-indices
    for i in range(1,max_order+1):
        midxs_new_set = set()
        for midx_old in midxs_old_set:
            for d in range(dim):
                if midx_old[d] < max_order_list[d]:
                    midx_new = list(midx_old)
                    midx_new[d] += 1
                    midxs_set.add( tuple(midx_new) )
                    if sum(midx_new) < max_order:
                        midxs_new_set.add( tuple(midx_new) )
        midxs_old_set = midxs_new_set
    # Transform to list of tuples
    midxs_list = list(midxs_set)
    return midxs_list
    