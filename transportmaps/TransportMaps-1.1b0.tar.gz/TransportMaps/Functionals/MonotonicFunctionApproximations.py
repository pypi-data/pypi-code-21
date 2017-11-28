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
import scipy.optimize as sciopt

import SpectralToolbox.Spectral1D as S1D

import TransportMaps as TM

from TransportMaps import mpi_eval
from TransportMaps.Functionals.ParametricFunctionApproximationBase import *
from TransportMaps.Functionals.LinearSpanApproximationBase import *
from TransportMaps.Functionals.AlgebraicLinearSpanApproximations import *
from TransportMaps.Functionals.ProductDistributionParametricPullbackComponentFunctionBase \
    import ProductDistributionParametricPullbackComponentFunction

__all__ = ['MonotonicFunctionApproximation',
           'MonotonicLinearSpanApproximation',
           'MonotonicIntegratedExponentialApproximation',
           'MonotonicIntegratedSquaredApproximation']

nax = np.newaxis

class MonotonicFunctionApproximation(ParametricFunctionApproximation):
    r""" Abstract class for the approximation :math:`f \approx f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}` assumed to be monotonic in :math:`x_d`

    The class defines a series of methods peculiar to monotonic functions.
    """

    def xd_misfit(self, x, args):
        r""" Compute :math:`f_{\bf a}({\bf x}) - y`

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, and the last coordinate :math:`{\bf x}_d`, compute:

        .. math::

           f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y

        Args:
          x (float): evaluation point :math:`{\bf x}_d`
          args (tuple): containing :math:`({\bc x}_{1:d-1},y)`

        Returns:
          (:class:`float<float>`) -- misfit.
        """
        (xkm1,y) = args
        x = np.hstack( (xkm1,x) )[nax,:]
        return self.evaluate(x) - y

    def partial_xd_misfit(self, x, args):
        r""" Compute :math:`\partial_{x_d} f_{\bf a}({\bf x}) - y = \partial_{x_d} f_{\bf a}({\bf x})`

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, and the last coordinate :math:`{\bf x}_d`, compute:

        .. math::

           \partial f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d)

        Args:
          x (float): evaluation point :math:`{\bf x}_d`
          args (tuple): containing :math:`({\bc x}_{1:d-1},y)`

        Returns:
          (:class:`float<float>`) -- misfit derivative.
        """
        (xkm1,y) = args
        x = np.hstack( (xkm1,x) )[nax,:]
        return self.partial_xd(x)
    
    def inverse(self, xmd, y, xtol=1e-12, rtol=1e-15):
        r""" Compute :math:`{\bf x}_d` s.t. :math:`f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0`.

        Given the fixed coordinates :math:`{\bf x}_{1:d-1}`, the value
        :math:`y`, find the last coordinate :math:`{\bf x}_d` such that:

        .. math::

           f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0

        We will define this value the inverse of :math:`f_{\bf a}({\bf x})` and
        denote it by :math:`f_{\bf a}^{-1}({\bf x}_{1:d-1})(y)`.

        Args:
          xmd (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`
          xtol (float): absolute tolerance
          rtol (float): relative tolerance

        Returns:
          (:class:`float<float>`) -- inverse value :math:`x`.
        """
        args = (xmd,y)
        fail = True
        ntry = 0
        maxtry = 10
        mul = 1.
        while fail and ntry < maxtry:
            ntry += 1
            try:
                # out = sciopt.bisect( self.xd_misfit, a=-10.*mul, b=10.*mul,
                #                      args=(args,), xtol=xtol, rtol=rtol, maxiter=100 )
                out = sciopt.brentq( self.xd_misfit, a=-10.*mul, b=10.*mul,
                                     args=(args,), xtol=xtol, rtol=rtol, maxiter=100 )
                fail = False
            except ValueError:
                mul *= 10.
        if ntry == maxtry:
            raise RuntimeError(
                "Failed to converge: the interval does not contain the root.")
        else:
            return out

    def partial_xd_inverse(self, xmd, y):
        r""" Compute :math:`\partial_y f_{\bf a}^{-1}({\bf x}_{1:d-1})(y)`.

        Args:
          xmd (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`

        Returns:
          (:class:`float<float>`) -- derivative of the inverse value :math:`x`.
        """
        x = self.inverse(xmd,y)
        xeval = np.hstack( (xkm1,x) )
        return 1. / self.partial_xd(xeval)

    def get_identity_coeffs(self):
        raise NotImplementedError("To be implemented in subclasses")
        
    def get_default_init_values_regression(self):
        return self.get_identity_coeffs()
        
    def get_default_init_values_minimize_kl_divergence_component(self):
        return self.get_identity_coeffs()

    def minimize_kl_divergence_component(self,
                                         f, x, w,
                                         x0=None,
                                         regularization=None,
                                         tol=1e-4, maxit=100, ders=2,
                                         fungrad=False, 
                                         precomp_type='uni',
                                         batch_size=None,
                                         cache_level=1,
                                         mpi_pool=None,
                                         import_set=set()):
        r""" Compute :math:`{\bf a}^\star = \arg\min_{\bf a}-\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i) = \arg\min_{\bf a}-\sum_{i=0}^m f(x_i)`

        Args:
          f (ProductDistributionParametricPullbackComponentFunction): function :math:`f` 
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
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
          fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>` or :class:`list<list>` of ``batch_size``):
            the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
            If the target distribution is a :class:`ProductDistribution`, then
            the optimization problem decouples and
            ``batch_size`` is a list of lists containing the batch sizes to be
            used for each component of the map.
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, and the gradient evaluation ``1`` or
            nothing ``-1``
          mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
            pool of processes to be used, ``None`` stands for one process.
            If the target distribution is a :class:`ProductDistribution`, then
            the minimization problem decouples and ``mpi_pool`` is a list containing
            ``mpi_pool``s for each component of the map.
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)
        """
        self.logger.debug("minimize_kl_divergence_component(): Precomputation started")

        self.mpi_pool = mpi_pool
        if batch_size is None:
            batch_size = [None] * 3
        # Init memory
        (_, paramsf) = mpi_eval("init_mem_precomp_minimize_kl_divergence_component",
                               dmem_key_out_list=['paramsf'],
                               obj=self, mpi_pool=self.mpi_pool,
                               concatenate=False)
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        # precomp_minimize_kl_divergence_component
        scatter_tuple = (['x'],[x])
        bcast_tuple = (['precomp_type'],[precomp_type])
        mpi_eval("precomp_minimize_kl_divergence_component",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=self,
                 mpi_pool=self.mpi_pool, concatenate=False)
        # allocate_cache_minimize_kl_divergence_component
        scatter_tuple = (['x'],[x])
        bcast_tuple = (['cache_level'],[cache_level])
        mpi_eval("allocate_cache_minimize_kl_divergence_component",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=self,
                 mpi_pool=self.mpi_pool, concatenate=False)
        self.logger.debug("minimize_kl_divergence(): Precomputation ended")
        params = {}
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        params['x'] = x
        params['w'] = w
        params['f'] = f
        params['paramsf'] = paramsf
        params['batch_size'] = batch_size
        params['cache_level'] = cache_level
        params['regularization'] = regularization

        if x0 is None:
            x0 = self.get_default_init_values_minimize_kl_divergence_component()

        if cache_level >= 0:
            params['objective_cache_coeffs'] = x0 - 1.
        if cache_level >= 1:
            params['grad_a_objective_cache_coeffs'] = x0 - 1.

        # Callback variables
        self.it_callback = 0
        self.ders_callback = ders
        self.params_callback = params
        self.hess_assembled = False

        # Options for optimizer
        options = {'maxiter': maxit,
                   'disp': False}

        # Solve
        if ders == 0:
            res = sciopt.minimize(self.minimize_kl_divergence_component_objective,
                                  args=params,
                                  x0=x0,
                                  method='BFGS',
                                  tol=tol,
                                  options=options,
                                  callback=self.minimize_kl_divergence_component_callback)
        elif ders == 1:
            if fungrad:
                raise NotImplementedError("Option fungrad not implemented for maps from samples")
                # res = sciopt.minimize(
                #     self.minimize_kl_divergence_component_tuple_grad_a_objective,
                #     args=params,
                #     x0=x0,
                #     jac=True,
                #     method='BFGS',
                #     tol=tol,
                #     options=options,
                #     callback=self.minimize_kl_divergence_component_callback)
            else:
                res = sciopt.minimize(
                    self.minimize_kl_divergence_component_objective,
                    args=params,
                    x0=x0,
                    jac=self.minimize_kl_divergence_component_grad_a_objective,
                    method='BFGS',
                    tol=tol,
                    options=options,
                    callback=self.minimize_kl_divergence_component_callback)
        elif ders == 2:
            res = sciopt.minimize(
                self.minimize_kl_divergence_component_objective, args=params, x0=x0,
                jac=self.minimize_kl_divergence_component_grad_a_objective,
                hess=self.minimize_kl_divergence_component_hess_a_objective,
                method='newton-cg', tol=tol, options=options,
                callback=self.minimize_kl_divergence_component_callback)

        # Clean up callback stuff
        del self.it_callback
        del self.ders_callback
        del self.params_callback
        del self.hess_assembled

        # Log
        log = {}
        log['success'] = res['success']
        log['message'] = res['message']
        log['fval'] = res['fun']
        log['nit'] = res['nit']
        log['n_fun_ev'] = params['nobj']
        if ders >= 1:
            log['n_jac_ev'] = params['nda_obj']
            log['jac'] = res['jac']
        if ders >= 2:
            log['n_hess_ev'] = params['nda2_obj']
        # Display stats
        if log['success']:
            self.logger.info("Optimization terminated successfully")
        else:
            self.logger.info("Optimization failed.")
            self.logger.info("Message: %s" % log['message'])
        self.logger.info("  Function value:          %6f" % log['fval'])
        if ders >= 1:
            self.logger.info("  Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
        self.logger.info("  Number of iterations:    %6d" % log['nit'])
        self.logger.info("  N. function evaluations: %6d" % log['n_fun_ev'])
        if ders >= 1:
            self.logger.info("  N. Jacobian evaluations: %6d" % log['n_jac_ev'])
        if ders >= 2:
            self.logger.info("  N. Hessian evaluations:  %6d" % log['n_hess_ev'])
        
        # Set coefficients
        self.mpi_pool = None
        self.coeffs = res['x']
        return log

        raise NotImplementedError("TO BE FINISHED! (missing params)")

    def init_mem_precomp_minimize_kl_divergence_component(self, params_dens=None):
        r""" Function initializing memory for precomputed values
        """
        out = {'params_pi': params_dens,
               'params_t': {} }
        return (None, out)

    def precomp_minimize_kl_divergence_component(self, x, params, precomp_type='uni'):
        r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence_component`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters to be updated
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
              strucutres. The first argument is needed for consistency with 
        """
        self.precomp_evaluate(x, params['params_t'], precomp_type)
        self.precomp_partial_xd(x, params['params_t'], precomp_type)

    def allocate_cache_minimize_kl_divergence_component(self, x, params, cache_level):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): dictionary of precomputed values
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, and the gradient evaluation ``1``, or
            nothing ``-1``
        """
        precomp = params['params_t']
        tot_size = x.shape[0]
        if cache_level >= 0:
            precomp['cached_evaluate'] = ( np.zeros(tot_size,dtype=bool),
                                           np.empty(tot_size) )
            precomp['cached_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
                                             np.empty(tot_size) )
        if cache_level >= 1:
            precomp['cached_grad_a'] = ( np.zeros(tot_size,dtype=bool),
                                         np.empty((tot_size, self.n_coeffs)) )
            precomp['cached_grad_a_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
                                                    np.empty((tot_size, self.n_coeffs)) )

    def reset_cache_minimize_kl_divergence_component_objective(self, params):
        r""" Reset the objective part of the cache space for the KL-divergence minimization

        Args:
          params2 (dict): dictionary of precomputed values
        """
        precomp = params['params_t']
        batch_set, _ = precomp['cached_evaluate']
        batch_set[:] = False
        try:
            batch_set, _ = precomp['cached_partial_xd']
            batch_set[:] = False
        except KeyError:
            pass

    def reset_cache_minimize_kl_divergence_component_grad_a_objective(self, params):
        r""" Reset the gradient part of the cache space for the KL-divergence minimization

        Args:
          params (dict): dictionary of precomputed values
        """
        precomp = params['params_t']
        try:
            batch_set, _ = precomp['cached_grad_a']
            batch_set[:] = False
            batch_set, _ = precomp['cached_grad_a_partial_xd']
            batch_set[:] = False
        except KeyError:
            pass

    def minimize_kl_divergence_component_callback(self, xk):
        self.it_callback += 1
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("Iteration %d" % self.it_callback)
        if self.ders_callback == 2:
            self.hess_assembled = False

    def minimize_kl_divergence_component_objective(self, a, params):
        r""" Objective function :math:`-\sum_{i=0}^m f(x_i) = -\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i)`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nobj'] += 1
        x = params['x']
        w = params['w']
        f = params['f']
        paramsf = params['paramsf']
        batch_size = params['batch_size']
        self.coeffs = a
        if (params['cache_level'] >= 0 and
            (params['objective_cache_coeffs'] != self.coeffs).any()):
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['paramsf']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [paramsf]
            mpi_eval("reset_cache_minimize_kl_divergence_component_objective",
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=self, mpi_pool=self.mpi_pool,
                        concatenate=False)
        # Evaluate KL-divergence
        scatter_tuple = (['x', 'w'],[x, w])
        bcast_tuple = (['f', 'batch_size'],
                       [f, batch_size[0]])
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = mpi_eval(TM.kl_divergence_component,
                       scatter_tuple=scatter_tuple,
                       bcast_tuple=bcast_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       reduce_obj=reduce_obj,
                       mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] * npla.norm(a,2)**2.
        self.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], out))
        return out
        
    def minimize_kl_divergence_component_grad_a_objective(self, a, params):
        r""" Gradient of the objective function :math:`-\sum_{i=0}^m \nabla_{\bf a} f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla_{\bf a} \left( \log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda_obj'] += 1
        x = params['x']
        w = params['w']
        f = params['f']
        paramsf = params['paramsf']
        batch_size = params['batch_size']
        self.coeffs = a
        if (params['cache_level'] >= 0 and
            (params['objective_cache_coeffs'] != self.coeffs).any()):
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['paramsf']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [paramsf]
            mpi_eval("reset_cache_minimize_kl_divergence_component_objective",
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=self, mpi_pool=self.mpi_pool,
                        concatenate=False)
        if (params['cache_level'] >= 1 and
            (params['objective_cache_coeffs'] != self.coeffs).any()):
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['paramsf']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [paramsf]
            mpi_eval("reset_cache_minimize_kl_divergence_component_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=self, mpi_pool=self.mpi_pool,
                     concatenate=False)
        # Evaluate KL-divergence
        scatter_tuple = (['x', 'w'],[x, w])
        bcast_tuple = (['f', 'batch_size'],
                       [f, batch_size[0]])
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = mpi_eval(TM.grad_a_kl_divergence_component,
                       scatter_tuple=scatter_tuple,
                       bcast_tuple=bcast_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       reduce_obj=reduce_obj,
                       mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] * 2. * a
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Grad_a Obj. Eval. %d - ||grad_a KLdiv|| = %.10e" % (
                params['nda_obj'], npla.norm(out)))
        return out

    def minimize_kl_divergence_component_hess_a_objective(self, a, params):
        r""" Hessian of the objective function :math:`-\sum_{i=0}^m \nabla^2_{\bf a} f[{\bf a}](x_i) = -\sum_{i=0}^m \nabla^2_{\bf a} \left( \log\pi\circ T_k[{\bf a}](x_i) + \log\partial_{x_k}T_k[{\bf a}](x_i)\right)`

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda2_obj'] += 1
        x = params['x']
        w = params['w']
        f = params['f']
        paramsf = params['paramsf']
        batch_size = params['batch_size']
        self.coeffs = a
        if (params['cache_level'] >= 0 and
            (params['objective_cache_coeffs'] != self.coeffs).any()):
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['paramsf']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [paramsf]
            mpi_eval("reset_cache_minimize_kl_divergence_component_objective",
                        dmem_key_in_list=dmem_key_in_list,
                        dmem_arg_in_list=dmem_arg_in_list,
                        dmem_val_in_list=dmem_val_in_list,
                        obj=self, mpi_pool=self.mpi_pool,
                        concatenate=False)
        if (params['cache_level'] >= 1 and
            (params['objective_cache_coeffs'] != self.coeffs).any()):
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['paramsf']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [paramsf]
            mpi_eval("reset_cache_minimize_kl_divergence_component_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=self, mpi_pool=self.mpi_pool,
                     concatenate=False)
        # Evaluate KL-divergence
        scatter_tuple = (['x', 'w'],[x, w])
        bcast_tuple = (['f', 'batch_size'],
                       [f, batch_size[0]])
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        reduce_obj = TM.SumChunkReduce(axis=0)
        out = mpi_eval(TM.hess_a_kl_divergence_component,
                       scatter_tuple=scatter_tuple,
                       bcast_tuple=bcast_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       reduce_obj=reduce_obj,
                       mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += np.diag( np.ones(self.n_coeffs)*2.*params['regularization']['alpha'] )
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Hess_a Obj. Eval. %d " % params['nda2_obj'])
        return out
        
class MonotonicLinearSpanApproximation(LinearSpanApproximation,
                                       MonotonicFunctionApproximation):
    r""" Approximation of the type :math:`f \approx f_{\bf a} = \sum_{{\bf i} \in \mathcal{I}} {\bf a}_{\bf i} \Phi_{\bf i}`, monotonic in :math:`x_d`

    Args:
      basis_list (list): list of :math:`d`
        :class:`OrthogonalBasis<SpectralToolbox.OrthogonalBasis>`
      spantype (str): Span type. 'total' total order, 'full' full order,
        'midx' multi-indeces specified
      order_list (:class:`list<list>` of :class:`int<int>`): list of 
        orders :math:`\{N_i\}_{i=0}^d`
      multi_idxs (list): list of tuples containing the active multi-indices
    """
    def precomp_regression(self, x, precomp=None, *args, **kwargs):
        r""" Precompute necessary structures for the speed up of :func:`regression`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary to be updated

        Returns:
           (:class:`dict<dict>`) -- dictionary of necessary strucutres
        """
        if precomp is None:
            precomp = {}
        precomp.update( self.precomp_evaluate(x) )
        precomp.update( self.precomp_partial_xd(x) )
        return precomp

    def get_identity_coeffs(self):
        coeffs = np.zeros(self.n_coeffs)
        idx = np.where(self.get_multi_idxs() == tuple([0]*(self.dim-1) + [1]))[0]
        coeffs[idx] = 1.
        return coeffs

    def regression(self, f, fparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None,
                   regularization=None, tol=1e-4, maxit=100,
                   batch_size=(None,None), mpi_pool=None, import_set=set()):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

        Args:
          f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`f` or its functions values
          d (Distribution): distribution :math:`\pi`
          fparams (dict): parameters for function :math:`f`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size (:class:`list<list>` [2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)

        Returns:
          (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
          :class:`list<list>`)) -- containing the :math:`N` coefficients and
          log information from the optimizer.

        .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`coeffs` in order
           to retrieve them.
        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        self.mpi_pool = mpi_pool        
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
        params = {}
        params['x'] = x
        params['w'] = w
        params['regularization'] = regularization
        params['batch_size'] = batch_size
        cons = ({'type': 'ineq',
                 'fun': self.regression_constraints,
                 'jac': self.regression_grad_a_constraints,
                 'args': (params,)})
        options = {'maxiter': maxit,
                   'disp': False}
        if x0 is None:
            x0 = self.get_default_init_values_regression()
        params['nobj'] = 0
        params['nda_obj'] = 0
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation started")
        # Prepare parameters
        if isinstance(f, np.ndarray):
            params['fvals'] = f
        else:
            scatter_tuple = (['x'], [x])
            bcast_tuple = (['precomp'], [fparams])
            params['fvals'] = mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                                       bcast_tuple=bcast_tuple,
                                       obj=f, mpi_pool=self.mpi_pool)
        # Init precomputation memory
        (_, params['params1']) = mpi_eval("init_mem_precomp_regression",
                                          dmem_key_out_list=['params1'],
                                          obj=self, mpi_pool=self.mpi_pool,
                                          concatenate=False)
        # Precompute
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_regression", scatter_tuple=scatter_tuple,
                 dmem_key_in_list=['params1'],
                 dmem_arg_in_list=['precomp'],
                 dmem_val_in_list=[params['params1']],
                 obj=self, mpi_pool=self.mpi_pool,
                 concatenate=False)
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation ended")
        # Minimize
        res = sciopt.minimize(self.regression_objective, x0, args=params, \
                              jac=self.regression_grad_a_objective,
                              constraints=cons, \
                              method='SLSQP', options=options, tol=tol)
        if not res['success']:
            self.logger.warn("Regression failure: " + res['message'])
        coeffs = res['x']
        self.coeffs = coeffs
        self.mpi_pool = None
        return (coeffs, res)
        
    def regression_constraints(self, a, params):
        self.coeffs = a
        x = params['x']
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list=['precomp']
        dmem_val_in_list = [params['params1']]
        out = mpi_eval("partial_xd", scatter_tuple=scatter_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=self, mpi_pool=self.mpi_pool)
        return out

    def regression_grad_a_constraints(self, a, params):
        self.coeffs = a
        x = params['x']
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params1']
        dmem_arg_in_list=['precomp']
        dmem_val_in_list = [params['params1']]
        out = mpi_eval("grad_a_partial_xd", scatter_tuple=scatter_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=self, mpi_pool=self.mpi_pool)
        return out

    def minimize_kl_divergence_component(self,
                                         f, x, w,
                                         x0=None,
                                         regularization=None,
                                         tol=1e-4, maxit=100, ders=2,
                                         fungrad=False, 
                                         precomp_type='uni',
                                         batch_size=None,
                                         cache_level=1,
                                         mpi_pool=None,
                                         import_set=set()):
        r""" Compute :math:`{\bf a}^\star = \arg\min_{\bf a}-\sum_{i=0}^m \log\pi\circ T_k(x_i) + \log\partial_{x_k}T_k(x_i) = \arg\min_{\bf a}-\sum_{i=0}^m f(x_i)`

        Args:
          f (ProductDistributionParametricPullbackComponentFunction): function :math:`f` 
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
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
          fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>` or :class:`list<list>` of ``batch_size``):
            the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
            If the target distribution is a :class:`ProductDistribution`, then
            the optimization problem decouples and
            ``batch_size`` is a list of lists containing the batch sizes to be
            used for each component of the map.
          cache_level (int): use high-level caching during the optimization, storing the
            function evaluation ``0``, and the gradient evaluation ``1`` or
            nothing ``-1``
          mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
            pool of processes to be used, ``None`` stands for one process.
            If the target distribution is a :class:`ProductDistribution`, then
            the minimization problem decouples and ``mpi_pool`` is a list containing
            ``mpi_pool``s for each component of the map.
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)
        """
        self.logger.debug("minimize_kl_divergence_component(): Precomputation started")

        self.mpi_pool = mpi_pool
        if batch_size is None:
            batch_size = [None] * 3
        # Init memory
        (_, paramsf) = mpi_eval("init_mem_precomp_minimize_kl_divergence_component",
                               dmem_key_out_list=['paramsf'],
                               obj=self, mpi_pool=self.mpi_pool,
                               concatenate=False)
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        # precomp_minimize_kl_divergence_component
        scatter_tuple = (['x'],[x])
        bcast_tuple = (['precomp_type'],[precomp_type])
        mpi_eval("precomp_minimize_kl_divergence_component",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=self,
                 mpi_pool=self.mpi_pool, concatenate=False)
        # allocate_cache_minimize_kl_divergence_component
        scatter_tuple = (['x'],[x])
        bcast_tuple = (['cache_level'],[cache_level])
        mpi_eval("allocate_cache_minimize_kl_divergence_component",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=self,
                 mpi_pool=self.mpi_pool, concatenate=False)
        self.logger.debug("minimize_kl_divergence(): Precomputation ended")

        params = {}
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['x'] = x
        params['w'] = w
        params['f'] = f
        params['paramsf'] = paramsf
        params['batch_size'] = batch_size
        params['cache_level'] = cache_level
        params['regularization'] = regularization

        if x0 is None:
            x0 = self.get_default_init_values_minimize_kl_divergence_component()

        # Link params_t on the first level of params
        # (this is needed for the MPI implementation of the constraints)
        dmem_key_in_list = ['paramsf']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [paramsf]
        dmem_key_out_list = ['params_t']
        (_, params['params_t']) = mpi_eval("link_mem_precomp_minimize_kl_divergence_component",
                                           dmem_key_in_list=dmem_key_in_list,
                                           dmem_arg_in_list=dmem_arg_in_list,
                                           dmem_val_in_list=dmem_val_in_list,
                                           dmem_key_out_list=dmem_key_out_list,
                                           obj=self, mpi_pool=self.mpi_pool,
                                           concatenate=False)

        cons = ({'type': 'ineq',
                 'fun': self.minimize_kl_divergence_component_constraints,
                 'jac': self.minimize_kl_divergence_component_da_constraints,
                 'args': (params,)})

        if cache_level >= 0:
            params['objective_cache_coeffs'] = x0 - 1.

        # Callback variables
        self.it_callback = 0
        self.ders_callback = ders
        self.params_callback = params

        # Options for optimizer
        options = {'maxiter': maxit,
                   'disp': False}

        # Solve
        if ders == 0:
            res = sciopt.minimize(self.minimize_kl_divergence_component_objective,
                                  args=params,
                                  x0=x0,
                                  constraints=cons,
                                  method='SLSQP',
                                  tol=tol, 
                                  options=options,
                                  callback=self.minimize_kl_divergence_component_callback)
        elif ders == 1:
            if fungrad:
                raise NotImplementedError("Option fungrad not implemented for maps from samples")
                # res = sciopt.minimize(self.minimize_kl_divergence_tuple_grad_a_objective,
                #                       args=params, x0=x0,
                #                       jac=True,
                #                       constraints=cons,
                #                       method='SLSQP',
                #                       tol=tol, 
                #                       options=options,
                #                       callback=self.minimize_kl_divergence_callback)
            else:
                res = sciopt.minimize(self.minimize_kl_divergence_component_objective, args=params,
                                      x0=x0,
                                      jac=self.minimize_kl_divergence_component_grad_a_objective,
                                      constraints=cons,
                                      method='SLSQP',
                                      tol=tol, 
                                      options=options,
                                      callback=self.minimize_kl_divergence_component_callback)

        # Clean up callback stuff
        del self.it_callback
        del self.ders_callback
        del self.params_callback

        # Log
        log = {}
        log['success'] = res['success']
        log['message'] = res['message']
        log['fval'] = res['fun']
        log['nit'] = res['nit']
        log['n_fun_ev'] = params['nobj']
        if ders >= 1:
            log['n_jac_ev'] = params['nda_obj']
            log['jac'] = res['jac']
        # Display stats
        if log['success']:
            self.logger.info("Optimization terminated successfully")
        else:
            self.logger.info("Optimization failed.")
            self.logger.info("Message: %s" % log['message'])
        self.logger.info("  Function value:          %6f" % log['fval'])
        if ders >= 1:
            self.logger.info("  Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
        self.logger.info("  Number of iterations:    %6d" % log['nit'])
        self.logger.info("  N. function evaluations: %6d" % log['n_fun_ev'])
        if ders >= 1:
            self.logger.info("  N. Jacobian evaluations: %6d" % log['n_jac_ev'])

        # Set coefficients
        self.mpi_pool = None
        self.coeffs = res['x']
        return log

    def link_mem_precomp_minimize_kl_divergence_component(self, params):
        return (None, params['params_t'])

    def minimize_kl_divergence_component_constraints(self, a, params):
        self.coeffs = a
        x = params['x']
        # MPI call
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params_t']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [ params['params_t'] ]
        out = mpi_eval("partial_xd", scatter_tuple=scatter_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=self, mpi_pool=self.mpi_pool)
        return out

    def minimize_kl_divergence_component_da_constraints(self, a, params):
        self.coeffs = a
        x = params['x']
        # MPI call
        scatter_tuple = (['x'], [x])
        dmem_key_in_list = ['params_t']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [ params['params_t'] ]
        out = mpi_eval("grad_a_partial_xd", scatter_tuple=scatter_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=self, mpi_pool=self.mpi_pool)
        return out.reshape( x.shape[0], self.n_coeffs )

    # def init_mem_precomp_minimize_kl_divergence_component(self, params_dens=None):
    #     r""" Function initializing memory for precomputed values
    #     """
    #     out = {'params_pi': params_dens,
    #            'params_t': {} }
    #     return (None, out)

    # def precomp_minimize_kl_divergence_component(self, x, params, precomp_type='uni'):
    #     r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence_component`

    #     Args:
    #       x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #       params (dict): parameters to be updated
    #       precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
    #         multivariate Vandermonde matrices 'multi'

    #     Returns:
    #        (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
    #           strucutres. The first argument is needed for consistency with 
    #     """
    #     self.precomp_evaluate(x, params['params_t'], precomp_type)
    #     self.precomp_partial_xd(x, params['params_t'], precomp_type)

    # def allocate_cache_minimize_kl_divergence_component(self, x, params, cache_level):
    #     r""" Allocate cache space for the KL-divergence minimization

    #     Args:
    #       x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
    #       params (dict): dictionary of precomputed values
    #       cache_level (int): use high-level caching during the optimization, storing the
    #         function evaluation ``0``, and the gradient evaluation ``1``, or
    #         nothing ``-1``
    #     """
    #     precomp = params['params_t']
    #     tot_size = x.shape[0]
    #     if cache_level >= 0:
    #         precomp['cached_evaluate'] = ( np.zeros(tot_size,dtype=bool),
    #                                        np.empty((tot_size, self.dim)) )
    #         precomp['cached_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
    #                                          np.empty(tot_size) )
    #     if cache_level >= 1:
    #         precomp['cached_grad_a'] = ( np.zeros(tot_size,dtype=bool),
    #                                      np.empty((tot_size, self.n_coeffs)) )
    #         precomp['cached_grad_a_partial_xd'] = ( np.zeros(tot_size,dtype=bool),
    #                                                 np.empty((tot_size, self.n_coeffs)) )

    # def reset_cache_minimize_kl_divergence_component_objective(self, params):
    #     r""" Reset the objective part of the cache space for the KL-divergence minimization

    #     Args:
    #       params2 (dict): dictionary of precomputed values
    #     """
    #     precomp = params['params_t']
    #     batch_set, _ = precomp['cached_evaluate']
    #     batch_set[:] = False
    #     try:
    #         batch_set, _ = precomp['cached_partial_xd']
    #         batch_set[:] = False
    #     except KeyError:
    #         pass

    @staticmethod
    def from_xml_element(node, dim):
        import TransportMaps.Functionals as FUNC
        from TransportMaps import XML_NAMESPACE
        # Check span type
        multidimtype = node.attrib['multidimtype'] 
        if multidimtype == 'tensorized':
            stype = node.attrib['spantype']
            if stype == 'total' or stype == 'full':
                span_node = node.find(XML_NAMESPACE + 'spanorder')
                # Retrieve the list of orders
                order_list = LinearSpanApproximation.order_list_from_xml_element(
                    span_node, dim)
                # Retrieve the list of basis
                basis_list = LinearSpanApproximation.basis_list_from_xml_element(
                    node, dim)
                return MonotonicLinearSpanApproximation(
                    basis_list, spantype=stype, order_list=order_list)
            elif stype == 'midx':
                midxlist_node = node.find(XML_NAMESPACE + 'midxlist')
                # Retrieve the list of multi-indices
                midx_list = LinearSpanApproximation.midx_list_from_xml_element(
                    midxlist_node, dim)
                # Retrieve the list of basis
                basis_list = LinearSpanApproximation.basis_list_from_xml_element(
                    node, dim)
                return MonotonicLinearSpanApproximation(
                    basis_list, spantype=stype, multi_idxs=midx_list)
            raise ValueError("No recognizable spantype provided (%s)" % stype)
        raise ValueError("No recognizable multidimtype provided (%s)" % multidimtype)
    
