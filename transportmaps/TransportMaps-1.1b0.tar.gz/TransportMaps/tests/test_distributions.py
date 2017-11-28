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
from scipy import stats

import TransportMaps as TM
import TransportMaps.Likelihoods as LKL
import TransportMaps.Maps as MAPS
import TransportMaps.Distributions as DIST
import TransportMaps.Distributions.Inference as INFDIST
import TransportMaps.Distributions.Decomposable as DECDIST
import TransportMaps.Distributions.Examples as DIST_EX
import TransportMaps.Distributions.Examples.StochasticVolatility as SV
from TransportMaps import FiniteDifference as FD

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class DistributionTest(unittest.TestCase):

    def setUp(self):
        npr.seed(5)
        # Defined in subclasses
        self.d = self.get_d()
        self.distribution = self.get_distribution()
        self.sampling_d = self.get_sampling_distribution()
        self.integ = self.get_analytic_integral()
        self.f = self.get_test_function()
        self.mc_eps = self.get_mc_eps()
        self.quad_eps = self.get_quad_eps()

    def get_d(self):
        raise NotImplementedError("Define the dimension in sub-class")

    def get_sampling_distribution(self):
        return self.distribution # Default is the same

    def get_distribution(self):
        raise NotImplementedError("Define the distribution in sub-class")

    def get_analytic_integral(self):
        r""" Value :math:`\mathbb{E}_\pi[x]`
        """
        raise NotImplementedError("Define the analytic integral with respect " +
                                  "to the distribution sub-class")

    def get_test_function(self):
        raise NotImplementedError("Define the test function in sub-class")

    def get_mc_eps(self):
        raise NotImplementedError("Define eps for mc test in sub-class")

    def get_quad_eps(self):
        raise NotImplementedError("Define eps for quadrature tests in sub-class")

    def test_rvs(self):
        n = 100
        ninc = 5
        success = False
        nit = 0
        while not success and nit < ninc:
            n *= 10
            x = self.sampling_d.rvs(n)
            intapp = np.sum(self.f(x))/float(n)
            success = np.isclose(intapp,self.integ,atol=self.mc_eps)
            nit += 1
        self.assertTrue(success)

    def test_log_pdf(self):
        n = 100
        x = self.sampling_d.rvs(n)
        pdf = self.distribution.pdf(x)
        log_pdf = self.distribution.log_pdf(x)
        self.assertTrue( np.allclose( np.log(pdf), log_pdf ) )

    def test_grad_x_log_pdf(self):
        n = 100
        dx = 1e-5
        x = self.sampling_d.rvs(n)
        gxlp_exa = self.distribution.grad_x_log_pdf(x)
        gxlp_fd = FD.grad_x_fd(self.distribution.log_pdf, x, dx, None)
        self.assertTrue( np.allclose(gxlp_fd, gxlp_exa, rtol=50*dx, atol=10*dx) )

    def test_hess_x_log_pdf(self):
        n = 100
        dx = 1e-5
        x = self.sampling_d.rvs(n) / 5. # Closer to 0 finite difference works better.
        hxlp_exa = self.distribution.hess_x_log_pdf(x)
        hxlp_fd = FD.grad_x_fd(self.distribution.grad_x_log_pdf, x, dx, None)
        self.assertTrue( np.allclose(hxlp_fd, hxlp_exa, rtol=50*dx, atol=10*dx) )

    def test_mean_log_pdf(self):
        n = 100
        ninc = 5
        success = False
        nit = 0
        while not success and nit < ninc:
            n *= 10
            x = self.sampling_d.rvs(n)
            samps = self.distribution.log_pdf(x)
            intapp = np.sum(samps)/float(n)
            success = np.isclose(intapp, self.distribution.mean_log_pdf(),
                                 atol=self.mc_eps)
            nit += 1
        self.assertTrue(success)

