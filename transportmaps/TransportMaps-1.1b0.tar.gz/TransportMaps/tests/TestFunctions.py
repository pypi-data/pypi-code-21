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

import numpy as np
import numpy.linalg as npla
import scipy.stats as stats
import scipy.optimize as sciopt
import scipy.linalg as scila

import TransportMaps.Maps as MAPS
import TransportMaps.Distributions as DIST
import TransportMaps.Functionals as FUNC

NAX = np.newaxis

def get(TESTN):
    setup = {}
    test = {}
    
    if TESTN == 0:
        # Setup variables
        setup['mu'] = np.array([2.])
        setup['sigma2'] = np.array([[.5]])
        setup['dim'] = 1
        setup['refplotspan'] = np.array([[-7.,7.]])
        setup['plotspan'] = np.array([[-2.,4.]])
        title = 'lin-gauss-mu%s-sig%s' % (str(setup['mu']), str(setup['sigma2']))
        test['target_distribution'] = DIST.GaussianDistribution(setup['mu'], setup['sigma2'])
        test['target_map'] = LinearGaussianMap(setup['mu'], setup['sigma2'])
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.]),
                                                                    np.array([1.]))

    elif TESTN == 1:
        raise NotImplementedError("This test is missing right now")
        # # Mixture parameters
        # setup['dim'] = 1
        # setup['refdist'] = stats.norm(0.,1.)
        # setup['mu1'] = -1.
        # setup['mu2'] = 2.
        # setup['sigma1'] = 1.
        # setup['sigma2'] = .5
        # setup['p'] = 0.3
        # setup['plotspan'] = np.array([[-7.,7.]])
        # setup['refplotspan'] = np.array([[-7.,7.]])
        # title='mixture-p%s-mu1%s-mu2%s-sig1%s-sig2%s' % (str(setup['p']), str(setup['mu1']),
        #                                                  str(setup['mu2']), str(setup['sigma1']),
        #                                                  str(setup['sigma2']))
        # mean_logref = - 1./2*np.log(2.*np.pi) - 1./2.
        # # Missing logpdf's
        # def cdf(x, params):
        #     p = params['p']
        #     mu1 = params['mu1']
        #     mu2 = params['mu2']
        #     sigma1 = params['sigma1']
        #     sigma2 = params['sigma2']
        #     d1 = stats.norm(mu1, sigma1)
        #     d2 = stats.norm(mu2, sigma2)
        #     out = p * d1.cdf( x ) + (1-p) * d2.cdf( x )
        #     return out
        # def misfit_cdf(x,cdfx,params):
        #     return params['cdf'](x, params) - cdfx
        # def T(x, params):
        #     """
        #     One dimensional transport map along the first axis.
        #     """
        #     if isinstance(x,float):
        #         x = np.array([[x]])
        #     if x.ndim == 1:
        #         x = x[:,NAX]
        #     out = np.zeros(x.shape)
        #     reference = params['refdist']
        #     cdfx = reference.cdf(x.flatten())   # cdfx distributed U([0,1])
        #     a = -10.
        #     b = 10.
        #     for i,cc in np.ndenumerate(cdfx):
        #         x0 = 0.
        #         out[i,0] = sciopt.brentq(misfit_cdf, a, b, args=(cc,params))
        #     return out
        # def refpdf(x, params):
        #     return params['refdist'].pdf(x)
        # def pdf(x, params):
        #     p = params['p']
        #     mu1 = params['mu1']
        #     mu2 = params['mu2']
        #     sigma1 = params['sigma1']
        #     sigma2 = params['sigma2']
        #     d1 = stats.norm(mu1, sigma1)
        #     d2 = stats.norm(mu2, sigma2)
        #     out = p * d1.pdf( x ) + (1-p) * d2.pdf( x )
        #     return out
        # def dx_pdf(x, params):
        #     p = params['p']
        #     mu1 = params['mu1']
        #     mu2 = params['mu2']
        #     sigma1 = params['sigma1']
        #     sigma2 = params['sigma2']
        #     d1 = stats.norm(mu1, sigma1)
        #     d2 = stats.norm(mu2, sigma2)
        #     out = - p * (x-mu1) * d1.pdf(x) / sigma1**2. \
        #           - (1-p) * (x-mu2) * d2.pdf(x) / sigma2**2.
        #     return out
        # def dx2_pdf(x, params):
        #     p = params['p']
        #     mu1 = params['mu1']
        #     mu2 = params['mu2']
        #     sigma1 = params['sigma1']
        #     sigma2 = params['sigma2']
        #     d1 = stats.norm(mu1, sigma1)
        #     d2 = stats.norm(mu2, sigma2)
        #     out = p * ( (x-mu1)**2./sigma1**2. - 1. )/sigma1**2. * d1.pdf(x) \
        #           + (1-p) * ( (x-mu2)**2./sigma2**2. - 1. )/sigma2**2. * d2.pdf(x)
        #     return out
        # Tparams['T'] = T
        # Tparams['cdf'] = cdf
        # Tparams['suppmap'] = TM.FrozenLinearDiagonalTransportMap(np.array([0.]),np.array([1.]))
        # Tparams['reference'] = TM.FrozenDistribution(1, refpdf, setup)
        # Tparams['target'] = TM.FrozenDistribution(1, pdf, setup, logpdf, dx_logpdf,
        #                                      dx2_logpdf, mean_logref)
        # TM.link(Tparams['suppmap'], Tparams['target'])

    elif TESTN == 2:
        # Prescribed transport map
        # T(x) = a + b * x + c * arctan(d + e * x)
        setup['dim'] = 1
        setup['a'] = 1.
        setup['b'] = 1.
        setup['c'] = 2.
        setup['d'] = 2.
        setup['e'] = 5.
        title = 'arctan-a%s-b%s-c%s-d%s-e%s' % (str(setup['a']), str(setup['b']),
                                                str(setup['c']), str(setup['d']),
                                                str(setup['e']))
        setup['plotspan'] = np.array([[-7.,7.]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        test['target_map'] = ArcTanTransportMap(setup['a'], setup['b'], setup['c'],
                                                setup['d'], setup['e'])
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = ArcTanDistribution(test['target_map'], test['base_distribution'])
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.]),
                                                                    np.array([1.]))

    elif TESTN == 3:
        # Prescribed transport map to log normal
        # Y ~ logN(0,a^2) -- i.e. log(Y)~N(0,a^2)
        setup['dim'] = 1
        title = 'exp'
        setup['refdist'] = stats.norm(0.,1.)
        setup['mu'] = 0.
        setup['s'] = .3
        setup['scale'] = 1.
        setup['tardist'] = stats.lognorm(s=setup['s'],
                                         loc=setup['mu'],
                                         scale=setup['scale'])
        setup['plotspan'] = np.array([[1e-4,4.]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        # Log Normal distribution
        test['target_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([setup['mu']]),
                                                                   np.array([setup['s']]) )
        test['support_map'] = MAPS.FrozenExponentialDiagonalTransportMap(1)
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.LogNormalDistribution(setup['s'], setup['mu'], setup['scale'])

    elif TESTN == 4:
        # Logistic distribution: Y~Logistic(\mu,s)
        setup['dim'] = 1
        title = 'logistic'
        setup['mu'] = 5.
        setup['s'] = 2.
        setup['plotspan'] = np.array([[-10.,10.]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        test['target_map'] = LogisticTransportMap(setup['mu'], setup['s'])
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.]),
                                                                    np.array([1.]))
        # test['base_distribution'] = DIST.LogisticDistribution(0.,1.)
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.LogisticDistribution(setup['mu'], setup['s'])
    
    elif TESTN == 5:
        # Gamma distribution: Y~Gamma(loc,scale)
        # Support [0,inf[
        setup['dim'] = 1
        title = 'gamma'
        setup['refdist'] = stats.norm(0.,1.)
        setup['kappa'] = 2.
        setup['theta'] = 0.5
        setup['tardist'] = stats.gamma(setup['kappa'],scale=setup['theta'])
        setup['plotspan'] = np.array([[1e-4,5.]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        test['target_map'] = GammaTransportMap(setup['kappa'], setup['theta'])
        test['support_map'] = MAPS.FrozenExponentialDiagonalTransportMap(1)
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.GammaDistribution(setup['kappa'], setup['theta'])
    
    elif TESTN == 6:
        # Beta distribution: Y~Beta(a,b)
        # Support [0,1]
        setup['dim'] = 1
        title = 'beta'
        setup['refdist'] = stats.norm(0.,1.)
        setup['alpha'] = 2.
        setup['beta'] = 5.
        setup['tardist'] = stats.beta(setup['alpha'], setup['beta'])
        mean_logref = - 1./2*np.log(2.*np.pi) - 1./2.
        setup['plotspan'] = np.array([[1e-4,1.-1e-4]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        test['target_map'] = BetaTransportMap(setup['alpha'], setup['beta'])
        test['support_map'] = MAPS.FrozenGaussianToUniformDiagonalTransportMap(1)
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.BetaDistribution(setup['alpha'], setup['beta'])

    elif TESTN == 7:
        # Gumbel distribution: Y~Gum(mu,beta)
        # Support -inf,inf
        setup['dim'] = 1
        title = 'Gumbel'
        setup['refdist'] = stats.norm(0.,1.)
        setup['mu'] = 3.
        setup['beta'] = 4.
        setup['tardist'] = stats.gumbel_r(loc=setup['mu'], scale=setup['beta'])
        mean_logref = - 1./2*np.log(2.*np.pi) - 1./2.
        setup['plotspan'] = np.array([[-10.,40.]])
        setup['refplotspan'] = np.array([[-7.,7.]])
        test['target_map'] = GumbelTransportMap(setup['mu'], setup['beta'])
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.]),
                                                                    np.array([1.]))
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.GumbelDistribution(setup['mu'], setup['beta'])

    elif TESTN == 8:
        # Weibull distribution: Y~Weibull(a,b)
        # Support 0,inf
        setup['dim'] = 1
        title = 'Weibull'
        setup['c'] = 3.
        setup['mu'] = 0.
        setup['sigma'] = 2.
        setup['plotspan'] = np.array([[1e-4,10.]])
        setup['refplotspan'] = np.array([[-5.,5.]])
        #  transport map
        test['target_map'] = WeibullTransportMap(setup['c'], setup['mu'], setup['sigma'])
        test['support_map'] = MAPS.FrozenExponentialDiagonalTransportMap(1)
        test['base_distribution'] = DIST.StandardNormalDistribution(1)
        test['target_distribution'] = DIST.WeibullDistribution(setup['c'], setup['mu'], setup['sigma'])

    elif TESTN == 9:
        # Linear Gaussian
        dim = 2
        setup['dim'] = dim
        setup['mu'] = np.array([0.1,-0.1])
        setup['sigma2'] = 2. * np.array([[.5, .25],[.25, .3]])
        setup['plotspan'] = np.array([[-7.,7.],[-7.,7.]])
        setup['refplotspan'] = np.array([[-7.,7.],[-7.,7.]])
        title = 'lin-gauss-0mu%s-1mu%s-00sig%s-01sig%s-11sig%s' % \
                ( str(setup['mu'][0]), str(setup['mu'][1]),
                  str(setup['sigma2'][0,0]), str(setup['sigma2'][0,1]),
                  str(setup['sigma2'][1,1]) )
        test['target_distribution'] = DIST.GaussianDistribution(setup['mu'], setup['sigma2'])
        test['target_map'] = MAPS.LinearTransportMap(setup['mu'], setup['sigma2'])
        test['base_distribution'] = DIST.StandardNormalDistribution(2)
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.,0.]),
                                                                    np.array([1.,1.]))

    elif TESTN == 10:
        # Banana function
        dim = 2
        setup['dim'] = dim
        setup['refdist'] = stats.multivariate_normal(np.zeros(dim),np.eye(dim))
        setup['a'] = 1.
        setup['b'] = 1.
        setup['mu'] = np.zeros(dim)
        setup['sigma2'] = np.array([[1., 0.9],[0.9, 1.]])
        setup['plotspan'] = np.array([[-3.,3.],[-7.,2.]])
        setup['refplotspan'] = np.array([[-7.,7.],[-7.,7.]])
        title = 'banana-a%s-b%s' % (str(setup['a']), str(setup['b']))
        # Banana transport map
        gauss_map = MAPS.LinearTransportMap( setup['mu'], npla.cholesky(setup['sigma2']) )
        ban_map = MAPS.FrozenBananaTransportMap( setup['a'], setup['b'] )
        test['target_map'] = MAPS.CompositeTransportMap(ban_map, gauss_map)
        test['base_distribution'] = DIST.StandardNormalDistribution(2)
        test['target_distribution'] = DIST.BananaDistribution( setup['a'], setup['b'],
                                                     setup['mu'], setup['sigma2'] )
        test['support_map'] = MAPS.FrozenLinearDiagonalTransportMap(np.array([0.,0.]),
                                                                    np.array([1.,1.]))

    elif TESTN == 11:
        # 3 dimensional test
        raise NotImplementedError("To be implemented")

    else:
        raise NotImplementedError("The selected test is not implemented.")

    return (title,setup,test)

