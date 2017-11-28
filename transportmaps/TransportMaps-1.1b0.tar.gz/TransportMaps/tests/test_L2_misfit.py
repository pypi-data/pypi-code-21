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
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import unittest
import numpy as np
import numpy.random as npr
import TransportMaps as TM
import TransportMaps.Distributions as DIST
import TransportMaps.FiniteDifference as FD
import TransportMaps.Functionals as FUNC
import SpectralToolbox.Spectral1D as S1D

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class L2_misfit_DerivativeChecks(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.d = DIST.StandardNormalDistribution(2)
        self.order = 2
        self.fd_eps = 1e-4
        self.qtype = 3
        self.qparams = [10] * 2

    def test_grad_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def L2_misfit(a, params):
            f1.coeffs = a
            out = TM.L2squared_misfit(f1, f2, d=d, qtype=qtype, qparams=qparams,
                               mpi_pool=mpi_pool)
            return out

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, d=d, qtype=qtype, qparams=qparams,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_grad_a(L2_misfit, grad_a_L2_misfit,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, d=d, qtype=qtype, qparams=qparams,
                                      mpi_pool=mpi_pool)
            return out

        def hess_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.hess_a_L2squared_misfit(f1, f2, d=d, qtype=qtype, qparams=qparams,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_hess_a_from_grad_a(
            grad_a_L2_misfit, hess_a_L2_misfit,
            self.coeffs, self.fd_eps,
            None, verbose=False)
        self.assertTrue( flag )

    def test_action_storage_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        v = np.random.randn( len(self.coeffs) )

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, d=d, qtype=qtype, qparams=qparams,
                                      mpi_pool=mpi_pool)
            return out

        def action_storage_hess_a_L2_misfit(a, v, params):
            f1.coeffs = a
            params1 = {}
            (_, H) = TM.storage_hess_a_L2squared_misfit(
                f1, f2, d=d, params1=params1, qtype=qtype, qparams=qparams,
                mpi_pool=mpi_pool)
            out = TM.action_hess_a_L2squared_misfit(H, v)
            return out

        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_L2_misfit, action_storage_hess_a_L2_misfit,
            self.coeffs, self.fd_eps, v,
            None, verbose=False)
        self.assertTrue( flag )

    def test_batch_grad_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)

        def L2_misfit(a, params):
            f1.coeffs = a
            out = TM.L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                               mpi_pool=mpi_pool)
            return out

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_grad_a(L2_misfit, grad_a_L2_misfit,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_batch_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      mpi_pool=mpi_pool)
            return out

        def hess_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.hess_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_hess_a_from_grad_a(
            grad_a_L2_misfit, hess_a_L2_misfit,
            self.coeffs, self.fd_eps,
            None, verbose=False)
        self.assertTrue( flag )

    def test_batch_action_storage_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        v = np.random.randn( len(self.coeffs) )
        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      mpi_pool=mpi_pool)
            return out

        def action_storage_hess_a_L2_misfit(a, v, params):
            f1.coeffs = a
            (_, H) = TM.storage_hess_a_L2squared_misfit(
                f1, f2, d=d, qtype=qtype, qparams=qparams,
                batch_size=batch_size, mpi_pool=mpi_pool)
            out = TM.action_hess_a_L2squared_misfit(H, v)
            return out

        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_L2_misfit, action_storage_hess_a_L2_misfit,
            self.coeffs, self.fd_eps, v,
            None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_grad_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x, w) = d.quadrature(qtype, qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)

        def L2_misfit(a, params):
            f1.coeffs = a
            out = TM.L2squared_misfit(f1, f2, x=x, w=w, params1=params1,
                               mpi_pool=mpi_pool)
            return out

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, params1=params1,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_grad_a(L2_misfit, grad_a_L2_misfit,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x, w) = d.quadrature(qtype, qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, params1=params1,
                                      mpi_pool=mpi_pool)
            return out

        def hess_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.hess_a_L2squared_misfit(f1, f2, x=x, w=w, params1=params1,
                                      mpi_pool=mpi_pool)
            return out

        flag = FD.check_hess_a_from_grad_a(
            grad_a_L2_misfit, hess_a_L2_misfit,
            self.coeffs, self.fd_eps,
            None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_action_storage_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x, w) = d.quadrature(qtype, qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)
        v = np.random.randn( len(self.coeffs) )

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, params1=params1,
                                      mpi_pool=mpi_pool)
            return out

        def action_storage_hess_a_L2_misfit(a, v, params):
            f1.coeffs = a
            (_, H) = TM.storage_hess_a_L2squared_misfit(
                f1, f2, x=x, w=w, params1=params1,
                mpi_pool=mpi_pool)
            out = TM.action_hess_a_L2squared_misfit(H, v)
            return out

        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_L2_misfit, action_storage_hess_a_L2_misfit,
            self.coeffs, self.fd_eps, v,
            None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_grad_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)

        def L2_misfit(a, params):
            f1.coeffs = a
            out = TM.L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                               params1=params1, mpi_pool=mpi_pool)
            return out

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      params1=params1, mpi_pool=mpi_pool)
            return out

        flag = FD.check_grad_a(L2_misfit, grad_a_L2_misfit,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      params1=params1, mpi_pool=mpi_pool)
            return out

        def hess_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.hess_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      params1=params1, mpi_pool=mpi_pool)
            return out

        flag = FD.check_hess_a_from_grad_a(
            grad_a_L2_misfit, hess_a_L2_misfit,
            self.coeffs, self.fd_eps,
            None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_action_storage_hess_a_l2_misfit(self):
        d = self.d
        f1 = self.f1
        f2 = self.f2
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        v = np.random.randn( len(self.coeffs) )
        batch_size = 3
        (x,w) = d.quadrature(qtype,qparams)
        (_, params1) = TM.mpi_eval('init_mem_precomp_regression',
                                   dmem_key_out_list=['params1'],
                                   obj=f1, mpi_pool=mpi_pool,
                                   concatenate=False)
        dmem_key_in_list = ['params1']
        dmem_arg_in_list = ['precomp']
        dmem_val_in_list = [params1]
        scatter_tuple = (['x'], [x])
        TM.mpi_eval('precomp_regression', scatter_tuple=scatter_tuple,
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj=f1, mpi_pool=mpi_pool, concatenate=False)

        def grad_a_L2_misfit(a, params):
            f1.coeffs = a
            out = TM.grad_a_L2squared_misfit(f1, f2, x=x, w=w, batch_size=batch_size,
                                      params1=params1, mpi_pool=mpi_pool)
            return out

        def action_storage_hess_a_L2_misfit(a, v, params):
            f1.coeffs = a
            (_, H) = TM.storage_hess_a_L2squared_misfit(
                f1, f2, x=x, w=w, batch_size=batch_size,
                params1=params1, mpi_pool=mpi_pool)
            out = TM.action_hess_a_L2squared_misfit(H, v)
            return out

        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_L2_misfit, action_storage_hess_a_L2_misfit,
            self.coeffs, self.fd_eps, v,
            None, verbose=False)
        self.assertTrue( flag )

