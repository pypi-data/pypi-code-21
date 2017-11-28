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

import copy as cp
import numpy as np
import scipy.stats as stats

from TransportMaps.Distributions.DistributionBase import *
from TransportMaps.Distributions.FrozenDistributions import GaussianDistribution
from TransportMaps.Distributions.Decomposable.SequentialInferenceDistributions import SequentialHiddenMarkovChainDistribution

from TransportMaps.Functionals.FunctionBase import Function
from TransportMaps.Likelihoods.LikelihoodBase import LogLikelihood

__all__ = [
    'F_phi', 'F_sigma', 'IdentityFunction', 'ConstantFunction',
    'PriorHyperParameters',
    'PriorDynamicsInitialConditions',
    'PriorDynamicsTransition',
    'LogLikelihood',
    'StocVolHyperDistribution',
    'generate_data', 'trim_distribution']

############################
# Transformation functions #
############################

class F_phi(object): 
    def __init__(self,mean,std):
        self.mean = mean
        self.std = std
    def evaluate(self, x):
        Xh = self.mean+self.std*x
        return  2*( np.exp(Xh) ) / (1+np.exp(Xh)) - 1.
    def grad_x(self,x):
        Xh = self.mean+self.std*x
        return  2*self.std*np.exp(Xh) / ( np.exp(Xh) + 1. )**2
    def hess_x(self,x):
        Xh = self.mean+self.std*x
        return  -2*self.std**2*np.exp(Xh) * \
            ( np.exp(Xh) - 1. ) / ( np.exp(Xh) + 1. )**3

class F_sigma(object): #Square root of an inverse gamma
    def __init__(self,k,theta):
        self.k = k
        self.theta = theta
        self.F_Gauss2InvGamma=F_Gauss2InvGamma(k,theta)
    def evaluate(self, x):
        return  np.sqrt( self.F_Gauss2InvGamma.evaluate(x) )
    def grad_x(self,x):
        return  .5*(self.F_Gauss2InvGamma.evaluate(x)**-0.5) * \
            self.F_Gauss2InvGamma.grad_x(x)
    def hess_x(self,x):
        FX=self.F_Gauss2InvGamma.evaluate(x)
        return  -.25*(FX**-1.5)*(self.F_Gauss2InvGamma.grad_x(x)**2) + \
                 .5*(FX**-0.5)*self.F_Gauss2InvGamma.hess_x(x)

class F_Gauss2InvGamma(object):
    def __init__(self,k,theta):
        self.k = k
        self.theta = theta
        self.std = stats.norm()
        self.invGamma = stats.invgamma(k, scale = theta)
    def evaluate(self, X):
        return self.invGamma.ppf( self.std.cdf(X) )
    def grad_x(self,X):
        FX = self.evaluate(X)
        return self.std.pdf(X)/self.invGamma.pdf(FX)
    def hess_x(self,X):
        FX = self.evaluate(X)
        grad_FX = self.grad_x(X)
        a = self.k
        b = self.theta
        gamma = (b - (a+1)*FX )/FX**2
        return - grad_FX*( X + grad_FX*gamma )

class ConstantFunction(Function):
    def __init__(self,constant):
        if not isinstance(constant, float) and not isinstance(constant, int):
            raise ValueError("Constant must be float or int")
        self.constant = float(constant)
        super(ConstantFunction,self).__init__(1)
    def evaluate(self, x):
        return self.constant
    def grad_x(self, x):
        return 0.
    def hess_x(self, x):
        return 0.

class IdentityFunction(Function):
    def __init__(self):
        super(IdentityFunction, self).__init__(1)
    def evaluate(self, x):
        return x
    def grad_x(self, x):
        return 1.
    def hess_x(self, x):
        return 0.


        
################
#    Priors    #
################
        
