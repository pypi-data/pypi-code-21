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
import numpy.random as npr

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class LaplaceApproximation(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.tol = 1e-8

    def compute_laplace(self, setup, test):
        import numpy as np
        import numpy.linalg as npla
        import TransportMaps as TM

        distribution = test['target_distribution']

        # Build Laplace approximation
        d_laplace = TM.laplace_approximation(distribution, None, tol=self.tol)

        # Compare mean
        self.assertTrue( npla.norm(distribution.mu - d_laplace.mu) <= self.tol )

        # Compute KL divergence between the two
        qtype = 3
        qparams = [10]*distribution.dim
        kldiv = TM.kl_divergence(distribution, d_laplace, None, None,
                                 qtype=qtype, qparams=qparams)
        self.assertTrue( np.abs(kldiv) <= 1e-2 )

    def test_linear1d(self):
        import TransportMaps.tests.TestFunctions as TF
        title, setup, Tparams = TF.get(0)
        self.compute_laplace(setup, Tparams)

    def test_linear2d(self):
        import TransportMaps.tests.TestFunctions as TF
        title, setup, Tparams = TF.get(9)
        self.compute_laplace(setup, Tparams)

def build_suite(ttype='all'):
    suite_laplace_approx = unittest.TestLoader().loadTestsFromTestCase( LaplaceApproximation )
    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list = [ suite_laplace_approx ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites


def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
