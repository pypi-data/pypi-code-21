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

import unittest
import numpy as np
import numpy.random as npr
from TransportMaps import mpi_eval

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class KL_divergence_DerivativeChecks(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.fd_eps = 1e-6
        self.nprocs = 1

    def test_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def kl_divergence(a, params):
            d2.coeffs = a
            out = TM.kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_tuple_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def kl_divergence(a, params):
            d2.coeffs = a
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.hess_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, qtype=qtype, qparams=qparams,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            (_, H) = TM.storage_hess_a_kl_divergence(
                d1, d2, qtype=qtype, qparams=qparams,
                mpi_pool_tuple=(None,mpi_pool))
            out = TM.action_hess_a_kl_divergence(H, v)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

    def test_batch_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        params2 = None

        def kl_divergence(a, params):
            d2.coeffs = a
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   batch_size=batch_size,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_batch_tuple_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        params2 = None

        def kl_divergence(a, params):
            d2.coeffs = a
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  batch_size=batch_size,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  batch_size=batch_size,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_batch_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        params2 = None

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.hess_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size, 
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_batch_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        params2 = None

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            (_, H) = TM.storage_hess_a_kl_divergence(
                d1, d2, params2=params2, qtype=qtype, qparams=qparams,
                batch_size=batch_size, mpi_pool_tuple=(None,mpi_pool))
            out = TM.action_hess_a_kl_divergence(H, v)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_tuple_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.hess_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            scatter_tuple = (['x', 'w'],[x, w])
            bcast_tuple = (['d1', 'd2'], [d1, d2])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params2']
            dmem_val_in_list = [params2]
            dmem_key_out_list = ['hess_a_kl_divergence']
            (_, H) = TM.mpi_eval(
                TM.storage_hess_a_kl_divergence, scatter_tuple=scatter_tuple,
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list,
                mpi_pool=mpi_pool, concatenate=False)
            bcast_tuple = (['v'], [v])
            dmem_key_in_list = ['hess_a_kl_divergence']
            dmem_arg_in_list = ['H']
            dmem_val_in_list = [H]
            reduce_obj = TM.SumChunkReduce(axis=0)
            out = TM.mpi_eval(TM.action_hess_a_kl_divergence,
                              bcast_tuple=bcast_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              reduce_obj=reduce_obj,
                              mpi_pool=mpi_pool)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   batch_size=batch_size, mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_tuple_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                                bcast_tuple=bcast_tuple,
                                dmem_key_out_list=['params2'],
                                obj=d2.transport_map,
                                mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  batch_size=batch_size, mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  batch_size=batch_size,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool,
                               concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.hess_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_batch_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool,
                               concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            scatter_tuple = (['x', 'w'],[x, w])
            bcast_tuple = (['d1', 'd2', 'batch_size'], [d1, d2, batch_size])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params2']
            dmem_val_in_list = [params2]
            dmem_key_out_list = ['hess_a_kl_divergence']
            (_, H) = TM.mpi_eval(
                TM.storage_hess_a_kl_divergence, scatter_tuple=scatter_tuple,
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list,
                mpi_pool=mpi_pool, concatenate=False)
            bcast_tuple = (['v'], [v])
            dmem_key_in_list = ['hess_a_kl_divergence']
            dmem_arg_in_list = ['H']
            dmem_val_in_list = [H]
            reduce_obj = TM.SumChunkReduce(axis=0)
            out = TM.mpi_eval(TM.action_hess_a_kl_divergence,
                              bcast_tuple=bcast_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              reduce_obj=reduce_obj,
                              mpi_pool=mpi_pool)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        
        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        
        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[1])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with grad_a_kl_divergence
            TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                    mpi_pool_tuple=(None,mpi_pool))
            # Evaluate
            out = TM.hess_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[1])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with grad_a_kl_divergence
            TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                    mpi_pool_tuple=(None,mpi_pool))
            # Evaluate
            scatter_tuple = (['x', 'w'],[x, w])
            bcast_tuple = (['d1', 'd2'], [d1, d2])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params2']
            dmem_val_in_list = [params2]
            dmem_key_out_list = ['hess_a_kl_divergence']
            (_, H) = TM.mpi_eval(
                TM.storage_hess_a_kl_divergence, scatter_tuple=scatter_tuple,
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list,
                mpi_pool=mpi_pool, concatenate=False)
            bcast_tuple = (['v'], [v])
            dmem_key_in_list = ['hess_a_kl_divergence']
            dmem_arg_in_list = ['H']
            dmem_val_in_list = [H]
            reduce_obj = TM.SumChunkReduce(axis=0)
            out = TM.mpi_eval(TM.action_hess_a_kl_divergence,
                              bcast_tuple=bcast_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              reduce_obj=reduce_obj,
                              mpi_pool=mpi_pool)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_batch_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   batch_size=batch_size,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_batch_tuple_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out,_ = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                 batch_size=batch_size,
                                                 mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            _,out = TM.tuple_grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                                  batch_size=batch_size,
                                                  mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_batch_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[1])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def hess_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with grad_a_kl_divergence
            TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                    mpi_pool_tuple=(None,mpi_pool))
            # Evaluate
            out = TM.hess_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_hess_a_from_grad_a(grad_a_kl_divergence, hess_a_kl_divergence,
                                           self.coeffs, self.fd_eps,
                                           None, verbose=False)
        self.assertTrue( flag )

    def test_precomp_cached_batch_action_storage_hess_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        batch_size = 3

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Precomp
        scatter_tuple = (['x'], [x])
        mpi_eval("precomp_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[1])
        mpi_eval("allocate_cache_minimize_kl_divergence",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          batch_size=batch_size,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out
        def action_storage_hess_a_kl_divergence(a, v, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            mpi_eval("reset_cache_minimize_kl_divergence_grad_a_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with grad_a_kl_divergence
            TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                    mpi_pool_tuple=(None,mpi_pool))
            # Evaluate
            scatter_tuple = (['x', 'w'],[x, w])
            bcast_tuple = (['d1', 'd2', 'batch_size'], [d1, d2, batch_size])
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params2']
            dmem_val_in_list = [params2]
            dmem_key_out_list = ['hess_a_kl_divergence']
            (_, H) = TM.mpi_eval(
                TM.storage_hess_a_kl_divergence, scatter_tuple=scatter_tuple,
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list,
                mpi_pool=mpi_pool, concatenate=False)
            bcast_tuple = (['v'], [v])
            dmem_key_in_list = ['hess_a_kl_divergence']
            dmem_arg_in_list = ['H']
            dmem_val_in_list = [H]
            reduce_obj = TM.SumChunkReduce(axis=0)
            out = TM.mpi_eval(TM.action_hess_a_kl_divergence,
                              bcast_tuple=bcast_tuple,
                              dmem_key_in_list=dmem_key_in_list,
                              dmem_arg_in_list=dmem_arg_in_list,
                              dmem_val_in_list=dmem_val_in_list,
                              reduce_obj=reduce_obj,
                              mpi_pool=mpi_pool)
            return out

        v = np.random.randn( d2.n_coeffs )
        flag = FD.check_action_hess_a_from_grad_a(
            grad_a_kl_divergence, action_storage_hess_a_kl_divergence,
            self.coeffs, self.fd_eps, v, None, verbose=False)
        self.assertTrue( flag )

#
# Serial and parallel tests
#
class Serial_KL_divergence_DerivativeChecks(KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Serial_KL_divergence_DerivativeChecks,self).setUp()
        self.mpi_pool = None

class ParallelPool_KL_divergence_DerivativeChecks(KL_divergence_DerivativeChecks):
    def setUp(self):
        import TransportMaps as TM
        super(ParallelPool_KL_divergence_DerivativeChecks,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)

#
# PullBack and PushForward test cases
#
class Serial_PullBackTMD_KL_divergence_DerivativeChecks(
        Serial_KL_divergence_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PullBackTransportMapDistribution( self.tm_approx,
                                                         self.distribution_pi )
        super(Serial_PullBackTMD_KL_divergence_DerivativeChecks,self).setUp()

class ParallelPool_PullBackTMD_KL_divergence_DerivativeChecks(
        ParallelPool_KL_divergence_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PullBackTransportMapDistribution( self.tm_approx,
                                                         self.distribution_pi )
        super(ParallelPool_PullBackTMD_KL_divergence_DerivativeChecks,self).setUp()

class Serial_PushForwardTMD_KL_divergence_DerivativeChecks(
        Serial_KL_divergence_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PushForwardTransportMapDistribution( self.tm_approx,
                                                            self.distribution_pi )
        super(Serial_PushForwardTMD_KL_divergence_DerivativeChecks,self).setUp()

class ParallelPool_PushForwardTMD_KL_divergence_DerivativeChecks(
        ParallelPool_KL_divergence_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PushForwardTransportMapDistribution( self.tm_approx,
                                                            self.distribution_pi )
        super(ParallelPool_PushForwardTMD_KL_divergence_DerivativeChecks,self).setUp()

#
# Transport Map
# 
class IntegratedExponentialTM(object):
    def setUp_tm(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='full',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='full',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.IntegratedExponentialTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 100.

#
# Serial and parallel transport map tests
#
class Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks(
        IntegratedExponentialTM,
        Serial_PullBackTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks,
              self).setUp()

class Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks(
        IntegratedExponentialTM,
        Serial_PushForwardTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks,
              self).setUp()

    @unittest.skip("Not implemented")
    def test_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_action_storage_hess_a_kl_divergence(self):
        pass
    def test_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence_inverse",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence_inverse",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

class ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks(
        IntegratedExponentialTM,
        ParallelPool_PullBackTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks,
              self).setUp()

class ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks(
        IntegratedExponentialTM,
        ParallelPool_PushForwardTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks,
              self).setUp()

    @unittest.skip("Not implemented")
    def test_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_action_storage_hess_a_kl_divergence(self):
        pass
    def test_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence_inverse",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence_inverse",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        
        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

class IntegratedSquaredTM(object):
    def setUp_tm(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 3
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='full',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='full',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.IntegratedSquaredTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        coeffs = []
        for approx in self.tm_approx.approx_list:
            # coeffs.append( np.zeros(approx.c.n_coeffs) )
            # h_coeffs = np.zeros(approx.h.n_coeffs)
            coeffs.append( npr.randn(approx.c.n_coeffs) / 10. )
            h_coeffs = npr.randn(approx.h.n_coeffs) / 10.
            midx = approx.h.get_multi_idxs()
            idx0 = midx.index( tuple([0]*approx.dim) )
            h_coeffs[idx0] += 1.
            coeffs.append( h_coeffs )
        self.coeffs = np.hstack(coeffs)

#
# Serial and parallel transport map tests
#
class Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks(
        IntegratedSquaredTM,
        Serial_PullBackTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks,
              self).setUp()

class Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks(
        IntegratedSquaredTM,
        Serial_PushForwardTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks,
              self).setUp()

    @unittest.skip("Not implemented")
    def test_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_action_storage_hess_a_kl_divergence(self):
        pass
    def test_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence_inverse",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence_inverse",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)

        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

class ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks(
        IntegratedSquaredTM,
        ParallelPool_PullBackTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks,
              self).setUp()

class ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks(
        IntegratedSquaredTM,
        ParallelPool_PushForwardTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks,
              self).setUp_tm()
        super(ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks,
              self).setUp()

    @unittest.skip("Not implemented")
    def test_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_grad_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_batch_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_action_storage_hess_a_kl_divergence(self):
        pass
    @unittest.skip("Not implemented")
    def test_precomp_cached_batch_action_storage_hess_a_kl_divergence(self):
        pass
    def test_cached_grad_a_kl_divergence(self):
        import TransportMaps as TM
        import TransportMaps.FiniteDifference as FD

        d1 = self.base_distribution
        d2 = self.distribution
        qtype = self.qtype
        qparams = self.qparams
        mpi_pool = self.mpi_pool

        (x,w) = d1.quadrature(qtype, qparams)
        # Init
        bcast_tuple = (['params_dens'], [None])
        (_,params2) = mpi_eval("init_mem_precomp_minimize_kl_divergence_inverse",
                               bcast_tuple=bcast_tuple,
                               dmem_key_out_list=['params2'],
                               obj=d2.transport_map,
                               mpi_pool=mpi_pool, concatenate=False)
        dmem_key_in_list = ['params2']
        dmem_arg_in_list = ['params']
        dmem_val_in_list = [params2]
        # Init cache
        scatter_tuple = (['x'], [x])
        bcast_tuple = (['cache_level'],[0])
        mpi_eval("allocate_cache_minimize_kl_divergence_inverse",
                 scatter_tuple=scatter_tuple,
                 bcast_tuple=bcast_tuple,
                 dmem_key_in_list=dmem_key_in_list,
                 dmem_arg_in_list=dmem_arg_in_list,
                 dmem_val_in_list=dmem_val_in_list,
                 obj=d2.transport_map, mpi_pool=mpi_pool,
                 concatenate=False)
        
        def kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Evaluate
            out = TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                   mpi_pool_tuple=(None,mpi_pool))
            return out
        def grad_a_kl_divergence(a, params):
            d2.coeffs = a
            # Reset cache
            dmem_key_in_list = ['params2']
            dmem_arg_in_list = ['params']
            dmem_val_in_list = [params2]
            mpi_eval("reset_cache_minimize_kl_divergence_objective",
                     dmem_key_in_list=dmem_key_in_list,
                     dmem_arg_in_list=dmem_arg_in_list,
                     dmem_val_in_list=dmem_val_in_list,
                     obj=d2.transport_map, mpi_pool=mpi_pool,
                     concatenate=False)
            # Fill cache with kl_divergence
            TM.kl_divergence(d1, d2, params2=params2, x=x, w=w,
                             mpi_pool_tuple=(None,mpi_pool))
            # Evaluate grad_a_kl_divergence using cached values
            out = TM.grad_a_kl_divergence(d1, d2, params2=params2, x=x, w=w,
                                          mpi_pool_tuple=(None,mpi_pool))
            return out

        flag = FD.check_grad_a(kl_divergence, grad_a_kl_divergence,
                               self.coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

        
#
# Specific tests
#
class TMD_TestCase(object):

    def setUp_test_case(self):
        import TransportMaps.Distributions as DIST
        self.dim = self.setup['dim']
        self.target_distribution = self.Tparams['target_distribution']
        self.support_map = self.Tparams['support_map']
        self.distribution_pi = DIST.PullBackTransportMapDistribution( self.support_map,
                                                            self.target_distribution )
        self.base_distribution = self.Tparams['base_distribution']
        self.qtype = 3
        self.qparams = [2]*self.dim

class Linear1D_TMD_TestCase(TMD_TestCase):    
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(0)
        super(Linear1D_TMD_TestCase,self).setUp_test_case()

class ArcTan1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(2)
        super(ArcTan1D_TMD_TestCase,self).setUp_test_case()

class Exp1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(3)
        super(Exp1D_TMD_TestCase,self).setUp_test_case()

class Logistic1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(4)
        super(Logistic1D_TMD_TestCase,self).setUp_test_case()

class Gamma1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(5)
        super(Gamma1D_TMD_TestCase,self).setUp_test_case()

class Beta1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(6)
        super(Beta1D_TMD_TestCase,self).setUp_test_case()

class Gumbel1D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(7)
        super(Gumbel1D_TMD_TestCase,self).setUp_test_case()

class Linear2D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(9)
        super(Linear2D_TMD_TestCase,self).setUp_test_case()

class Banana2D_TMD_TestCase(TMD_TestCase):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(10)
        super(Banana2D_TMD_TestCase,self).setUp_test_case()

#
# Serial PullBack tests
#
class Linear1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_Serial_IEPBTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        Serial_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_Serial_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

#
# Serial PushForward tests
#
class Linear1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_Serial_IEPFTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        Serial_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_Serial_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

#
# ParallelPool PullBack tests
#
class Linear1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks,self).setUp()

#
# ParallelPool PushForward tests
#
class Linear1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        ParallelPool_IntegratedExponentialPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks,self).setUp()

#
# Integrated Squared Serial PullBack tests
#
class Linear1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_Serial_ISPBTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        Serial_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_Serial_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

#
# Integrated Squared Serial PushForward tests
#
class Linear1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_Serial_ISPFTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        Serial_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_Serial_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

#
# Integrated Squared ParallelPool PullBack tests
#
class Linear1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPBTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks,self).setUp()

#
# Integrated Squared ParallelPool PushForward tests
#
class Linear1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Linear1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class ArcTan1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Exp1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Exp1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Logistic1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gamma1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Beta1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Beta1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Gumbel1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Linear2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Linear2D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()

class Banana2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks(
        Banana2D_TMD_TestCase,
        ParallelPool_IntegratedSquaredPFTMD_KL_divergence_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks,self).setUp()


def build_suite(ttype='all'):
    # INTEGRATED EXPONENTIAL
    # Serial PullBack tests
    suite_linear1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_exp1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_beta1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_linear2d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    suite_banana2d_se_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_Serial_IEPBTMD_KLdiv_DerivativeChecks )
    # Serial PushForward tests
    suite_linear1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_exp1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_beta1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_linear2d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    suite_banana2d_se_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_Serial_IEPFTMD_KLdiv_DerivativeChecks )
    # ParallelPool PullBack tests
    suite_linear1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_exp1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_beta1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_linear2d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    suite_banana2d_pa_pool_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ParallelPool_IEPBTMD_KLdiv_DerivativeChecks )
    # ParallelPool PushForward tests
    suite_linear1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_exp1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_beta1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_linear2d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )
    suite_banana2d_pa_pool_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ParallelPool_IEPFTMD_KLdiv_DerivativeChecks )

    # INTEGRATED SQUARED
    # Serial PullBack tests
    suite_linear1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_exp1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_beta1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_linear2d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    suite_banana2d_se_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_Serial_ISPBTMD_KLdiv_DerivativeChecks )
    # Serial PushForward tests
    suite_linear1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_exp1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_beta1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_linear2d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    suite_banana2d_se_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_Serial_ISPFTMD_KLdiv_DerivativeChecks )
    # ParallelPool PullBack tests
    suite_linear1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_exp1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_beta1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_linear2d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    suite_banana2d_pa_pool_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ParallelPool_ISPBTMD_KLdiv_DerivativeChecks )
    # ParallelPool PushForward tests
    suite_linear1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_arctan1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_exp1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_logistic1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_gamma1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_beta1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_gumbel1d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_linear2d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )
    suite_banana2d_pa_pool_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ParallelPool_ISPFTMD_KLdiv_DerivativeChecks )

    
    # GROUP SUITES
    # Serial
    suites_list = []
    if ttype in ['all','serial']:
        suites_list = [
            # INTEGRATED EXPONENTIAL
            # Serial Pull Back
            suite_linear1d_se_iepbtmd, suite_arctan1d_se_iepbtmd,
            suite_exp1d_se_iepbtmd, suite_logistic1d_se_iepbtmd,
            suite_gamma1d_se_iepbtmd, suite_beta1d_se_iepbtmd,
            suite_gumbel1d_se_iepbtmd, suite_linear2d_se_iepbtmd,
            suite_banana2d_se_iepbtmd,
            # # Serial Push Forward
            # suite_linear1d_se_iepftmd,
            # suite_arctan1d_se_iepftmd, suite_exp1d_se_iepftmd,
            # suite_logistic1d_se_iepftmd, suite_gamma1d_se_iepftmd,
            # suite_beta1d_se_iepftmd, suite_gumbel1d_se_iepftmd,
            # suite_linear2d_se_iepftmd, suite_banana2d_se_iepftmd,
            # INTEGRATED SQUARED
            # Serial Pull Back
            suite_linear1d_se_ispbtmd, suite_arctan1d_se_ispbtmd,
            suite_exp1d_se_ispbtmd, suite_logistic1d_se_ispbtmd,
            suite_gamma1d_se_ispbtmd, suite_beta1d_se_ispbtmd,
            suite_gumbel1d_se_ispbtmd, 
            suite_linear2d_se_ispbtmd,
            suite_banana2d_se_ispbtmd,
            # # Serial Push Forward
            # suite_linear1d_se_ispftmd,
            # suite_arctan1d_se_ispftmd, suite_exp1d_se_ispftmd,
            # suite_logistic1d_se_ispftmd, suite_gamma1d_se_ispftmd,
            # suite_beta1d_se_ispftmd, suite_gumbel1d_se_ispftmd,
            # suite_linear2d_se_ispftmd, suite_banana2d_se_ispftmd,
        ]
    # Parallel
    if ttype in ['all','parallel'] and MPI_SUPPORT:
        suites_list += [
            # INTEGRATED EXPONENTIAL
            # ParallelPool Pull Back
            suite_linear1d_pa_pool_iepbtmd, suite_arctan1d_pa_pool_iepbtmd,
            suite_exp1d_pa_pool_iepbtmd, suite_logistic1d_pa_pool_iepbtmd,
            suite_gamma1d_pa_pool_iepbtmd, suite_beta1d_pa_pool_iepbtmd,
            suite_gumbel1d_pa_pool_iepbtmd, suite_linear2d_pa_pool_iepbtmd,
            suite_banana2d_pa_pool_iepbtmd,
            # # ParallelPool Push Forward
            # suite_linear1d_pa_pool_iepftmd,
            # suite_arctan1d_pa_pool_iepftmd, suite_exp1d_pa_pool_iepftmd,
            # suite_logistic1d_pa_pool_iepftmd, suite_gamma1d_pa_pool_iepftmd,
            # suite_beta1d_pa_pool_iepftmd, suite_gumbel1d_pa_pool_iepftmd,
            # suite_linear2d_pa_pool_iepftmd, suite_banana2d_pa_pool_iepftmd,
            # INTEGRATED SQUARED
            # ParallelPool Pull Back
            suite_linear1d_pa_pool_ispbtmd, suite_arctan1d_pa_pool_ispbtmd,
            suite_exp1d_pa_pool_ispbtmd, suite_logistic1d_pa_pool_ispbtmd,
            suite_gamma1d_pa_pool_ispbtmd, suite_beta1d_pa_pool_ispbtmd,
            suite_gumbel1d_pa_pool_ispbtmd, suite_linear2d_pa_pool_ispbtmd,
            suite_banana2d_pa_pool_ispbtmd,
            # # ParallelPool Push Forward
            # suite_linear1d_pa_pool_ispftmd,
            # suite_arctan1d_pa_pool_ispftmd, suite_exp1d_pa_pool_ispftmd,
            # suite_logistic1d_pa_pool_ispftmd, suite_gamma1d_pa_pool_ispftmd,
            # suite_beta1d_pa_pool_ispftmd, suite_gumbel1d_pa_pool_ispftmd,
            # suite_linear2d_pa_pool_ispftmd, suite_banana2d_pa_pool_ispftmd
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)
    
if __name__ == '__main__':
    run_tests()