class PriorHyperParameters(GaussianDistribution):
    r""" Distribution :math:`\pi(\mu, \sigma, \phi)`

    Here :math:`\mu \sim \mathcal{N}(0,\sigma^2_\mu)`,
    :math:`\phi \sim \mathcal{N}(0,1)` and
    :math:`\sigma \sim \mathcal{N}(0,1)`, if they are to be considered
    hyper-parameters.

    Args:
      is_mu_hyper (bool): whether :math:`\mu` is an hyper-parameter
      is_sigma_hyper (bool): whether :math:`\sigma` is an hyper-parameter
      is_phi_hyper (bool): whether :math:`\phi` is an hyper-parameter
      mu_sigma (float): parameter :math:`\sigma_\mu`
    """
    def __init__(self, is_mu_hyper=False, is_sigma_hyper=False, is_phi_hyper=False,
                 sigma_mu=None):
        dim = is_mu_hyper + is_sigma_hyper + is_phi_hyper
        if dim == 0:
            raise ValueError("Avoid defining densities of dimension 0")
        self.is_mu_hyper = is_mu_hyper
        self.is_sigma_hyper = is_sigma_hyper
        self.is_phi_hyper = is_phi_hyper
        self.sigma_mu = sigma_mu
        # Define mean and covariance matrix
        mu = np.zeros(dim)
        cov = np.eye(dim)
        if self.is_mu_hyper:
            cov[0,0] = self.sigma_mu**2.
        # Initialize Gaussian distribution
        super(PriorHyperParameters, self).__init__(mu, sigma=cov)
            
