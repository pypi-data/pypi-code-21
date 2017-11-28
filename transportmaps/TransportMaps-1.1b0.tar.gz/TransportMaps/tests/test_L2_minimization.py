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

class L2_minimization(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.reg = {'type': 'L2',
                    'alpha': 1e-7}
        self.tol = 1e-3
        self.dim = 2
        self.order = 3
        self.span = 'total'
        self.batch_size_list = [(None,None,None),(None,None,5)]

    def test_L2_minimization(self):
        import TransportMaps as TM
        import TransportMaps.Distributions as DIST

        # Approximate
        qtype = 3
        qparams = [10] * self.dim
        d = DIST.StandardNormalDistribution(self.dim)

        log = self.tm_approx.regression(self.target, d=d, qtype=qtype, qparams=qparams,
                                        regularization=self.reg, tol=self.tol,
                                        batch_size_list=self.batch_size_list,
                                        mpi_pool_list=[self.mpi_pool]*self.dim)

        # Check L2 accuracy
        (x,w) = d.quadrature(qtype,qparams)
        t1 = self.target.evaluate(x)
        t2 = self.tm_approx.evaluate(x)
        misfit = np.sqrt( np.sum((t1-t2)**2, axis=1) )
        l2_misfit = np.dot(misfit, w)
        assertion = l2_misfit < 10 * self.dim * self.tol
        if not assertion:
            print("Misfit > 10 * d * tol : %e > %e" % (l2_misfit, 10 * self.dim * self.tol))
        self.assertTrue( assertion )

#
# Monotone types
#
class IntExp_L2_min(L2_minimization):
    def setUp(self):
        import TransportMaps as TM
        super(IntExp_L2_min,self).setUp()
        # Generate a random integrated exponential map
        self.target = TM.Default_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, self.span)
        self.target.coeffs = np.random.randn( self.target.n_coeffs ) / 10. 
        # Generate approximation
        self.tm_approx = TM.Default_IsotropicIntegratedExponentialTriangularTransportMap(
            self.dim, self.order, self.span)
        self.ders = 2
class IntSq_L2_min(L2_minimization):
    def setUp(self):
        import TransportMaps as TM
        super(IntSq_L2_min,self).setUp()
        # Generate a random integrated exponential map
        self.target = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
            self.dim, self.order, self.span)
        coeffs = self.target.get_identity_coeffs()
        self.target.coeffs = coeffs + np.random.randn( self.target.n_coeffs ) / 10. 
        # Generate approximation
        self.tm_approx = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
            self.dim, self.order, self.span)
        self.ders = 2
class LinSpan_L2_min(L2_minimization):
    def setUp(self):
        import TransportMaps as TM
        super(LinSpan_L2_min,self).setUp()
        # Generate a random integrated exponential map
        self.target = TM.Default_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, self.span)
        self.target.coeffs = np.random.randn( self.target.n_coeffs ) / 10. 
        # Generate approximation
        self.tm_approx = TM.Default_IsotropicLinearSpanTriangularTransportMap(
            self.dim, self.order, self.span)
        self.ders = 1

#
# Serial/Parallel    
#
class Serial_IntExp_L2_min(IntExp_L2_min):
    def setUp(self):
        super(Serial_IntExp_L2_min, self).setUp()
        self.mpi_pool = None
class Serial_IntSq_L2_min(IntSq_L2_min):
    def setUp(self):
        super(Serial_IntSq_L2_min, self).setUp()
        self.mpi_pool = None
class Serial_LinSpan_L2_min(LinSpan_L2_min):
    def setUp(self):
        super(Serial_LinSpan_L2_min, self).setUp()
        self.mpi_pool = None
class Parallel_IntExp_L2_min(IntExp_L2_min):
    def setUp(self):
        super(Parallel_IntExp_L2_min, self).setUp()
        import TransportMaps as TM
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)
class Parallel_IntSq_L2_min(IntSq_L2_min):
    def setUp(self):
        super(Parallel_IntSq_L2_min, self).setUp()
        import TransportMaps as TM
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)
class Parallel_LinSpan_L2_min(LinSpan_L2_min):
    def setUp(self):
        super(Parallel_LinSpan_L2_min, self).setUp()
        import TransportMaps as TM
        import_set = set([ ('numpy', 'np') ])
        self.mpi_pool = TM.get_mpi_pool()
        self.mpi_pool.start(2, import_set)
    def tearDown(self):
        import time
        self.mpi_pool.stop()
        time.sleep(0.2)
        
def build_suite(ttype='all'):
    suite_se_ie_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Serial_IntExp_L2_min )
    suite_se_is_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Serial_IntSq_L2_min )
    suite_se_ls_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Serial_LinSpan_L2_min )
    suite_pa_ie_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_IntExp_L2_min )
    suite_pa_is_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_IntSq_L2_min )
    suite_pa_ls_l2_min = unittest.TestLoader().loadTestsFromTestCase(
        Parallel_LinSpan_L2_min )

    # GROUP SUITES
    # Serial
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [
            suite_se_ie_l2_min, suite_se_is_l2_min, suite_se_ls_l2_min
        ]
    if ttype in ['all','parallel'] and MPI_SUPPORT:
        # Parallel
        suites_list += [
            suite_pa_ie_l2_min, suite_pa_is_l2_min, suite_pa_ls_l2_min
        ]

    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)
    
if __name__ == '__main__':
    run_tests()