#
# Serial and parallel tests
#
class Serial_L2_misfit_DerivativeChecks(L2_misfit_DerivativeChecks):
    def setUp(self):
        super(Serial_L2_misfit_DerivativeChecks,self).setUp()
        self.mpi_pool = None

class Parallel_L2_misfit_DerivativeChecks(L2_misfit_DerivativeChecks):
    def setUp(self):
        super(Parallel_L2_misfit_DerivativeChecks,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)

#
# Linear Span and Integrated Exponential and Integrated Squared
#
class LinSpan():
    def setUp_approx(self):
        basis_list = [ S1D.HermiteProbabilistsPolynomial() ] * 2
        order_list = [ self.order ]*2
        # 2d Random target function
        self.f2 = FUNC.LinearSpanApproximation(
            basis_list, spantype='total', order_list=order_list)
        self.f2.coeffs = np.random.randn( self.f2.n_coeffs ) 
        # Approximating Function
        self.f1 = FUNC.LinearSpanApproximation(
            basis_list, spantype='total', order_list=order_list)
        # Random point on coeff space
        self.coeffs = np.random.randn( self.f1.n_coeffs )
class MonoLinSpan():
    def setUp_approx(self):
        basis_list = [ S1D.HermiteProbabilistsPolynomial() ] * 2
        order_list = [ self.order ]*2
        # 2d Random target function
        self.f2 = FUNC.MonotonicLinearSpanApproximation(
            basis_list, spantype='total', order_list=order_list)
        self.f2.coeffs = np.random.randn( self.f2.n_coeffs ) 
        # Approximating Function
        self.f1 = FUNC.MonotonicLinearSpanApproximation(
            basis_list, spantype='total', order_list=order_list)
        # Random point on coeff space
        self.coeffs = np.random.randn( self.f1.n_coeffs )