class PriorDynamicsInitialConditions(ConditionalDistribution):
    r""" Conditional distribution :math:`\pi({\bf X}_{t_0}\vert \mu, \sigma, \phi)`

    Args:
      is_mu_hyper (bool): whether :math:`\mu` is an hyper-parameter
      is_sigma_hyper (bool): whether :math:`\sigma` is an hyper-parameter
      is_phi_hyper (bool): whether :math:`\phi` is an hyper-parameter
    """
    def __init__(self,
                 is_mu_hyper=False, mu=None,
                 is_sigma_hyper=False, sigma=None,
                 is_phi_hyper=False, phi=None):
        #Local ordering of the input function: Xmu, Xsigma, Xphi, X0
        self.is_mu_hyper = is_mu_hyper
        self.is_sigma_hyper = is_sigma_hyper
        self.is_phi_hyper = is_phi_hyper
        self.hyper_dim = self.is_mu_hyper + self.is_sigma_hyper + self.is_phi_hyper
        self.state_dim = 1
        super(PriorDynamicsInitialConditions, self).__init__(
            self.state_dim, self.hyper_dim)
        # Init hyper-parameters transformations
        self.mu = mu
        self.phi = phi
        self.sigma = sigma
        counter = 0
        if is_mu_hyper:
            self.index_mu = counter
            counter += 1
        if is_sigma_hyper:
            self.index_sigma = counter
            counter += 1
        if is_phi_hyper:
            self.index_phi = counter
            counter += 1

    def extract_variables(self, x):
        # Extract variables Xmu, Xsigma, Xphi
        (Xmu, Xsigma, Xphi) = (None, None, None)
        if self.is_mu_hyper:
            Xmu = x[:,self.index_mu]
        if self.is_sigma_hyper:
            Xsigma = x[:,self.index_sigma]
        if self.is_phi_hyper:
            Xphi = x[:,self.index_phi]
        return (Xmu, Xsigma, Xphi)

    def log_pdf(self, x, y, *args, **kwargs):
        X0 = x[:,0]
        Xmu, Xsigma, Xphi = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate
        return -.5*(1-f_Xphi**2)/f_Xsigma**2*(X0-f_Xmu)**2 + \
            - np.log(f_Xsigma) + 0.5 * np.log(1-f_Xphi**2)

    def grad_x_log_pdf(self, x, y, *args, **kwargs):
        X0 = x[:,0]
        Xmu, Xsigma, Xphi = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate gradients of transform functions
        if self.is_phi_hyper:
            grad_f_Xphi = self.phi.grad_x(Xphi)
        if self.is_sigma_hyper:
            grad_f_Xsigma = self.sigma.grad_x(Xsigma)
        # Evaluate
        sdim = self.state_dim
        hdim = self.hyper_dim
        grad = np.zeros( (x.shape[0], sdim + hdim) )
        grad[:,0] = - (1-f_Xphi**2)/f_Xsigma**2*(X0-f_Xmu)
        if self.is_mu_hyper:
            grad[:,sdim+self.index_mu] = (1-f_Xphi**2)/f_Xsigma**2*(X0-f_Xmu)
        if self.is_phi_hyper:
            grad[:,sdim+self.index_phi] = f_Xphi*grad_f_Xphi/f_Xsigma**2*(X0-f_Xmu)**2 + \
                                          - f_Xphi / (1-f_Xphi**2)*grad_f_Xphi
        if self.is_sigma_hyper:
            grad[:,sdim+self.index_sigma] = grad_f_Xsigma / f_Xsigma * \
                                            ( (1-f_Xphi**2)/f_Xsigma**2*(X0-f_Xmu)**2 - 1 )
        return grad

    def hess_x_log_pdf(self, x, y, *args, **kwargs):
        X0 = x[:,0]
        Xmu, Xsigma, Xphi = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate gradients and Hessians of transform functions
        if self.is_phi_hyper:
            grad_f_Xphi = self.phi.grad_x(Xphi)
            hess_f_Xphi = self.phi.hess_x(Xphi)
        if self.is_sigma_hyper:
            grad_f_Xsigma = self.sigma.grad_x(Xsigma)
            hess_f_Xsigma = self.sigma.hess_x(Xsigma)
        # Evaluate
        sdim = self.state_dim
        hdim = self.hyper_dim
        hess = np.zeros( (x.shape[0], sdim+hdim, sdim+hdim) )
        hess[:,0,0] = -(1-f_Xphi**2)/f_Xsigma**2
        if self.is_mu_hyper:
            hess[:,sdim+self.index_mu, sdim+self.index_mu] = -(1-f_Xphi**2)/f_Xsigma**2
            hess[:,0,sdim+self.index_mu] = (1-f_Xphi**2)/f_Xsigma**2
            hess[:,sdim+self.index_mu,0] = hess[:,0,sdim+self.index_mu]
            if self.is_sigma_hyper:
                hess[:,sdim+self.index_mu,sdim+self.index_sigma] = \
                    -2*grad_f_Xsigma/f_Xsigma**3*(1-f_Xphi**2)*(X0-f_Xmu)
                hess[:,sdim+self.index_sigma,sdim+self.index_mu] = \
                    hess[:,sdim+self.index_mu,sdim+self.index_sigma]
            if self.is_phi_hyper:
                hess[:,sdim+self.index_mu ,sdim+self.index_phi] = \
                    -2*f_Xphi/f_Xsigma**2*grad_f_Xphi*(X0-f_Xmu)
                hess[:,sdim+self.index_phi,sdim+self.index_mu] = \
                    hess[:,sdim+self.index_mu,sdim+self.index_phi]
        if self.is_sigma_hyper:
            hess[:,sdim+self.index_sigma,sdim+self.index_sigma] = \
                (1-f_Xphi**2)/f_Xsigma**3*(X0-f_Xmu)**2 * \
                (hess_f_Xsigma-3*grad_f_Xsigma**2/f_Xsigma) + \
                grad_f_Xsigma**2/f_Xsigma**2 - hess_f_Xsigma/f_Xsigma
            hess[:,0,sdim+self.index_sigma] = \
                2*grad_f_Xsigma/f_Xsigma**3*(1-f_Xphi**2)*(X0-f_Xmu)
            hess[:,sdim+self.index_sigma,0] = hess[:,0,sdim+self.index_sigma]
            if self.is_phi_hyper:
                hess[:,sdim+self.index_sigma,sdim+self.index_phi]= \
                    -2*f_Xphi/f_Xsigma**3 * grad_f_Xphi * \
                    grad_f_Xsigma*(X0-f_Xmu)**2
                hess[:,sdim+self.index_phi,sdim+self.index_sigma] = \
                    hess[:,sdim+self.index_sigma,sdim+self.index_phi]
        if self.is_phi_hyper:
            hess[:,sdim+self.index_phi,sdim+self.index_phi] = \
                (grad_f_Xphi**2 + f_Xphi*hess_f_Xphi) * \
                ( (X0-f_Xmu)**2/f_Xsigma**2-1./(1.-f_Xphi**2)) - \
                2*f_Xphi**2*grad_f_Xphi**2/(1.-f_Xphi**2)**2
            hess[:,0,sdim+self.index_phi] = 2*f_Xphi/f_Xsigma**2 * \
                                       grad_f_Xphi*(X0-f_Xmu)
            hess[:,sdim+self.index_phi,0] = hess[:,0,sdim+self.index_phi]
        return hess

