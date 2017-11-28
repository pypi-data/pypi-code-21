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
import numpy.linalg as npla

from TransportMaps.Distributions.Examples import InertialNavigationSystem as INS
from TransportMaps.Distributions.Examples import StochasticVolatility as SV
from TransportMaps.Algorithms import SequentialInference as ALGSI
from TransportMaps.Algorithms import Adaptivity as ALGADPT
import TransportMaps.Distributions as DIST
import TransportMaps.Maps as MAPS
import TransportMaps.Diagnostics as DIAG
import TransportMaps as TM

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class LinearGaussianSequentialInferenceTest(unittest.TestCase):
    def setUp(self):
        npr.seed(1)

    def test(self):
        nsteps = 96

        # Generate data
        T,Z,Y = INS.generate_data(nsteps)
        for n in range(20,29):
            Y[n] = None
            
        # Run smoother
        pi_prior = INS.Prior()
        pi_trans = INS.Transition()
        SMT = ALGSI.LinearSmoother(lag=None)
        for n in range(nsteps+1):
            # Define log-likelihood
            if Y[n] is None: # Missing data
                ll = None
            else: 
                ll = INS.LogLikelihood(Y[n])
            # Define transition / prior
            if n > 0: 
                pin = pi_trans
            else:
                pin = pi_prior
            # Assimilation
            SMT.assimilate(pin, ll)

        M = SMT.smoothing_map
        pi = SMT.pi
        cov_list = SMT.smoothing_covariance_list
        
        # Test variance diagnostic
        pull_M_pi = DIST.PullBackTransportMapDistribution(M, pi)
        rho = DIST.StandardNormalDistribution(pi.dim)
        var_seq = DIAG.variance_approx_kl(rho, pull_M_pi, qtype=0, qparams=1000)
        self.assertTrue( var_seq < 1e-14 )
            
        # Compare full covariances
        pi_hx = npla.inv(-pi.hess_x_log_pdf(np.zeros((1,pi.dim)))[0,:,:])
        gx_M = M.grad_x(np.zeros((1,pi.dim)))[0,:,:]
        M_hx = np.dot(gx_M, gx_M.T)
        self.assertTrue( np.allclose(pi_hx, M_hx) )

        # Compare smoothing covariances
        for i, cov in enumerate(cov_list):
            cx = pi_hx[i*6:(i+1)*6,i*6:(i+1)*6]
            self.assertTrue( np.allclose(cx, cov) )

class NonLinearStocVolSequentialInferenceTest(unittest.TestCase):
    def setUp(self):
        npr.seed(1)

    def test(self):
        nsteps = 10

        # Generate data
        mu = -.5
        phi = .95
        sigma = 0.25
        yB, ZA = SV.generate_data(nsteps, mu, sigma, phi)

        # Set up model
        is_mu_h = True
        is_sigma_h = False
        is_phi_h = True
        pi_hyper = SV.PriorHyperParameters(is_mu_h, is_sigma_h, is_phi_h, 1)
        mu_h = SV.IdentityFunction()
        phi_h = SV.F_phi(3.,1.)
        sigma_h = SV.ConstantFunction(0.25)
        pi_ic = SV.PriorDynamicsInitialConditions(
            is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)
        pi_trans = SV.PriorDynamicsTransition(
            is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)

        # Run smoother
        INT = ALGSI.TransportMapsSmoother(pi_hyper)
        for n, yt in enumerate(yB):
            if yt is None: ll = None # Missing data
            else: ll = SV.LogLikelihood(yt, is_mu_h, is_sigma_h, is_phi_h)
            if n == 0: pin = pi_ic # Prior initial conditions
            else: pin = pi_trans   # Prior transition dynamics
            # Transport map specification
            if n == 0: dim_tm = 3
            else: dim_tm = 4
            tm = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
                dim=dim_tm, order=3)
            # Solution builder (link to standard adaptivity algorithm, i.e. no adaptivity)
            builder = ALGADPT.KullbackLeiblerBuilder()
            # Solution parameters
            solve_params = {'qtype': 3, 'qparams': [7]*dim_tm,
                            'tol': 1e-3}
            # Regression map specification
            hyper_tm = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
                dim=pi_hyper.dim, order=3)
            # Regression parameters
            rho_hyper = DIST.StandardNormalDistribution(pi_hyper.dim)
            reg_params = {'d': rho_hyper, 'qtype': 3,
                          'qparams': [7]*pi_hyper.dim,
                          'tol': 1e-4}
            # Assimilation
            INT.assimilate(pin, ll,
                           tm=tm, solve_params=solve_params,
                           builder=builder,
                           hyper_tm=hyper_tm, regression_params=reg_params)

        # Diagnostic: compare to Laplace approximation
        rho = DIST.StandardNormalDistribution(INT.pi.dim)
        
        lpl = TM.laplace_approximation(INT.pi)
        lpl_tm = MAPS.LinearTransportMap.build_from_Gaussian(lpl)
        pull_lpl_pi = DIST.PullBackTransportMapDistribution(lpl_tm, INT.pi)
        var_lpl = DIAG.variance_approx_kl(rho, pull_lpl_pi, qtype=0, qparams=1000)
        
        pull_T_pi = DIST.PullBackTransportMapDistribution(INT.smoothing_map, INT.pi)
        var_seq = DIAG.variance_approx_kl(rho, pull_T_pi, qtype=0, qparams=1000)

        assert(var_seq < var_lpl)

def build_suite(ttype='all'):
    suite_lgsi = unittest.TestLoader().loadTestsFromTestCase(
        LinearGaussianSequentialInferenceTest)
    suite_nlsvsi = unittest.TestLoader().loadTestsFromTestCase(
        NonLinearStocVolSequentialInferenceTest)

    # Group suites
    suites_list = []
    if ttype in ['all', 'serial']:
        suites_list += [ suite_lgsi, suite_nlsvsi ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
