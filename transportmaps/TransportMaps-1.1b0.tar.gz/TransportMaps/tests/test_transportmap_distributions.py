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

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class TransportMapDistribution_DerivativeChecks(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.fd_eps = 1e-4

    def test_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        params = {}
        params['params_pi'] = None
        params['x'] = self.x

        def pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.pdf(x, params_pi)
            return out

        def log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.log_pdf(x, params_pi)
            return out

        # Check log_pdf = log(pdf)
        maxerr = np.max( np.abs( pdf(coeffs, params) - np.exp(log_pdf(coeffs, params)) ) )
        self.assertTrue( maxerr <= 1e-10 )

    def test_grad_a_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        params = {}
        params['params_pi'] = None
        params['x'] = self.x

        def log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.log_pdf(x, params_pi)
            return out

        def grad_a_log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.grad_a_log_pdf(x, params_pi)
            return out

        flag = FD.check_grad_a(log_pdf, grad_a_log_pdf, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_tuple_grad_a_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        params = {}
        params['params_pi'] = None
        params['x'] = self.x

        def log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out,_ = d.tuple_grad_a_log_pdf(x, params_pi)
            return out

        def grad_a_log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            _, out = d.tuple_grad_a_log_pdf(x, params_pi)
            return out

        flag = FD.check_grad_a(log_pdf, grad_a_log_pdf, coeffs, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )


    def test_hess_a_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        params = {}
        params['params_pi'] = None
        params['x'] = self.x

        def grad_a_log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.grad_a_log_pdf(x, params_pi)
            return out

        def hess_a_log_pdf(a, params):
            d.coeffs = a
            x = params['x']
            params_pi = params['params_pi']
            out = d.hess_a_log_pdf(x, params_pi)
            return out    

        flag = FD.check_hess_a_from_grad_a(grad_a_log_pdf,
                                           hess_a_log_pdf, coeffs,
                                           self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

    def test_grad_x_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        d.coeffs = coeffs
        params = {}
        params['params_pi'] = None

        def log_pdf(x, params):
            params_pi = params['params_pi']
            out = d.log_pdf(x, params_pi)
            return out

        def grad_x_log_pdf(x, params):
            params_pi = params['params_pi']
            out = d.grad_x_log_pdf(x, params_pi)
            return out

        flag = FD.check_grad_x(log_pdf, grad_x_log_pdf, self.x, self.fd_eps,
                               params, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_log_pdf(self):
        import TransportMaps.FiniteDifference as FD

        d = self.distribution
        coeffs = self.coeffs
        d.coeffs = coeffs
        params = {}
        params['params_pi'] = None

        def grad_x_log_pdf(x, params):
            params_pi = params['params_pi']
            out = d.grad_x_log_pdf(x, params_pi)
            return out

        def hess_x_log_pdf(x, params):
            params_pi = params['params_pi']
            out = d.hess_x_log_pdf(x, params_pi)
            return out

        flag = FD.check_hess_x_from_grad_x(grad_x_log_pdf, hess_x_log_pdf,
                                           self.x, self.fd_eps,
                                           params, verbose=False)
        self.assertTrue( flag )

class PullBackTMD_DerivativeChecks(TransportMapDistribution_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PullBackTransportMapDistribution( self.tm_approx,
                                                         self.distribution_pi )
        super(PullBackTMD_DerivativeChecks,self).setUp()

class PushForwardTMD_DerivativeChecks(TransportMapDistribution_DerivativeChecks):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PushForwardTransportMapDistribution( self.tm_approx,
                                                            self.distribution_pi )
        super(PushForwardTMD_DerivativeChecks,self).setUp()

    @unittest.skip("Not Implemented")
    def test_tuple_grad_a_log_pdf(self):
        pass
        
    @unittest.skip("Not Implemented")
    def test_hess_a_log_pdf(self):
        pass

    @unittest.skip("Not Implemented")
    def test_grad_x_log_pdf(self):
        pass

    @unittest.skip("Not Implemented")
    def test_hess_x_log_pdf(self):
        pass

class IntegratedExponential:
    def setUpApprox(self):
        import numpy.random as npr
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
        self.coeffs = np.zeros( self.tm_approx.n_coeffs )
        # self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 100.

class IntegratedExponentialPBTMD_DerivativeChecks(IntegratedExponential,
                                                  PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(IntegratedExponentialPBTMD_DerivativeChecks, self).setUpApprox()
        super(IntegratedExponentialPBTMD_DerivativeChecks, self).setUp()

class IntegratedExponentialPFTMD_DerivativeChecks(IntegratedExponential,
                                                  PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(IntegratedExponentialPFTMD_DerivativeChecks, self).setUpApprox()
        super(IntegratedExponentialPFTMD_DerivativeChecks, self).setUp()

class CommonBasisIntegratedExponential:
    def setUpApprox(self):
        import numpy.random as npr
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction() for i in range(self.dim)]
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
        self.coeffs = np.zeros( self.tm_approx.n_coeffs )
        # self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 100. 

class CommonBasisIntegratedExponentialPBTMD_DerivativeChecks(CommonBasisIntegratedExponential,
                                                             PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(CommonBasisIntegratedExponentialPBTMD_DerivativeChecks, self).setUpApprox()
        super(CommonBasisIntegratedExponentialPBTMD_DerivativeChecks, self).setUp()

class CommonBasisIntegratedExponentialPFTMD_DerivativeChecks(CommonBasisIntegratedExponential,
                                                             PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(CommonBasisIntegratedExponentialPFTMD_DerivativeChecks, self).setUpApprox()
        super(CommonBasisIntegratedExponentialPFTMD_DerivativeChecks, self).setUp()

class TotOrdIntegratedExponential:
    def setUpApprox(self):
        import numpy.random as npr
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
            c_approx = FUNC.LinearSpanApproximation(c_basis_list, spantype='total',
                                                             order_list=c_orders_list)
            e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * (i+1)
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
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        # self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 100.

class TotOrdIntegratedExponentialPBTMD_DerivativeChecks(TotOrdIntegratedExponential,
                                                        PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(TotOrdIntegratedExponentialPBTMD_DerivativeChecks, self).setUpApprox()
        super(TotOrdIntegratedExponentialPBTMD_DerivativeChecks, self).setUp()

class TotOrdIntegratedExponentialPFTMD_DerivativeChecks(TotOrdIntegratedExponential,
                                                        PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(TotOrdIntegratedExponentialPFTMD_DerivativeChecks, self).setUpApprox()
        super(TotOrdIntegratedExponentialPFTMD_DerivativeChecks, self).setUp()

class CommonBasisTotOrdIntegratedExponential:
    def setUpApprox(self):
        import numpy.random as npr
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
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
            approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
            approx_list.append( approx )
            active_vars.append( range(i+1) )
        self.tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(active_vars,
                                                                                     approx_list)
        self.params = {}
        self.params['params_t'] = None
        self.coeffs = np.zeros(self.tm_approx.n_coeffs)
        # self.coeffs = npr.randn(self.tm_approx.n_coeffs) / 100.

class CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponential,
        PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks, self).setUpApprox()
        super(CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks, self).setUp()

class CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks(
        CommonBasisTotOrdIntegratedExponential,
        PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks, self).setUpApprox()
        super(CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks, self).setUp()

class IntegratedSquared:
    def setUpApprox(self):
        import numpy.random as npr
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
            # coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            # coeffs.append( npr.random(approx.h.n_coeffs) )
            coeffs.append( npr.randn(approx.c.n_coeffs) / 10. )
            h_coeffs = npr.randn(approx.h.n_coeffs) / 10.
            midx = approx.h.get_multi_idxs()
            idx0 = midx.index( tuple([0]*approx.dim) )
            h_coeffs[idx0] += 1.
            coeffs.append( h_coeffs )
        self.coeffs = np.hstack(coeffs)

class IntegratedSquaredPBTMD_DerivativeChecks(IntegratedSquared,
                                              PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(IntegratedSquaredPBTMD_DerivativeChecks, self).setUpApprox()
        super(IntegratedSquaredPBTMD_DerivativeChecks, self).setUp()

class IntegratedSquaredPFTMD_DerivativeChecks(IntegratedSquared,
                                              PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(IntegratedSquaredPFTMD_DerivativeChecks, self).setUpApprox()
        super(IntegratedSquaredPFTMD_DerivativeChecks, self).setUp()

class TotOrdIntegratedSquared:
    def setUpApprox(self):
        import numpy.random as npr
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
            # coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            # coeffs.append( npr.random(approx.h.n_coeffs) )
            coeffs.append( npr.randn(approx.c.n_coeffs) / 10. )
            h_coeffs = npr.randn(approx.h.n_coeffs) / 10.
            midx = approx.h.get_multi_idxs()
            idx0 = midx.index( tuple([0]*approx.dim) )
            h_coeffs[idx0] += 1.
            coeffs.append( h_coeffs )
        self.coeffs = np.hstack(coeffs)

class TotOrdIntegratedSquaredPBTMD_DerivativeChecks(TotOrdIntegratedSquared,
                                                    PullBackTMD_DerivativeChecks):
    def setUp(self):
        super(TotOrdIntegratedSquaredPBTMD_DerivativeChecks, self).setUpApprox()
        super(TotOrdIntegratedSquaredPBTMD_DerivativeChecks, self).setUp()

class TotOrdIntegratedSquaredPFTMD_DerivativeChecks(TotOrdIntegratedSquared,
                                                    PushForwardTMD_DerivativeChecks):
    def setUp(self):
        super(TotOrdIntegratedSquaredPFTMD_DerivativeChecks, self).setUpApprox()
        super(TotOrdIntegratedSquaredPFTMD_DerivativeChecks, self).setUp()
        
class LinearSpanPBTMD_DerivativeChecks(PullBackTMD_DerivativeChecks):

    def setUp(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
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
        self.coeffs[1] = 1.
        idx = (self.order+1)
        for d in range(2,self.dim+1):
            self.coeffs[ idx + 1 ] = 1.
            idx += (self.order+1)**d
        super(LinearSpanPBTMD_DerivativeChecks, self).setUp()

class CommonBasisLinearSpanPBTMD_DerivativeChecks(PullBackTMD_DerivativeChecks):

    def setUp(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
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
        self.coeffs[1] = 1.
        idx = (self.order+1)
        for d in range(2,self.dim+1):
            self.coeffs[ idx + 1 ] = 1.
            idx += (self.order+1)**d
        super(CommonBasisLinearSpanPBTMD_DerivativeChecks, self).setUp()

class TMD_TestCase(object):

    def setUp_test_case(self):
        import TransportMaps.Distributions as DIST
        self.dim = self.setup['dim']
        self.target_distribution = self.Tparams['target_distribution']
        self.support_map = self.Tparams['support_map']
        self.distribution_pi = DIST.PullBackTransportMapDistribution( self.support_map,
                                                            self.target_distribution )
        self.base_distribution = self.Tparams['base_distribution']
        self.qtype = 0
        self.qparams = 5
        (self.x, self.w) = self.base_distribution.quadrature(self.qtype, self.qparams)

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

# INTEGRATED EXPONENTIAL PULLBACK
class Linear1D_IEPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_IEPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_IEPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_IEPBTMD_DerivativeChecks,self).setUp()

class Exp1D_IEPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_IEPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_IEPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_IEPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_IEPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_IEPBTMD_DerivativeChecks,self).setUp()

class Beta1D_IEPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_IEPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_IEPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_IEPBTMD_DerivativeChecks,self).setUp()

class Linear2D_IEPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_IEPBTMD_DerivativeChecks,self).setUp()

class Banana2D_IEPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        IntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_IEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_IEPBTMD_DerivativeChecks,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PULLBACK
class Linear1D_CBIEPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_CBIEPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Exp1D_CBIEPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                       CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_CBIEPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                            CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_CBIEPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                         CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Beta1D_CBIEPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                        CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_CBIEPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Linear2D_CBIEPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_CBIEPBTMD_DerivativeChecks,self).setUp()

class Banana2D_CBIEPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_CBIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_CBIEPBTMD_DerivativeChecks,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Linear1D_TOIEPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_TOIEPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Exp1D_TOIEPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_TOIEPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_TOIEPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Beta1D_TOIEPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_TOIEPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Linear2D_TOIEPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_TOIEPBTMD_DerivativeChecks,self).setUp()

class Banana2D_TOIEPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_TOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_TOIEPBTMD_DerivativeChecks,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Linear1D_CBTOIEPBTMD_DerivativeChecks(
        Linear1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_CBTOIEPBTMD_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Exp1D_CBTOIEPBTMD_DerivativeChecks(
        Exp1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_CBTOIEPBTMD_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_CBTOIEPBTMD_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Beta1D_CBTOIEPBTMD_DerivativeChecks(
        Beta1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_CBTOIEPBTMD_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Linear2D_CBTOIEPBTMD_DerivativeChecks(
        Linear2D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

class Banana2D_CBTOIEPBTMD_DerivativeChecks(
        Banana2D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_CBTOIEPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_CBTOIEPBTMD_DerivativeChecks,self).setUp()

# INTEGRATED EXPONENTIAL PUSHFORWARD
class Linear1D_IEPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_IEPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_IEPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_IEPFTMD_DerivativeChecks,self).setUp()

class Exp1D_IEPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_IEPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_IEPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_IEPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_IEPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_IEPFTMD_DerivativeChecks,self).setUp()

class Beta1D_IEPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_IEPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_IEPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_IEPFTMD_DerivativeChecks,self).setUp()

class Linear2D_IEPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_IEPFTMD_DerivativeChecks,self).setUp()

class Banana2D_IEPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        IntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_IEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_IEPFTMD_DerivativeChecks,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PUSHFORWARD
class Linear1D_CBIEPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_CBIEPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Exp1D_CBIEPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                       CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_CBIEPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                            CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_CBIEPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                         CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Beta1D_CBIEPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                        CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_CBIEPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Linear2D_CBIEPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_CBIEPFTMD_DerivativeChecks,self).setUp()

class Banana2D_CBIEPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                          CommonBasisIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_CBIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_CBIEPFTMD_DerivativeChecks,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Linear1D_TOIEPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_TOIEPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Exp1D_TOIEPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_TOIEPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_TOIEPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Beta1D_TOIEPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_TOIEPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Linear2D_TOIEPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_TOIEPFTMD_DerivativeChecks,self).setUp()

class Banana2D_TOIEPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        TotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_TOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_TOIEPFTMD_DerivativeChecks,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Linear1D_CBTOIEPFTMD_DerivativeChecks(
        Linear1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_CBTOIEPFTMD_DerivativeChecks(
        ArcTan1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Exp1D_CBTOIEPFTMD_DerivativeChecks(
        Exp1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_CBTOIEPFTMD_DerivativeChecks(
        Logistic1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_CBTOIEPFTMD_DerivativeChecks(
        Gamma1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Beta1D_CBTOIEPFTMD_DerivativeChecks(
        Beta1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_CBTOIEPFTMD_DerivativeChecks(
        Gumbel1D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Linear2D_CBTOIEPFTMD_DerivativeChecks(
        Linear2D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

class Banana2D_CBTOIEPFTMD_DerivativeChecks(
        Banana2D_TMD_TestCase,
        CommonBasisTotOrdIntegratedExponentialPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_CBTOIEPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_CBTOIEPFTMD_DerivativeChecks,self).setUp()

# INTEGRATED SQUARED PULLBACK
class Linear1D_ISPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ISPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_ISPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ISPBTMD_DerivativeChecks,self).setUp()

class Exp1D_ISPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ISPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_ISPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ISPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_ISPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ISPBTMD_DerivativeChecks,self).setUp()

class Beta1D_ISPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ISPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_ISPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ISPBTMD_DerivativeChecks,self).setUp()

class Linear2D_ISPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ISPBTMD_DerivativeChecks,self).setUp()

class Banana2D_ISPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        IntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ISPBTMD_DerivativeChecks,self).setUp()

# # COMMON BASIS INTEGRATED SQUARED PULLBACK
# class Linear1D_CBISPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class ArcTan1D_CBISPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(ArcTan1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(ArcTan1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Exp1D_CBISPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
#                                        CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Exp1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Exp1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Logistic1D_CBISPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
#                                             CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Logistic1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Logistic1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Gamma1D_CBISPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
#                                          CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gamma1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gamma1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Beta1D_CBISPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
#                                         CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Beta1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Beta1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Gumbel1D_CBISPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gumbel1D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gumbel1D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Linear2D_CBISPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear2D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear2D_CBISPBTMD_DerivativeChecks,self).setUp()

# class Banana2D_CBISPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Banana2D_CBISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Banana2D_CBISPBTMD_DerivativeChecks,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PULLBACK
class Linear1D_TOISPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_TOISPBTMD_DerivativeChecks,self).setUp()

class ArcTan1D_TOISPBTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Exp1D_TOISPBTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Logistic1D_TOISPBTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Gamma1D_TOISPBTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Beta1D_TOISPBTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Gumbel1D_TOISPBTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_TOISPBTMD_DerivativeChecks,self).setUp()

class Linear2D_TOISPBTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_TOISPBTMD_DerivativeChecks,self).setUp()

class Banana2D_TOISPBTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPBTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_TOISPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_TOISPBTMD_DerivativeChecks,self).setUp()

# # COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PULLBACK
# class Linear1D_CBTOISPBTMD_DerivativeChecks(
#         Linear1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class ArcTan1D_CBTOISPBTMD_DerivativeChecks(
#         ArcTan1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(ArcTan1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(ArcTan1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Exp1D_CBTOISPBTMD_DerivativeChecks(
#         Exp1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Exp1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Exp1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Logistic1D_CBTOISPBTMD_DerivativeChecks(
#         Logistic1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Logistic1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Logistic1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Gamma1D_CBTOISPBTMD_DerivativeChecks(
#         Gamma1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gamma1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gamma1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Beta1D_CBTOISPBTMD_DerivativeChecks(
#         Beta1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Beta1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Beta1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Gumbel1D_CBTOISPBTMD_DerivativeChecks(
#         Gumbel1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gumbel1D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gumbel1D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Linear2D_CBTOISPBTMD_DerivativeChecks(
#         Linear2D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear2D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear2D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# class Banana2D_CBTOISPBTMD_DerivativeChecks(
#         Banana2D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPBTMD_DerivativeChecks):
#     def setUp(self):
#         super(Banana2D_CBTOISPBTMD_DerivativeChecks,self).setUp_test_case()
#         super(Banana2D_CBTOISPBTMD_DerivativeChecks,self).setUp()

# INTEGRATED SQUARED PUSHFORWARD
class Linear1D_ISPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_ISPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_ISPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_ISPFTMD_DerivativeChecks,self).setUp()

class Exp1D_ISPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_ISPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_ISPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_ISPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_ISPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_ISPFTMD_DerivativeChecks,self).setUp()

class Beta1D_ISPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_ISPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_ISPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_ISPFTMD_DerivativeChecks,self).setUp()

class Linear2D_ISPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_ISPFTMD_DerivativeChecks,self).setUp()