class PriorDynamicsTransition(ConditionalDistribution):
    r""" Transition distribution :math:`\pi({\bf X}_{t_{k+1}}\vert {\bf X}_{t_{k}}, \mu, \sigma, \phi)`

    Args:
      is_mu_hyper (bool): whether :math:`\mu` is an hyper-parameter
      is_sigma_hyper (bool): whether :math:`\sigma` is an hyper-parameter
      is_phi_hyper (bool): whether :math:`\phi` is an hyper-parameter
    """
    def __init__(self,
                 is_mu_hyper=False, mu=None,
                 is_sigma_hyper=False, sigma=None,
                 is_phi_hyper=False, phi=None):
        #Local ordering of the input function: Xmu, Xsigma, Xphi, X0
        self.is_mu_hyper = is_mu_hyper
        self.is_phi_hyper = is_phi_hyper
        self.is_sigma_hyper = is_sigma_hyper
        self.hyper_dim = self.is_mu_hyper + self.is_sigma_hyper + self.is_phi_hyper
        self.state_dim = 1
        super(PriorDynamicsTransition, self).__init__(
            self.state_dim, self.state_dim + self.hyper_dim)
        # Init hyper-parameters transformations
        self.mu = mu
        self.phi = phi
        self.sigma = sigma
        counter = 1
        if is_mu_hyper:
            self.index_mu = counter
            counter += 1
        if is_sigma_hyper:
            self.index_sigma = counter
            counter += 1
        if is_phi_hyper:
            self.index_phi = counter
            counter += 1

    def extract_variables(self, x):
        # Extract variables Xt, Xmu, Xsigma, Xphi
        (Xt, Xmu, Xsigma, Xphi) = (x[:,0], None, None, None)
        if self.is_mu_hyper:
            Xmu = x[:,self.index_mu]
        if self.is_phi_hyper:
            Xphi = x[:,self.index_phi]
        if self.is_sigma_hyper:
            Xsigma = x[:,self.index_sigma]
        return (Xt, Xmu, Xsigma, Xphi)

    def log_pdf(self, x, y, *args, **kwargs):
        Xtp1 = x[:,0]
        (Xt, Xmu, Xsigma, Xphi) = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate
        return -.5*1/f_Xsigma**2 * \
            ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )**2 - np.log(f_Xsigma)

    def grad_x_log_pdf(self, x, y, *args, **kwargs):
        Xtp1 = x[:,0]
        (Xt, Xmu, Xsigma, Xphi) = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate gradients of transform functions
        if self.is_phi_hyper:
            grad_f_Xphi = self.phi.grad_x(Xphi)
        if self.is_sigma_hyper:
            grad_f_Xsigma = self.sigma.grad_x(Xsigma)
        # Evaluate
        sdim = self.state_dim
        hdim = self.hyper_dim
        grad = np.zeros( (x.shape[0], 2*sdim + hdim) )
        grad[:,1] = f_Xphi/f_Xsigma**2*( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
        grad[:,0] = -1/f_Xsigma**2*( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
        if self.is_mu_hyper:
            grad[:,sdim+self.index_mu] = - (f_Xphi-1)/f_Xsigma**2 * \
                                    ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
        if self.is_sigma_hyper:
            grad[:,sdim+self.index_sigma] = grad_f_Xsigma/f_Xsigma * \
                (1/f_Xsigma**2 * (Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu))**2-1)
        if self.is_phi_hyper:
            grad[:,sdim+self.index_phi] =  grad_f_Xphi/f_Xsigma**2 * \
                ( Xt - f_Xmu ) * ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
        return grad

    def hess_x_log_pdf(self, x, y, *args, **kwargs):
        Xtp1 = x[:,0]
        (Xt, Xmu, Xsigma, Xphi) = self.extract_variables(y)
        # Evaluate transform functions
        f_Xmu = self.mu.evaluate(Xmu)
        f_Xphi = self.phi.evaluate(Xphi)
        f_Xsigma = self.sigma.evaluate(Xsigma)
        # Evaluate gradients and Hessians of transform functions
        if self.is_phi_hyper:
            grad_f_Xphi = self.phi.grad_x(Xphi)
            hess_f_Xphi = self.phi.hess_x(Xphi)
        if self.is_sigma_hyper:
            grad_f_Xsigma = self.sigma.grad_x(Xsigma)
            hess_f_Xsigma = self.sigma.hess_x(Xsigma)
        # Evaluate
        sdim = self.state_dim
        hdim = self.hyper_dim
        hess = np.zeros( (x.shape[0], 2*sdim+hdim, 2*sdim+hdim) )
        hess[:,1,1] = -(f_Xphi/f_Xsigma)**2
        hess[:,0,0] = -1/f_Xsigma**2
        hess[:,1,0] =  f_Xphi/f_Xsigma**2
        hess[:,0,1] = hess[:,1,0]
        if self.is_mu_hyper:
            hess[:,sdim+self.index_mu,sdim+self.index_mu] =  - ( (f_Xphi-1)/f_Xsigma )**2
            hess[:,1,sdim+self.index_mu] =  (f_Xphi*(f_Xphi-1))/f_Xsigma**2
            hess[:,sdim+self.index_mu,1] = hess[:,1,sdim+self.index_mu]
            hess[:,0,sdim+self.index_mu] =  -(f_Xphi-1)/f_Xsigma**2
            hess[:,sdim+self.index_mu,0] = hess[:,0,sdim+self.index_mu]
            if self.is_sigma_hyper:
                hess[:,sdim+self.index_mu,sdim+self.index_sigma] = \
                    2*(f_Xphi-1)*grad_f_Xsigma/f_Xsigma**3 * \
                    ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
                hess[:,sdim+self.index_sigma,sdim+self.index_mu] = \
                    hess[:,sdim+self.index_mu,sdim+self.index_sigma]
            if self.is_phi_hyper:
                hess[:,sdim+self.index_mu,sdim+self.index_phi] = \
                    -grad_f_Xphi/f_Xsigma**2 * \
                    ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) ) + \
                    (f_Xphi - 1)/f_Xsigma**2*grad_f_Xphi*(Xt - f_Xmu)
                hess[:,sdim+self.index_phi,sdim+self.index_mu] = \
                    hess[:,sdim+self.index_mu,sdim+self.index_phi]
        if self.is_sigma_hyper:
            hess[:,sdim+self.index_sigma,sdim+self.index_sigma] = \
                (hess_f_Xsigma/f_Xsigma - (grad_f_Xsigma/f_Xsigma)**2) * \
                (1/f_Xsigma**2*(Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu))**2-1) - \
                2*grad_f_Xsigma**2/f_Xsigma**4*(Xtp1-f_Xmu-f_Xphi*(Xt-f_Xmu))**2
            hess[:,1,sdim+self.index_sigma] = \
                -2*f_Xphi/f_Xsigma**3*grad_f_Xsigma * \
                ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
            hess[:,sdim+self.index_sigma,1] = hess[:,1,sdim+self.index_sigma]
            hess[:,0,sdim+self.index_sigma] = \
                2*1/f_Xsigma**3*grad_f_Xsigma*( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
            hess[:,sdim+self.index_sigma,0] = hess[:,0,sdim+self.index_sigma]
            if self.is_phi_hyper:
                hess[:,sdim+self.index_sigma,sdim+self.index_phi]= \
                    -2*grad_f_Xsigma*grad_f_Xphi/f_Xsigma**3*(Xt-f_Xmu) * \
                    ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) )
                hess[:,sdim+self.index_phi,sdim+self.index_sigma] = \
                    hess[:,sdim+self.index_sigma,sdim+self.index_phi]
        if self.is_phi_hyper:
            hess[:,sdim+self.index_phi,sdim+self.index_phi] = \
                hess_f_Xphi/f_Xsigma**2*(Xt-f_Xmu) * \
                ( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) ) - \
                (grad_f_Xphi/f_Xsigma)**2*(Xt - f_Xmu)**2
            hess[:,1,sdim+self.index_phi] = \
                grad_f_Xphi/f_Xsigma**2*( Xtp1 - f_Xmu - f_Xphi*(Xt - f_Xmu) ) \
                - f_Xphi * grad_f_Xphi / f_Xsigma**2*(Xt - f_Xmu)
            hess[:,sdim+self.index_phi,1] = hess[:,1,sdim+self.index_phi]
            hess[:,0,sdim+self.index_phi] = grad_f_Xphi/f_Xsigma**2*(Xt - f_Xmu)
            hess[:,sdim+self.index_phi,0] = hess[:,0,sdim+self.index_phi]
        return hess


