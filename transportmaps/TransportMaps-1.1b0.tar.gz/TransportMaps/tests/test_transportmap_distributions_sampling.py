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

class TransportMapDistribution_SamplingCheck(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.nmc = 11
        self.nquad = 5
        self.nprocs = 1

    def test_rvs(self):
        # Check only for errors
        d = self.distribution
        coeffs = self.coeffs
        d.coeffs = coeffs
        d.rvs(self.nmc, mpi_pool=self.mpi_pool)

    def test_quadrature(self):
        # Check only for errors
        d = self.distribution
        coeffs = self.coeffs
        d.coeffs = coeffs
        d.quadrature(qtype=3, qparams=[self.nquad]*d.dim,
                     mpi_pool=self.mpi_pool)

class PullBackTMD_SamplingCheck(TransportMapDistribution_SamplingCheck):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PullBackTransportMapDistribution( self.tm_approx,
                                                         self.distribution_pi )
        super(PullBackTMD_SamplingCheck,self).setUp()

class PushForwardTMD_SamplingCheck(TransportMapDistribution_SamplingCheck):
    def setUp(self):
        import TransportMaps.Distributions as DIST
        self.distribution = DIST.PushForwardTransportMapDistribution( self.tm_approx,
                                                            self.distribution_pi )
        super(PushForwardTMD_SamplingCheck,self).setUp()

#
# Serial test cases
#
class Serial_PBTMD_SamplingCheck(PullBackTMD_SamplingCheck):
    def setUp(self):
        super(Serial_PBTMD_SamplingCheck,self).setUp()
        self.mpi_pool = None

class Serial_PFTMD_SamplingCheck(PushForwardTMD_SamplingCheck):
    def setUp(self):
        super(Serial_PFTMD_SamplingCheck,self).setUp()
        self.mpi_pool = None

#
# Parallel test cases
#
class Parallel_PBTMD_SamplingCheck(PullBackTMD_SamplingCheck):
    def setUp(self):
        import TransportMaps as TM
        super(Parallel_PBTMD_SamplingCheck,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)

class Parallel_PFTMD_SamplingCheck(PushForwardTMD_SamplingCheck):
    def setUp(self):
        import TransportMaps as TM
        super(Parallel_PFTMD_SamplingCheck,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)

#
# Approximations
#
class IntegratedExponential:
    def setUpApprox(self):
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

class Serial_IntegratedExponentialPBTMD_SamplingCheck(IntegratedExponential,
                                                      Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_IntegratedExponentialPBTMD_SamplingCheck, self).setUpApprox()
        super(Serial_IntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Serial_IntegratedExponentialPFTMD_SamplingCheck(IntegratedExponential,
                                                      Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_IntegratedExponentialPFTMD_SamplingCheck, self).setUpApprox()
        super(Serial_IntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class Parallel_IntegratedExponentialPBTMD_SamplingCheck(IntegratedExponential,
                                                        Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_IntegratedExponentialPBTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_IntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Parallel_IntegratedExponentialPFTMD_SamplingCheck(IntegratedExponential,
                                                        Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_IntegratedExponentialPFTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_IntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class CommonBasisIntegratedExponential:
    def setUpApprox(self):
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

class Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck(
        CommonBasisIntegratedExponential, Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck(
        CommonBasisIntegratedExponential, Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck(
        CommonBasisIntegratedExponential, Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck(
        CommonBasisIntegratedExponential, Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class TotOrdIntegratedExponential:
    def setUpApprox(self):
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

class Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck(
        TotOrdIntegratedExponential, Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck, self).setUpApprox()
        super(Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck(
        TotOrdIntegratedExponential, Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck, self).setUpApprox()
        super(Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck(
        TotOrdIntegratedExponential, Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck, self).setUp()

class Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck(
        TotOrdIntegratedExponential, Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck, self).setUp()

class CommonBasisTotOrdIntegratedExponential:
    def setUpApprox(self):
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

class Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedExponential,
        Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck,
              self).setUp()

class Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedExponential,
        Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck,
              self).setUp()

class Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedExponential,
        Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck,
              self).setUp()

class Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedExponential,
        Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck,
              self).setUp()

class IntegratedSquared:
    def setUpApprox(self):
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
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)

class Serial_IntegratedSquaredPBTMD_SamplingCheck(IntegratedSquared,
                                                      Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_IntegratedSquaredPBTMD_SamplingCheck, self).setUpApprox()
        super(Serial_IntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Serial_IntegratedSquaredPFTMD_SamplingCheck(IntegratedSquared,
                                                      Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_IntegratedSquaredPFTMD_SamplingCheck, self).setUpApprox()
        super(Serial_IntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class Parallel_IntegratedSquaredPBTMD_SamplingCheck(IntegratedSquared,
                                                        Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_IntegratedSquaredPBTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_IntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Parallel_IntegratedSquaredPFTMD_SamplingCheck(IntegratedSquared,
                                                        Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_IntegratedSquaredPFTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_IntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class CommonBasisIntegratedSquared:
    def setUpApprox(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
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
        coeffs = []
        for approx in self.tm_approx.approx_list:
            coeffs.append( npr.random(approx.c.n_coeffs)/10. )
            coeffs.append( npr.random(approx.h.n_coeffs) )
        self.coeffs = np.hstack(coeffs)
        
class Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck(
        CommonBasisIntegratedSquared, Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck(
        CommonBasisIntegratedSquared, Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck(
        CommonBasisIntegratedSquared, Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck(
        CommonBasisIntegratedSquared, Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class TotOrdIntegratedSquared:
    def setUpApprox(self):
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
            e_basis_list = [S1D.HermiteProbabilistsPolynomial()] * (i+1)
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

class Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck(
        TotOrdIntegratedSquared, Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck, self).setUpApprox()
        super(Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck(
        TotOrdIntegratedSquared, Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck, self).setUpApprox()
        super(Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck(
        TotOrdIntegratedSquared, Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck, self).setUp()

class Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck(
        TotOrdIntegratedSquared, Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck, self).setUpApprox()
        super(Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck, self).setUp()

class CommonBasisTotOrdIntegratedSquared:
    def setUpApprox(self):
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        import TransportMaps.Maps as MAPS
        # Build the transport map (isotropic for each entry)
        self.order = 5
        approx_list = []
        active_vars = []
        c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
        e_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(self.dim)]
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

class Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedSquared,
        Serial_PBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck,
              self).setUp()

class Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedSquared,
        Serial_PFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck,
              self).setUp()

class Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedSquared,
        Parallel_PBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck,
              self).setUp()

class Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck(
        CommonBasisTotOrdIntegratedSquared,
        Parallel_PFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck,
              self).setUpApprox()
        super(Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck,
              self).setUp()

        
class Serial_LinearSpanPBTMD_SamplingCheck(Serial_PBTMD_SamplingCheck):

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
        super(Serial_LinearSpanPBTMD_SamplingCheck, self).setUp()

class Serial_CommonBasisLinearSpanPBTMD_SamplingCheck(Serial_PBTMD_SamplingCheck):

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
        super(Serial_CommonBasisLinearSpanPBTMD_SamplingCheck, self).setUp()

class Parallel_LinearSpanPBTMD_SamplingCheck(Parallel_PBTMD_SamplingCheck):

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
        super(Parallel_LinearSpanPBTMD_SamplingCheck, self).setUp()

class Parallel_CommonBasisLinearSpanPBTMD_SamplingCheck(Parallel_PBTMD_SamplingCheck):

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
        super(Parallel_CommonBasisLinearSpanPBTMD_SamplingCheck, self).setUp()

#
# Test cases
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

#
# Serial test cases
# 

# INTEGRATED EXPONENTIAL PULLBACK
class Serial_Linear1D_IEPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                     Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_IEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_IEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_IEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_IEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_IEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_IEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_IEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_IEPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_IEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_IEPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PULLBACK
class Serial_Linear1D_CBIEPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase, Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBIEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBIEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBIEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBIEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBIEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBIEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBIEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBIEPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBIEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBIEPBTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Serial_Linear1D_TOIEPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_TOIEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_TOIEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_TOIEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_TOIEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_TOIEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_TOIEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_TOIEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_TOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_TOIEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_TOIEPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Serial_Linear1D_CBTOIEPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBTOIEPBTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBTOIEPBTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBTOIEPBTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBTOIEPBTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBTOIEPBTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBTOIEPBTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBTOIEPBTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBTOIEPBTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBTOIEPBTMD_SamplingCheck,self).setUp()

# INTEGRATED EXPONENTIAL PUSHFORWARD
class Serial_Linear1D_IEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_IEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_IEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_IEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_IEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_IEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_IEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_IEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_IEPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_IEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_IEPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PUSHFORWARD
class Serial_Linear1D_CBIEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBIEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBIEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBIEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBIEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBIEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBIEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBIEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBIEPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBIEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBIEPFTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Serial_Linear1D_TOIEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_TOIEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_TOIEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_TOIEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_TOIEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_TOIEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_TOIEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_TOIEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_TOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_TOIEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_TOIEPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Serial_Linear1D_CBTOIEPFTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBTOIEPFTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBTOIEPFTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBTOIEPFTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBTOIEPFTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBTOIEPFTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBTOIEPFTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBTOIEPFTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBTOIEPFTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBTOIEPFTMD_SamplingCheck,self).setUp()

# INTEGRATED SQUARED PULLBACK
class Serial_Linear1D_ISPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                     Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_ISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_ISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_ISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_ISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_ISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_ISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_ISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_ISPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_ISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_ISPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED SQUARED PULLBACK
class Serial_Linear1D_CBISPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase, Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBISPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBISPBTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PULLBACK
class Serial_Linear1D_TOISPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_TOISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_TOISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_TOISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_TOISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_TOISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_TOISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_TOISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_TOISPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_TOISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_TOISPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PULLBACK
class Serial_Linear1D_CBTOISPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBTOISPBTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBTOISPBTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBTOISPBTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBTOISPBTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBTOISPBTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBTOISPBTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBTOISPBTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBTOISPBTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBTOISPBTMD_SamplingCheck,self).setUp()

# INTEGRATED SQUARED PUSHFORWARD
class Serial_Linear1D_ISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_ISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_ISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_ISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_ISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_ISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_ISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_ISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_ISPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_ISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_ISPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED SQUARED PUSHFORWARD
class Serial_Linear1D_CBISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBISPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Serial_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBISPFTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
class Serial_Linear1D_TOISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_TOISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_TOISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_TOISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_TOISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_TOISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_TOISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_TOISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_TOISPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_TOISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Serial_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_TOISPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
class Serial_Linear1D_CBTOISPFTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_ArcTan1D_CBTOISPFTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_ArcTan1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_ArcTan1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Exp1D_CBTOISPFTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Exp1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Exp1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Logistic1D_CBTOISPFTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Logistic1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Logistic1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Gamma1D_CBTOISPFTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gamma1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gamma1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Beta1D_CBTOISPFTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Beta1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Beta1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Gumbel1D_CBTOISPFTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Gumbel1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Gumbel1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Linear2D_CBTOISPFTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Linear2D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear2D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Serial_Banana2D_CBTOISPFTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Serial_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Serial_Banana2D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Banana2D_CBTOISPFTMD_SamplingCheck,self).setUp()

        
# LINEAR APPROXIMATIONS
class Serial_Linear1D_LSPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                            Serial_LinearSpanPBTMD_SamplingCheck):

    def setUp(self):
        super(Serial_Linear1D_LSPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_LSPBTMD_SamplingCheck,self).setUp()

class Serial_Linear1D_CBLSPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Serial_CommonBasisLinearSpanPBTMD_SamplingCheck):

    def setUp(self):
        super(Serial_Linear1D_CBLSPBTMD_SamplingCheck,self).setUp_test_case()
        super(Serial_Linear1D_CBLSPBTMD_SamplingCheck,self).setUp()

#
# Parallel test cases
# 

# INTEGRATED EXPONENTIAL PULLBACK
class Parallel_Linear1D_IEPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                     Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_IEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_IEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_IEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_IEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_IEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_IEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_IEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_IEPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_IEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_IEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_IEPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PULLBACK
class Parallel_Linear1D_CBIEPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase, Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBIEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBIEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBIEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBIEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBIEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBIEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBIEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBIEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBIEPBTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Parallel_Linear1D_TOIEPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_TOIEPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_TOIEPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_TOIEPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_TOIEPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_TOIEPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_TOIEPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_TOIEPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_TOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_TOIEPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_TOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_TOIEPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PULLBACK
class Parallel_Linear1D_CBTOIEPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBTOIEPBTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBTOIEPBTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBTOIEPBTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBTOIEPBTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBTOIEPBTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBTOIEPBTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBTOIEPBTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBTOIEPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBTOIEPBTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBTOIEPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBTOIEPBTMD_SamplingCheck,self).setUp()

# INTEGRATED EXPONENTIAL PUSHFORWARD
class Parallel_Linear1D_IEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_IEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_IEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_IEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_IEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_IEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_IEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_IEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_IEPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_IEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_IntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_IEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_IEPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED EXPONENTIAL PUSHFORWARD
class Parallel_Linear1D_CBIEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBIEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBIEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBIEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBIEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBIEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBIEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBIEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBIEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBIEPFTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Parallel_Linear1D_TOIEPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_TOIEPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_TOIEPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_TOIEPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_TOIEPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_TOIEPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_TOIEPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_TOIEPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_TOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_TOIEPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_TOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_TOIEPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED EXPONENTIAL PUSHFORWARD
class Parallel_Linear1D_CBTOIEPFTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBTOIEPFTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBTOIEPFTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBTOIEPFTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBTOIEPFTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBTOIEPFTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBTOIEPFTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBTOIEPFTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBTOIEPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBTOIEPFTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedExponentialPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBTOIEPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBTOIEPFTMD_SamplingCheck,self).setUp()

# INTEGRATED SQUARED PULLBACK
class Parallel_Linear1D_ISPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                     Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_ISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_ISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_ISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_ISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_ISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_ISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_ISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_ISPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_ISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_ISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_ISPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED SQUARED PULLBACK
class Parallel_Linear1D_CBISPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase, Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBISPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBISPBTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PULLBACK
class Parallel_Linear1D_TOISPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_TOISPBTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_TOISPBTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_TOISPBTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_TOISPBTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_TOISPBTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_TOISPBTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_TOISPBTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_TOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_TOISPBTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_TOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_TOISPBTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PULLBACK
class Parallel_Linear1D_CBTOISPBTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBTOISPBTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBTOISPBTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBTOISPBTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBTOISPBTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBTOISPBTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBTOISPBTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBTOISPBTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBTOISPBTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBTOISPBTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPBTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBTOISPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBTOISPBTMD_SamplingCheck,self).setUp()

# INTEGRATED SQUARED PUSHFORWARD
class Parallel_Linear1D_ISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_ISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_ISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_ISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_ISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_ISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_ISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_ISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_ISPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_ISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_IntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_ISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_ISPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS INTEGRATED SQUARED PUSHFORWARD
class Parallel_Linear1D_CBISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                       Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                            Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                         Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                        Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBISPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                          Parallel_CommonBasisIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBISPFTMD_SamplingCheck,self).setUp()

# TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
class Parallel_Linear1D_TOISPFTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_TOISPFTMD_SamplingCheck(ArcTan1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_TOISPFTMD_SamplingCheck(Exp1D_TMD_TestCase,
                                     Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_TOISPFTMD_SamplingCheck(Logistic1D_TMD_TestCase,
                                          Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_TOISPFTMD_SamplingCheck(Gamma1D_TMD_TestCase,
                                       Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_TOISPFTMD_SamplingCheck(Beta1D_TMD_TestCase,
                                      Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_TOISPFTMD_SamplingCheck(Gumbel1D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_TOISPFTMD_SamplingCheck(Linear2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_TOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_TOISPFTMD_SamplingCheck(Banana2D_TMD_TestCase,
                                        Parallel_TotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_TOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_TOISPFTMD_SamplingCheck,self).setUp()

# COMMON BASIS TOTAL ORDER INTEGRATED SQUARED PUSHFORWARD
class Parallel_Linear1D_CBTOISPFTMD_SamplingCheck(
        Linear1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_ArcTan1D_CBTOISPFTMD_SamplingCheck(
        ArcTan1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_ArcTan1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_ArcTan1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Exp1D_CBTOISPFTMD_SamplingCheck(
        Exp1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Exp1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Exp1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Logistic1D_CBTOISPFTMD_SamplingCheck(
        Logistic1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Logistic1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Logistic1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gamma1D_CBTOISPFTMD_SamplingCheck(
        Gamma1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gamma1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gamma1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Beta1D_CBTOISPFTMD_SamplingCheck(
        Beta1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Beta1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Beta1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Gumbel1D_CBTOISPFTMD_SamplingCheck(
        Gumbel1D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Gumbel1D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Gumbel1D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Linear2D_CBTOISPFTMD_SamplingCheck(
        Linear2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Linear2D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear2D_CBTOISPFTMD_SamplingCheck,self).setUp()

class Parallel_Banana2D_CBTOISPFTMD_SamplingCheck(
        Banana2D_TMD_TestCase,
        Parallel_CommonBasisTotOrdIntegratedSquaredPFTMD_SamplingCheck):
    def setUp(self):
        super(Parallel_Banana2D_CBTOISPFTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Banana2D_CBTOISPFTMD_SamplingCheck,self).setUp()

        
# LINEAR APPROXIMATIONS
class Parallel_Linear1D_LSPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                            Parallel_LinearSpanPBTMD_SamplingCheck):

    def setUp(self):
        super(Parallel_Linear1D_LSPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_LSPBTMD_SamplingCheck,self).setUp()

class Parallel_Linear1D_CBLSPBTMD_SamplingCheck(Linear1D_TMD_TestCase,
                                          Parallel_CommonBasisLinearSpanPBTMD_SamplingCheck):

    def setUp(self):
        super(Parallel_Linear1D_CBLSPBTMD_SamplingCheck,self).setUp_test_case()
        super(Parallel_Linear1D_CBLSPBTMD_SamplingCheck,self).setUp()


def build_suite(ttype='all'):
    # SERIAL TESTS
    # Integrated exponential pullback
    suite_se_linear1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_IEPBTMD_SamplingCheck )
    suite_se_arctan1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_IEPBTMD_SamplingCheck )
    suite_se_exp1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_IEPBTMD_SamplingCheck )
    suite_se_logistic1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_IEPBTMD_SamplingCheck )
    suite_se_gamma1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_IEPBTMD_SamplingCheck )
    suite_se_beta1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_IEPBTMD_SamplingCheck )
    suite_se_gumbel1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_IEPBTMD_SamplingCheck )
    suite_se_linear2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_IEPBTMD_SamplingCheck )
    suite_se_banana2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_IEPBTMD_SamplingCheck )
    # CommonBasis integrated exponential pullback
    suite_se_linear1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBIEPBTMD_SamplingCheck )
    suite_se_arctan1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBIEPBTMD_SamplingCheck )
    suite_se_exp1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBIEPBTMD_SamplingCheck )
    suite_se_logistic1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBIEPBTMD_SamplingCheck )
    suite_se_gamma1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBIEPBTMD_SamplingCheck )
    suite_se_beta1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBIEPBTMD_SamplingCheck )
    suite_se_gumbel1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBIEPBTMD_SamplingCheck )
    suite_se_linear2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBIEPBTMD_SamplingCheck )
    suite_se_banana2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBIEPBTMD_SamplingCheck )
    # Total order integrated exponential pullback
    suite_se_linear1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_TOIEPBTMD_SamplingCheck )
    suite_se_arctan1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_TOIEPBTMD_SamplingCheck )
    suite_se_exp1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_TOIEPBTMD_SamplingCheck )
    suite_se_logistic1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_TOIEPBTMD_SamplingCheck )
    suite_se_gamma1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_TOIEPBTMD_SamplingCheck )
    suite_se_beta1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_TOIEPBTMD_SamplingCheck )
    suite_se_gumbel1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_TOIEPBTMD_SamplingCheck )
    suite_se_linear2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_TOIEPBTMD_SamplingCheck )
    suite_se_banana2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_TOIEPBTMD_SamplingCheck )
    # Total order commonBasis integrated exponential pullback
    suite_se_linear1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_arctan1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_exp1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_logistic1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_gamma1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_beta1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_gumbel1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBTOIEPBTMD_SamplingCheck )
    suite_se_linear2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBTOIEPBTMD_SamplingCheck )
    suite_se_banana2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBTOIEPBTMD_SamplingCheck )
    # Integrated exponential pushforward
    suite_se_linear1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_IEPFTMD_SamplingCheck )
    suite_se_arctan1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_IEPFTMD_SamplingCheck )
    suite_se_exp1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_IEPFTMD_SamplingCheck )
    suite_se_logistic1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_IEPFTMD_SamplingCheck )
    suite_se_gamma1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_IEPFTMD_SamplingCheck )
    suite_se_beta1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_IEPFTMD_SamplingCheck )
    suite_se_gumbel1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_IEPFTMD_SamplingCheck )
    suite_se_linear2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_IEPFTMD_SamplingCheck )
    suite_se_banana2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_IEPFTMD_SamplingCheck )
    # CommonBasis integrated exponential pushforward
    suite_se_linear1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBIEPFTMD_SamplingCheck )
    suite_se_arctan1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBIEPFTMD_SamplingCheck )
    suite_se_exp1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBIEPFTMD_SamplingCheck )
    suite_se_logistic1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBIEPFTMD_SamplingCheck )
    suite_se_gamma1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBIEPFTMD_SamplingCheck )
    suite_se_beta1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBIEPFTMD_SamplingCheck )
    suite_se_gumbel1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBIEPFTMD_SamplingCheck )
    suite_se_linear2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBIEPFTMD_SamplingCheck )
    suite_se_banana2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBIEPFTMD_SamplingCheck )
    # Total order integrated exponential pushforward
    suite_se_linear1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_TOIEPFTMD_SamplingCheck )
    suite_se_arctan1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_TOIEPFTMD_SamplingCheck )
    suite_se_exp1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_TOIEPFTMD_SamplingCheck )
    suite_se_logistic1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_TOIEPFTMD_SamplingCheck )
    suite_se_gamma1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_TOIEPFTMD_SamplingCheck )
    suite_se_beta1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_TOIEPFTMD_SamplingCheck )
    suite_se_gumbel1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_TOIEPFTMD_SamplingCheck )
    suite_se_linear2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_TOIEPFTMD_SamplingCheck )
    suite_se_banana2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_TOIEPFTMD_SamplingCheck )
    # Total order commonBasis integrated exponential pushforward
    suite_se_linear1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_arctan1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_exp1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_logistic1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_gamma1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_beta1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_gumbel1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBTOIEPFTMD_SamplingCheck )
    suite_se_linear2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBTOIEPFTMD_SamplingCheck )
    suite_se_banana2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBTOIEPFTMD_SamplingCheck )

    # Integrated squared pullback
    suite_se_linear1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_ISPBTMD_SamplingCheck )
    suite_se_arctan1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_ISPBTMD_SamplingCheck )
    suite_se_exp1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_ISPBTMD_SamplingCheck )
    suite_se_logistic1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_ISPBTMD_SamplingCheck )
    suite_se_gamma1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_ISPBTMD_SamplingCheck )
    suite_se_beta1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_ISPBTMD_SamplingCheck )
    suite_se_gumbel1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_ISPBTMD_SamplingCheck )
    suite_se_linear2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_ISPBTMD_SamplingCheck )
    suite_se_banana2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_ISPBTMD_SamplingCheck )
    # CommonBasis integrated squared pullback
    suite_se_linear1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBISPBTMD_SamplingCheck )
    suite_se_arctan1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBISPBTMD_SamplingCheck )
    suite_se_exp1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBISPBTMD_SamplingCheck )
    suite_se_logistic1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBISPBTMD_SamplingCheck )
    suite_se_gamma1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBISPBTMD_SamplingCheck )
    suite_se_beta1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBISPBTMD_SamplingCheck )
    suite_se_gumbel1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBISPBTMD_SamplingCheck )
    suite_se_linear2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBISPBTMD_SamplingCheck )
    suite_se_banana2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBISPBTMD_SamplingCheck )
    # Total order integrated squared pullback
    suite_se_linear1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_TOISPBTMD_SamplingCheck )
    suite_se_arctan1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_TOISPBTMD_SamplingCheck )
    suite_se_exp1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_TOISPBTMD_SamplingCheck )
    suite_se_logistic1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_TOISPBTMD_SamplingCheck )
    suite_se_gamma1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_TOISPBTMD_SamplingCheck )
    suite_se_beta1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_TOISPBTMD_SamplingCheck )
    suite_se_gumbel1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_TOISPBTMD_SamplingCheck )
    suite_se_linear2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_TOISPBTMD_SamplingCheck )
    suite_se_banana2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_TOISPBTMD_SamplingCheck )
    # Total order commonBasis integrated squared pullback
    suite_se_linear1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBTOISPBTMD_SamplingCheck )
    suite_se_arctan1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBTOISPBTMD_SamplingCheck )
    suite_se_exp1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBTOISPBTMD_SamplingCheck )
    suite_se_logistic1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBTOISPBTMD_SamplingCheck )
    suite_se_gamma1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBTOISPBTMD_SamplingCheck )
    suite_se_beta1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBTOISPBTMD_SamplingCheck )
    suite_se_gumbel1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBTOISPBTMD_SamplingCheck )
    suite_se_linear2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBTOISPBTMD_SamplingCheck )
    suite_se_banana2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBTOISPBTMD_SamplingCheck )
    # Integrated squared pushforward
    suite_se_linear1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_ISPFTMD_SamplingCheck )
    suite_se_arctan1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_ISPFTMD_SamplingCheck )
    suite_se_exp1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_ISPFTMD_SamplingCheck )
    suite_se_logistic1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_ISPFTMD_SamplingCheck )
    suite_se_gamma1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_ISPFTMD_SamplingCheck )
    suite_se_beta1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_ISPFTMD_SamplingCheck )
    suite_se_gumbel1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_ISPFTMD_SamplingCheck )
    suite_se_linear2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_ISPFTMD_SamplingCheck )
    suite_se_banana2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_ISPFTMD_SamplingCheck )
    # CommonBasis integrated squared pushforward
    suite_se_linear1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBISPFTMD_SamplingCheck )
    suite_se_arctan1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBISPFTMD_SamplingCheck )
    suite_se_exp1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBISPFTMD_SamplingCheck )
    suite_se_logistic1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBISPFTMD_SamplingCheck )
    suite_se_gamma1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBISPFTMD_SamplingCheck )
    suite_se_beta1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBISPFTMD_SamplingCheck )
    suite_se_gumbel1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBISPFTMD_SamplingCheck )
    suite_se_linear2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBISPFTMD_SamplingCheck )
    suite_se_banana2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBISPFTMD_SamplingCheck )
    # Total order integrated squared pushforward
    suite_se_linear1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_TOISPFTMD_SamplingCheck )
    suite_se_arctan1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_TOISPFTMD_SamplingCheck )
    suite_se_exp1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_TOISPFTMD_SamplingCheck )
    suite_se_logistic1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_TOISPFTMD_SamplingCheck )
    suite_se_gamma1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_TOISPFTMD_SamplingCheck )
    suite_se_beta1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_TOISPFTMD_SamplingCheck )
    suite_se_gumbel1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_TOISPFTMD_SamplingCheck )
    suite_se_linear2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_TOISPFTMD_SamplingCheck )
    suite_se_banana2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_TOISPFTMD_SamplingCheck )
    # Total order commonBasis integrated squared pushforward
    suite_se_linear1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBTOISPFTMD_SamplingCheck )
    suite_se_arctan1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_ArcTan1D_CBTOISPFTMD_SamplingCheck )
    suite_se_exp1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Exp1D_CBTOISPFTMD_SamplingCheck )
    suite_se_logistic1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Logistic1D_CBTOISPFTMD_SamplingCheck )
    suite_se_gamma1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gamma1D_CBTOISPFTMD_SamplingCheck )
    suite_se_beta1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Beta1D_CBTOISPFTMD_SamplingCheck )
    suite_se_gumbel1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Gumbel1D_CBTOISPFTMD_SamplingCheck )
    suite_se_linear2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear2D_CBTOISPFTMD_SamplingCheck )
    suite_se_banana2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Banana2D_CBTOISPFTMD_SamplingCheck )

    # Linear Span
    suite_se_linear1d_lspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_LSPBTMD_SamplingCheck )
    suite_se_linear1d_cblspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Serial_Linear1D_CBLSPBTMD_SamplingCheck )

    # PARALLEL TESTS
    # Integrated exponential pullback
    suite_pa_linear1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_IEPBTMD_SamplingCheck )
    suite_pa_arctan1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_IEPBTMD_SamplingCheck )
    suite_pa_exp1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_IEPBTMD_SamplingCheck )
    suite_pa_logistic1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_IEPBTMD_SamplingCheck )
    suite_pa_gamma1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_IEPBTMD_SamplingCheck )
    suite_pa_beta1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_IEPBTMD_SamplingCheck )
    suite_pa_gumbel1d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_IEPBTMD_SamplingCheck )
    suite_pa_linear2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_IEPBTMD_SamplingCheck )
    suite_pa_banana2d_iepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_IEPBTMD_SamplingCheck )
    # CommonBasis integrated exponential pullback
    suite_pa_linear1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBIEPBTMD_SamplingCheck )
    suite_pa_arctan1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBIEPBTMD_SamplingCheck )
    suite_pa_exp1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBIEPBTMD_SamplingCheck )
    suite_pa_logistic1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBIEPBTMD_SamplingCheck )
    suite_pa_gamma1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBIEPBTMD_SamplingCheck )
    suite_pa_beta1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBIEPBTMD_SamplingCheck )
    suite_pa_gumbel1d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBIEPBTMD_SamplingCheck )
    suite_pa_linear2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBIEPBTMD_SamplingCheck )
    suite_pa_banana2d_cbiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBIEPBTMD_SamplingCheck )
    # Total order integrated exponential pullback
    suite_pa_linear1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_TOIEPBTMD_SamplingCheck )
    suite_pa_arctan1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_TOIEPBTMD_SamplingCheck )
    suite_pa_exp1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_TOIEPBTMD_SamplingCheck )
    suite_pa_logistic1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_TOIEPBTMD_SamplingCheck )
    suite_pa_gamma1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_TOIEPBTMD_SamplingCheck )
    suite_pa_beta1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_TOIEPBTMD_SamplingCheck )
    suite_pa_gumbel1d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_TOIEPBTMD_SamplingCheck )
    suite_pa_linear2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_TOIEPBTMD_SamplingCheck )
    suite_pa_banana2d_toiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_TOIEPBTMD_SamplingCheck )
    # Total order commonBasis integrated exponential pullback
    suite_pa_linear1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_arctan1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_exp1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_logistic1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_gamma1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_beta1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_gumbel1d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_linear2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBTOIEPBTMD_SamplingCheck )
    suite_pa_banana2d_cbtoiepbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBTOIEPBTMD_SamplingCheck )
    # Integrated exponential pushforward
    suite_pa_linear1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_IEPFTMD_SamplingCheck )
    suite_pa_arctan1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_IEPFTMD_SamplingCheck )
    suite_pa_exp1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_IEPFTMD_SamplingCheck )
    suite_pa_logistic1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_IEPFTMD_SamplingCheck )
    suite_pa_gamma1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_IEPFTMD_SamplingCheck )
    suite_pa_beta1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_IEPFTMD_SamplingCheck )
    suite_pa_gumbel1d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_IEPFTMD_SamplingCheck )
    suite_pa_linear2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_IEPFTMD_SamplingCheck )
    suite_pa_banana2d_iepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_IEPFTMD_SamplingCheck )
    # CommonBasis integrated exponential pushforward
    suite_pa_linear1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBIEPFTMD_SamplingCheck )
    suite_pa_arctan1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBIEPFTMD_SamplingCheck )
    suite_pa_exp1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBIEPFTMD_SamplingCheck )
    suite_pa_logistic1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBIEPFTMD_SamplingCheck )
    suite_pa_gamma1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBIEPFTMD_SamplingCheck )
    suite_pa_beta1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBIEPFTMD_SamplingCheck )
    suite_pa_gumbel1d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBIEPFTMD_SamplingCheck )
    suite_pa_linear2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBIEPFTMD_SamplingCheck )
    suite_pa_banana2d_cbiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBIEPFTMD_SamplingCheck )
    # Total order integrated exponential pushforward
    suite_pa_linear1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_TOIEPFTMD_SamplingCheck )
    suite_pa_arctan1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_TOIEPFTMD_SamplingCheck )
    suite_pa_exp1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_TOIEPFTMD_SamplingCheck )
    suite_pa_logistic1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_TOIEPFTMD_SamplingCheck )
    suite_pa_gamma1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_TOIEPFTMD_SamplingCheck )
    suite_pa_beta1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_TOIEPFTMD_SamplingCheck )
    suite_pa_gumbel1d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_TOIEPFTMD_SamplingCheck )
    suite_pa_linear2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_TOIEPFTMD_SamplingCheck )
    suite_pa_banana2d_toiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_TOIEPFTMD_SamplingCheck )
    # Total order commonBasis integrated exponential pushforward
    suite_pa_linear1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_arctan1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_exp1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_logistic1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_gamma1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_beta1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_gumbel1d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_linear2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBTOIEPFTMD_SamplingCheck )
    suite_pa_banana2d_cbtoiepftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBTOIEPFTMD_SamplingCheck )

    # Integrated squared pullback
    suite_pa_linear1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_ISPBTMD_SamplingCheck )
    suite_pa_arctan1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_ISPBTMD_SamplingCheck )
    suite_pa_exp1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_ISPBTMD_SamplingCheck )
    suite_pa_logistic1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_ISPBTMD_SamplingCheck )
    suite_pa_gamma1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_ISPBTMD_SamplingCheck )
    suite_pa_beta1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_ISPBTMD_SamplingCheck )
    suite_pa_gumbel1d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_ISPBTMD_SamplingCheck )
    suite_pa_linear2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_ISPBTMD_SamplingCheck )
    suite_pa_banana2d_ispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_ISPBTMD_SamplingCheck )
    # CommonBasis integrated squared pullback
    suite_pa_linear1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBISPBTMD_SamplingCheck )
    suite_pa_arctan1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBISPBTMD_SamplingCheck )
    suite_pa_exp1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBISPBTMD_SamplingCheck )
    suite_pa_logistic1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBISPBTMD_SamplingCheck )
    suite_pa_gamma1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBISPBTMD_SamplingCheck )
    suite_pa_beta1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBISPBTMD_SamplingCheck )
    suite_pa_gumbel1d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBISPBTMD_SamplingCheck )
    suite_pa_linear2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBISPBTMD_SamplingCheck )
    suite_pa_banana2d_cbispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBISPBTMD_SamplingCheck )
    # Total order integrated squared pullback
    suite_pa_linear1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_TOISPBTMD_SamplingCheck )
    suite_pa_arctan1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_TOISPBTMD_SamplingCheck )
    suite_pa_exp1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_TOISPBTMD_SamplingCheck )
    suite_pa_logistic1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_TOISPBTMD_SamplingCheck )
    suite_pa_gamma1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_TOISPBTMD_SamplingCheck )
    suite_pa_beta1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_TOISPBTMD_SamplingCheck )
    suite_pa_gumbel1d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_TOISPBTMD_SamplingCheck )
    suite_pa_linear2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_TOISPBTMD_SamplingCheck )
    suite_pa_banana2d_toispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_TOISPBTMD_SamplingCheck )
    # Total order commonBasis integrated squared pullback
    suite_pa_linear1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_arctan1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_exp1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_logistic1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_gamma1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_beta1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_gumbel1d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBTOISPBTMD_SamplingCheck )
    suite_pa_linear2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBTOISPBTMD_SamplingCheck )
    suite_pa_banana2d_cbtoispbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBTOISPBTMD_SamplingCheck )
    # Integrated squared pushforward
    suite_pa_linear1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_ISPFTMD_SamplingCheck )
    suite_pa_arctan1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_ISPFTMD_SamplingCheck )
    suite_pa_exp1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_ISPFTMD_SamplingCheck )
    suite_pa_logistic1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_ISPFTMD_SamplingCheck )
    suite_pa_gamma1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_ISPFTMD_SamplingCheck )
    suite_pa_beta1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_ISPFTMD_SamplingCheck )
    suite_pa_gumbel1d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_ISPFTMD_SamplingCheck )
    suite_pa_linear2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_ISPFTMD_SamplingCheck )
    suite_pa_banana2d_ispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_ISPFTMD_SamplingCheck )
    # CommonBasis integrated squared pushforward
    suite_pa_linear1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBISPFTMD_SamplingCheck )
    suite_pa_arctan1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBISPFTMD_SamplingCheck )
    suite_pa_exp1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBISPFTMD_SamplingCheck )
    suite_pa_logistic1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBISPFTMD_SamplingCheck )
    suite_pa_gamma1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBISPFTMD_SamplingCheck )
    suite_pa_beta1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBISPFTMD_SamplingCheck )
    suite_pa_gumbel1d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBISPFTMD_SamplingCheck )
    suite_pa_linear2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBISPFTMD_SamplingCheck )
    suite_pa_banana2d_cbispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBISPFTMD_SamplingCheck )
    # Total order integrated squared pushforward
    suite_pa_linear1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_TOISPFTMD_SamplingCheck )
    suite_pa_arctan1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_TOISPFTMD_SamplingCheck )
    suite_pa_exp1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_TOISPFTMD_SamplingCheck )
    suite_pa_logistic1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_TOISPFTMD_SamplingCheck )
    suite_pa_gamma1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_TOISPFTMD_SamplingCheck )
    suite_pa_beta1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_TOISPFTMD_SamplingCheck )
    suite_pa_gumbel1d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_TOISPFTMD_SamplingCheck )
    suite_pa_linear2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_TOISPFTMD_SamplingCheck )
    suite_pa_banana2d_toispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_TOISPFTMD_SamplingCheck )
    # Total order commonBasis integrated squared pushforward
    suite_pa_linear1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_arctan1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_ArcTan1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_exp1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Exp1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_logistic1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Logistic1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_gamma1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gamma1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_beta1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Beta1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_gumbel1d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Gumbel1D_CBTOISPFTMD_SamplingCheck )
    suite_pa_linear2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear2D_CBTOISPFTMD_SamplingCheck )
    suite_pa_banana2d_cbtoispftmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Banana2D_CBTOISPFTMD_SamplingCheck )
    
    # Linear Span
    suite_pa_linear1d_lspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_LSPBTMD_SamplingCheck )
    suite_pa_linear1d_cblspbtmd = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_Linear1D_CBLSPBTMD_SamplingCheck )

    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [
            # SERIAL TESTS
            # Integrated exponential pullback
            suite_se_linear1d_iepbtmd, suite_se_arctan1d_iepbtmd, suite_se_exp1d_iepbtmd,
            suite_se_logistic1d_iepbtmd, suite_se_gamma1d_iepbtmd, 
            suite_se_beta1d_iepbtmd,
            suite_se_gumbel1d_iepbtmd, suite_se_linear2d_iepbtmd, 
            suite_se_banana2d_iepbtmd,
            # Common basis integrated exponential pullback
            suite_se_linear1d_cbiepbtmd, suite_se_arctan1d_cbiepbtmd, 
            suite_se_exp1d_cbiepbtmd,
            suite_se_logistic1d_cbiepbtmd, suite_se_gamma1d_cbiepbtmd,
            suite_se_beta1d_cbiepbtmd,
            suite_se_gumbel1d_cbiepbtmd, suite_se_linear2d_cbiepbtmd,
            suite_se_banana2d_cbiepbtmd,
            # Total order integrated exponential pullback
            suite_se_linear1d_toiepbtmd, suite_se_arctan1d_toiepbtmd, 
            suite_se_exp1d_toiepbtmd,
            suite_se_logistic1d_toiepbtmd, suite_se_gamma1d_toiepbtmd,
            suite_se_beta1d_toiepbtmd,
            suite_se_gumbel1d_toiepbtmd, suite_se_linear2d_toiepbtmd,
            suite_se_banana2d_toiepbtmd,
            # Common basis total order integrated exponential pullback
            suite_se_linear1d_cbtoiepbtmd, suite_se_arctan1d_cbtoiepbtmd,
            suite_se_exp1d_cbtoiepbtmd,
            suite_se_logistic1d_cbtoiepbtmd, suite_se_gamma1d_cbtoiepbtmd,
            suite_se_beta1d_cbtoiepbtmd,
            suite_se_gumbel1d_cbtoiepbtmd, suite_se_linear2d_cbtoiepbtmd,
            suite_se_banana2d_cbtoiepbtmd,
            # Integrated exponential pushforward
            suite_se_linear1d_iepftmd, suite_se_arctan1d_iepftmd, suite_se_exp1d_iepftmd,
            suite_se_logistic1d_iepftmd, suite_se_gamma1d_iepftmd, 
            suite_se_beta1d_iepftmd,
            suite_se_gumbel1d_iepftmd, suite_se_linear2d_iepftmd, 
            suite_se_banana2d_iepftmd,
            # Common basis integrated exponential pushforward
            suite_se_linear1d_cbiepftmd, suite_se_arctan1d_cbiepftmd, 
            suite_se_exp1d_cbiepftmd,
            suite_se_logistic1d_cbiepftmd, suite_se_gamma1d_cbiepftmd,
            suite_se_beta1d_cbiepftmd,
            suite_se_gumbel1d_cbiepftmd, suite_se_linear2d_cbiepftmd,
            suite_se_banana2d_cbiepftmd,
            # Total order integrated exponential pushforward
            suite_se_linear1d_toiepftmd, suite_se_arctan1d_toiepftmd, 
            suite_se_exp1d_toiepftmd,
            suite_se_logistic1d_toiepftmd, suite_se_gamma1d_toiepftmd,
            suite_se_beta1d_toiepftmd,
            suite_se_gumbel1d_toiepftmd, suite_se_linear2d_toiepftmd,
            suite_se_banana2d_toiepftmd,
            # Common basis total order integrated exponential pushforward
            suite_se_linear1d_cbtoiepftmd, suite_se_arctan1d_cbtoiepftmd,
            suite_se_exp1d_cbtoiepftmd,
            suite_se_logistic1d_cbtoiepftmd, suite_se_gamma1d_cbtoiepftmd,
            suite_se_beta1d_cbtoiepftmd,
            suite_se_gumbel1d_cbtoiepftmd, suite_se_linear2d_cbtoiepftmd,
            suite_se_banana2d_cbtoiepftmd,

            # Integrated squared pullback
            suite_se_linear1d_ispbtmd, suite_se_arctan1d_ispbtmd, suite_se_exp1d_ispbtmd,
            suite_se_logistic1d_ispbtmd, suite_se_gamma1d_ispbtmd, 
            suite_se_beta1d_ispbtmd,
            suite_se_gumbel1d_ispbtmd, suite_se_linear2d_ispbtmd, 
            suite_se_banana2d_ispbtmd,
            # # Common basis integrated squared pullback
            # suite_se_linear1d_cbispbtmd, suite_se_arctan1d_cbispbtmd, 
            # suite_se_exp1d_cbispbtmd,
            # suite_se_logistic1d_cbispbtmd, suite_se_gamma1d_cbispbtmd,
            # suite_se_beta1d_cbispbtmd,
            # suite_se_gumbel1d_cbispbtmd, suite_se_linear2d_cbispbtmd,
            # suite_se_banana2d_cbispbtmd,
            # Total order integrated squared pullback
            suite_se_linear1d_toispbtmd, suite_se_arctan1d_toispbtmd, 
            suite_se_exp1d_toispbtmd,
            suite_se_logistic1d_toispbtmd, suite_se_gamma1d_toispbtmd,
            suite_se_beta1d_toispbtmd,
            suite_se_gumbel1d_toispbtmd, suite_se_linear2d_toispbtmd,
            suite_se_banana2d_toispbtmd,
            # # Common basis total order integrated squared pullback
            # suite_se_linear1d_cbtoispbtmd, suite_se_arctan1d_cbtoispbtmd,
            # suite_se_exp1d_cbtoispbtmd,
            # suite_se_logistic1d_cbtoispbtmd, suite_se_gamma1d_cbtoispbtmd,
            # suite_se_beta1d_cbtoispbtmd,
            # suite_se_gumbel1d_cbtoispbtmd, suite_se_linear2d_cbtoispbtmd,
            # suite_se_banana2d_cbtoispbtmd,
            # Integrated squared pushforward
            suite_se_linear1d_ispftmd, suite_se_arctan1d_ispftmd, suite_se_exp1d_ispftmd,
            suite_se_logistic1d_ispftmd, suite_se_gamma1d_ispftmd, 
            suite_se_beta1d_ispftmd,
            suite_se_gumbel1d_ispftmd, suite_se_linear2d_ispftmd, 
            suite_se_banana2d_ispftmd,
            # # Common basis integrated squared pushforward
            # suite_se_linear1d_cbispftmd, suite_se_arctan1d_cbispftmd, 
            # suite_se_exp1d_cbispftmd,
            # suite_se_logistic1d_cbispftmd, suite_se_gamma1d_cbispftmd,
            # suite_se_beta1d_cbispftmd,
            # suite_se_gumbel1d_cbispftmd, suite_se_linear2d_cbispftmd,
            # suite_se_banana2d_cbispftmd,
            # Total order integrated squared pushforward
            suite_se_linear1d_toispftmd, suite_se_arctan1d_toispftmd, 
            suite_se_exp1d_toispftmd,
            suite_se_logistic1d_toispftmd, suite_se_gamma1d_toispftmd,
            suite_se_beta1d_toispftmd,
            suite_se_gumbel1d_toispftmd, suite_se_linear2d_toispftmd,
            suite_se_banana2d_toispftmd,
            # # Common basis total order integrated squared pushforward
            # suite_se_linear1d_cbtoispftmd, suite_se_arctan1d_cbtoispftmd,
            # suite_se_exp1d_cbtoispftmd,
            # suite_se_logistic1d_cbtoispftmd, suite_se_gamma1d_cbtoispftmd,
            # suite_se_beta1d_cbtoispftmd,
            # suite_se_gumbel1d_cbtoispftmd, suite_se_linear2d_cbtoispftmd,
            # suite_se_banana2d_cbtoispftmd,

            # Linear span pullback
            suite_se_linear1d_lspbtmd, suite_se_linear1d_cblspbtmd,
        ]
    
    # Parallel
    if ttype in ['all','parallel'] and MPI_SUPPORT:
        suites_list += [
            # PARALLEL TESTS
            # Integrated exponential pullback
            suite_pa_linear1d_iepbtmd, suite_pa_arctan1d_iepbtmd, suite_pa_exp1d_iepbtmd,
            suite_pa_logistic1d_iepbtmd, suite_pa_gamma1d_iepbtmd, 
            suite_pa_beta1d_iepbtmd,
            suite_pa_gumbel1d_iepbtmd, suite_pa_linear2d_iepbtmd, 
            suite_pa_banana2d_iepbtmd,
            # Common basis integrated exponential pullback
            suite_pa_linear1d_cbiepbtmd, suite_pa_arctan1d_cbiepbtmd, 
            suite_pa_exp1d_cbiepbtmd,
            suite_pa_logistic1d_cbiepbtmd, suite_pa_gamma1d_cbiepbtmd,
            suite_pa_beta1d_cbiepbtmd,
            suite_pa_gumbel1d_cbiepbtmd, suite_pa_linear2d_cbiepbtmd,
            suite_pa_banana2d_cbiepbtmd,
            # Total order integrated exponential pullback
            suite_pa_linear1d_toiepbtmd, suite_pa_arctan1d_toiepbtmd, 
            suite_pa_exp1d_toiepbtmd,
            suite_pa_logistic1d_toiepbtmd, suite_pa_gamma1d_toiepbtmd,
            suite_pa_beta1d_toiepbtmd,
            suite_pa_gumbel1d_toiepbtmd, suite_pa_linear2d_toiepbtmd,
            suite_pa_banana2d_toiepbtmd,
            # Common basis total order integrated exponential pullback
            suite_pa_linear1d_cbtoiepbtmd, suite_pa_arctan1d_cbtoiepbtmd,
            suite_pa_exp1d_cbtoiepbtmd,
            suite_pa_logistic1d_cbtoiepbtmd, suite_pa_gamma1d_cbtoiepbtmd,
            suite_pa_beta1d_cbtoiepbtmd,
            suite_pa_gumbel1d_cbtoiepbtmd, suite_pa_linear2d_cbtoiepbtmd,
            suite_pa_banana2d_cbtoiepbtmd,
            # Integrated exponential pushforward
            suite_pa_linear1d_iepftmd, suite_pa_arctan1d_iepftmd, suite_pa_exp1d_iepftmd,
            suite_pa_logistic1d_iepftmd, suite_pa_gamma1d_iepftmd, 
            suite_pa_beta1d_iepftmd,
            suite_pa_gumbel1d_iepftmd, suite_pa_linear2d_iepftmd, 
            suite_pa_banana2d_iepftmd,
            # Common basis integrated exponential pushforward
            suite_pa_linear1d_cbiepftmd, suite_pa_arctan1d_cbiepftmd, 
            suite_pa_exp1d_cbiepftmd,
            suite_pa_logistic1d_cbiepftmd, suite_pa_gamma1d_cbiepftmd,
            suite_pa_beta1d_cbiepftmd,
            suite_pa_gumbel1d_cbiepftmd, suite_pa_linear2d_cbiepftmd,
            suite_pa_banana2d_cbiepftmd,
            # Total order integrated exponential pushforward
            suite_pa_linear1d_toiepftmd, suite_pa_arctan1d_toiepftmd, 
            suite_pa_exp1d_toiepftmd,
            suite_pa_logistic1d_toiepftmd, suite_pa_gamma1d_toiepftmd,
            suite_pa_beta1d_toiepftmd,
            suite_pa_gumbel1d_toiepftmd, suite_pa_linear2d_toiepftmd,
            suite_pa_banana2d_toiepftmd,
            # Common basis total order integrated exponential pushforward
            suite_pa_linear1d_cbtoiepftmd, suite_pa_arctan1d_cbtoiepftmd,
            suite_pa_exp1d_cbtoiepftmd,
            suite_pa_logistic1d_cbtoiepftmd, suite_pa_gamma1d_cbtoiepftmd,
            suite_pa_beta1d_cbtoiepftmd,
            suite_pa_gumbel1d_cbtoiepftmd, suite_pa_linear2d_cbtoiepftmd,
            suite_pa_banana2d_cbtoiepftmd,

            # Integrated squared pullback
            suite_pa_linear1d_ispbtmd, suite_pa_arctan1d_ispbtmd, suite_pa_exp1d_ispbtmd,
            suite_pa_logistic1d_ispbtmd, suite_pa_gamma1d_ispbtmd, 
            suite_pa_beta1d_ispbtmd,
            suite_pa_gumbel1d_ispbtmd, suite_pa_linear2d_ispbtmd, 
            suite_pa_banana2d_ispbtmd,
            # # Common basis integrated squared pullback
            # suite_pa_linear1d_cbispbtmd, suite_pa_arctan1d_cbispbtmd, 
            # suite_pa_exp1d_cbispbtmd,
            # suite_pa_logistic1d_cbispbtmd, suite_pa_gamma1d_cbispbtmd,
            # suite_pa_beta1d_cbispbtmd,
            # suite_pa_gumbel1d_cbispbtmd, suite_pa_linear2d_cbispbtmd,
            # suite_pa_banana2d_cbispbtmd,
            # Total order integrated squared pullback
            suite_pa_linear1d_toispbtmd, suite_pa_arctan1d_toispbtmd, 
            suite_pa_exp1d_toispbtmd,
            suite_pa_logistic1d_toispbtmd, suite_pa_gamma1d_toispbtmd,
            suite_pa_beta1d_toispbtmd,
            suite_pa_gumbel1d_toispbtmd, suite_pa_linear2d_toispbtmd,
            suite_pa_banana2d_toispbtmd,
            # # Common basis total order integrated squared pullback
            # suite_pa_linear1d_cbtoispbtmd, suite_pa_arctan1d_cbtoispbtmd,
            # suite_pa_exp1d_cbtoispbtmd,
            # suite_pa_logistic1d_cbtoispbtmd, suite_pa_gamma1d_cbtoispbtmd,
            # suite_pa_beta1d_cbtoispbtmd,
            # suite_pa_gumbel1d_cbtoispbtmd, suite_pa_linear2d_cbtoispbtmd,
            # suite_pa_banana2d_cbtoispbtmd,
            # Integrated squared pushforward
            suite_pa_linear1d_ispftmd, suite_pa_arctan1d_ispftmd, suite_pa_exp1d_ispftmd,
            suite_pa_logistic1d_ispftmd, suite_pa_gamma1d_ispftmd, 
            suite_pa_beta1d_ispftmd,
            suite_pa_gumbel1d_ispftmd, suite_pa_linear2d_ispftmd, 
            suite_pa_banana2d_ispftmd,
            # # Common basis integrated squared pushforward
            # suite_pa_linear1d_cbispftmd, suite_pa_arctan1d_cbispftmd, 
            # suite_pa_exp1d_cbispftmd,
            # suite_pa_logistic1d_cbispftmd, suite_pa_gamma1d_cbispftmd,
            # suite_pa_beta1d_cbispftmd,
            # suite_pa_gumbel1d_cbispftmd, suite_pa_linear2d_cbispftmd,
            # suite_pa_banana2d_cbispftmd,
            # Total order integrated squared pushforward
            suite_pa_linear1d_toispftmd, suite_pa_arctan1d_toispftmd, 
            suite_pa_exp1d_toispftmd,
            suite_pa_logistic1d_toispftmd, suite_pa_gamma1d_toispftmd,
            suite_pa_beta1d_toispftmd,
            suite_pa_gumbel1d_toispftmd, suite_pa_linear2d_toispftmd,
            suite_pa_banana2d_toispftmd,
            # # Common basis total order integrated squared pushforward
            # suite_pa_linear1d_cbtoispftmd, suite_pa_arctan1d_cbtoispftmd,
            # suite_pa_exp1d_cbtoispftmd,
            # suite_pa_logistic1d_cbtoispftmd, suite_pa_gamma1d_cbtoispftmd,
            # suite_pa_beta1d_cbtoispftmd,
            # suite_pa_gumbel1d_cbtoispftmd, suite_pa_linear2d_cbtoispftmd,
            # suite_pa_banana2d_cbtoispftmd,
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)
    
if __name__ == '__main__':
    run_tests()
