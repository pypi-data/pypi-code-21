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

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class KL_divergence_minimization(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        import TransportMaps as TM
        self.reg = {'type': 'L2',
                    'alpha': 1e-3}
        self.tol = 1e-4
        self.order = 3
        self.span = 'total'
        if self.monotone == 'linspan':
            self.tm_approx = TM.Default_IsotropicMonotonicLinearSpanTriangularTransportMap(
                self.setup['dim'], self.order, self.span)
        elif self.monotone == 'intexp':
            self.tm_approx = TM.Default_IsotropicIntegratedExponentialTriangularTransportMap(
                self.setup['dim'], self.order, self.span)
        elif self.monotone == 'intsq':
            self.tm_approx = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
                self.setup['dim'], self.order, self.span)

    def test_direct_t(self):
        import TransportMaps.Distributions as DIST

        qtype = 3
        qparams = [10] * self.setup['dim']
        tm_approx = self.tm_approx

        # Build distribution T_\sharp \pi
        tm_distribution = DIST.PushForwardTransportMapDistribution(
            tm_approx, self.Tparams['base_distribution'])
        # Target distribution to be approximated L^\sharp \pi_{\rm tar}
        target_distribution = DIST.PullBackTransportMapDistribution(
            self.Tparams['support_map'], self.Tparams['target_distribution'])

        # SOLVE
        log_entry_solve = tm_distribution.minimize_kl_divergence(
            target_distribution, qtype=qtype, qparams=qparams,
            regularization=self.reg, tol=self.tol, ders=self.ders,
            mpi_pool=self.mpi_pool)

    def test_fungrad_direct_t(self):
        import TransportMaps.Distributions as DIST

        qtype = 3
        qparams = [10] * self.setup['dim']
        tm_approx = self.tm_approx

        # Build distribution T_\sharp \pi
        tm_distribution = DIST.PushForwardTransportMapDistribution(
            tm_approx, self.Tparams['base_distribution'])
        # Target distribution to be approximated L^\sharp \pi_{\rm tar}
        target_distribution = DIST.PullBackTransportMapDistribution(
            self.Tparams['support_map'], self.Tparams['target_distribution'])

        # SOLVE
        log_entry_solve = tm_distribution.minimize_kl_divergence(
            target_distribution, qtype=qtype, qparams=qparams,
            regularization=self.reg, tol=self.tol, ders=1, fungrad=True,
            mpi_pool=self.mpi_pool)

    def test_inverse_from_samples_t(self):
        import TransportMaps.Distributions as DIST

        qtype = 0
        qparams = 100
        tm_approx = self.tm_approx
        
        # Construct distribution
        # Target distribution to be approximated L^\sharp \pi_{\rm tar}
        target_distribution = DIST.PullBackTransportMapDistribution(
            self.Tparams['support_map'], self.Tparams['target_distribution'])
        # Distribution T_\sharp L^\sharp \pi_{\rm tar}
        tm_distribution = DIST.PushForwardTransportMapDistribution(
            tm_approx, target_distribution)

        # SOLVE
        log_entry_solve = tm_distribution.minimize_kl_divergence(
            self.Tparams['base_distribution'], qtype=qtype, qparams=qparams,
            regularization=self.reg, tol=self.tol, ders=self.ders,
            mpi_pool=[self.mpi_pool]*self.tm_approx.dim)

    def test_inverse_t(self):
        import TransportMaps.Distributions as DIST

        qtype = 3
        qparams = [10] * self.setup['dim']
        self.ders = 1
        tm_approx = self.tm_approx
        
        # Construct distribution
        # Distribution T^\sharp \pi
        tm_distribution = DIST.PullBackTransportMapDistribution(
            tm_approx, self.Tparams['base_distribution'])
        # Target distribution to be approximated L^\sharp \pi_{\rm tar}
        target_distribution = DIST.PullBackTransportMapDistribution(
            self.Tparams['support_map'], self.Tparams['target_distribution'])

        # SOLVE
        log_entry_solve = tm_distribution.minimize_kl_divergence(
            self.Tparams['base_distribution'], qtype=qtype, qparams=qparams,
            regularization=self.reg, tol=self.tol, ders=self.ders,
            mpi_pool=self.mpi_pool)