##################
#   Likelihood   #        
##################
        
class LogLikelihood(LogLikelihood):
    r""" Abstract class for log-likelihood :math:`\log \pi({\bf y}_t \vert {\bf X}_t), \mu, \phi, \sigma`

    where, up to integration constants,

    .. math::

       \log\pi({\bf y}_t \vert {\bf X}_t, \mu, \phi, \sigma) = - \frac{1}{2}({\bf y}_t^2 \exp(-{\bf X}_t))
    
    Args:
      y (:class:`ndarray<numpy.ndarray>`): data
      is_mu_hyper (bool): whether :math:`\mu` is an hyper-parameter
      is_phi_hyper (bool): whether :math:`\phi` is an hyper-parameter
      is_sigma_hyper (bool): whether :math:`\sigma` is an hyper-parameter
    """
    def __init__(self, y,
                 is_mu_hyper=False, is_sigma_hyper=False, is_phi_hyper=False):
        #Local ordering of the input function: X0, Xmu, Xsigma, Xphi
        self.is_mu_hyper = is_mu_hyper
        self.is_sigma_hyper = is_phi_hyper
        self.is_phi_hyper = is_sigma_hyper
        self.hyper_dim = self.is_mu_hyper + self.is_sigma_hyper + self.is_phi_hyper
        self.state_dim = 1
        dim = self.state_dim + self.hyper_dim
        super(LogLikelihood, self).__init__(y, dim)

    def extract_variables(self, x):
        # Extract variable Xt out of (Xt, Xmu, Xsigma, Xphi)
        Xt = x[:,0]
        return Xt
    
    def evaluate(self, x, *args, **kwargs):
        Xt = self.extract_variables(x)
        return -.5 * self.y**2. * np.exp(-Xt) -.5 * Xt

    def grad_x(self, x, *args, **kwargs):
        Xt = self.extract_variables(x)
        out = np.zeros((x.shape[0], self.dim))
        out[:,0] = .5 * self.y**2. * np.exp(-Xt) - .5
        return out

    def hess_x(self, x, *args, **kwargs):
        Xt = self.extract_variables(x)
        out = np.zeros((x.shape[0], self.dim, self.dim))
        out[:,0,0] = - .5 * self.y**2. * np.exp(-Xt)
        return out


