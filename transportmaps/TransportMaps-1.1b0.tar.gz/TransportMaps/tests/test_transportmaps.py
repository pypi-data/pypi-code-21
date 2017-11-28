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

import logging
import unittest
import numpy as np
import numpy.random as npr
import numpy.linalg as npla

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class TransportMap_DerivativeChecks(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        import TransportMaps.Distributions as DIST
        self.dim = 2
        self.order = 3
        self.fd_eps = 1e-6
        self.qtype = 3
        self.qpar = [5]*self.dim
        self.distribution = DIST.StandardNormalDistribution(self.dim)
        (x,w) = self.distribution.quadrature(self.qtype, self.qpar)
        self.x = x
        self.w = w
        self.y = np.zeros((1,self.dim))
        self.build_tm_approx()

    def test_grad_a(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.evaluate(x, params_t)
            return out
        def grad_a_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(tm, grad_a_tm, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_a(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out
        def hess_a_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            ncoeffs = tm_approx.n_coeffs
            hess_list = tm_approx.hess_a(x, params_t)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs, ncoeffs))
            start = 0
            for k, hess in enumerate(hess_list):
                stop = start + hess.shape[1]
                out[:,k,start:stop,start:stop] = hess
                start = stop
            return out

        # Check Hessian transport map
        flag = FD.check_hess_a_from_grad_a(grad_a_tm, hess_a_tm, coeffs, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_partial_xd(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def partial_xd_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.partial_xd(x, params_t)
            return out
        def grad_a_partial_xd_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.grad_a_partial_xd(x, params_t)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(partial_xd_tm, grad_a_partial_xd_tm,
                               coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.log_det_grad_x(x, params_t)
            return out
        def grad_a_log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.grad_a_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(log_det_grad_x_tm, grad_a_log_det_grad_x_tm,
                               coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_a_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_a_log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.grad_a_log_det_grad_x(x, params_t)
            return out
        def hess_a_log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            params_t = params['params_t']
            out = tm_approx.hess_a_log_det_grad_x(x, params_t)
            return out

        # Check Hessian transport map
        flag = FD.check_hess_a_from_grad_a(grad_a_log_det_grad_x_tm,
                                           hess_a_log_det_grad_x_tm,
                                           coeffs, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_inverse(self):
        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        y = self.y
        x = tm_approx.inverse(y)
        yrec = tm_approx.evaluate(x)
        self.assertTrue( np.allclose(y, yrec, rtol=1e-10, atol=1e-10) )

    def test_grad_a_inverse(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        y = self.y

        # Define transport map, gradient
        def tm_inverse(a, params):
            tm_approx.coeffs = a
            out = tm_approx.inverse(y)
            return out
        def grad_a_tm_inverse(a, params):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_inverse(y)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(tm_inverse, grad_a_tm_inverse, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

class OnTheFly_TM_DerivativeChecks( TransportMap_DerivativeChecks ):
    """ Special test definitions for evaluation on-the-fly
    """
    def test_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params):
            out = tm_approx.evaluate(x)
            return out
        def grad_x_tm(x, params):
            out = tm_approx.grad_x(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(tm, grad_x_tm, x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_grad_x_inverse(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        y = self.y

        # Define transport map, gradient
        def tm(x, params):
            out = tm_approx.inverse(x)
            return out
        def grad_x_tm(x, params):
            out = tm_approx.grad_x_inverse(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(tm, grad_x_tm, y, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_x_tm(x, params):
            out = tm_approx.grad_x(x)
            return out
        def hess_x_tm(x, params):
            out = tm_approx.hess_x(x)
            return out

        # Check Hessian transport map
        flag = FD.check_hess_x_from_grad_x(grad_x_tm, hess_x_tm,
                                           x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_tm(x, params):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k] = grad
                start = stop
            return out

        def grad_a_grad_x_tm(x, params):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_grad_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(grad_a_tm, grad_a_grad_x_tm, x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_hess_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_a_grad_x_tm(x, params):
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_grad_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1] = grad
                start = stop
            return out

        def grad_a_hess_x_tm(x, params):
            ncoeffs = tm_approx.n_coeffs
            hess_list = tm_approx.grad_a_hess_x(x)
            out = np.zeros((len(x), ncoeffs, tm_approx.dim, tm_approx.dim, tm_approx.dim))
            start = 0
            for k, grad in enumerate(hess_list):
                stop = start + grad.shape[1]
                out[:,start:stop,k,:k+1,:k+1] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = FD.check_hess_x_from_grad_x(grad_a_grad_x_tm, grad_a_hess_x_tm, x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_log_det_grad_x(self):
        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Compute \log\det\nabla_xT from \nabla_xT
        gx = tm_approx.grad_x(x)
        ldgx_from_gx = np.zeros(x.shape[0])
        for i in range(x.shape[0]):
            ldgx_from_gx[i] = np.log(npla.det(gx[i,:,:]))
        # Compute \log\det\nabla_xT directly
        ldgx = tm_approx.log_det_grad_x(x)

        # Check result
        flag = np.max(np.abs(ldgx - ldgx_from_gx)) < 1e-10
        self.assertTrue(flag)

    def test_grad_x_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(x, params):
            out = tm_approx.log_det_grad_x(x)
            return out
        def grad_x_log_det_grad_x_tm(x, params):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
                               x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_x_log_det_grad_x_tm(x, params):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out
        def hess_x_log_det_grad_x_tm(x, params):
            out = tm_approx.hess_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = FD.check_hess_x_from_grad_x(grad_x_log_det_grad_x_tm,
                                           hess_x_log_det_grad_x_tm,
                                           x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_log_det_grad_x_inverse(self):
        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        y = self.y

        # Compute \log\det\nabla_xT from \nabla_xT
        gx = tm_approx.grad_x_inverse(y)
        ldgx_from_gx = np.zeros(y.shape[0])
        for i in range(y.shape[0]):
            ldgx_from_gx[i] = np.log(npla.det(gx[i,:,:]))
        # Compute \log\det\nabla_xT directly
        ldgx = tm_approx.log_det_grad_x_inverse(y)

        # Check result
        flag = np.max(np.abs(ldgx - ldgx_from_gx)) < 1e-10
        self.assertTrue(flag)

    # def test_grad_x_log_det_grad_x_inverse(self):
    #     import TransportMaps.FiniteDifference as FD

    #     tm_approx = self.tm_approx
    #     tm_approx.coeffs = self.coeffs
    #     params = self.params
    #     x = self.x

    #     # Define transport map, gradient
    #     def log_det_grad_x_tm(x, params):
    #         out = tm_approx.log_det_grad_x_inverse(x)
    #         return out
    #     def grad_x_log_det_grad_x_tm(x, params):
    #         out = tm_approx.grad_x_log_det_grad_x_inverse(x)
    #         return out

    #     # Check gradient transport map
    #     flag = FD.check_grad_x(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
    #                            x, self.fd_eps,
    #                            params, verbose=False)
    #     self.assertTrue( flag )

    # def test_hess_x_log_det_grad_x_inverse(self):
    #     import TransportMaps.FiniteDifference as FD

    #     tm_approx = self.tm_approx
    #     coeffs = self.coeffs
    #     tm_approx.coeffs = coeffs
    #     params = self.params
    #     x = self.x

    #     # Define transport map, gradient
    #     def grad_x_log_det_grad_x_tm(x, params):
    #         out = tm_approx.grad_x_log_det_grad_x_inverse(x)
    #         return out
    #     def hess_x_log_det_grad_x_tm(x, params):
    #         out = tm_approx.hess_x_log_det_grad_x_inverse(x)
    #         return out

    #     # Check gradient transport map
    #     flag = FD.check_hess_x_from_grad_x(grad_x_log_det_grad_x_tm,
    #                                        hess_x_log_det_grad_x_tm,
    #                                        x, self.fd_eps,
    #                                        params, verbose=False)
    #     self.assertTrue( flag )

    def test_grad_a_hess_x_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def hess_x_log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            out = tm_approx.hess_x_log_det_grad_x(x)
            return out
        def grad_a_hess_x_log_det_grad_x_tm(a, params):
            tm_approx.coeffs = a
            out = tm_approx.grad_a_hess_x_log_det_grad_x(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(hess_x_log_det_grad_x_tm, grad_a_hess_x_log_det_grad_x_tm,
                               coeffs, self.fd_eps, params, end=False, verbose=False)
        self.assertTrue( flag )

class OnTheFly_InverseTM_DerivativeChecks( TransportMap_DerivativeChecks ):
    def test_grad_x_inverse(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params):
            out = tm_approx.inverse(x)
            return out
        def grad_x_tm(x, params):
            out = tm_approx.grad_x_inverse(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(tm, grad_x_tm, x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_inverse(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(a, params):
            tm_approx.coeffs = a
            out = tm_approx.inverse(x)
            return out
        def grad_a_tm(a, params):
            tm_approx.coeffs = a
            ncoeffs = tm_approx.n_coeffs
            grad_list = tm_approx.grad_a_inverse(x)
            out = np.zeros((len(x), tm_approx.dim, ncoeffs))
            start = 0
            for k, grad in enumerate(grad_list):
                stop = start + grad.shape[1]
                out[:,k,start:stop] = grad
                start = stop
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(tm, grad_a_tm, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_grad_a(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm_inverse(a, params):
            tm_approx.coeffs = a
            out = tm_approx.evaluate(x)
            return out
        def grad_a_tm_inverse(a, params):
            tm_approx.coeffs = a
            out = tm_approx.grad_a(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(tm_inverse, grad_a_tm_inverse, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    @unittest.skip("Not Implemented")
    def test_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_partial_xd(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x_log_det_grad_x(self):
        pass

class OnTheFly_CompositeTM_DerivativeChecks( OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Not Implemented")
    def test_grad_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_inverse(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_a_log_det_grad_x(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_partial_xd(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_a_hess_x_log_det_grad_x(self):
        pass

class Precomp_TM_DerivativeChecks( TransportMap_DerivativeChecks ):
    """ Special test definitions with precomputed Vandermonde matrices.
    """
    def test_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def tm(x, params):
            out = tm_approx.evaluate(x)
            return out
        def grad_x_tm(x, params):
            params_t = params['params_t']
            out = tm_approx.grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(tm, grad_x_tm, x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport gradient and hessian
        def grad_x_tm(x, params):
            out = tm_approx.grad_x(x)
            return out
        def hess_x_tm(x, params):
            params_t = params['params_t']
            out = tm_approx.hess_x(x, params_t)
            return out

        # Check Hessian transport map
        flag = FD.check_hess_x_from_grad_x(grad_x_tm, hess_x_tm,
                                           x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_grad_x_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        tm_approx.coeffs = self.coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def log_det_grad_x_tm(x, params):
            out = tm_approx.log_det_grad_x(x)
            return out
        def grad_x_log_det_grad_x_tm(x, params):
            params_t = params['params_t']
            out = tm_approx.grad_x_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(log_det_grad_x_tm, grad_x_log_det_grad_x_tm,
                               x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_log_det_grad_x(self):
        import TransportMaps.FiniteDifference as FD

        tm_approx = self.tm_approx
        coeffs = self.coeffs
        tm_approx.coeffs = coeffs
        params = self.params
        x = self.x

        # Define transport map, gradient
        def grad_x_log_det_grad_x_tm(x, params):
            out = tm_approx.grad_x_log_det_grad_x(x)
            return out
        def hess_x_log_det_grad_x_tm(x, params):
            params_t = params['params_t']
            out = tm_approx.hess_x_log_det_grad_x(x, params_t)
            return out

        # Check gradient transport map
        flag = FD.check_hess_x_from_grad_x(grad_x_log_det_grad_x_tm,
                                           hess_x_log_det_grad_x_tm,
                                           x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

class PrecompUni_TM_DerivativeChecks( Precomp_TM_DerivativeChecks ):
    """ Precompute uni-variate Vandermonde matrices
    """
    def setUp(self):
        super(PrecompUni_TM_DerivativeChecks,self).setUp()
        x = self.x
        self.params['params_t'] = {'components': [{} for i in range(self.dim)]}
        self.tm_approx.precomp_evaluate(x, self.params['params_t'])
        self.tm_approx.precomp_partial_xd(x, self.params['params_t'])
        self.tm_approx.precomp_grad_x(x, self.params['params_t'])
        self.tm_approx.precomp_hess_x(x, self.params['params_t'])
        self.tm_approx.precomp_grad_x_partial_xd(x, self.params['params_t'])
        self.tm_approx.precomp_hess_x_partial_xd(x, self.params['params_t'])

class PrecompMulti_TM_DerivativeChecks( Precomp_TM_DerivativeChecks ):
    """ Precompute multi-variate Vandermonde matrices
    """
    def setUp(self):
        super(PrecompMulti_TM_DerivativeChecks,self).setUp()
        x = self.x
        self.params['params_t'] = {'components': [{} for i in range(self.dim)]}
        self.tm_approx.precomp_evaluate(x, self.params['params_t'],
                                        precomp_type='multi')
        self.tm_approx.precomp_partial_xd(x, self.params['params_t'],
                                        precomp_type='multi')
        self.tm_approx.precomp_grad_x(x, self.params['params_t'],
                                      precomp_type='multi')
        self.tm_approx.precomp_hess_x(x, self.params['params_t'],
                                      precomp_type='multi')
        self.tm_approx.precomp_grad_x_partial_xd(x, self.params['params_t'],
                                                 precomp_type='multi')
        self.tm_approx.precomp_hess_x_partial_xd(x, self.params['params_t'],
                                                 precomp_type='multi')

class IntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='full',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='full',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(
                c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.IntegratedExponentialTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class CommonBasisIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='full',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='full',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class TotOrdIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='total',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.IntegratedExponentialTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class CommonBasisTotOrdIntegratedExponentialTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class IntegratedSquaredTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
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
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.IntegratedSquaredTriangularTransportMap(active_vars,
                                                                      approx_list)
        self.params = {}
        self.params['params_t'] = None
        coeffs = []
        for approx in self.tm_approx.approx_list:
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

class CommonBasisIntegratedSquaredTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='full',
                                                    order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='full',
                                                    order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        self.coeffs = npr.randn(self.tm_approx.n_coeffs)

class TotOrdIntegratedSquaredTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='total',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='total',
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
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

class CommonBasisTotOrdIntegratedSquaredTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction() for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        coeffs = []
        for approx in self.tm_approx.approx_list:
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

# INTEGRATES SQUARED RBF

class IntegratedSquaredRBFTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='full',
                                                    order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                self.order)] * (i+1)
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
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

class CommonBasisIntegratedSquaredRBFTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='full',
                                                    order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='full',
                                                    order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        self.coeffs = npr.randn(self.tm_approx.n_coeffs)

class TotOrdIntegratedSquaredRBFTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            c_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='total',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                self.order)] * (i+1)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list, spantype='total',
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
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

class CommonBasisTotOrdIntegratedSquaredRBFTTM( object ):
    """ Integrated exponential approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        coeffs = []
        for approx in self.tm_approx.approx_list:
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

# LINEAR SPAN
        
class LinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            orders_list = [self.order] * (i+1)
            approx = FUNC.MonotonicLinearSpanApproximation(basis_list, spantype='full',
                                                           order_list=orders_list)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.LinearSpanTriangularTransportMap(active_vars,
                                                              approx_list)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class CommonBasisLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        approx_list = []
        active_vars = []
        basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        for i in range(self.dim):
            orders_list = [self.order] * (i+1)
            approx = FUNC.MonotonicLinearSpanApproximation(basis_list[:i+1], spantype='full',
                                                           order_list=orders_list)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisLinearSpanTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class TotOrdLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        approx_list = []
        active_vars = []
        for i in range(self.dim):
            basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
            orders_list = [self.order] * (i+1)
            approx = FUNC.MonotonicLinearSpanApproximation(basis_list, spantype='total',
                                                           order_list=orders_list)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.LinearSpanTriangularTransportMap(active_vars,
                                                              approx_list)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

class CommonBasisTotOrdLinearSpanTTM( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        approx_list = []
        active_vars = []
        basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        for i in range(self.dim):
            orders_list = [self.order] * (i+1)
            approx = FUNC.MonotonicLinearSpanApproximation(basis_list[:i+1], spantype='total',
                                                           order_list=orders_list)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisLinearSpanTriangularTransportMap(active_vars,
                                                                          approx_list)
        self.params = {}
        self.params['params_t'] = None
        # Set coefficients for linear map
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        all_midxs = []
        for tm_comp in self.tm_approx.approx_list:
            all_midxs.extend( tm_comp.multi_idxs )
        for d in range(self.tm_approx.dim):
            idx = all_midxs.index( tuple([0]*d + [1]) )
            self.coeffs[idx] = 1.

#
# INVERSE MAP
#
class InverseCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(active_vars,
                                                                                approx_list)
        self.tm_approx = MAPS.InverseTransportMap( tm_approx )
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

class InverseCommonBasisTotOrdIntegratedSquaredTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                        for i in range(self.dim)]
        for i in range(self.dim):
            c_orders_list = ([self.order] * i) + [0]
            c_approx = FUNC.LinearSpanApproximation(c_basis_list[:i+1], spantype='total',
                                                             order_list=c_orders_list)
            e_orders_list = [self.order] * (i+1)
            e_approx = FUNC.LinearSpanApproximation(e_basis_list[:i+1], spantype='total',
                                                             order_list=e_orders_list)
            approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(active_vars,
                                                                                approx_list)
        self.tm_approx = MAPS.InverseTransportMap( tm_approx )
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.
        
#
# COMPOSITE MAP
#
class CompositeCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        tm_approx_list = []
        for i in range(2):
            # Build the transport map (isotropic for each entry)
            approx_list = []
            active_vars = []
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                            for i in range(self.dim)]
            for i in range(self.dim):
                c_orders_list = ([self.order] * i) + [0]
                c_approx = FUNC.LinearSpanApproximation(
                    c_basis_list[:i+1], spantype='total', order_list=c_orders_list)
                e_orders_list = [self.order] * (i+1)
                e_approx = FUNC.LinearSpanApproximation(
                    e_basis_list[:i+1], spantype='total', order_list=e_orders_list)
                approx = FUNC.MonotonicIntegratedExponentialApproximation(
                    c_approx, e_approx)
                approx_list.append( approx )
                active_vars.append( range(i+1) )
            tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(
                active_vars,
                approx_list)
            tm_approx_list.append( tm_approx )
        self.tm_approx = MAPS.CompositeTransportMap(tm_approx_list[0], tm_approx_list[1])
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

#
# LIST COMPOSITE MAP
#
class ListCompositeCommonBasisTotOrdIntegratedExponentialTTM( object ):
    def build_tm_approx(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        tm_approx_list = []
        for i in range(3):
            # Build the transport map (isotropic for each entry)
            approx_list = []
            active_vars = []
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction(self.order)
                            for i in range(self.dim)]
            for i in range(self.dim):
                c_orders_list = ([self.order] * i) + [0]
                c_approx = FUNC.LinearSpanApproximation(
                    c_basis_list[:i+1], spantype='total', order_list=c_orders_list)
                e_orders_list = [self.order] * (i+1)
                e_approx = FUNC.LinearSpanApproximation(
                    e_basis_list[:i+1], spantype='total', order_list=e_orders_list)
                approx = FUNC.MonotonicIntegratedExponentialApproximation(
                    c_approx, e_approx)
                approx_list.append( approx )
                active_vars.append( range(i+1) )
            tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(
                active_vars,
                approx_list)
            tm_approx_list.append( tm_approx )
        self.tm_approx = MAPS.ListCompositeTransportMap(tm_approx_list)
        self.params = {}
        self.params['params_t'] = None
        # self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 10.

        
# FULL ORDER LINEAR SPAN
class OnTheFly_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                              OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                                PrecompUni_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompMulti_LinearSpanTM_DerivativeChecks( LinearSpanTTM,
                                                  PrecompMulti_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass

class OnTheFly_CommonBasisLinearSpanTM_DerivativeChecks( CommonBasisLinearSpanTTM,
                                                         OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_CommonBasisLinearSpanTM_DerivativeChecks( CommonBasisLinearSpanTTM,
                                                           PrecompUni_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

# TOTAL ORDER LINEAR SPAN
class OnTheFly_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                    OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                      PrecompUni_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompMulti_TotOrdLinearSpanTM_DerivativeChecks( TotOrdLinearSpanTTM,
                                                        PrecompMulti_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class OnTheFly_CommonBasisTotOrdLinearSpanTM_DerivativeChecks( CommonBasisTotOrdLinearSpanTTM,
                                                               OnTheFly_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

class PrecompUni_CommonBasisTotOrdLinearSpanTM_DerivativeChecks( CommonBasisTotOrdLinearSpanTTM,
                                                                 PrecompUni_TM_DerivativeChecks ):
    @unittest.skip("Expected to fail")
    def test_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_a_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_grad_x_inverse(self):
        pass
    @unittest.skip("Expected to fail")
    def test_log_det_grad_x_inverse(self):
        pass

# FULL ORDER INTEGRATED EXPONENTIAL
class OnTheFly_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                         OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                           PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_IntegratedExponentialTM_DerivativeChecks( IntegratedExponentialTTM,
                                                             PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisIntegratedExponentialTM_DerivativeChecks(
        CommonBasisIntegratedExponentialTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisIntegratedExponentialTM_DerivativeChecks(
        CommonBasisIntegratedExponentialTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass

# TOTAL ORDER INTEGRATED EXPONENTIAL
class OnTheFly_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                               OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                                 PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_TotOrdIntegratedExponentialTM_DerivativeChecks( TotOrdIntegratedExponentialTTM,
                                                                   PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponentialTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass

# TOTAL ORDER INVERSE INTEGRATED EXPONENTIAL
class OnTheFly_InverseCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        InverseCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_InverseTM_DerivativeChecks ):
    pass

# TOTAL ORDER COMPOSITE INTEGRATED EXPONENTIAL
class OnTheFly_CompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        CompositeCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_CompositeTM_DerivativeChecks ):
    pass

# TOTAL ORDER LIST COMPOSITE INTEGRATED EXPONENTIAL
class OnTheFly_ListCompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks(
        ListCompositeCommonBasisTotOrdIntegratedExponentialTTM,
        OnTheFly_CompositeTM_DerivativeChecks ):
    @unittest.skip("Not Implemented")
    def test_hess_x_log_det_grad_x(self):
        pass

# FULL ORDER INTEGRATED SQUARED
class OnTheFly_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                         OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                           PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_IntegratedSquaredTM_DerivativeChecks( IntegratedSquaredTTM,
                                                             PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisIntegratedSquaredTM_DerivativeChecks(
        CommonBasisIntegratedSquaredTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisIntegratedSquaredTM_DerivativeChecks(
        CommonBasisIntegratedSquaredTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass

# TOTAL ORDER INTEGRATED SQUARED
class OnTheFly_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                               OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                                 PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_TotOrdIntegratedSquaredTM_DerivativeChecks( TotOrdIntegratedSquaredTTM,
                                                                   PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedSquaredTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedSquaredTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass
    
# TOTAL ORDER INVERSE INTEGRATED SQUARED
class OnTheFly_InverseCommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks(
        InverseCommonBasisTotOrdIntegratedSquaredTTM,
        OnTheFly_InverseTM_DerivativeChecks ):
    pass

# FULL ORDER INTEGRATED SQUARED RBF
class OnTheFly_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                         OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                           PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_IntegratedSquaredRBFTM_DerivativeChecks( IntegratedSquaredRBFTTM,
                                                             PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks(
        CommonBasisIntegratedSquaredRBFTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks(
        CommonBasisIntegratedSquaredRBFTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass

# TOTAL ORDER INTEGRATED SQUARED RBF
class OnTheFly_TotOrdIntegratedSquaredRBFTM_DerivativeChecks( TotOrdIntegratedSquaredRBFTTM,
                                                               OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_TotOrdIntegratedSquaredRBFTM_DerivativeChecks( TotOrdIntegratedSquaredRBFTTM,
                                                                 PrecompUni_TM_DerivativeChecks ):
    pass

class PrecompMulti_TotOrdIntegratedSquaredRBFTM_DerivativeChecks( TotOrdIntegratedSquaredRBFTTM,
                                                                   PrecompMulti_TM_DerivativeChecks ):
    pass

class OnTheFly_CommonBasisTotOrdIntegratedSquaredRBFTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedSquaredRBFTTM,
        OnTheFly_TM_DerivativeChecks ):
    pass

class PrecompUni_CommonBasisTotOrdIntegratedSquaredRBFTM_DerivativeChecks(
        CommonBasisTotOrdIntegratedSquaredRBFTTM,
        PrecompUni_TM_DerivativeChecks ):
    pass

    
def build_suite(ttype='all'):
    # Full order linear span
    suite_of_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_LinearSpanTM_DerivativeChecks )
    suite_pu_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_LinearSpanTM_DerivativeChecks )
    suite_pm_lstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_LinearSpanTM_DerivativeChecks )
    suite_of_cblstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisLinearSpanTM_DerivativeChecks )
    suite_pu_cblstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisLinearSpanTM_DerivativeChecks )
    # Total order linear span
    suite_of_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdLinearSpanTM_DerivativeChecks )
    suite_pu_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdLinearSpanTM_DerivativeChecks )
    suite_pm_tolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdLinearSpanTM_DerivativeChecks )
    suite_of_cbtolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdLinearSpanTM_DerivativeChecks )
    suite_pu_cbtolstm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdLinearSpanTM_DerivativeChecks )
    # Full order integrated exponential
    suite_of_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedExponentialTM_DerivativeChecks )
    suite_pu_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedExponentialTM_DerivativeChecks )
    suite_pm_ietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedExponentialTM_DerivativeChecks )
    suite_of_cbietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisIntegratedExponentialTM_DerivativeChecks )
    suite_pu_cbietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisIntegratedExponentialTM_DerivativeChecks )
    # Total order integrated exponential
    suite_of_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pu_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pm_toietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_of_cbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    suite_pu_cbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # Inverse integrated exponential
    suite_of_icbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_InverseCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # Composite integrated exponential
    suite_of_ccbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # List composite integrated exponential
    suite_of_lccbtoietm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_ListCompositeCommonBasisTotOrdIntegratedExponentialTM_DerivativeChecks )
    # Full order integrated squared
    suite_of_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedSquaredTM_DerivativeChecks )
    suite_pu_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedSquaredTM_DerivativeChecks )
    suite_pm_istm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedSquaredTM_DerivativeChecks )
    suite_of_cbistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisIntegratedSquaredTM_DerivativeChecks )
    suite_pu_cbistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisIntegratedSquaredTM_DerivativeChecks )
    # Total order integrated squared
    suite_of_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_pu_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_pm_toistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_of_cbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )
    suite_pu_cbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )
    # Inverse integrated squared
    suite_of_icbtoistm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_InverseCommonBasisTotOrdIntegratedSquaredTM_DerivativeChecks )
    # Full order integrated squared rbf
    suite_of_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_IntegratedSquaredRBFTM_DerivativeChecks )
    suite_pu_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_IntegratedSquaredRBFTM_DerivativeChecks )
    suite_pm_isrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_IntegratedSquaredRBFTM_DerivativeChecks )
    suite_of_cbisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks )
    suite_pu_cbisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisIntegratedSquaredRBFTM_DerivativeChecks )
    # Total order integrated squared rbf
    suite_of_toisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_TotOrdIntegratedSquaredRBFTM_DerivativeChecks )
    suite_pu_toisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_TotOrdIntegratedSquaredRBFTM_DerivativeChecks )
    suite_pm_toisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompMulti_TotOrdIntegratedSquaredRBFTM_DerivativeChecks )
    suite_of_cbtoisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_CommonBasisTotOrdIntegratedSquaredRBFTM_DerivativeChecks )
    suite_pu_cbtoisrbftm_dc = unittest.TestLoader().loadTestsFromTestCase(
        PrecompUni_CommonBasisTotOrdIntegratedSquaredRBFTM_DerivativeChecks )
    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [
            # Linear span
            suite_of_lstm_dc, suite_pu_lstm_dc, suite_pm_lstm_dc,
            suite_of_cblstm_dc, suite_pu_cblstm_dc,
            suite_of_tolstm_dc, suite_pu_tolstm_dc, suite_pm_tolstm_dc,
            suite_of_cbtolstm_dc, suite_pu_cbtolstm_dc,

            # Integrated exponential
            suite_of_ietm_dc, suite_pu_ietm_dc, suite_pm_ietm_dc,
            suite_of_cbietm_dc, suite_pu_cbietm_dc,
            suite_of_toietm_dc, suite_pu_toietm_dc, suite_pm_toietm_dc,
            suite_of_cbtoietm_dc, suite_pu_cbtoietm_dc,
            suite_of_icbtoietm_dc,
            suite_of_ccbtoietm_dc,
            suite_of_lccbtoietm_dc,

            # Integrated squared
            suite_of_istm_dc, suite_pu_istm_dc, suite_pm_istm_dc,
            # suite_of_cbistm_dc, suite_pu_cbistm_dc,
            suite_of_toistm_dc, suite_pu_toistm_dc, suite_pm_toistm_dc,
            # suite_of_cbtoistm_dc, suite_pu_cbtoistm_dc,
            # suite_of_icbtoistm_dc

            # Integrated squared rbf
            suite_of_isrbftm_dc, suite_pu_isrbftm_dc, suite_pm_isrbftm_dc,
            # suite_of_cbisrbftm_dc, suite_pu_cbisrbftm_dc,
            suite_of_toisrbftm_dc, suite_pu_toisrbftm_dc, suite_pm_toisrbftm_dc,
            # suite_of_cbtoisrbftm_dc, suite_pu_cbtoisrbftm_dc,
        ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