class ConditionalDistributionTest(unittest.TestCase):

    def setUp(self):
        npr.seed(5)
        # Defined in subclasses
        self.distribution = self.get_distribution()
        self.dx = self.distribution.dim
        self.dy = self.distribution.dim_y
        self.d = self.get_d()
        self.sampling_d = self.get_sampling_distribution()

    def get_d(self):
        return self.dx + self.dy

    def get_sampling_distribution(self):
        return DIST.StandardNormalDistribution(self.get_d())

    def get_distribution(self):
        raise NotImplementedError("Define the distribution in sub-class")

    def test_log_pdf(self):
        n = 100
        x = self.sampling_d.rvs(n)
        xin = x[:,:self.dx]
        yin = x[:,self.dx:]
        pdf = self.distribution.pdf(xin, yin)
        log_pdf = self.distribution.log_pdf(xin, yin)
        self.assertTrue( np.allclose( np.log(pdf), log_pdf ) )

    def test_grad_x_log_pdf(self):
        n = 100
        dx = 1e-5
        x = self.sampling_d.rvs(n)
        xin = x[:,:self.dx]
        yin = x[:,self.dx:]
        gxlp_exa = self.distribution.grad_x_log_pdf(xin, yin)
        def f(x, *args):
            xin = x[:,:self.dx]
            yin = x[:,self.dx:]
            return self.distribution.log_pdf(xin, yin)
        gxlp_fd = FD.grad_x_fd(f, x, dx, None)
        self.assertTrue( np.allclose(gxlp_fd, gxlp_exa, rtol=50*dx, atol=10*dx) )

    def test_hess_x_log_pdf(self):
        n = 100
        dx = 1e-5
        x = self.sampling_d.rvs(n) / 5. # Closer to 0 finite difference works better.
        xin = x[:,:self.dx]
        yin = x[:,self.dx:]
        hxlp_exa = self.distribution.hess_x_log_pdf(xin, yin)
        def f(x, *args):
            xin = x[:,:self.dx]
            yin = x[:,self.dx:]
            return self.distribution.grad_x_log_pdf(xin, yin)
        hxlp_fd = FD.grad_x_fd(f, x, dx, None)
        self.assertTrue( np.allclose(hxlp_fd, hxlp_exa, rtol=50*dx, atol=10*dx) )
        
class GaussianDistributionSigmaTests(DistributionTest):

    def get_distribution(self):
        mu = stats.norm().rvs(self.d)
        S = stats.norm().rvs(self.d**2).reshape((self.d,self.d))
        sig = np.dot(S.T, S)
        return DIST.GaussianDistribution(mu, sig)    

    def get_d(self):
        return 5

    def get_test_function(self):
        f = lambda x: np.sum(x, axis=0)
        return f

    def get_analytic_integral(self):
        return np.sum(self.distribution.mu)

    def get_mc_eps(self):
        return 1e-2

    def get_quad_eps(self):
        return 1e-10

    def test_gauss_quadrature(self):
        order = 1
        success = 0
        maxord = 20
        while not success and order <= maxord:
            (x,w) = self.distribution.quadrature(3, [order]*self.d)
            intapp = np.dot(self.f(x.T), w)
            success = np.isclose(intapp,self.integ,atol=self.quad_eps)
            order += 1
        self.assertTrue(success)

class GaussianDistributionPrecisionTests(DistributionTest):

    def get_distribution(self):
        mu = stats.norm().rvs(self.d)
        S = stats.norm().rvs(self.d**2).reshape((self.d,self.d))
        sig = np.dot(S.T, S)
        prec = npla.solve(sig, np.eye(self.d))
        return DIST.GaussianDistribution(mu, precision=prec)    

    def get_d(self):
        return 5

    def get_test_function(self):
        f = lambda x: np.sum(x, axis=0)
        return f

    def get_analytic_integral(self):
        return np.sum(self.distribution.mu)

    def get_mc_eps(self):
        return 1e-2

    def get_quad_eps(self):
        return 1e-10

    def test_gauss_quadrature(self):
        order = 1
        success = 0
        maxord = 20
        while not success and order <= maxord:
            (x,w) = self.distribution.quadrature(3, [order]*self.d)
            intapp = np.dot(self.f(x.T), w)
            success = np.isclose(intapp,self.integ,atol=self.quad_eps)
            order += 1
        self.assertTrue(success)