##################
# Full Posterior #
##################

class StocVolHyperDistribution(SequentialHiddenMarkovChainDistribution):
    def __init__(self,
                 is_mu_hyper=False, is_sigma_hyper=False, is_phi_hyper=False,
                 mu=None, sigma=None, phi=None, 
                 mu_sigma=1.,
                 sigma_k=1., sigma_theta=.1,
                 phi_mean=3., phi_std=1.):
        # Initialize true dynamic (optionally provided)
        self.Xt = None
        # Build prior on hyper parameters if necessary
        self.is_mu_hyper = is_mu_hyper
        self.is_phi_hyper = is_phi_hyper
        self.is_sigma_hyper = is_sigma_hyper
        hyper_dim = is_mu_hyper + is_phi_hyper + is_sigma_hyper
        if hyper_dim > 0:
            pi_hyper = PriorHyperParameters(is_mu_hyper, is_sigma_hyper, is_phi_hyper,
                                            mu_sigma)
        else:
            pi_hyper = None
        # Store transformations
        if is_mu_hyper:
            self.mu = IdentityFunction()
        else:
            self.mu = ConstantFunction(mu)
        if is_phi_hyper:
            self.phi = F_phi(phi_mean, phi_std)
        else:
            self.phi = ConstantFunction(phi)
        if is_sigma_hyper:
            self.sigma = F_sigma(sigma_k, sigma_theta)
        else:
            self.sigma = ConstantFunction(sigma)
        # Initialize distribution (no transitions defined yet)
        super(StocVolHyperDistribution, self).__init__([], [], pi_hyper)

    @property
    def index_mu(self):
        if self.is_mu_hyper:
            return 0
        else:
            return None
    @property
    def index_sigma(self):
        if self.is_sigma_hyper:
            counter = len([o for o in [self.index_mu] if o is not None])
            return counter
        else:
             return None
    @property
    def index_phi(self):
        if self.is_phi_hyper:
            counter = len([o for o in [self.index_mu, self.index_sigma]
                           if o is not None])
            return counter
        else:
            return None

    def get_tvec(self):
        return np.arange(self.get_nsteps())

    def get_nsteps(self):
        return len(self.pi_list)

    def assimilate(self, y=None, Xt=None):
        r""" Assimilate one piece of data.

        Args:
          y (:class:`ndarray<numpy.ndarray>`): data. ``y==None`` stands for missing data.
          Xt (:class:`ndarray<numpy.ndarray>`): true dynamics
        """
        ll = None
        if y is not None:
            ll = LogLikelihood(y, self.is_mu_hyper,
                               self.is_sigma_hyper, self.is_phi_hyper)
        if len(self.pi_list) == 0: # Initial conditions
            pi = PriorDynamicsInitialConditions(
                self.is_mu_hyper, self.mu,
                self.is_sigma_hyper, self.sigma,
                self.is_phi_hyper, self.phi)
            if Xt is not None:
                self.Xt = [Xt]
        else: # Transitions
            pi = PriorDynamicsTransition(
                self.is_mu_hyper, self.mu,
                self.is_sigma_hyper, self.sigma,
                self.is_phi_hyper, self.phi)
            if Xt is not None:
                if self.Xt is None or len(self.Xt) != len(self.pi_list):
                    raise ValueError("The true dynamics must be provided " + \
                                     "at all steps, if one wish to privide them")
                self.Xt.append(Xt)
        self.append(pi, ll)