class MonotonicIntegratedExponentialApproximation(MonotonicFunctionApproximation):
    r""" Integrated Exponential approximation.

    For :math:`{\bf x} \in \mathbb{R}^d` The approximation takes the form:

    .. math::
       :label: integ-exp
       
       f_{\bf a}({\bf x}) = c({\bf x};{\bf a}^c) + \int_0^{{\bf x}_d} \exp\left( h({\bf x}_{1:d-1},t;{\bf a}^e) \right) dt

    where

    .. math::
    
       c({\bf x};{\bf a}^c) = \Phi({\bf x}) {\bf a}^c = \sum_{{\bf i}\in \mathcal{I}_c} \Phi_{\bf i}({\bf x}) {\bf a}^c_{\bf i} \qquad \text{and} \qquad h({\bf x}_{1:d-1},t;{\bf a}^e) = \Psi({\bf x}_{1:d-1},t) {\bf a}^e = \sum_{{\bf i}\in \mathcal{I}_e} \Psi_{\bf i}({\bf x}_{1:d-1},t) {\bf a}^e_{\bf i}

    for the set of basis :math:`\Phi` and :math:`\Psi` with cardinality :math:`\sharp \mathcal{I}_c = N_c` and :math:`\sharp \mathcal{I}_e = N_e`. In the following :math:`N=N_c+N_e`.

    Args:
       c (:class:`LinearSpanApproximation`): :math:`d-1` dimensional
         approximation of :math:`c({\bf x}_{1:d-1};{\bf a}^c)`.
       h (:class:`LinearSpanApproximation`): :math:`d` dimensional
         approximation of :math:`h({\bf x}_{1:d-1},t;{\bf a}^e)`.
       integ_ord_mult (int): multiplier for the number of Gauss points to be used
         in the approximation of :math:`\int_0^{{\bf x}_d}`. The resulting number of
         points is given by the product of the order in the :math:`d` direction
         and ``integ_ord_mult``.
    """

    def __init__(self, c, h, integ_ord_mult=6):
        if c.dim != h.dim:
            raise ValueError("The dimension of the constant part and the " +
                             "exponential part of the approximation must be " +
                             "the same.")
        if c.get_directional_orders()[-1] != 0:
            raise ValueError("The order along the last direction of the constant " +
                             "part of the approximation must be zero")
        self.c = c
        self.h = h
        super(MonotonicIntegratedExponentialApproximation, self).__init__(h.dim)
        self.P_JAC = S1D.JacobiPolynomial(0.,0.)
        self.integ_ord_mult = integ_ord_mult

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self.c.init_coeffs()
        self.h.init_coeffs()

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        return self.c.n_coeffs + self.h.n_coeffs

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        return np.hstack( (self.c.coeffs, self.h.coeffs) )

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        if len(coeffs) != self.n_coeffs:
            raise ValueError("Wrong number of coefficients provided.")
        nc = self.c.n_coeffs
        self.c.coeffs = coeffs[:nc]
        self.h.coeffs = coeffs[nc:]

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_evaluate(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_evaluate(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        try: precomp_intexp = precomp['intexp']
        except KeyError as e: precomp['intexp'] = {}
        try:
            xjsc_list = precomp['intexp']['xjsc_list']
            wjsc_list = precomp['intexp']['wjsc_list']
        except KeyError as e:
            precomp['intexp']['xjsc_list'] = []
            precomp['intexp']['wjsc_list'] = []
            xd_order = (self.h.get_directional_orders())[-1]
            (xj,wj) = self.P_JAC.Quadrature( self.integ_ord_mult * xd_order, norm=True )
            xj = xj / 2. + 0.5  # Mapped to [0,1]
            for idx in range(x.shape[0]):
                wjsc = wj * x[idx,-1]
                xjsc = xj * x[idx,-1]
                xother = np.tile( x[idx,:-1], (len(xjsc), 1) )
                xeval = np.hstack( (xother, xjsc[:,nax]) )
                # Append values
                precomp['intexp']['xjsc_list'].append( xeval )
                precomp['intexp']['wjsc_list'].append( wjsc )
        try: precomp_intexp_list = precomp['intexp']['prec_list']
        except KeyError as e:
            precomp['intexp']['prec_list'] = [{} for i in range(x.shape[0])]
        for idx, (xeval, p) in enumerate(zip(precomp['intexp']['xjsc_list'],
                                             precomp['intexp']['prec_list'])):
            if precomp_type == 'uni':
                self.h.precomp_evaluate(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_evaluate(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_evaluate(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_evaluate(x, precomp, precomp_type='multi')

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        out = self.c.evaluate(x, prec_const, idxs_slice)
        for i, idx in enumerate(idxs_list):# other_idxs:
            h_eval = self.h.evaluate(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            exp = np.exp( h_eval )
            out[i] += np.dot( exp, prec_intexp_wjsc_list[idx] )
        return out

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_evaluate part
        self.precomp_evaluate(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        for xeval, p in zip(precomp['intexp']['xjsc_list'],
                            precomp['intexp']['prec_list']):
            if precomp_type == 'uni':
                self.h.precomp_grad_x(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_grad_x(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        # precomp_partial_xd part
        self.precomp_partial_xd(x, precomp, precomp_type)
        return precomp

    def precomp_Vandermonde_grad_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_grad_x(x, precomp, precomp_type='multi')

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

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
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        # Evaluation
        out = self.c.grad_x(x, prec_const)
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )
            grad_x_exp = self.h.grad_x( prec_intexp_xjsc_list[idx],
                                        precomp=prec_intexp_prec_list[idx] ) \
                         * exp[:,nax]
            out[idx,:] += np.dot( prec_intexp_wjsc_list[idx], grad_x_exp )
        out[:,-1] = self.partial_xd(x, precomp)
        return out

    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        # Evaluation
        out = np.zeros((x.shape[0], self.n_coeffs, x.shape[1]))
        N_cc = self.c.n_coeffs
        out[:,:N_cc,:] = self.c.grad_a_grad_x(x, prec_const)
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )
            grad_x_h = self.h.grad_x( prec_intexp_xjsc_list[idx],
                                        precomp=prec_intexp_prec_list[idx] )
            grad_a_h = self.h.grad_a( prec_intexp_xjsc_list[idx],
                                        precomp=prec_intexp_prec_list[idx] )
            grad_a_grad_x_h = self.h.grad_a_grad_x( prec_intexp_xjsc_list[idx],
                                        precomp=prec_intexp_prec_list[idx] )
            grad_a_grad_x_exp = grad_a_grad_x_h * exp[:,nax,nax] + grad_x_h[:,nax,:] * grad_a_h[:,:,nax] * exp[:,nax,nax]
            out[idx,N_cc:,:] += np.einsum('i,ijk->jk', prec_intexp_wjsc_list[idx], grad_a_grad_x_exp )
        out[:,:,-1] = self.grad_a_partial_xd(x, precomp)
        return out

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x part (and precomp_evaluate)
        self.precomp_grad_x(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        for xeval, p in zip(precomp['intexp']['xjsc_list'],
                            precomp['intexp']['prec_list']):
            if precomp_type == 'uni':
                self.h.precomp_hess_x(xeval, p)
            elif precomp_type == 'multi':
                self.h.precomp_Vandermonde_hess_x(xeval, p)
            else: raise ValueError("Unrecognized precomp_type")
        # precomp_grad_x_partial_xd part
        self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        return precomp

    def precomp_Vandermonde_hess_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_hess_x(x, precomp, precomp_type='multi')
        
    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        try: # precomp_hess_x structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial2_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_hess_x(x, precomp)
        # Evaluation
        out = self.c.hess_x(x, prec_const)
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )
            hess_x_h = self.h.hess_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            grad_x_h = self.h.grad_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            integrand = (hess_x_h + grad_x_h[:,:,nax] * grad_x_h[:,nax,:]) * exp[:,nax,nax]
            out[idx,:,:] += np.einsum( 'i,ijk->jk', prec_intexp_wjsc_list[idx], integrand )
        out[:,-1,:] = self.grad_x_partial_xd(x, precomp) 
        out[:,:,-1] = out[:,-1,:]
        return out
        
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d,d`]) --
            :math:`\nabla_{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        try: # precomp_grad_x structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_grad_x(x, precomp)
        try: # precomp_hess_x structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            for p in prec_intexp_prec_list:
                if 'partial2_x_V_list' not in p: raise KeyError()
        except KeyError as e:
            precomp = self.precomp_hess_x(x, precomp)
        # Evaluation
        out = np.zeros((x.shape[0], self.n_coeffs, x.shape[1], x.shape[1]))
        N_cc = self.c.n_coeffs
        out[:,:N_cc,:,:] = self.c.grad_a_hess_x(x, prec_const)
        for idx in range(x.shape[0]):
            exp = np.exp( self.h.evaluate( prec_intexp_xjsc_list[idx],
                                           precomp=prec_intexp_prec_list[idx] ) )
            hess_x_h = self.h.hess_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            grad_x_h = self.h.grad_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            grad_a_hess_x_h = self.h.grad_a_hess_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            grad_a_h = self.h.grad_a(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            grad_a_grad_x_h = self.h.grad_a_grad_x(prec_intexp_xjsc_list[idx],
                                     precomp=prec_intexp_prec_list[idx])
            integrand = (grad_a_hess_x_h + hess_x_h[:,nax,:,:] * grad_a_h[:,:,nax,nax] 
                    + grad_a_grad_x_h[:,:,:,nax] * grad_x_h[:,nax,nax,:]
                    + grad_x_h[:,nax,:,nax] * grad_a_grad_x_h[:,:,nax,:] 
                    + grad_x_h[:,nax,:,nax] * grad_x_h[:,nax,nax,:] * grad_a_h[:,:,nax,nax]) * exp[:,nax,nax,nax]
            out[idx,N_cc:,:,:] += np.einsum( 'i,ijkl->jkl', prec_intexp_wjsc_list[idx], integrand )
        out[:,:,-1,:] = self.grad_a_grad_x_partial_xd(x, precomp) 
        out[:,:,:,-1] = out[:,:,-1,:]
        return out
        
    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

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
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs))
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        # Constant part
        out[:,:ncc] = self.c.grad_a(x, prec_const, idxs_slice)
        # Integrated exponential part
        for i, idx in enumerate(idxs_list):
            xjsc = prec_intexp_xjsc_list[idx]
            wjsc = prec_intexp_wjsc_list[idx]
            precomp_exp = prec_intexp_prec_list[idx]
            exp = np.exp( self.h.evaluate(xjsc, precomp_exp) )
            VIexp = self.h.grad_a(xjsc, precomp_exp) * exp[:,nax]
            out[i,ncc:] = np.dot( wjsc, VIexp )
        return out

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

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
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intexp = precomp['intexp']
            prec_intexp_xjsc_list = prec_intexp['xjsc_list']
            prec_intexp_wjsc_list = prec_intexp['wjsc_list']
            prec_intexp_prec_list = prec_intexp['prec_list']
            for p in prec_intexp_prec_list:
                if 'V_list' not in p: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intexp = precomp['intexp']
        prec_intexp_xjsc_list = prec_intexp['xjsc_list']
        prec_intexp_wjsc_list = prec_intexp['wjsc_list']
        prec_intexp_prec_list = prec_intexp['prec_list']
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        nce = nc - ncc
        out = np.zeros((x.shape[0],nc,nc))
        # Convert slice to range
        if idxs_slice.start is None: start = 0
        else: start = idxs_slice.start
        if idxs_slice.stop is None: stop = x.shape[0]
        else: stop = idxs_slice.stop
        idxs_list = range(start, stop)
        # Evaluate
        # Constant part
        if not isinstance(self.c, LinearSpanApproximation):
            out[:,:ncc,:ncc] = self.c.hess_a(x, prec_const, idxs_slice)
        # Integrated exponential part
        for i, idx in enumerate(idxs_list):
            xjsc = prec_intexp_xjsc_list[idx]
            wjsc = prec_intexp_wjsc_list[idx]
            precomp_exp = prec_intexp_prec_list[idx]
            exp = np.exp( self.h.evaluate( xjsc, precomp_exp ) )
            if isinstance(self.h, LinearSpanApproximation):
                grad_a_h_t = self.h.grad_a_t( xjsc, precomp_exp )
                exp *= wjsc
                sqrt_exp_abs = np.sqrt(np.abs(exp))
                exp_sign = np.sign(exp)
                grad_a_h_t_1 = grad_a_h_t * sqrt_exp_abs[nax,:]
                grad_a_h_t_2 = grad_a_h_t * (exp_sign*sqrt_exp_abs)[nax,:]
                np.einsum('ik,jk->ij', grad_a_h_t_1, grad_a_h_t_2,
                          out=out[i,ncc:,ncc:], casting='unsafe')
            else:
                hess_a_h = self.h.hess_a( xjsc, precomp_exp ) # Always zero if h LinSpanApprox
                grad_a_h = self.h.grad_a( xjsc, precomp_exp )
                hess_exp = (hess_a_h + grad_a_h[:,:,nax] * grad_a_h[:,nax,:]) * exp[:,nax,nax]
                np.einsum('i...,i', hess_exp, wjsc, out=out[i,ncc:,ncc:])
        return out

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated exponential part
        try: precomp_exp = precomp['exp']
        except KeyError as e: precomp['exp'] = {}
        if precomp_type == 'uni':
            self.h.precomp_evaluate(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_evaluate(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial_xd(x, precomp, precomp_type='multi')

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        # Evaluation
        out = self.c.partial_xd(x, prec_const, idxs_slice) + \
              np.exp( self.h.evaluate(x, prec_exp, idxs_slice) )
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_partial_xd
        self.precomp_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        if precomp_type == 'uni':
            self.h.precomp_grad_x(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_grad_x(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_grad_x_partial_xd(x, precomp, precomp_type='multi')

    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        # Evaluation
        exp = np.exp( self.h.evaluate(x, precomp=prec_exp) )
        out = self.c.grad_x_partial_xd(x, precomp=prec_const) + \
              self.h.grad_x(x, precomp=prec_exp) * exp[:,nax]
        return out

    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla_{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        # Evaluation 
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0],nc,x.shape[1]))
        
        exp = np.exp( self.h.evaluate(x, precomp=prec_exp) )
        grad_x = self.h.grad_x(x, precomp=prec_exp)  
        grad_a = self.h.grad_a(x, precomp=prec_exp) 
        out[:,:ncc,:] = self.c.grad_a_grad_x_partial_xd(x, precomp=prec_const) 
        out[:,ncc:,:] = self.h.grad_a_grad_x(x, precomp=prec_exp) * exp[:,nax,nax] + \
              grad_x[:,nax,:] * grad_a[:,:,nax] * exp[:,nax,nax]
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x_partial_xd (and precomp_partial_xd)
        self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        if precomp_type == 'uni':
            self.h.precomp_hess_x(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_hess_x(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_hess_x_partial_xd(x, precomp, precomp_type='multi')

    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        try: # precomp_hess_x_partial_xd structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            if 'partial3_xd_V_last' not in prec_const: raise KeyError()
            if 'partial2_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_hess_x_partial_xd(x, precomp)
        # Evaluation
        exp = np.exp( self.h.evaluate(x, prec_exp) )
        hx = self.h.hess_x(x, prec_exp)
        gx = self.h.grad_x(x, prec_exp)
        out = self.c.hess_x_partial_xd(x, prec_const) + \
              (hx + gx[:,:,nax] * gx[:,nax,:]) * exp[:,nax,nax]
        return out

    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla_{\bf a}\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        try: # precomp_grad_x_partial_xd structures
            if 'partial_x_V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            if 'partial_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        try: # precomp_hess_x_partial_xd structures
            if 'partial2_x_V_list' not in prec_const: raise KeyError()
            if 'partial3_xd_V_last' not in prec_const: raise KeyError()
            if 'partial2_x_V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            precomp = self.precomp_hess_x_partial_xd(x, precomp)
        # Evaluation
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0],nc,x.shape[1],x.shape[1]))

        exp  = np.exp( self.h.evaluate(x, prec_exp) )
        hx   = self.h.grad_x(x, prec_exp)
        hxx  = self.h.hess_x(x, prec_exp)
        ha   = self.h.grad_a(x, prec_exp)
        haxx = self.h.grad_a_hess_x(x, prec_exp)
        hax  = self.h.grad_a_grad_x(x, prec_exp)

        out[:,:ncc,:,:] = self.c.grad_a_hess_x_partial_xd(x, precomp=prec_const) 
        out[:,ncc:,:,:] = ha[:,:,nax,nax] * hxx[:,nax,:,:] * exp[:,nax,nax,nax] + \
                haxx * exp[:,nax,nax,nax] + ha[:,:,nax,nax] * hx[:,nax,:,nax] * hx[:,nax,nax,:] *exp[:,nax,nax,nax] + \
                hax[:,:,:,nax] * hx[:,nax,nax,:] * exp[:,nax,nax,nax] + hx[:,nax,:,nax] * hax[:,:,nax,:] * exp[:,nax,nax,nax]
        return out

    def precomp_partial2_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial2_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial2_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Exponential part
        try: exp = precomp['exp']
        except KeyError as e: precomp['exp'] = {}
        if precomp_type == 'uni':
            self.h.precomp_partial_xd(x, precomp['exp'])
        elif precomp_type == 'multi':
            self.h.precomp_Vandermonde_partial_xd(x, precomp['exp'])
        else: raise ValueError("Unrecognized precomp_type")
        return precomp

    def precomp_Vandermonde_partial2_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial2_xd(x, precomp, precomp_type='multi')

    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial2_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial2_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
            if 'partial_xd_V_last' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial2_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Evaluation
        exp = np.exp( self.h.evaluate(x, prec_exp) )
        out = self.c.partial2_xd(x, prec_const) + \
              self.h.partial_xd(x, prec_exp) * exp
        return out

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs))
        out[:,:ncc] = self.c.grad_a_partial_xd(x, prec_const, idxs_slice)
        exp = np.exp( self.h.evaluate(x, prec_exp, idxs_slice) )
        out[:,ncc:] = self.h.grad_a(x, prec_exp, idxs_slice) * exp[:,nax]
        return out

    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            if 'partial_xd_V_last' not in prec_const: raise KeyError()
            prec_exp = precomp['exp']
            if 'V_list' not in prec_exp: raise KeyError()
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_exp = precomp['exp']
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        nc = self.n_coeffs
        out = np.zeros((x.shape[0], nc, nc))
        if not isinstance(self.c, LinearSpanApproximation):
            out[:,:ncc,:ncc] = self.c.hess_a_partial_xd(x, prec_const, idxs_slice)
        exp = np.exp( self.h.evaluate(x, prec_exp, idxs_slice) )
        grad_a_h = self.h.grad_a(x, prec_exp, idxs_slice)
        if isinstance(self.h, LinearSpanApproximation):
            sqrt_exp = np.sqrt(exp)
            grad_a_h_sq_exp = grad_a_h * sqrt_exp[:,nax]
            np.einsum('ki,kj->kij', grad_a_h_sq_exp, grad_a_h_sq_exp,
                      out=out[:,ncc:,ncc:], casting='unsafe')
        else:
            hess_a_h = self.h.hess_a(x, prec_exp, idxs_slice)
            out[:,ncc:,ncc:] = (hess_a_h + grad_a_h[:,:,nax] * grad_a_h[:,nax,:]) * exp[:,nax,nax]
        return out

    def get_identity_coeffs(self):
        return np.zeros(self.n_coeffs)

    def precomp_regression(self, x, precomp=None, *args, **kwargs):
        r""" Precompute necessary structures for the speed up of :func:`regression`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary to be updated

        Returns:
           (:class:`dict<dict>`) -- dictionary of necessary strucutres
        """
        if precomp is None:
            precomp = {}
        precomp.update( self.precomp_evaluate(x) )
        return precomp

    def regression(self, f, fparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None,
                   regularization=None, tol=1e-4, maxit=100,
                   batch_size=(None,None,None), mpi_pool=None, import_set=set()):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

        Args:
          f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`f` or its functions values
          fparams (dict): parameters for function :math:`f`
          d (Distribution): distribution :math:`\pi`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size (:class:`list<list>` [3] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)

        Returns:
          (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
          :class:`list<list>`)) -- containing the :math:`N` coefficients and
          log information from the optimizer.

        .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`coeffs` in order
           to retrieve them.
        
        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
           exclusive, but one pair of them is necessary.
        """
        self.mpi_pool = mpi_pool
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
            
        params = {}
        params['x'] = x
        params['w'] = w
        params['regularization'] = regularization
        params['batch_size'] = batch_size
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        options = {'maxiter': maxit,
                   'disp': False}
        if x0 is None:
            x0 = np.zeros( np.sum(self.n_coeffs) )
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation started")
        if isinstance(f, np.ndarray):
            params['fvals'] = f
        else:
            scatter_tuple = (['x'], [x])
            bcast_tuple = (['precomp'], [fparams])
            params['fvals'] = mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                                       bcast_tuple=bcast_tuple,
                                       obj=f, mpi_pool=self.mpi_pool)
        # Init precomputation memory
        (_, params['params1']) = mpi_eval("init_mem_precomp_regression",
                                          dmem_key_out_list=['params1'],
                                          obj=self, mpi_pool=self.mpi_pool,
                                          concatenate=False)
        # Precompute
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_regression", scatter_tuple=scatter_tuple,
                 dmem_key_in_list=['params1'],
                 dmem_arg_in_list=['precomp'],
                 dmem_val_in_list=[params['params1']],
                 obj=self, mpi_pool=self.mpi_pool, concatenate=False)

        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation ended")

        # Callback variables
        self.params1_callback = params['params1']
        self.hess_assembled = False

        # Minimize
        res = sciopt.minimize(
            self.regression_objective, args=params, x0=x0,
            jac=self.regression_grad_a_objective,
            hessp=self.regression_action_storage_hess_a_objective,
            method='Newton-CG', tol=tol, options=options,
            callback=self.regression_callback)
        if not res['success']:
            self.logger.warn("Regression failure: " + res['message'])

        # Clean up callback stuff
        del self.params1_callback
        del self.hess_assembled
        
        coeffs = res['x']
        self.coeffs = coeffs
        self.mpi_pool = None
        return (coeffs, res)

    def regression_callback(self, xk):
        self.hess_assembled = False

    @staticmethod
    def from_xml_element(node, dim):
        from TransportMaps import XML_NAMESPACE
        iom = int(node.attrib.get('integration_multiplier', 6))
        const_node = node.find(XML_NAMESPACE + 'constant')
        c = ParametricFunctionApproximation.from_xml_element(const_node, dim)
        exp_node = node.find(XML_NAMESPACE + 'exponential')
        e = ParametricFunctionApproximation.from_xml_element(exp_node, dim)
        return MonotonicIntegratedExponentialApproximation(c, e, integ_ord_mult=iom)

class MonotonicIntegratedSquaredApproximation(MonotonicFunctionApproximation):
    r""" Integrated Squared approximation.

    For :math:`{\bf x} \in \mathbb{R}^d` The approximation takes the form:

    .. math::
       :label: integ-exp
       
       f_{\bf a}({\bf x}) = c({\bf x};{\bf a}^c) + \int_0^{{\bf x}_d} \left( h({\bf x}_{1:d-1},t;{\bf a}^e) \right)^2 dt

    where

    .. math::
    
       c({\bf x};{\bf a}^c) = \Phi({\bf x}) {\bf a}^c = \sum_{{\bf i}\in \mathcal{I}_c} \Phi_{\bf i}({\bf x}) {\bf a}^c_{\bf i} \qquad \text{and} \qquad h({\bf x}_{1:d-1},t;{\bf a}^e) = \Psi({\bf x}_{1:d-1},t) {\bf a}^e = \sum_{{\bf i}\in \mathcal{I}_e} \Psi_{\bf i}({\bf x}_{1:d-1},t) {\bf a}^e_{\bf i}

    for the set of basis :math:`\Phi` and :math:`\Psi` with cardinality :math:`\sharp \mathcal{I}_c = N_c` and :math:`\sharp \mathcal{I}_e = N_e`. In the following :math:`N=N_c+N_e`.

    Args:
       c (:class:`LinearSpanApproximation`): :math:`d-1` dimensional
         approximation of :math:`c({\bf x}_{1:d-1};{\bf a}^c)`.
       h (:class:`LinearSpanApproximation`): :math:`d` dimensional
         approximation of :math:`h({\bf x}_{1:d-1},t;{\bf a}^e)`.
    """

    def __init__(self, c, h):
        if c.dim != h.dim:
            raise ValueError("The dimension of the constant part and the " +
                             "squared part of the approximation must be " +
                             "the same.")
        if c.get_directional_orders()[-1] != 0:
            raise ValueError("The order along the last direction of the constant " +
                             "part of the approximation must be zero")
        self.c = c
        self.h = IntegratedSquaredParametricFunctionApproximation( h )
        super(MonotonicIntegratedSquaredApproximation, self).__init__(h.dim)

    def init_coeffs(self):
        r""" Initialize the coefficients :math:`{\bf a}`
        """
        self.c.init_coeffs()
        self.h.init_coeffs()

    @property
    def n_coeffs(self):
        r""" Get the number :math:`N` of coefficients :math:`{\bf a}`

        Returns:
          (:class:`int<int>`) -- number of coefficients
        """
        return self.c.n_coeffs + self.h.n_coeffs

    @property
    def coeffs(self):
        r""" Get the coefficients :math:`{\bf a}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients
        """
        return np.hstack( (self.c.coeffs, self.h.coeffs) )

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients :math:`{\bf a}`.

        Args:
          coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
        """
        if len(coeffs) != self.n_coeffs:
            raise ValueError("Wrong number of coefficients provided.")
        nc = self.c.n_coeffs
        self.c.coeffs = coeffs[:nc]
        self.h.coeffs = coeffs[nc:]

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_evaluate(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_evaluate(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated squared part
        try: precomp_intsq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_evaluate(x, precomp['intsq'], precomp_type)
        return precomp

    def precomp_Vandermonde_evaluate(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_evaluate(x, precomp, precomp_type='multi')

    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function evaluations
        """
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluate
        out = self.c.evaluate(x, prec_const, idxs_slice)
        out += self.h.evaluate(x, prec_intsq, idxs_slice)
        return out

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_evaluate part
        self.precomp_evaluate(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated squared part
        self.h.precomp_grad_x(x, precomp['intsq'], precomp_type=precomp_type)
        return precomp

    def precomp_Vandermonde_grad_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_grad_x(x, precomp, precomp_type='multi')

    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}` at ``x``.

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
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.grad_x(x, prec_const)
        out += self.h.grad_x(x, prec_intsq)
        return out

    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla{\bf a} \nabla_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla{\bf a} \nabla_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim))
        # Evaluation
        out[:,:ncc,:] = self.c.grad_a_grad_x(x, prec_const)
        out[:,ncc:,:] = self.h.grad_a_grad_x(x, prec_intsq)
        return out

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x part (and precomp_evaluate)
        self.precomp_grad_x(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Squared part
        self.h.precomp_hess_x(x, precomp['intsq'], precomp_type=precomp_type)
        return precomp

    def precomp_Vandermonde_hess_x(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``

        Enriches the ``precomp`` dictionary if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary containing the necessary structures
        """
        return self.precomp_hess_x(x, precomp, precomp_type='multi')
        
    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_hess_x(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.hess_x(x, prec_const)
        out += self.h.hess_x(x, prec_intsq)
        return out
        
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla{\bf a} \nabla^2_{\bf x} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d,d`]) --
            :math:`\nabla{\bf a} \nabla^2_{\bf x} f_{\bf a}({\bf x})`
        """
        try: # precomp_evaluate structures
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim, self.dim))
        # Evaluation
        out[:,:ncc,:,:] = self.c.grad_a_hess_x(x, prec_const)
        out[:,ncc:,:,:] = self.h.grad_a_hess_x(x, prec_intsq)
        return out

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a} f_{\bf a}` at ``x``.

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
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs))
        # Constant part
        out[:,:ncc] = self.c.grad_a(x, prec_const, idxs_slice)
        # Integrated squared part
        out[:,ncc:] = self.h.grad_a(x, prec_intsq, idxs_slice)
        return out

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a} f_{\bf a}` at ``x``.

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
        try:
            prec_const = precomp['const']
            if 'V_list' not in prec_const: raise KeyError()
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_evaluate(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        nc = self.n_coeffs
        ncc = self.c.n_coeffs
        nce = nc - ncc
        out = np.zeros((x.shape[0],nc,nc))
        # Constant part
        if not isinstance(self.c, LinearSpanApproximation):
            out[:,:ncc,:ncc] = self.c.hess_a(x, prec_const, idxs_slice)
        # Integrated squared part
        out[:,ncc:,ncc:] = self.h.hess_a(x, prec_intsq, idxs_slice)
        return out
        
    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Integrated squared part
        try: precomp_sq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_partial_xd(x, precomp['intsq'], precomp_type)
        return precomp

    def precomp_Vandermonde_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial_xd(x, precomp, precomp_type='multi')

    def partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        # Evaluation
        out = self.c.partial_xd(x, prec_const, idxs_slice) + \
              self.h.partial_xd(x, prec_sq, idxs_slice)
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_partial_xd
        self.precomp_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_grad_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_grad_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Squared part
        self.h.precomp_grad_x_partial_xd(x, precomp['intsq'], precomp_type)
        return precomp

    def precomp_Vandermonde_grad_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_grad_x_partial_xd(x, precomp, precomp_type='multi')

    def grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        # Evaluation
        out = self.c.grad_x_partial_xd(x, precomp=prec_const) + \
              self.h.grad_x_partial_xd(x, precomp=prec_sq)
        return out

    def grad_a_grad_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d`]) --
            :math:`\nabla{\bf a} \nabla_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_grad_x_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim))
        # Evaluation
        out[:,:ncc,:] = self.c.grad_a_grad_x_partial_xd(x, precomp=prec_const)
        out[:,ncc:,:] = self.h.grad_a_grad_x_partial_xd(x, precomp=prec_sq)
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        if precomp is None: precomp = {}
        # precomp_grad_x_partial_xd (and precomp_partial_xd)
        self.precomp_grad_x_partial_xd(x, precomp, precomp_type)
        # Constant part
        if precomp_type == 'uni':
            self.c.precomp_hess_x_partial_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_hess_x_partial_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Squared part
        self.h.precomp_hess_x_partial_xd(x, precomp['intsq'], precomp_type)
        return precomp

    def precomp_Vandermonde_hess_x_partial_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with the necessary structures
        """
        return self.precomp_hess_x_partial_xd(x, precomp, precomp_type='multi')

    def hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        out = self.c.hess_x_partial_xd(x, prec_const) + \
              self.h.hess_x_partial_xd(x, prec_intsq)
        return out

    def grad_a_hess_x_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla{\bf a} \nabla^2_{\bf x}\partial_{x_d} f_{\bf a}` at ``x``.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d,d`]) --
            :math:`\nabla{\bf a} \nabla^2_{\bf x}\partial_{x_d} f_{\bf a}({\bf x})`
        """
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim, self.dim))
        # Evaluation
        out[:,:ncc,:,:] = self.c.grad_a_hess_x_partial_xd(x, prec_const)
        out[:,ncc:,:,:] = self.h.grad_a_hess_x_partial_xd(x, prec_intsq)
        return out

    def precomp_partial2_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary uni/multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values
          precomp_type (str): whether to precompute uni-variate Vandermonde matrices
            (``uni``) or to precompute the multi-variate Vandermonde matrices (``multi``)

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        if precomp is None: precomp = {}
        # Constant part
        try: precomp_const = precomp['const']
        except KeyError as e: precomp['const'] = {}
        if precomp_type == 'uni':
            self.c.precomp_partial2_xd(x, precomp['const'])
        elif precomp_type == 'multi':
            self.c.precomp_Vandermonde_partial2_xd(x, precomp['const'])
        else: raise ValueError("Unrecognized precomp_type")
        # Squared part
        try: sq = precomp['intsq']
        except KeyError as e: precomp['intsq'] = {}
        self.h.precomp_partial2_xd(x, precomp['intsq'], precomp_type)
        return precomp

    def precomp_Vandermonde_partial2_xd(self, x, precomp=None):
        r""" Precompute necessary multi-variate structures for the evaluation of :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

        Enriches the ``precomp`` dictionary if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary of precomputed values

        Returns:
          (:class:`dict<dict>`) -- dictionary with necessary structures
        """
        return self.precomp_partial2_xd(x, precomp, precomp_type='multi')

    def partial2_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\partial^2_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial2_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial2_xd(x, precomp)
        prec_const = precomp['const']
        prec_sq = precomp['intsq']
        # Evaluation
        out = self.c.partial2_xd(x, prec_const) + \
              self.h.partial2_xd(x, prec_sq)
        return out

    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_sq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        out = np.zeros((x.shape[0], self.n_coeffs))
        out[:,:ncc] = self.c.grad_a_partial_xd(x, prec_const, idxs_slice)
        out[:,ncc:] = self.h.grad_a_partial_xd(x, prec_intsq, idxs_slice)
        return out

    def hess_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate :math:`\nabla^2_{\bf a}\partial_{x_d} f_{\bf a}` at ``x``.

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
        try: # precomp_partial_xd structures
            prec_const = precomp['const']
            prec_intsq = precomp['intsq']
        except (TypeError, KeyError) as e:
            idxs_slice = slice(None)
            precomp = self.precomp_partial_xd(x, precomp)
        prec_const = precomp['const']
        prec_intsq = precomp['intsq']
        # Evaluation
        if idxs_slice is None: idxs_slice = range(x.shape[0])
        ncc = self.c.n_coeffs
        nc = self.n_coeffs
        out = np.zeros((x.shape[0], nc, nc))
        if not isinstance(self.c, LinearSpanApproximation):
            out[:,:ncc,:ncc] = self.c.hess_a_partial_xd(x, prec_const, idxs_slice)
        out[:,ncc:,ncc:] = self.h.hess_a_partial_xd(x, prec_intsq, idxs_slice)
        return out

    def get_identity_coeffs(self):
        # Define the identity map
        coeffs = np.zeros(self.n_coeffs)
        idx = next(i for i,x in enumerate(self.h.get_multi_idxs()) if x == tuple([0]*self.h.dim))
        coeffs[self.c.n_coeffs + idx] = 1.
        return coeffs
        
    def precomp_regression(self, x, precomp=None, *args, **kwargs):
        r""" Precompute necessary structures for the speed up of :func:`regression`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): dictionary to be updated

        Returns:
           (:class:`dict<dict>`) -- dictionary of necessary strucutres
        """
        if precomp is None:
            precomp = {}
        precomp.update( self.precomp_evaluate(x) )
        return precomp

    def regression(self, f, fparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None, regularization=None, tol=1e-4, maxit=100,
                   batch_size=(None,None,None), mpi_pool=None, import_set=set()):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert f - f_{\bf a} \Vert_{\pi}`.

        Args:
          f (:class:`Function` or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`f` or its functions values
          fparams (dict): parameters for function :math:`f`
          d (Distribution): distribution :math:`\pi`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size (:class:`list<list>` [3] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          mpi_pool (:class:`mpi_map.MPI_Pool`): pool of processes to be used
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field`` (for MPI purposes)

        Returns:
          (:class:`tuple<tuple>`(:class:`ndarray<numpy.ndarray>` [:math:`N`],
          :class:`list<list>`)) -- containing the :math:`N` coefficients and
          log information from the optimizer.

        .. seealso:: :func:`TransportMaps.TriangularTransportMap.regression`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`coeffs` in order
           to retrieve them.
        
        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
           exclusive, but one pair of them is necessary.
        """
        self.mpi_pool = mpi_pool
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
            
        params = {}
        params['x'] = x
        params['w'] = w
        params['regularization'] = regularization
        params['batch_size'] = batch_size
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        options = {'maxiter': maxit,
                   'disp': False}
        if x0 is None:
            x0 = self.get_default_init_values_regression()
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation started")
        if isinstance(f, np.ndarray):
            params['fvals'] = f
        else:
            scatter_tuple = (['x'], [x])
            bcast_tuple = (['precomp'], [fparams])
            params['fvals'] = mpi_eval("evaluate", scatter_tuple=scatter_tuple,
                                       bcast_tuple=bcast_tuple,
                                       obj=f, mpi_pool=self.mpi_pool)
        # Init precomputation memory
        (_, params['params1']) = mpi_eval("init_mem_precomp_regression",
                                          dmem_key_out_list=['params1'],
                                          obj=self, mpi_pool=self.mpi_pool,
                                          concatenate=False)
        # Precompute
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_regression", scatter_tuple=scatter_tuple,
                 dmem_key_in_list=['params1'],
                 dmem_arg_in_list=['precomp'],
                 dmem_val_in_list=[params['params1']],
                 obj=self, mpi_pool=self.mpi_pool, concatenate=False)

        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("regression(): Precomputation ended")

        # Callback variables
        self.params1_callback = params['params1']
        self.hess_assembled = False

        # Minimize
        res = sciopt.minimize(
            self.regression_objective, args=params, x0=x0,
            jac=self.regression_grad_a_objective,
            hessp=self.regression_action_storage_hess_a_objective,
            method='Newton-CG', tol=tol, options=options,
            callback=self.regression_callback)
        if not res['success']:
            self.logger.warn("Regression failure: " + res['message'])

        # Clean up callback stuff
        del self.params1_callback
        del self.hess_assembled
        
        coeffs = res['x']
        self.coeffs = coeffs
        self.mpi_pool = None
        return (coeffs, res)

    def regression_callback(self, xk):
        self.hess_assembled = False

    @staticmethod
    def from_xml_element(node, dim):
        from TransportMaps import XML_NAMESPACE
        const_node = node.find(XML_NAMESPACE + 'constant')
        c = ParametricFunctionApproximation.from_xml_element(const_node, dim)
        sq_node = node.find(XML_NAMESPACE + 'squared')
        e = ParametricFunctionApproximation.from_xml_element(sq_node, dim)
        return MonotonicIntegratedSquaredApproximation(c, e)