class StandardNormalDistributionTest(GaussianDistributionSigmaTests):

    def get_distribution(self):
        return DIST.StandardNormalDistribution(self.d)

class LogNormalDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.LogNormalDistribution(.3,0.,2.)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class LogisticDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.LogisticDistribution(1.,1.5)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class GammaDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.GammaDistribution(2.,5.)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class BetaDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.BetaDistribution(2.,5.)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class GumbelDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.GumbelDistribution(2.,5.)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class WeibullDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.WeibullDistribution(2.,2.,2.)
    def get_d(self): return 1
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class BananaDistributionTest(DistributionTest):
    def get_distribution(self):
        return DIST.BananaDistribution(a=2.,b=2.,mu=np.zeros(2),sigma2=np.eye(2))
    def get_d(self): return 2
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class FactorizedDistributionTest(DistributionTest):
    r"""
    We test the joint distribution :math:`\pi(x_0,x_1)=\pi_1(x_1|x_0)\pi_2(x_0)` defined by

    .. math::

       x_0 \sim \mathcal{N}(0,1) \\
       x_1 | x_0 \sim \mathcal{N}(x_0^2, 1)
    
    """
    def get_sampling_distribution(self):
        return DIST.StandardNormalDistribution(self.d)
    def get_distribution(self):
        return DIST_EX.FactorizedBananaDistribution()
    def get_d(self): return 2
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class LinearBayesPosteriorDistributionTest(DistributionTest):
    r"""
    Test the Bayesian posterior for a linear Gaussian additive model with
    Gaussian prior.

    .. math::

       {\bf y} = {\bf c} + {\bf T}{\bf x} + \varepsilon \;, \quad
       \varepsilon \sim \mathcal{N}(\mu, \Sigma) \;, \quad
       {\bf x} \sim \mathcal{N}(\mu_x, \Sigma_x)

    To make it more interesting we set :math:`d_y=2` and :math:`d_x=3`
    """
    def get_sampling_distribution(self):
        return DIST.StandardNormalDistribution(self.d)
    def get_distribution(self):
        dx = self.d
        dy = dx - 1
        # Prior
        mux = npr.randn(dx)
        sigmax = npr.randn(dx**2).reshape((dx,dx))
        sigmax = np.dot(sigmax, sigmax.T)
        prior = DIST.GaussianDistribution(mux, sigmax)
        # Likelihood
        mu = npr.randn(dy)
        sigma = npr.randn(dy**2).reshape((dy,dy))
        sigma = np.dot(sigma, sigma.T)
        c = npr.randn(dy)
        T = npr.randn(dy*dx).reshape((dy,dx))
        y = c + np.dot(T, prior.rvs(1)[0,:])
        logL = LKL.AdditiveLinearGaussianLogLikelihood(y, c, T, mu, sigma)
        # Posterior
        pi = INFDIST.BayesPosteriorDistribution(logL, prior)
        return pi
    def get_d(self): return 3
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class NonLinearBayesPosteriorDistributionTest(DistributionTest):
    r"""
    Test the Bayesian posterior for a non-linear Gaussian additive model with
    Gaussian prior.

    .. math::

       {\bf y} = T({\bf x}) + \varepsilon \;, \quad
       \varepsilon \sim \mathcal{N}(\mu, \Sigma) \;, \quad
       {\bf x} \sim \mathcal{N}(\mu_x, \Sigma_x)

    To make it more interesting we set :math:`d_y=2` and :math:`d_x=3`
    """
    def get_sampling_distribution(self):
        return DIST.StandardNormalDistribution(self.d)
    def get_distribution(self):
        dx = self.d
        dy = dx - 1
        # Prior
        mux = npr.randn(dx)
        sigmax = npr.randn(dx**2).reshape((dx,dx))
        sigmax = np.dot(sigmax, sigmax.T)
        prior = DIST.GaussianDistribution(mux, sigmax)
        # Likelihood
        mu = npr.randn(dy)
        sigma = npr.randn(dy**2).reshape((dy,dy))
        sigma = np.dot(sigma, sigma.T)
        obs_pi = DIST.GaussianDistribution(mu, sigma)
        Tfull = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(dx, 2)
        coeffs = Tfull.get_identity_coeffs()
        coeffs += npr.randn(len(coeffs)) / 10.
        Tfull.coeffs = coeffs
        T = MAPS.TransportMap( Tfull.active_vars[dx-dy:],
                               Tfull.approx_list[dx-dy:] )
        y = T.evaluate(prior.rvs(1)).flatten()
        logL = LKL.AdditiveLogLikelihood(y, obs_pi, T)
        # Posterior
        pi = INFDIST.BayesPosteriorDistribution(logL, prior)
        return pi
    def get_d(self): return 3
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class AR1TransitionDistributionTest(ConditionalDistributionTest):
    r"""
    We test for the transition probability associated to the folllowing process

    .. math::

       {\bf Z}_{k+1} = T({\bf Z}_k, \Theta) + \varepsilon
       \;, \quad
       \varepsilon \sim \nu_\pi

    where :math:`T` is a non-linear map and \nu_\pi is the banana distribution.
    """
    def get_distribution(self):
        # \nu_\pi
        a = 1.
        b = 1.
        mu = np.zeros(2)
        sigma2 = np.array([[1., 0.9],[0.9, 1.]])
        nupi = DIST.BananaDistribution(a, b, mu, sigma2)
        # T:R^(2+2) -> R^2 (bottom part of a lower triangular linear span map)
        Tfull = TM.Default_IsotropicLinearSpanTriangularTransportMap(4, 2)
        T = MAPS.TransportMap( Tfull.active_vars[2:],
                               Tfull.approx_list[2:] )
        # Build transition probability
        ar1trans = DECDIST.AR1TransitionDistribution(nupi, T)
        return ar1trans
    