def generate_data(nsteps, mu = None, sigma = None, phi = None):
    #Random initial conditions
    x0 = sigma/np.sqrt(1.-phi**2)*np.random.randn(1) + mu
    #Noise observations
    noise_obs = np.random.randn(nsteps)
    #Noise dynamics
    noise_dyn = np.random.randn(nsteps)
    # Allocate variables
    Xt = np.zeros(nsteps)
    Xt[0] = x0
    # Simulate
    for ii in range(nsteps-1):
        Xt[ii+1] = mu+phi*(Xt[ii]-mu) + sigma*noise_dyn[ii]
    #Collect observations
    dataObs = list(noise_obs*np.exp(.5*Xt))
    return (dataObs, Xt)

def trim_distribution(old_dens, nsteps):
    old_nsteps = old_dens.get_nsteps()
    if nsteps > old_nsteps:
        raise ValueError("The number of steps can only be decreased with this function")
    new_dens = cp.deepcopy(old_dens)
    # re-init distribution
    new_dens.dim = new_dens.hyper_dim
    new_pi_list = new_dens.pi_list[:nsteps]
    new_ll_list = new_dens.ll_list[:nsteps]
    new_dens.pi_list = []
    new_dens.ll_list = []
    for pi, ll in zip(new_pi_list, new_ll_list):
        new_dens.append(pi, ll)
    return new_dens
    
    