class IntExp():
    def setUp_approx(self):
        c_basis_list = [ S1D.HermiteProbabilistsPolynomial() ] * 2
        e_basis_list = [ S1D.ConstantExtendedHermiteProbabilistsFunction() ] * 2
        c_order_list = [self.order, 0]
        e_order_list = [self.order, self.order-1]
        # 2d Random target function
        c2 = FUNC.LinearSpanApproximation(c_basis_list, spantype='total', order_list=c_order_list)
        e2 = FUNC.LinearSpanApproximation(e_basis_list, spantype='total', order_list=e_order_list)
        self.f2 = FUNC.MonotonicIntegratedExponentialApproximation(c2, e2)
        self.f2.coeffs = np.random.randn( self.f2.n_coeffs ) 
        # Approximating Function
        c1 = FUNC.LinearSpanApproximation(c_basis_list, spantype='total', order_list=c_order_list)
        e1 = FUNC.LinearSpanApproximation(e_basis_list, spantype='total', order_list=e_order_list)
        self.f1 = FUNC.MonotonicIntegratedExponentialApproximation(c1, e1)
        # Random point on coeff space
        self.coeffs = np.random.randn( self.f1.n_coeffs )
class IntSq():
    def setUp_approx(self):
        c_basis_list = [ S1D.HermiteProbabilistsPolynomial() ] * 2
        e_basis_list = [ S1D.HermiteProbabilistsPolynomial() ] * 2
        c_order_list = [self.order, 0]
        e_order_list = [self.order, self.order-1]
        # 2d Random target function
        c2 = FUNC.LinearSpanApproximation(c_basis_list, spantype='total', order_list=c_order_list)
        e2 = FUNC.LinearSpanApproximation(e_basis_list, spantype='total', order_list=e_order_list)
        self.f2 = FUNC.MonotonicIntegratedSquaredApproximation(c2, e2)
        self.f2.coeffs = np.random.randn( self.f2.n_coeffs ) 
        # Approximating Function
        c1 = FUNC.LinearSpanApproximation(c_basis_list, spantype='total', order_list=c_order_list)
        e1 = FUNC.LinearSpanApproximation(e_basis_list, spantype='total', order_list=e_order_list)
        self.f1 = FUNC.MonotonicIntegratedSquaredApproximation(c1, e1)
        # Random point on coeff space
        self.coeffs = np.random.randn( self.f1.n_coeffs )

        
#
# Single tests
#
class Serial_LinSpan_L2_misfit_DerivativeChecks(
        Serial_L2_misfit_DerivativeChecks, LinSpan):
    def setUp(self):
        super(Serial_LinSpan_L2_misfit_DerivativeChecks,self).setUp()
        super(Serial_LinSpan_L2_misfit_DerivativeChecks,self).setUp_approx()
