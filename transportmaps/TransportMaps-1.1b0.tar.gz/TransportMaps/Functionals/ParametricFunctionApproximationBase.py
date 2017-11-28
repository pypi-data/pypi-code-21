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

import logging
import numpy as np
import numpy.linalg as npla

import TransportMaps as TM
from TransportMaps.Functionals.FunctionBase import *

__all__ = ['ParametricFunctionApproximation',
           'TensorizedFunctionApproximation']

class ParametricFunctionApproximation(Function):
    r""" Abstract class for parametric approximation :math:`f_{\bf a}:\mathbb{R}^d\rightarrow\mathbb{R}` of :math:`f:\mathbb{R}^d\rightarrow\mathbb{R}`.

    Args:
      dim (int): number of dimensions
    """

    def __init__(self, dim):
        super(ParametricFunctionApproximation,self).__init__(dim)
        self.init_coeffs()

    def init_coeffs(self):
        r""" [Abstract] Initialize the coefficients :math:`{\bf a}`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @property
    def n_coeffs(self):
        r""" [Abstract] Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def get_n_coeffs(self):
        TM.deprecate("ParametricFunctionApproximation.get_n_coeffs()", "1.0b3",
                     "Use property ParametricFunctionApproximation.n_coeffs instead")
        return self.n_coeffs

    @property
    def coeffs(self):
        r""" [Abstract] Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def get_coeffs(self):
        TM.deprecate("ParametricFunctionApproximation.get_coeffs()", "1.0b3",
                     "Use property ParametricFunctionApproximation.coeffs instead")
        return self.coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" [Abstract] Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def set_coeffs(self, coeffs):
        TM.deprecate("ParametricFunctionApproximation.set_coeffs(value)", "1.0b3",
                     "Use setter ParametricFunctionApproximation.coeffs = value instead.")
        self.coeffs = coeffs

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            :math:`\nabla_{\bf a} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
            :math:`\nabla^2_{\bf a} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial^2_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
            :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_evaluate(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_grad_x(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Return:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_partial_xd(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_grad_x_partial_xd(self, x, precomp=None):
        r""" [Abstract] Precompute  necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def precomp_partial2_xd(self, x, precomp=None):
        r""" [Abstract] Precompute necessary structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
          (:class:`dict<dict>`) -- data structures
        """
        raise NotImplementedError("To be implemented in sub-classes")

    def init_mem_precomp_regression(self):
        r""" Returns initialized dictionary for precomputation parameters
        """
        return (None, {})

    def regression_objective(self, a, params):
        r""" Objective function :math:`\Vert f - f_{\bf a} \Vert^2_{\pi}`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nobj'] += 1
        self.coeffs = a
        x = params['x']
        w = params['w']
        fvals = params['fvals']
        batch_size = params['batch_size'][0]
        # Evaluate L2 misfit
        scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
        bcast_tuple = (['f1', 'batch_size'], [self, batch_size])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['params1']
        dmem_val_in_list = [params['params1']]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = TM.mpi_eval(TM.L2squared_misfit, scatter_tuple=scatter_tuple,
                          bcast_tuple=bcast_tuple,
                          dmem_key_in_list=dmem_key_in_list,
                          dmem_arg_in_list=dmem_arg_in_list,
                          dmem_val_in_list=dmem_val_in_list,
                          reduce_obj=reduce_obj,
                          mpi_pool=self.mpi_pool)
        if params['regularization'] is None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] * npla.norm(a,2)**2.
        if self.logger.getEffectiveLevel() <= logging.INFO:
            self.logger.info("Regression Obj. Eval. %d - L2-misfit = %.10e" % (params['nobj'], out))
        return out

    def regression_grad_a_objective(self, a, params):
        r""" Objective function :math:`\nabla_{\bf a} \Vert f - f_{\bf a} \Vert^2_{\pi}`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda_obj'] += 1
        self.coeffs = a
        x = params['x']
        w = params['w']
        fvals = params['fvals']
        batch_size = params['batch_size'][1]
        # Evaluate grad_a L2 misfit
        scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
        bcast_tuple = (['f1', 'batch_size'], [self, batch_size])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['params1']
        dmem_val_in_list = [params['params1']]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = TM.mpi_eval(TM.grad_a_L2squared_misfit,
                          scatter_tuple=scatter_tuple,
                          bcast_tuple=bcast_tuple,
                          dmem_key_in_list=dmem_key_in_list,
                          dmem_arg_in_list=dmem_arg_in_list,
                          dmem_val_in_list=dmem_val_in_list,
                          reduce_obj=reduce_obj,
                          mpi_pool=self.mpi_pool)
        if params['regularization'] is None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] * 2. * a
        if self.logger.getEffectiveLevel() <= logging.INFO:
            self.logger.info("Regression Grad_a Obj. Eval. %d - ||grad_a L2-misfit|| = %.10e" % (
                params['nda_obj'], npla.norm(out)))
        return out

    def regression_hess_a_objective(self, a, params):
        r""" Objective function :math:`\nabla_{\bf a}^2 \Vert f - f_{\bf a} \Vert^2_{\pi}`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda2_obj'] += 1
        self.coeffs = a
        x = params['x']
        w = params['w']
        fvals = params['fvals']
        batch_size = params['batch_size'][2]
        # Evaluate hess_a L2 misfit
        scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
        bcast_tuple = (['f1', 'batch_size'], [self, batch_size])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['params1']
        dmem_val_in_list = [params['params1']]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = TM.mpi_eval(TM.hess_a_L2squared_misfit,
                          scatter_tuple=scatter_tuple,
                          bcast_tuple=bcast_tuple,
                          dmem_key_in_list=dmem_key_in_list,
                          dmem_arg_in_list=dmem_arg_in_list,
                          dmem_val_in_list=dmem_val_in_list,
                          reduce_obj=reduce_obj,
                          mpi_pool=self.mpi_pool)
        if params['regularization'] is None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += np.diag( np.ones(len(self.coeffs))*2.*params['regularization']['alpha'] )
        if self.logger.getEffectiveLevel() <= logging.INFO:
            self.logger.info("Regression Hess_a Obj. Eval. %d " % params['nda2_obj'])
        return out

    def regression_action_storage_hess_a_objective(self, a, v, params):
        r""" Assemble/fetch Hessian :math:`\nabla_{\bf a}^2 \Vert f - f_{\bf a} \Vert^2_{\pi}` and evaluate its action on :math:`v`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector on which to apply the Hessian
          params (dict): dictionary of parameters
        """
        self.coeffs = a
        x = params['x']
        w = params['w']
        fvals = params['fvals']
        batch_size = params['batch_size'][2]
        # Assemble Hessian
        if not self.hess_assembled:
            params['nda2_obj'] += 1
            scatter_tuple = (['x', 'w', 'f2'], [x, w, fvals])
            bcast_tuple = (['f1', 'batch_size'], [self, batch_size])
            dmem_key_in_list = ['params1']
            dmem_arg_in_list = ['params1']
            dmem_val_in_list = [params['params1']]
            dmem_key_out_list = ['hess_a_L2_misfit']
            (_, params['hess_a_L2_misfit']) = TM.mpi_eval(
                TM.storage_hess_a_L2squared_misfit, scatter_tuple=scatter_tuple,
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list, 
                mpi_pool=self.mpi_pool, concatenate=False)
            self.hess_assembled = True
            if self.logger.getEffectiveLevel() <= logging.INFO:
                self.logger.info("Regression Storage Hess_a Obj. Eval. %d " % params['nda2_obj'])
        # Evaluate the action of hess_a L2 misfit
        params['nda2_obj_dot'] += 1
        bcast_tuple = (['v'], [v])
        dmem_key_in_list = ['hess_a_L2_misfit']
        dmem_arg_in_list = ['H']
        dmem_val_in_list = [params['hess_a_L2_misfit']]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = TM.mpi_eval(TM.action_hess_a_L2squared_misfit,
                          bcast_tuple=bcast_tuple,
                          dmem_key_in_list=dmem_key_in_list,
                          dmem_arg_in_list=dmem_arg_in_list,
                          dmem_val_in_list=dmem_val_in_list,
                          reduce_obj=reduce_obj,
                          mpi_pool=self.mpi_pool)
        if params['regularization'] is None:
            pass
        elif params['regularization']['type'] == 'L2':
            regmat = np.diag( np.ones(len(self.coeffs))*2.*params['regularization']['alpha'] )
            out += np.dot(regmat, v)
        if self.logger.getEffectiveLevel() <= logging.INFO:
            self.logger.info("Regression Action Hess_a Obj. Eval. %d " % params['nda2_obj_dot'])
        return out

    @staticmethod
    def from_xml_element(node, dim):
        from TransportMaps import XML_NAMESPACE
        import TransportMaps.Functionals as FUNC
        if node.find(XML_NAMESPACE + 'linspan') is not None:
            approx_node = node.find(XML_NAMESPACE + 'linspan')
            return FUNC.LinearSpanApproximation.from_xml_element( approx_node, dim )
        elif node.find(XML_NAMESPACE + 'monotlinspan') is not None:
            approx_node = node.find(XML_NAMESPACE + 'monotlinspan')
            return FUNC.MonotonicLinearSpanApproximation.from_xml_element( approx_node, dim )
        elif node.find(XML_NAMESPACE + 'intexp') is not None:
            approx_node = node.find(XML_NAMESPACE + 'intexp')
            return FUNC.MonotonicIntegratedExponentialApproximation.from_xml_element(
                approx_node, dim )
        elif node.find(XML_NAMESPACE + 'intsq') is not None:
            approx_node = node.find(XML_NAMESPACE + 'intsq')
            return FUNC.MonotonicIntegratedSquaredApproximation.from_xml_element(
                approx_node, dim )
        else:
            raise ValueError("No recognised approximation.")

class TensorizedFunctionApproximation(ParametricFunctionApproximation):
    r""" [Abstract] Class for approximations using tensorization of unidimensional basis

    Args:
      basis_list (list): list of :math:`d` :class:`Basis<SpectralToolbox.Basis>`
    """
    def __init__(self, basis_list):
        self.basis_list = basis_list
        super(TensorizedFunctionApproximation,self).__init__(len(self.basis_list))

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        # Vandermonde matrices
        try: V_list = precomp['V_list']
        except KeyError as e:
            precomp['V_list'] = [ b.GradVandermonde(x[:,i], o)
                                  for i,(b,o) in
                                  enumerate(zip(self.basis_list,
                                                self.get_directional_orders())) ]
        if precomp_type == 'multi':
            self.precomp_Vandermonde_evaluate(x, precomp)
        return precomp

    def precomp_grad_x(self, x, precomp=None):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Letting :math:`\Phi^{(i)}(x_i)` being the uni-variate Vandermonde in
        :math:`x_i`, the ``i``-th element of the returned list is
        :math:`\partial_{x_i}\Phi^{(i)}(x_i)`.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            partial_x_V_list = [ b.GradVandermonde(x[:,i], o, k=1)
                                 for i,(b,o)
                                 in enumerate(zip(self.basis_list,
                                                  self.get_directional_orders())) ]
            precomp['partial_x_V_list'] = partial_x_V_list
        return precomp

    def precomp_hess_x(self, x, precomp=None):
        r""" Precompute the uni-variate Vandermonde matrices for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Letting :math:`\Phi^{(i)}(x_i)` being the uni-variate Vandermonde in
        :math:`x_i`, the ``i``-th element of the returned list is
        :math:`\partial^2_{x_i}\Phi^{(i)}(x_i)`.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Return:
          (:class:`dict<dict>` with :class:`list<list>`
            [:math:`d`] of :class:`ndarray<numpy.ndarray>` [:math:`m,n_i`]) --
            dictionary containing the list of Vandermonde matrices
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_x_V_list = precomp['partial2_x_V_list']
        except KeyError as e:
            partial2_x_V_list = [ b.GradVandermonde(x[:,i], o, k=2)
                                  for i,(b,o) in enumerate(zip(
                                          self.basis_list, self.get_directional_orders())) ]
            precomp['partial2_x_V_list'] = partial2_x_V_list
        return precomp

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_xd_V_last = precomp['partial_xd_V_last']
        except KeyError as e:
            o = self.get_directional_orders()[-1]
            precomp['partial_xd_V_last'] = self.basis_list[-1].GradVandermonde(
                x[:,-1], o, k=1)
        if precomp_type == 'multi':
            self.precomp_Vandermonde_partial_xd(x, precomp)
        return precomp

    def precomp_partial2_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial2_xd_V_last = precomp['partial2_xd_V_last']
        except KeyError as e:
            o = self.get_directional_orders()[-1]
            precomp['partial2_xd_V_last'] = self.basis_list[-1].GradVandermonde(x[:,-1], o, k=2)
        return precomp

    def precomp_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of uni-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_xd_V_last = precomp['partial2_xd_V_last']
        except KeyError as e:
            self.precomp_partial2_xd(x, precomp)
        return precomp

    def precomp_partial3_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrix for the evaluation of :math:`\partial^3_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`ndarray<numpy.ndarray>` [:math:`m,n_d`]) --
            dictionary with Vandermonde matrix
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial3_xd_V_last = precomp['partial3_xd_V_last']
        except KeyError as e:
            o = self.get_directional_orders()[-1]
            precomp['partial3_xd_V_last'] = self.basis_list[-1].GradVandermonde(x[:,-1], o, k=3)
        return precomp

    def precomp_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute uni-variate Vandermonde matrices for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>` with :class:`list<list>` [d]
            :class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
            dictionary containing the list of uni-variate Vandermonde matrices.
        """
        if precomp is None: precomp = {}
        try: V_list = precomp['V_list']
        except KeyError as e:
            self.precomp_evaluate(x, precomp)
        try: partial_x_V_list = precomp['partial_x_V_list']
        except KeyError as e:
            self.precomp_grad_x(x, precomp)
        try: partial2_x_V_list = precomp['partial2_x_V_list']
        except KeyError as e:
            self.precomp_hess_x(x, precomp)
        try: partial3_xd_V_last = precomp['partial3_xd_V_last']
        except KeyError as e:
            self.precomp_partial3_xd(x, precomp)
        return precomp