#
# Monotone types
#
class IntExp_KL_div_min(KL_divergence_minimization):
    def setUp(self):
        self.monotone = 'intexp'
        super(IntExp_KL_div_min,self).setUp()
        self.ders = 2
class IntSq_KL_div_min(KL_divergence_minimization):
    def setUp(self):
        self.monotone = 'intsq'
        super(IntSq_KL_div_min,self).setUp()
        self.ders = 2
class LinSpan_KL_div_min(KL_divergence_minimization):
    def setUp(self):
        self.monotone = 'linspan'
        super(LinSpan_KL_div_min,self).setUp()
        self.ders = 1

#
# Serial/Parallel
#
class Serial_IntExp_KL_div_min(IntExp_KL_div_min):
    def setUp(self):
        super(Serial_IntExp_KL_div_min,self).setUp()
        self.mpi_pool = None
class Serial_IntSq_KL_div_min(IntSq_KL_div_min):
    def setUp(self):
        super(Serial_IntSq_KL_div_min,self).setUp()
        self.mpi_pool = None
class Serial_LinSpan_KL_div_min(LinSpan_KL_div_min):
    def setUp(self):
        super(Serial_LinSpan_KL_div_min,self).setUp()
        self.mpi_pool = None
class Parallel_IntExp_KL_div_min(IntExp_KL_div_min):
    def setUp(self):
        import TransportMaps as TM
        super(Parallel_IntExp_KL_div_min,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)
class Parallel_IntSq_KL_div_min(IntSq_KL_div_min):
    def setUp(self):
        import TransportMaps as TM
        super(Parallel_IntSq_KL_div_min,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)
class Parallel_LinSpan_KL_div_min(LinSpan_KL_div_min):
    def setUp(self):
        import TransportMaps as TM
        super(Parallel_LinSpan_KL_div_min,self).setUp()
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)

#
# Specific tests
#
class Linear1D_TMD_TestCase(object):    
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(0)

class ArcTan1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(2)

class Exp1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(3)

class Logistic1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(4)

class Gamma1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(5)

class Beta1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(6)

class Gumbel1D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(7)

class Linear2D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(9)

class Banana2D_TMD_TestCase(object):
    def setUp_test_case(self):
        import TransportMaps.tests.TestFunctions as TF
        title, self.setup, self.Tparams = TF.get(10)

#
# Serial Integrated Exponential tests
#
class Linear1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Linear1D_se_IE_KL_div_min,self).setUp()

class ArcTan1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_se_IE_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_se_IE_KL_div_min,self).setUp()

class Exp1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Exp1D_se_IE_KL_div_min,self).setUp()

class Logistic1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Logistic1D_se_IE_KL_div_min,self).setUp()

class Gamma1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Gamma1D_se_IE_KL_div_min,self).setUp()

class Beta1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Beta1D_se_IE_KL_div_min,self).setUp()

class Gumbel1D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_se_IE_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_se_IE_KL_div_min,self).setUp()

class Linear2D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_se_IE_KL_div_min,self).setUp_test_case()
        super(Linear2D_se_IE_KL_div_min,self).setUp()

class Banana2D_se_IE_KL_div_min( Serial_IntExp_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_se_IE_KL_div_min,self).setUp_test_case()
        super(Banana2D_se_IE_KL_div_min,self).setUp()

#
# Serial Integrated Squared tests
#
class Linear1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Linear1D_se_SQ_KL_div_min,self).setUp()

class ArcTan1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_se_SQ_KL_div_min,self).setUp()

class Exp1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Exp1D_se_SQ_KL_div_min,self).setUp()