class Serial_MonoLinSpan_L2_misfit_DerivativeChecks(
        Serial_L2_misfit_DerivativeChecks, MonoLinSpan):
    def setUp(self):
        super(Serial_MonoLinSpan_L2_misfit_DerivativeChecks,self).setUp()
        super(Serial_MonoLinSpan_L2_misfit_DerivativeChecks,self).setUp_approx()
class Serial_IntExp_L2_misfit_DerivativeChecks(
        Serial_L2_misfit_DerivativeChecks, IntExp):
    def setUp(self):
        super(Serial_IntExp_L2_misfit_DerivativeChecks,self).setUp()
        super(Serial_IntExp_L2_misfit_DerivativeChecks,self).setUp_approx()
class Serial_IntSq_L2_misfit_DerivativeChecks(
        Serial_L2_misfit_DerivativeChecks, IntSq):
    def setUp(self):
        super(Serial_IntSq_L2_misfit_DerivativeChecks,self).setUp()
        super(Serial_IntSq_L2_misfit_DerivativeChecks,self).setUp_approx()
class Parallel_LinSpan_L2_misfit_DerivativeChecks(
        Parallel_L2_misfit_DerivativeChecks, LinSpan):
    def setUp(self):
        super(Parallel_LinSpan_L2_misfit_DerivativeChecks,self).setUp()
        super(Parallel_LinSpan_L2_misfit_DerivativeChecks,self).setUp_approx()
class Parallel_MonoLinSpan_L2_misfit_DerivativeChecks(
        Parallel_L2_misfit_DerivativeChecks, MonoLinSpan):
    def setUp(self):
        super(Parallel_MonoLinSpan_L2_misfit_DerivativeChecks,self).setUp()
        super(Parallel_MonoLinSpan_L2_misfit_DerivativeChecks,self).setUp_approx()
class Parallel_IntExp_L2_misfit_DerivativeChecks(
        Parallel_L2_misfit_DerivativeChecks, IntExp):
    def setUp(self):
        super(Parallel_IntExp_L2_misfit_DerivativeChecks,self).setUp()
        super(Parallel_IntExp_L2_misfit_DerivativeChecks,self).setUp_approx()
class Parallel_IntSq_L2_misfit_DerivativeChecks(
        Parallel_L2_misfit_DerivativeChecks, IntSq):
    def setUp(self):
        super(Parallel_IntSq_L2_misfit_DerivativeChecks,self).setUp()
        super(Parallel_IntSq_L2_misfit_DerivativeChecks,self).setUp_approx()
        
def build_suite(ttype='all'):
    suite_se_ls_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Serial_LinSpan_L2_misfit_DerivativeChecks )
    suite_se_mls_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Serial_MonoLinSpan_L2_misfit_DerivativeChecks )
    suite_se_ie_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Serial_IntExp_L2_misfit_DerivativeChecks )
    suite_se_sq_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Serial_IntSq_L2_misfit_DerivativeChecks )
    suite_pa_ls_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_LinSpan_L2_misfit_DerivativeChecks )
    suite_pa_mls_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_MonoLinSpan_L2_misfit_DerivativeChecks )
    suite_pa_ie_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_IntExp_L2_misfit_DerivativeChecks )
    suite_pa_sq_l2_mf = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_IntSq_L2_misfit_DerivativeChecks )

    # Serial
    suites_list = []
    if ttype in ['all','serial']:
        suites_list = [
            suite_se_ls_l2_mf,
            suite_se_mls_l2_mf, 
            suite_se_ie_l2_mf,
            suite_se_sq_l2_mf
        ]
    # Parallel
    if ttype in ['all','parallel'] and MPI_SUPPORT:
        suites_list += [
            suite_pa_ls_l2_mf,
            suite_pa_mls_l2_mf,
            suite_pa_ie_l2_mf,
            suite_pa_sq_l2_mf
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)
    
if __name__ == '__main__':
    run_tests()