class StochasticVolatilityDistributionTest(DistributionTest):
    r"""
    We test on the joint distribution of the stochastic volatility with hyper-parameters and
    4 steps.
    """
    def get_sampling_distribution(self):
        return DIST.StandardNormalDistribution(self.d)
    def get_distribution(self):
        # PRIOR HYPER PARAMTERS
        is_mu_h = True
        is_sigma_h = True
        is_phi_h = True
        pi_hyper = SV.PriorHyperParameters(is_mu_h, is_sigma_h, is_phi_h, 1)
        # INITIAL AND TRANSITION PROBABILITIES
        mu_h = SV.IdentityFunction()
        phi_h = SV.F_phi(3.,1.)
        sigma_h = SV.ConstantFunction(0.25)
        pi_ic = SV.PriorDynamicsInitialConditions(
            is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)
        pi_trans = SV.PriorDynamicsTransition(
            is_mu_h, mu_h, is_sigma_h, sigma_h, is_phi_h, phi_h)
        # GENERATE OBSERVATIONS
        mu = -.5
        phi = .95
        sigma = 0.25
        nsteps = 4
        yB, ZA = SV.generate_data(nsteps, mu, sigma, phi)
        yB[2] = None # Missing data y2
        # DEFINE POSTERIOR AND ASSIMILATE DATA
        pi = DECDIST.SequentialHiddenMarkovChainDistribution([], [], pi_hyper)
        for n, yt in enumerate(yB):
            if yt is None:
                ll = None
            else:
                ll = SV.LogLikelihood(yt, is_mu_h, is_sigma_h, is_phi_h)
            if n == 0: pin = pi_ic
            else: pin = pi_trans
            pi.append(pin, ll)
        return pi
    def get_d(self): return 7
    def get_analytic_integral(self): return None
    def get_test_function(self): return None
    def get_mc_eps(self): return None
    def get_quad_eps(self): return None
    @unittest.skip("Not defined")
    def test_rvs(self): pass
    @unittest.skip("Not defined")
    def test_mean_log_pdf(self): pass

