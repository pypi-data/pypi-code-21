#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2016 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Daniele Bigoni
# E-mail: dabi@limitcycle.it
#

import unittest
import numpy as np
import numpy.random as npr
import numpy.linalg as npla

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class Functionals_DerivativeChecks(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        
        import TransportMaps.Densities as DENS
        self.dim = 2
        self.order = 3
        self.fd_eps = 1e-5
        self.qtype = 3
        self.qpar = [5]*self.dim
        self.density = DENS.StandardNormalDensity(self.dim)
        (x,w) = self.density.quadrature(self.qtype, self.qpar)
        self.x = x
        self.w = w
        self.build_tm_approx()

    def test_grad_a(self):
        import TransportMaps.FiniteDifference as FD

        approx = self.approx
        coeffs = self.coeffs
        x = self.x

        # Define transport map, gradient
        def f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.evaluate(x)
            return out
        def grad_a_f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.grad_a(x)
            return out

        # Check gradient transport map
        flag = FD.check_grad_a(f, grad_a_f, coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_grad_x_partial_xd(self):
        import TransportMaps.FiniteDifference as FD

        approx = self.approx
        coeffs = self.coeffs
        x = self.x

        # Define transport map, gradient
        def f(x, *args, **kwargs):
            out = approx.partial_xd(x, {})
            return out
        def der(x, *args, **kwargs):
            out = approx.grad_x_partial_xd(x, {})
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(f, der, x, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_hess_x_partial_xd(self):
        import TransportMaps.FiniteDifference as FD

        approx = self.approx
        coeffs = self.coeffs
        x = self.x

        # Define transport map, gradient
        def f(x, *args, **kwargs):
            out = approx.grad_x_partial_xd(x, {})
            return out
        def der(x, *args, **kwargs):
            out = approx.hess_x_partial_xd(x, {})
            return out

        # Check gradient transport map
        flag = FD.check_grad_x(f, der, x, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )

    def test_grad_a_grad_x_partial_xd(self):
        import TransportMaps.FiniteDifference as FD

        approx = self.approx
        coeffs = self.coeffs
        x = self.x

        # Define transport map, gradient
        def f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.grad_x_partial_xd(x, {})
            return out
        def grad_a_f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.grad_a_grad_x_partial_xd(x, {})
            return np.transpose(out,(0,2,1))

        # Check gradient transport map
        flag = FD.check_grad_a(f, grad_a_f, coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )
        
    def test_grad_a_hess_x_partial_xd(self):
        import TransportMaps.FiniteDifference as FD

        approx = self.approx
        coeffs = self.coeffs
        x = self.x

        # Define transport map, gradient
        def f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.hess_x_partial_xd(x, {})
            return out
        def grad_a_f(a, *args, **kwargs):
            approx.coeffs = a
            out = approx.grad_a_hess_x_partial_xd(x, {})
            return np.transpose(out,(0,2,3,1))

        # Check gradient transport map
        flag = FD.check_grad_a(f, grad_a_f, coeffs, self.fd_eps,
                               None, verbose=False)
        self.assertTrue( flag )
        
class LinearSpanFunctional( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import numpy.random as npr
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        basis_list = [S1D.HermiteProbabilistsPolynomial()] * (self.dim)
        orders_list = [self.order] * (self.dim)
        self.approx = FUNC.MonotonicLinearSpanApproximation(basis_list, spantype="full",
                                                                order_list=orders_list)
        # Set coefficients for linear map
        self.coeffs = npr.randn(self.approx.n_coeffs)/10.

class MonotonicIntegratedExponentialFunctional( object ):
    """ Linear span approximation
    """
    def build_tm_approx(self):
        import numpy.random as npr
        import SpectralToolbox.Spectral1D as S1D
        import TransportMaps as TM
        import TransportMaps.Functionals as FUNC
        basis_list = [S1D.HermiteProbabilistsPolynomial()] * (self.dim)
        orders_list = [self.order] * (self.dim - 1) + [0]
        constant = FUNC.LinearSpanApproximation(basis_list, spantype="full",
                                                                order_list=orders_list)
        basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * (self.dim)
        orders_list = [self.order] * (self.dim)
        exponential = FUNC.LinearSpanApproximation(basis_list, spantype="full",
                                                                order_list=orders_list)
        self.approx = FUNC.MonotonicIntegratedExponentialApproximation(constant, exponential)
        # Set coefficients for linear map
        self.coeffs = npr.randn(self.approx.n_coeffs)/10.

# FULL ORDER LINEAR SPAN
class OnTheFly_LinearSpanFunctional_DerivativeChecks( LinearSpanFunctional,
                                                      Functionals_DerivativeChecks ):
    pass

class OnTheFly_MonotonicIntegratedExponentialFunctional_DerivativeChecks( MonotonicIntegratedExponentialFunctional,
                                                      Functionals_DerivativeChecks ):
    pass

def build_suite(ttype='all'):
    # Full order linear span
    suite_of_lsf_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_LinearSpanFunctional_DerivativeChecks )
    suite_of_mief_dc = unittest.TestLoader().loadTestsFromTestCase(
        OnTheFly_MonotonicIntegratedExponentialFunctional_DerivativeChecks )
    # GROUP SUITES
    suites_list = []
    if ttype in ['all','serial']:
        suites_list += [ suite_of_lsf_dc, suite_of_mief_dc ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