class Logistic1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Logistic1D_se_SQ_KL_div_min,self).setUp()

class Gamma1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Gamma1D_se_SQ_KL_div_min,self).setUp()

class Beta1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Beta1D_se_SQ_KL_div_min,self).setUp()

class Gumbel1D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_se_SQ_KL_div_min,self).setUp()

class Linear2D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Linear2D_se_SQ_KL_div_min,self).setUp()

class Banana2D_se_SQ_KL_div_min( Serial_IntSq_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_se_SQ_KL_div_min,self).setUp_test_case()
        super(Banana2D_se_SQ_KL_div_min,self).setUp()

        
#
# Serial Linear Span tests
#
class Linear1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Linear1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class ArcTan1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_se_LS_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Exp1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Exp1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Logistic1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Logistic1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Gamma1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Gamma1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Beta1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Beta1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Gumbel1D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_se_LS_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Linear2D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_se_LS_KL_div_min,self).setUp_test_case()
        super(Linear2D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Banana2D_se_LS_KL_div_min( Serial_LinSpan_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_se_LS_KL_div_min,self).setUp_test_case()
        super(Banana2D_se_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

#
# Parallel Integrated Exponential tests
#
class Linear1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Linear1D_pa_IE_KL_div_min,self).setUp()

class ArcTan1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_pa_IE_KL_div_min,self).setUp()

class Exp1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Exp1D_pa_IE_KL_div_min,self).setUp()

class Logistic1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Logistic1D_pa_IE_KL_div_min,self).setUp()

class Gamma1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Gamma1D_pa_IE_KL_div_min,self).setUp()

class Beta1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Beta1D_pa_IE_KL_div_min,self).setUp()

class Gumbel1D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_pa_IE_KL_div_min,self).setUp()

class Linear2D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Linear2D_pa_IE_KL_div_min,self).setUp()

class Banana2D_pa_IE_KL_div_min( Parallel_IntExp_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_pa_IE_KL_div_min,self).setUp_test_case()
        super(Banana2D_pa_IE_KL_div_min,self).setUp()

#
# Parallel Integrated Squared tests
#
class Linear1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Linear1D_pa_SQ_KL_div_min,self).setUp()

class ArcTan1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_pa_SQ_KL_div_min,self).setUp()

class Exp1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Exp1D_pa_SQ_KL_div_min,self).setUp()

class Logistic1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Logistic1D_pa_SQ_KL_div_min,self).setUp()

class Gamma1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Gamma1D_pa_SQ_KL_div_min,self).setUp()

class Beta1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Beta1D_pa_SQ_KL_div_min,self).setUp()

class Gumbel1D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_pa_SQ_KL_div_min,self).setUp()

class Linear2D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Linear2D_pa_SQ_KL_div_min,self).setUp()

class Banana2D_pa_SQ_KL_div_min( Parallel_IntSq_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_pa_SQ_KL_div_min,self).setUp_test_case()
        super(Banana2D_pa_SQ_KL_div_min,self).setUp()