class Banana2D_ISPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        IntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_ISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_ISPFTMD_DerivativeChecks,self).setUp()

# # COMMON BASIS INTEGRATED SQUARED PUSHFORWARD
# class Linear1D_CBISPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class ArcTan1D_CBISPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(ArcTan1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(ArcTan1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Exp1D_CBISPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
#                                        CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Exp1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Exp1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Logistic1D_CBISPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
#                                             CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Logistic1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Logistic1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Gamma1D_CBISPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
#                                          CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gamma1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gamma1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Beta1D_CBISPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
#                                         CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Beta1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Beta1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Gumbel1D_CBISPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gumbel1D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gumbel1D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Linear2D_CBISPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear2D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear2D_CBISPFTMD_DerivativeChecks,self).setUp()

# class Banana2D_CBISPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
#                                           CommonBasisIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Banana2D_CBISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Banana2D_CBISPFTMD_DerivativeChecks,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
class Linear1D_TOISPFTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_TOISPFTMD_DerivativeChecks,self).setUp()

class ArcTan1D_TOISPFTMD_DerivativeChecks(ArcTan1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(ArcTan1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(ArcTan1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Exp1D_TOISPFTMD_DerivativeChecks(Exp1D_TMD_TestCase,
                                     TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Exp1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Exp1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Logistic1D_TOISPFTMD_DerivativeChecks(Logistic1D_TMD_TestCase,
                                          TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Logistic1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Logistic1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Gamma1D_TOISPFTMD_DerivativeChecks(Gamma1D_TMD_TestCase,
                                       TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gamma1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gamma1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Beta1D_TOISPFTMD_DerivativeChecks(Beta1D_TMD_TestCase,
                                      TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Beta1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Beta1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Gumbel1D_TOISPFTMD_DerivativeChecks(Gumbel1D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Gumbel1D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Gumbel1D_TOISPFTMD_DerivativeChecks,self).setUp()

class Linear2D_TOISPFTMD_DerivativeChecks(Linear2D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Linear2D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear2D_TOISPFTMD_DerivativeChecks,self).setUp()

class Banana2D_TOISPFTMD_DerivativeChecks(Banana2D_TMD_TestCase,
                                        TotOrdIntegratedSquaredPFTMD_DerivativeChecks):
    def setUp(self):
        super(Banana2D_TOISPFTMD_DerivativeChecks,self).setUp_test_case()
        super(Banana2D_TOISPFTMD_DerivativeChecks,self).setUp()

# # COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
# class Linear1D_CBTOISPFTMD_DerivativeChecks(
#         Linear1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class ArcTan1D_CBTOISPFTMD_DerivativeChecks(
#         ArcTan1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(ArcTan1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(ArcTan1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Exp1D_CBTOISPFTMD_DerivativeChecks(
#         Exp1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Exp1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Exp1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Logistic1D_CBTOISPFTMD_DerivativeChecks(
#         Logistic1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Logistic1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Logistic1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Gamma1D_CBTOISPFTMD_DerivativeChecks(
#         Gamma1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gamma1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gamma1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Beta1D_CBTOISPFTMD_DerivativeChecks(
#         Beta1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Beta1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Beta1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Gumbel1D_CBTOISPFTMD_DerivativeChecks(
#         Gumbel1D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Gumbel1D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Gumbel1D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Linear2D_CBTOISPFTMD_DerivativeChecks(
#         Linear2D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Linear2D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Linear2D_CBTOISPFTMD_DerivativeChecks,self).setUp()

# class Banana2D_CBTOISPFTMD_DerivativeChecks(
#         Banana2D_TMD_TestCase,
#         CommonBasisTotOrdIntegratedSquaredPFTMD_DerivativeChecks):
#     def setUp(self):
#         super(Banana2D_CBTOISPFTMD_DerivativeChecks,self).setUp_test_case()
#         super(Banana2D_CBTOISPFTMD_DerivativeChecks,self).setUp()

        
# LINEAR APPROXIMATIONS
class Linear1D_LSPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                        LinearSpanPBTMD_DerivativeChecks):

    def setUp(self):
        super(Linear1D_LSPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_LSPBTMD_DerivativeChecks,self).setUp()

class Linear1D_CBLSPBTMD_DerivativeChecks(Linear1D_TMD_TestCase,
                                          CommonBasisLinearSpanPBTMD_DerivativeChecks):

    def setUp(self):
        super(Linear1D_CBLSPBTMD_DerivativeChecks,self).setUp_test_case()
        super(Linear1D_CBLSPBTMD_DerivativeChecks,self).setUp()

def build_suite(ttype='all'):
    # Integrated exponential pullback
    suite_linear1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_IEPBTMD_DerivativeChecks )
    suite_arctan1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_IEPBTMD_DerivativeChecks )
    suite_exp1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_IEPBTMD_DerivativeChecks )
    suite_logistic1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_IEPBTMD_DerivativeChecks )
    suite_gamma1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_IEPBTMD_DerivativeChecks )
    suite_beta1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_IEPBTMD_DerivativeChecks )
    suite_gumbel1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_IEPBTMD_DerivativeChecks )
    suite_linear2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_IEPBTMD_DerivativeChecks )
    suite_banana2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_IEPBTMD_DerivativeChecks )
    # CommonBasis integrated exponential pullback
    suite_linear1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_CBIEPBTMD_DerivativeChecks )
    suite_arctan1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_CBIEPBTMD_DerivativeChecks )
    suite_exp1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_CBIEPBTMD_DerivativeChecks )
    suite_logistic1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_CBIEPBTMD_DerivativeChecks )
    suite_gamma1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_CBIEPBTMD_DerivativeChecks )
    suite_beta1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_CBIEPBTMD_DerivativeChecks )
    suite_gumbel1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_CBIEPBTMD_DerivativeChecks )
    suite_linear2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_CBIEPBTMD_DerivativeChecks )
    suite_banana2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_CBIEPBTMD_DerivativeChecks )
    # Total order integrated exponential pullback
    suite_linear1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_TOIEPBTMD_DerivativeChecks )
    suite_arctan1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_TOIEPBTMD_DerivativeChecks )
    suite_exp1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_TOIEPBTMD_DerivativeChecks )
    suite_logistic1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_TOIEPBTMD_DerivativeChecks )
    suite_gamma1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_TOIEPBTMD_DerivativeChecks )
    suite_beta1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_TOIEPBTMD_DerivativeChecks )
    suite_gumbel1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_TOIEPBTMD_DerivativeChecks )
    suite_linear2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_TOIEPBTMD_DerivativeChecks )
    suite_banana2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_TOIEPBTMD_DerivativeChecks )
    # Total order commonBasis integrated exponential pullback
    suite_linear1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_CBTOIEPBTMD_DerivativeChecks )
    suite_arctan1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_CBTOIEPBTMD_DerivativeChecks )
    suite_exp1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_CBTOIEPBTMD_DerivativeChecks )
    suite_logistic1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_CBTOIEPBTMD_DerivativeChecks )
    suite_gamma1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_CBTOIEPBTMD_DerivativeChecks )
    suite_beta1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_CBTOIEPBTMD_DerivativeChecks )
    suite_gumbel1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_CBTOIEPBTMD_DerivativeChecks )
    suite_linear2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_CBTOIEPBTMD_DerivativeChecks )
    suite_banana2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_CBTOIEPBTMD_DerivativeChecks )
    # Integrated exponential pushforward
    suite_linear1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_IEPFTMD_DerivativeChecks )
    suite_arctan1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_IEPFTMD_DerivativeChecks )
    suite_exp1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_IEPFTMD_DerivativeChecks )
    suite_logistic1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_IEPFTMD_DerivativeChecks )
    suite_gamma1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_IEPFTMD_DerivativeChecks )
    suite_beta1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_IEPFTMD_DerivativeChecks )
    suite_gumbel1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_IEPFTMD_DerivativeChecks )
    suite_linear2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_IEPFTMD_DerivativeChecks )
    suite_banana2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_IEPFTMD_DerivativeChecks )
    # CommonBasis integrated exponential pushforward
    suite_linear1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_CBIEPFTMD_DerivativeChecks )
    suite_arctan1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_CBIEPFTMD_DerivativeChecks )
    suite_exp1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_CBIEPFTMD_DerivativeChecks )
    suite_logistic1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_CBIEPFTMD_DerivativeChecks )
    suite_gamma1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_CBIEPFTMD_DerivativeChecks )
    suite_beta1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_CBIEPFTMD_DerivativeChecks )
    suite_gumbel1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_CBIEPFTMD_DerivativeChecks )
    suite_linear2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_CBIEPFTMD_DerivativeChecks )
    suite_banana2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_CBIEPFTMD_DerivativeChecks )
    # Total order integrated exponential pushforward
    suite_linear1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_TOIEPFTMD_DerivativeChecks )
    suite_arctan1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_TOIEPFTMD_DerivativeChecks )
    suite_exp1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_TOIEPFTMD_DerivativeChecks )
    suite_logistic1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_TOIEPFTMD_DerivativeChecks )
    suite_gamma1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_TOIEPFTMD_DerivativeChecks )
    suite_beta1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_TOIEPFTMD_DerivativeChecks )
    suite_gumbel1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_TOIEPFTMD_DerivativeChecks )
    suite_linear2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_TOIEPFTMD_DerivativeChecks )
    suite_banana2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_TOIEPFTMD_DerivativeChecks )
    # Total order commonBasis integrated exponential pushforward
    suite_linear1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_CBTOIEPFTMD_DerivativeChecks )
    suite_arctan1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_CBTOIEPFTMD_DerivativeChecks )
    suite_exp1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_CBTOIEPFTMD_DerivativeChecks )
    suite_logistic1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_CBTOIEPFTMD_DerivativeChecks )
    suite_gamma1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_CBTOIEPFTMD_DerivativeChecks )
    suite_beta1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_CBTOIEPFTMD_DerivativeChecks )
    suite_gumbel1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_CBTOIEPFTMD_DerivativeChecks )
    suite_linear2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_CBTOIEPFTMD_DerivativeChecks )
    suite_banana2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_CBTOIEPFTMD_DerivativeChecks )
    # Integrated squared pullback
    suite_linear1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ISPBTMD_DerivativeChecks )
    suite_arctan1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ISPBTMD_DerivativeChecks )
    suite_exp1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ISPBTMD_DerivativeChecks )
    suite_logistic1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ISPBTMD_DerivativeChecks )
    suite_gamma1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ISPBTMD_DerivativeChecks )
    suite_beta1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ISPBTMD_DerivativeChecks )
    suite_gumbel1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ISPBTMD_DerivativeChecks )
    suite_linear2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ISPBTMD_DerivativeChecks )
    suite_banana2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ISPBTMD_DerivativeChecks )
    # # Common basis integrated squared pullback
    # suite_linear1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear1D_CBISPBTMD_DerivativeChecks )
    # suite_arctan1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     ArcTan1D_CBISPBTMD_DerivativeChecks )
    # suite_exp1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Exp1D_CBISPBTMD_DerivativeChecks )
    # suite_logistic1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Logistic1D_CBISPBTMD_DerivativeChecks )
    # suite_gamma1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gamma1D_CBISPBTMD_DerivativeChecks )
    # suite_beta1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Beta1D_CBISPBTMD_DerivativeChecks )
    # suite_gumbel1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gumbel1D_CBISPBTMD_DerivativeChecks )
    # suite_linear2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear2D_CBISPBTMD_DerivativeChecks )
    # suite_banana2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Banana2D_CBISPBTMD_DerivativeChecks )
    # Total order integrated squared pullback
    suite_linear1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_TOISPBTMD_DerivativeChecks )
    suite_arctan1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_TOISPBTMD_DerivativeChecks )
    suite_exp1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_TOISPBTMD_DerivativeChecks )
    suite_logistic1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_TOISPBTMD_DerivativeChecks )
    suite_gamma1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_TOISPBTMD_DerivativeChecks )
    suite_beta1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_TOISPBTMD_DerivativeChecks )
    suite_gumbel1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_TOISPBTMD_DerivativeChecks )
    suite_linear2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_TOISPBTMD_DerivativeChecks )
    suite_banana2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_TOISPBTMD_DerivativeChecks )
    # # Total order commonBasis integrated squared pullback
    # suite_linear1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear1D_CBTOISPBTMD_DerivativeChecks )
    # suite_arctan1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     ArcTan1D_CBTOISPBTMD_DerivativeChecks )
    # suite_exp1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Exp1D_CBTOISPBTMD_DerivativeChecks )
    # suite_logistic1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Logistic1D_CBTOISPBTMD_DerivativeChecks )
    # suite_gamma1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gamma1D_CBTOISPBTMD_DerivativeChecks )
    # suite_beta1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Beta1D_CBTOISPBTMD_DerivativeChecks )
    # suite_gumbel1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gumbel1D_CBTOISPBTMD_DerivativeChecks )
    # suite_linear2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear2D_CBTOISPBTMD_DerivativeChecks )
    # suite_banana2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Banana2D_CBTOISPBTMD_DerivativeChecks )
    # Integrated squared pushforward
    suite_linear1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_ISPFTMD_DerivativeChecks )
    suite_arctan1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_ISPFTMD_DerivativeChecks )
    suite_exp1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_ISPFTMD_DerivativeChecks )
    suite_logistic1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_ISPFTMD_DerivativeChecks )
    suite_gamma1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_ISPFTMD_DerivativeChecks )
    suite_beta1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_ISPFTMD_DerivativeChecks )
    suite_gumbel1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_ISPFTMD_DerivativeChecks )
    suite_linear2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_ISPFTMD_DerivativeChecks )
    suite_banana2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_ISPFTMD_DerivativeChecks )
    # # CommonBasis integrated squared pushforward
    # suite_linear1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear1D_CBISPFTMD_DerivativeChecks )
    # suite_arctan1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     ArcTan1D_CBISPFTMD_DerivativeChecks )
    # suite_exp1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Exp1D_CBISPFTMD_DerivativeChecks )
    # suite_logistic1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Logistic1D_CBISPFTMD_DerivativeChecks )
    # suite_gamma1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gamma1D_CBISPFTMD_DerivativeChecks )
    # suite_beta1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Beta1D_CBISPFTMD_DerivativeChecks )
    # suite_gumbel1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gumbel1D_CBISPFTMD_DerivativeChecks )
    # suite_linear2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear2D_CBISPFTMD_DerivativeChecks )
    # suite_banana2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Banana2D_CBISPFTMD_DerivativeChecks )
    # Total order integrated squared pushforward
    suite_linear1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_TOISPFTMD_DerivativeChecks )
    suite_arctan1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_TOISPFTMD_DerivativeChecks )
    suite_exp1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_TOISPFTMD_DerivativeChecks )
    suite_logistic1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_TOISPFTMD_DerivativeChecks )
    suite_gamma1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_TOISPFTMD_DerivativeChecks )
    suite_beta1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_TOISPFTMD_DerivativeChecks )
    suite_gumbel1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_TOISPFTMD_DerivativeChecks )
    suite_linear2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_TOISPFTMD_DerivativeChecks )
    suite_banana2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_TOISPFTMD_DerivativeChecks )
    # # Total order commonBasis integrated squared pushforward
    # suite_linear1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear1D_CBTOISPFTMD_DerivativeChecks )
    # suite_arctan1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     ArcTan1D_CBTOISPFTMD_DerivativeChecks )
    # suite_exp1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Exp1D_CBTOISPFTMD_DerivativeChecks )
    # suite_logistic1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Logistic1D_CBTOISPFTMD_DerivativeChecks )
    # suite_gamma1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gamma1D_CBTOISPFTMD_DerivativeChecks )
    # suite_beta1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Beta1D_CBTOISPFTMD_DerivativeChecks )
    # suite_gumbel1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Gumbel1D_CBTOISPFTMD_DerivativeChecks )
    # suite_linear2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Linear2D_CBTOISPFTMD_DerivativeChecks )
    # suite_banana2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
    #     Banana2D_CBTOISPFTMD_DerivativeChecks )
    
    # Linear Span
    suite_linear1d_lspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_LSPBTMD_DerivativeChecks )
    suite_linear1d_cblspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_CBLSPBTMD_DerivativeChecks )

    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [
            # Integrated exponential pullback
            suite_linear1d_iepbtmd, suite_arctan1d_iepbtmd, suite_exp1d_iepbtmd,
            suite_logistic1d_iepbtmd, suite_gamma1d_iepbtmd, suite_beta1d_iepbtmd,
            suite_gumbel1d_iepbtmd, suite_linear2d_iepbtmd,
            suite_banana2d_iepbtmd,
            # Common basis integrated exponential pullback
            suite_linear1d_cbiepbtmd, suite_arctan1d_cbiepbtmd, suite_exp1d_cbiepbtmd,
            suite_logistic1d_cbiepbtmd, suite_gamma1d_cbiepbtmd, suite_beta1d_cbiepbtmd,
            suite_gumbel1d_cbiepbtmd, suite_linear2d_cbiepbtmd, suite_banana2d_cbiepbtmd,
            # Total order integrated exponential pullback
            suite_linear1d_toiepbtmd, suite_arctan1d_toiepbtmd, suite_exp1d_toiepbtmd,
            suite_logistic1d_toiepbtmd, suite_gamma1d_toiepbtmd, suite_beta1d_toiepbtmd,
            suite_gumbel1d_toiepbtmd, suite_linear2d_toiepbtmd, suite_banana2d_toiepbtmd,
            # Common basis total order integrated exponential pullback
            suite_linear1d_cbtoiepbtmd, suite_arctan1d_cbtoiepbtmd, suite_exp1d_cbtoiepbtmd,
            suite_logistic1d_cbtoiepbtmd, suite_gamma1d_cbtoiepbtmd,
            suite_beta1d_cbtoiepbtmd,
            suite_gumbel1d_cbtoiepbtmd, suite_linear2d_cbtoiepbtmd,
            suite_banana2d_cbtoiepbtmd,
            # Integrated exponential pushforward
            suite_linear1d_iepftmd, suite_arctan1d_iepftmd, suite_exp1d_iepftmd,
            suite_logistic1d_iepftmd, suite_gamma1d_iepftmd, suite_beta1d_iepftmd,
            suite_gumbel1d_iepftmd, suite_linear2d_iepftmd, suite_banana2d_iepftmd,
            # Common basis integrated exponential pushforward
            suite_linear1d_cbiepftmd, suite_arctan1d_cbiepftmd, suite_exp1d_cbiepftmd,
            suite_logistic1d_cbiepftmd, suite_gamma1d_cbiepftmd, suite_beta1d_cbiepftmd,
            suite_gumbel1d_cbiepftmd, suite_linear2d_cbiepftmd, suite_banana2d_cbiepftmd,
            # Total order integrated exponential pushforward
            suite_linear1d_toiepftmd, suite_arctan1d_toiepftmd, suite_exp1d_toiepftmd,
            suite_logistic1d_toiepftmd, suite_gamma1d_toiepftmd, suite_beta1d_toiepftmd,
            suite_gumbel1d_toiepftmd, suite_linear2d_toiepftmd, suite_banana2d_toiepftmd,
            # Common basis total order integrated exponential pushforward
            suite_linear1d_cbtoiepftmd, suite_arctan1d_cbtoiepftmd, suite_exp1d_cbtoiepftmd,
            suite_logistic1d_cbtoiepftmd, suite_gamma1d_cbtoiepftmd,
            suite_beta1d_cbtoiepftmd,
            suite_gumbel1d_cbtoiepftmd, suite_linear2d_cbtoiepftmd,
            suite_banana2d_cbtoiepftmd,

            # INTEGRATED SQUARED PULLBACK
            suite_linear1d_ispbtmd, suite_arctan1d_ispbtmd, suite_exp1d_ispbtmd,
            suite_logistic1d_ispbtmd, suite_gamma1d_ispbtmd, suite_beta1d_ispbtmd,
            suite_gumbel1d_ispbtmd, suite_linear2d_ispbtmd,
            suite_banana2d_ispbtmd,
            # # COMMON BASIS INTEGRATED SQUARED PULLBACK
            # suite_linear1d_cbispbtmd, suite_arctan1d_cbispbtmd, suite_exp1d_cbispbtmd,
            # suite_logistic1d_cbispbtmd, suite_gamma1d_cbispbtmd, suite_beta1d_cbispbtmd,
            # suite_gumbel1d_cbispbtmd, suite_linear2d_cbispbtmd, suite_banana2d_cbispbtmd,
            # TOTAL ORDER INTEGRATED SQUARED PULLBACK
            suite_linear1d_toispbtmd, suite_arctan1d_toispbtmd, suite_exp1d_toispbtmd,
            suite_logistic1d_toispbtmd, suite_gamma1d_toispbtmd, suite_beta1d_toispbtmd,
            suite_gumbel1d_toispbtmd, suite_linear2d_toispbtmd, suite_banana2d_toispbtmd,
            # # COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PULLBACK
            # suite_linear1d_cbtoispbtmd, suite_arctan1d_cbtoispbtmd, suite_exp1d_cbtoispbtmd,
            # suite_logistic1d_cbtoispbtmd, suite_gamma1d_cbtoispbtmd,
            # suite_beta1d_cbtoispbtmd,
            # suite_gumbel1d_cbtoispbtmd, suite_linear2d_cbtoispbtmd,
            # suite_banana2d_cbtoispbtmd,
            # INTEGRATED SQUARED PUSHFORWARD
            suite_linear1d_ispftmd, suite_arctan1d_ispftmd, suite_exp1d_ispftmd,
            suite_logistic1d_ispftmd, suite_gamma1d_ispftmd, suite_beta1d_ispftmd,
            suite_gumbel1d_ispftmd, suite_linear2d_ispftmd, suite_banana2d_ispftmd,
            # # COMMON BASIS INTEGRATED SQUARED PUSHFORWARD
            # suite_linear1d_cbispftmd, suite_arctan1d_cbispftmd, suite_exp1d_cbispftmd,
            # suite_logistic1d_cbispftmd, suite_gamma1d_cbispftmd, suite_beta1d_cbispftmd,
            # suite_gumbel1d_cbispftmd, suite_linear2d_cbispftmd, suite_banana2d_cbispftmd,
            # TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
            suite_linear1d_toispftmd, suite_arctan1d_toispftmd, suite_exp1d_toispftmd,
            suite_logistic1d_toispftmd, suite_gamma1d_toispftmd, suite_beta1d_toispftmd,
            suite_gumbel1d_toispftmd, suite_linear2d_toispftmd, suite_banana2d_toispftmd,
            # # COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
            # suite_linear1d_cbtoispftmd, suite_arctan1d_cbtoispftmd, suite_exp1d_cbtoispftmd,
            # suite_logistic1d_cbtoispftmd, suite_gamma1d_cbtoispftmd,
            # suite_beta1d_cbtoispftmd,
            # suite_gumbel1d_cbtoispftmd, suite_linear2d_cbtoispftmd,
            # suite_banana2d_cbtoispftmd

            # LINEAR SPAN PULLBACK
            suite_linear1d_lspbtmd, suite_linear1d_cblspbtmd,
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