class MarkovComponentZeroStochasticVolatilityDistributionTest(
        StochasticVolatilityDistributionTest):
    r"""
    We test on the joint distribution of the stochastic volatility with hyper-parameters and
    4 steps.
    """
    def get_distribution(self):
        pi = super(MarkovComponentZeroStochasticVolatilityDistributionTest,
                   self).get_distribution()
        mkv = pi.get_MarkovComponent(0, n=2)
        return mkv
    def get_d(self): return 6

class MarkovComponentOneStochasticVolatilityDistributionTest(
        StochasticVolatilityDistributionTest):
    r"""
    We test on the joint distribution of the stochastic volatility with hyper-parameters and
    4 steps.
    """
    def get_distribution(self):
        pi = super(MarkovComponentOneStochasticVolatilityDistributionTest,
                   self).get_distribution()
        # Construct random map
        hdim = pi.hyper_dim
        sdim = pi.state_dim
        T = TM.Default_IsotropicIntegratedSquaredTriangularTransportMap(
            sdim+hdim, 1)
        coeffs = T.get_identity_coeffs()
        coeffs += npr.randn( len(coeffs) ) / 10.
        T.coeffs = coeffs
        # Retriever hyper map and Xt map
        H = MAPS.TransportMap( T.active_vars[:hdim],
                               T.approx_list[:hdim] )
        Mkm1 = MAPS.TransportMap( T.active_vars[hdim:hdim+sdim],
                                  T.approx_list[hdim:hdim+sdim] )
        mkv = pi.get_MarkovComponent(1, n=2, state_map=Mkm1, hyper_map=H)
        return mkv
    def get_d(self): return 6

    
def build_suite(ttype='all'):
    suite_stdnorm = unittest.TestLoader().loadTestsFromTestCase( StandardNormalDistributionTest )
    suite_gaussian_sigma = unittest.TestLoader().loadTestsFromTestCase( GaussianDistributionSigmaTests )
    suite_gaussian_precision = unittest.TestLoader().loadTestsFromTestCase( GaussianDistributionPrecisionTests )
    suite_lognormal = unittest.TestLoader().loadTestsFromTestCase( LogNormalDistributionTest )
    suite_logistic = unittest.TestLoader().loadTestsFromTestCase( LogisticDistributionTest )
    suite_gamma = unittest.TestLoader().loadTestsFromTestCase( GammaDistributionTest )
    suite_beta = unittest.TestLoader().loadTestsFromTestCase( BetaDistributionTest )
    suite_gumbel = unittest.TestLoader().loadTestsFromTestCase( GumbelDistributionTest )
    suite_weibull = unittest.TestLoader().loadTestsFromTestCase( WeibullDistributionTest )
    suite_banana = unittest.TestLoader().loadTestsFromTestCase( BananaDistributionTest )
    suite_factorized = unittest.TestLoader().loadTestsFromTestCase(
        FactorizedDistributionTest )
    suite_bayeslinear = unittest.TestLoader().loadTestsFromTestCase(
        LinearBayesPosteriorDistributionTest )
    suite_bayesnonlin = unittest.TestLoader().loadTestsFromTestCase(
        NonLinearBayesPosteriorDistributionTest )
    suite_ar1trans = unittest.TestLoader().loadTestsFromTestCase(
        AR1TransitionDistributionTest )
    suite_stocvol = unittest.TestLoader().loadTestsFromTestCase(
        StochasticVolatilityDistributionTest )
    suite_m0stocvol = unittest.TestLoader().loadTestsFromTestCase(
        MarkovComponentZeroStochasticVolatilityDistributionTest )
    suite_m1stocvol = unittest.TestLoader().loadTestsFromTestCase(
        MarkovComponentOneStochasticVolatilityDistributionTest )
    # Group suites
    suites_list = []
    if ttype in ['all', 'serial']:
        suites_list += [ suite_stdnorm, suite_gaussian_sigma,
                         suite_gaussian_precision,
                         suite_lognormal, suite_logistic, suite_gamma, suite_beta,
                         suite_gumbel, suite_weibull, suite_banana,
                         suite_factorized, suite_bayeslinear, suite_bayesnonlin,
                         suite_ar1trans,
                         suite_stocvol, suite_m0stocvol, suite_m1stocvol]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