#
# Analytical transport maps
#

class LinearGaussianMap(object):
    def __init__(self, mu, sigma2):
        self.mu = mu
        self.sigma2 = sigma2
    def evaluate(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.mu + np.sqrt(self.sigma2) * x
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = (x - self.mu) / np.sqrt(self.sigma2)
        return out

    
class ArcTanTransportMap(object):
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
    def evaluate(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        e = self.e
        out = a + b * x + c * np.arctan( d + e * x)
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def grad_x(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        b = self.b
        c = self.c
        d = self.d
        e = self.e
        out = b + (c*e)/((d + e*x)**2. + 1.)
        return out
    def hess_x(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        c = self.c
        d = self.d
        e = self.e
        out = - (2.*c * e**2. * (d+e*x))/((d+e*x)**2. + 1.)**2.
        return out
    def nabla3_x(self, x):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        c = self.c
        d = self.d
        e = self.e
        out = (2.*c * e**3. * (3.*(d+e*x)**2.-1.) )/((d+e*x)**2. + 1.)**3.
        return out
    def inverse(self, y):
        if isinstance(y,float):
            y = np.array([[y]])
        if y.ndim == 1:
            y = y[:,NAX]
        out = np.zeros(y.shape)
        x0 = 0.
        for i in range(y.shape[0]):
            yy = y[i,0]
            def func(x):
                return self.evaluate(x) - yy
            maxtry = 10
            mul = 1.
            ntry = 0
            fail = True
            while fail and ntry < maxtry:
                ntry += 1
                try:
                    out[i,0] = sciopt.brentq(func, a=-10.*mul, b=10.*mul,
                                             xtol=1e-12, maxiter=100)
                    fail = False
                except ValueError: mul *= 10.
            if ntry == maxtry:
                raise RuntimeError("Failed to converge")
        return out
    def grad_x_inverse(self, x, inv=None):
        if inv is None: inv = self.inverse(x)
        return 1./self.grad_x(inv)
    def hess_x_inverse(self, x, inv=None):
        if inv is None: inv = self.inverse(x)
        return - self.hess_x(inv) / self.grad_x(inv)**3.
    def nabla3_x_invserse(self, x, inv=None):
        if inv is None: inv = self.inverse(x)
        dxt1 = self.grad_x(inv)
        return - self.nabla3_x(inv) / dxt1**4. + \
            3. * self.hess_x(inv)**2. / dxt1**5.

class GumbelTransportMap(object):
    def __init__(self, mu, beta):
        self.tar = stats.gumbel_r(loc=mu, scale=beta)
        self.ref = stats.norm(0.,1.)
    def evaluate(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.tar.ppf( self.ref.cdf(x) )
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.ref.ppf( self.tar.cdf(x) )
        return out


class WeibullTransportMap(object):
    # Transport map from N(0,1) to L^\sharp W, where L is the
    # exponential transport map
    def __init__(self, c, mu, sigma):
        self.c = c
        self.mu = mu
        self.sigma = sigma
        self.tar = stats.weibull_min(c=self.c, loc=self.mu, scale=self.sigma)
        self.ref = stats.norm()
        self.suppmap = MAPS.FrozenExponentialDiagonalTransportMap(1)
    def evaluate(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.suppmap.inverse( self.tar.ppf( self.ref.cdf(x) ) )
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.suppmap.evaluate( self.ref.ppf( self.tar.cdf(x) ) )
        return out

class BetaTransportMap(object):
    def __init__(self, alpha, beta):
        self.tar = stats.beta(alpha, beta)
        self.ref = stats.norm(0.,1.)
    def suppmap(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        std = stats.norm()
        spd = stats.uniform()
        out = spd.ppf( std.cdf( x ) )
        return out
    def invsuppmap(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        std = stats.norm()
        spd = stats.uniform()
        out = std.ppf( spd.cdf( x ) )
        return out
    def evaluate(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.invsuppmap( self.tar.ppf( self.ref.cdf(x) ) )
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.ref.ppf( self.tar.cdf( self.suppmap(x) ) )
        return out

class LogisticTransportMap(object):
    def __init__(self, mu, s):
        self.tar = stats.logistic(loc=mu,scale=s)
        self.ref = stats.norm(0.,1.)
    def evaluate(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.tar.ppf( self.ref.cdf(x) )
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.ref.ppf( self.tar.cdf(x) )
        return out

class GammaTransportMap(object):
    def __init__(self, kappa, theta):
        self.tar = stats.gamma(kappa, scale=theta)
        self.ref = stats.norm(0.,1.)
    def evaluate(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = np.log( self.tar.ppf( self.ref.cdf(x) ) )
        return out
    def __call__(self, x):
        return self.evaluate(x)
    def inverse(self, x, params=None):
        if isinstance(x,float):
            x = np.array([[x]])
        if x.ndim == 1:
            x = x[:,NAX]
        out = self.ref.ppf( self.tar.cdf( np.exp(x) ) )
        return out

    
#
# Analytical densities
#
class ArcTanDistribution(DIST.Distribution):
    def __init__(self, atan_fun, base_distribution):
        super(ArcTanDistribution,self).__init__(1)
        self.atan = atan_fun
        self.base_distribution = base_distribution
    def rvs(self, n, *args, **kwargs):
        x = self.base_distribution.rvs(n).reshape((n,1))
        out = self.atan.evaluate(x)
        return out
    def quadrature(self, qtype, qparams, *args, **kwargs):
        if qtype == 0:
            # Monte Carlo sampling
            x = self.rvs(qparams)
            w = np.ones(qparams)/float(qparams)
        elif qtype == 1:
            # Quasi-Monte Carlo sampling
            raise NotImplementedError("Not implemented")
        elif qtype == 2:
            # Latin-Hyper cube sampling
            raise NotImplementedError("Todo")
        elif qtype == 3:
            # Gaussian quadrature
            (x1,w) = self.base_distribution.quadrature(3, qparams)
            x = self.atan.evaluate(x1)
        else:
            raise ValueError("Quadrature type not recognized")
        return (x,w)
    def pdf(self, x, *args, **kwargs):
        inv = self.atan.inverse(x)
        return self.base_distribution.pdf(inv) * \
            self.atan.grad_x_inverse(x,inv).flatten()
    def grad_x_pdf(self, x, *args, **kwargs):
        inv = self.atan.inverse(x)
        dxt1i = self.atan.grad_x_inverse(x,inv)
        dxxt1i = self.atan.hess_x_inverse(x,inv)
        d = self.base_distribution
        return d.grad_x_pdf(inv) * dxt1i**2. + d.pdf(inv) * dxxt1i
    def log_pdf(self, x,*args, **kwargs):
        inv = self.atan.inverse(x)
        out = self.base_distribution.log_pdf(inv) + \
              np.log(self.atan.grad_x_inverse(x,inv).flatten())
        return out
    def grad_x_log_pdf(self, x, *args, **kwargs):
        t1i = self.atan.inverse(x)
        dxt1i = self.atan.grad_x_inverse(x,t1i)
        dxxt1i = self.atan.hess_x_inverse(x,t1i)
        d = self.base_distribution
        return d.grad_x_log_pdf(t1i) * dxt1i + dxxt1i / dxt1i
    def hess_x_log_pdf(self, x, *args, **kwargs):
        t1i = self.atan.inverse(x)
        dxt1i = self.atan.grad_x_inverse(x,t1i).flatten()
        dxxt1i = self.atan.hess_x_inverse(x,t1i).flatten()
        dxxxt1i = self.atan.nabla3_x_invserse(x,t1i).flatten()
        d = self.base_distribution
        gxlpdf = d.grad_x_log_pdf(t1i).flatten()
        hxlpdf = d.hess_x_log_pdf(t1i).flatten()
        out = hxlpdf * dxt1i**2. + \
            gxlpdf * dxxt1i + \
            dxxxt1i/dxt1i - dxxt1i**2./dxt1i**2.
        return out.reshape((out.shape[0],1,1))