#
# Parallel Linear Span tests
#
class Linear1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Linear1D_TMD_TestCase ):
    def setUp(self):
        super(Linear1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Linear1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class ArcTan1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 ArcTan1D_TMD_TestCase ):
    def setUp(self):
        super(ArcTan1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(ArcTan1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Exp1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                              Exp1D_TMD_TestCase ):
    def setUp(self):
        super(Exp1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Exp1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Logistic1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                   Logistic1D_TMD_TestCase ):
    def setUp(self):
        super(Logistic1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Logistic1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Gamma1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Gamma1D_TMD_TestCase ):
    def setUp(self):
        super(Gamma1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Gamma1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Beta1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Beta1D_TMD_TestCase ):
    def setUp(self):
        super(Beta1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Beta1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Gumbel1D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Gumbel1D_TMD_TestCase ):
    def setUp(self):
        super(Gumbel1D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Gumbel1D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Linear2D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Linear2D_TMD_TestCase ):
    def setUp(self):
        super(Linear2D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Linear2D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

class Banana2D_pa_LS_KL_div_min( Parallel_LinSpan_KL_div_min,
                                 Banana2D_TMD_TestCase ):
    def setUp(self):
        super(Banana2D_pa_LS_KL_div_min,self).setUp_test_case()
        super(Banana2D_pa_LS_KL_div_min,self).setUp()
    @unittest.skip("Not implemented")
    def test_inverse_t(self):
        pass

def build_suite(ttype='all'):
    # Serial integrated exponentials
    suite_Linear1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_se_IE_KL_div_min )
    suite_ArcTan1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_se_IE_KL_div_min )
    suite_Exp1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_se_IE_KL_div_min )
    suite_Logistic1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_se_IE_KL_div_min )
    suite_Gamma1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_se_IE_KL_div_min )
    suite_Beta1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_se_IE_KL_div_min )
    suite_Gumbel1d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_se_IE_KL_div_min )
    suite_Linear2d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_se_IE_KL_div_min )
    suite_Banana2d_se_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_se_IE_KL_div_min )
    # Serial integrated squared
    suite_Linear1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_se_SQ_KL_div_min )
    suite_ArcTan1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_se_SQ_KL_div_min )
    suite_Exp1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_se_SQ_KL_div_min )
    suite_Logistic1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_se_SQ_KL_div_min )
    suite_Gamma1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_se_SQ_KL_div_min )
    suite_Beta1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_se_SQ_KL_div_min )
    suite_Gumbel1d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_se_SQ_KL_div_min )
    suite_Linear2d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_se_SQ_KL_div_min )
    suite_Banana2d_se_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_se_SQ_KL_div_min )
    # Serial linear span
    suite_Linear1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_se_LS_KL_div_min )
    suite_ArcTan1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_se_LS_KL_div_min )
    suite_Exp1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_se_LS_KL_div_min )
    suite_Logistic1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_se_LS_KL_div_min )
    suite_Gamma1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_se_LS_KL_div_min )
    suite_Beta1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_se_LS_KL_div_min )
    suite_Gumbel1d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_se_LS_KL_div_min )
    suite_Linear2d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_se_LS_KL_div_min )
    suite_Banana2d_se_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_se_LS_KL_div_min )
    # Parallel integrated exponentials
    suite_Linear1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_pa_IE_KL_div_min )
    suite_ArcTan1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_pa_IE_KL_div_min )
    suite_Exp1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_pa_IE_KL_div_min )
    suite_Logistic1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_pa_IE_KL_div_min )
    suite_Gamma1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_pa_IE_KL_div_min )
    suite_Beta1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_pa_IE_KL_div_min )
    suite_Gumbel1d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_pa_IE_KL_div_min )
    suite_Linear2d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_pa_IE_KL_div_min )
    suite_Banana2d_pa_ie_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_pa_IE_KL_div_min )
    # Parallel integrated squared
    suite_Linear1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_pa_SQ_KL_div_min )
    suite_ArcTan1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_pa_SQ_KL_div_min )
    suite_Exp1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_pa_SQ_KL_div_min )
    suite_Logistic1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_pa_SQ_KL_div_min )
    suite_Gamma1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_pa_SQ_KL_div_min )
    suite_Beta1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_pa_SQ_KL_div_min )
    suite_Gumbel1d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_pa_SQ_KL_div_min )
    suite_Linear2d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_pa_SQ_KL_div_min )
    suite_Banana2d_pa_sq_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_pa_SQ_KL_div_min )
    # Parallel linear span
    suite_Linear1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear1D_pa_LS_KL_div_min )
    suite_ArcTan1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        ArcTan1D_pa_LS_KL_div_min )
    suite_Exp1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Exp1D_pa_LS_KL_div_min )
    suite_Logistic1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Logistic1D_pa_LS_KL_div_min )
    suite_Gamma1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gamma1D_pa_LS_KL_div_min )
    suite_Beta1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Beta1D_pa_LS_KL_div_min )
    suite_Gumbel1d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Gumbel1D_pa_LS_KL_div_min )
    suite_Linear2d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Linear2D_pa_LS_KL_div_min )
    suite_Banana2d_pa_ls_kl_div_min = unittest.TestLoader().loadTestsFromTestCase(
        Banana2D_pa_LS_KL_div_min )

    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list = [
            # Serial integrated exponential
            suite_Linear1d_se_ie_kl_div_min, suite_ArcTan1d_se_ie_kl_div_min,
            suite_Exp1d_se_ie_kl_div_min, suite_Logistic1d_se_ie_kl_div_min,
            suite_Gamma1d_se_ie_kl_div_min, suite_Beta1d_se_ie_kl_div_min,
            suite_Gumbel1d_se_ie_kl_div_min, suite_Linear2d_se_ie_kl_div_min,
            suite_Banana2d_se_ie_kl_div_min,
            # Serial integrated squared
            suite_Linear1d_se_sq_kl_div_min, suite_ArcTan1d_se_sq_kl_div_min,
            suite_Exp1d_se_sq_kl_div_min, suite_Logistic1d_se_sq_kl_div_min,
            suite_Gamma1d_se_sq_kl_div_min, suite_Beta1d_se_sq_kl_div_min,
            suite_Gumbel1d_se_sq_kl_div_min, suite_Linear2d_se_sq_kl_div_min,
            suite_Banana2d_se_sq_kl_div_min,
            # Serial linear span
            suite_Linear1d_se_ls_kl_div_min, suite_ArcTan1d_se_ls_kl_div_min,
            suite_Exp1d_se_ls_kl_div_min, suite_Logistic1d_se_ls_kl_div_min,
            suite_Gamma1d_se_ls_kl_div_min, suite_Beta1d_se_ls_kl_div_min,
            suite_Gumbel1d_se_ls_kl_div_min, suite_Linear2d_se_ls_kl_div_min,
            suite_Banana2d_se_ls_kl_div_min,
        ]
    # Parallel
    if ttype in ['all','parallel'] and MPI_SUPPORT:
        suites_list += [
            # Parallel integrated exponential
            suite_Linear1d_pa_ie_kl_div_min, suite_ArcTan1d_pa_ie_kl_div_min,
            suite_Exp1d_pa_ie_kl_div_min, suite_Logistic1d_pa_ie_kl_div_min,
            suite_Gamma1d_pa_ie_kl_div_min, suite_Beta1d_pa_ie_kl_div_min,
            suite_Gumbel1d_pa_ie_kl_div_min, suite_Linear2d_pa_ie_kl_div_min,
            suite_Banana2d_pa_ie_kl_div_min,
            # Parallel integrated squared
            suite_Linear1d_pa_sq_kl_div_min, suite_ArcTan1d_pa_sq_kl_div_min,
            suite_Exp1d_pa_sq_kl_div_min, suite_Logistic1d_pa_sq_kl_div_min,
            suite_Gamma1d_pa_sq_kl_div_min, suite_Beta1d_pa_sq_kl_div_min,
            suite_Gumbel1d_pa_sq_kl_div_min, suite_Linear2d_pa_sq_kl_div_min,
            suite_Banana2d_pa_sq_kl_div_min,
            # Parallel linear span
            suite_Linear1d_pa_ls_kl_div_min, suite_ArcTan1d_pa_ls_kl_div_min,
            suite_Exp1d_pa_ls_kl_div_min, suite_Logistic1d_pa_ls_kl_div_min,
            suite_Gamma1d_pa_ls_kl_div_min, suite_Beta1d_pa_ls_kl_div_min,
            suite_Gumbel1d_pa_ls_kl_div_min, suite_Linear2d_pa_ls_kl_div_min,
            suite_Banana2d_pa_ls_kl_div_min
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='serial'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
