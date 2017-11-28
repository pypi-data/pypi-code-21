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

import numpy as np

from TransportMaps.Distributions.FrozenDistributions import GaussianDistribution
from TransportMaps.Likelihoods.LikelihoodBase import LogLikelihood
from TransportMaps.Distributions.Inference.InferenceBase import BayesPosteriorDistribution
from TransportMaps.Algorithms.SequentialInference.LinearSequentialInference import \
    LinearFilter

from .Coradia175VehicleStateSpace import *

__all__ = ['ParametersLogLikelihood',
           'ParametersPosterior']

class ParametersLogLikelihood(LogLikelihood):
    def __init__(self, y, vehicle, par_name_list):
        self._vehicle = vehicle
        self._par_name_list = par_name_list
        dim = len(par_name_list)
        super(ParametersLogLikelihood, self).__init__(y, dim)

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def par_name_list(self):
        return self._par_name_list

    def evaluate(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("Input dimension mismatch.")
        m = x.shape[0]
        out = np.zeros(m)
        for i in range(m):
            pi_hyper = ParametersPrior(self._par_name_list)
            pi_prior = StateSpacePrior(self.vehicle, self._par_name_list, x[i,:])
            pi_trans = StateSpaceTransition(self.vehicle, self._par_name_list, x[i,:])
            FLT = LinearFilter(pi_hyper=pi_hyper)
            for n, y in enumerate(self.y):
                # Define log-likelihood
                if y is None: # Missing data
                    ll = None
                else: 
                    ll = StateSpaceLogLikelihood(
                        y, self.vehicle, self._par_name_list, init_coeffs=x[i,:])
                # Define transition / prior
                if n > 0: 
                    pin = pi_trans
                else:
                    pin = pi_prior
                # Assimilation
                FLT.assimilate(pin, ll)
            out[i] = FLT.marginal_log_likelihood
        return out

    def grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("Input dimension mismatch.")
        m = x.shape[0]
        out = np.zeros((m,len(self._par_name_list)))
        for i in range(m):
            pi_hyper = ParametersPrior(self._par_name_list)
            pi_prior = StateSpacePrior(self.vehicle, self._par_name_list, x[i,:])
            pi_trans = StateSpaceTransition(self.vehicle, self._par_name_list, x[i,:])
            FLT = LinearFilter(ders=1, pi_hyper=pi_hyper)
            for n, y in enumerate(self.y):
                # Define log-likelihood
                if y is None: # Missing data
                    ll = None
                else: 
                    ll = StateSpaceLogLikelihood(
                        y, self.vehicle, self._par_name_list, init_coeffs=x[i,:])
                # Define transition / prior
                if n > 0: 
                    pin = pi_trans
                else:
                    pin = pi_prior
                # Assimilation
                FLT.assimilate(pin, ll)
            out[i] = FLT.grad_marginal_log_likelihood
        return out

    def tuple_grad_x(self, x, *args, **kwargs):
        if x.shape[1] != self.dim:
            raise ValueError("Input dimension mismatch.")
        m = x.shape[0]
        ev = np.zeros(m)
        gx = np.zeros((m,len(self._par_name_list)))
        for i in range(m):
            pi_hyper = ParametersPrior(self._par_name_list)
            pi_prior = StateSpacePrior(self.vehicle, self._par_name_list, x[i,:])
            pi_trans = StateSpaceTransition(self.vehicle, self._par_name_list, x[i,:])
            FLT = LinearFilter(ders=1, pi_hyper=pi_hyper)
            for n, y in enumerate(self.y):
                # Define log-likelihood
                if y is None: # Missing data
                    ll = None
                else: 
                    ll = StateSpaceLogLikelihood(
                        y, self.vehicle, self._par_name_list, init_coeffs=x[i,:])
                # Define transition / prior
                if n > 0: 
                    pin = pi_trans
                else:
                    pin = pi_prior
                # Assimilation
                FLT.assimilate(pin, ll)
            ev[i] = FLT.marginal_log_likelihood
            gx[i] = FLT.grad_marginal_log_likelihood
        return (ev, gx)

class ParametersPosterior(BayesPosteriorDistribution):
    def __init__(self, y, vehicle, par_name_list, T=None, Z=None):
        self.T = T
        self.Z = Z
        prior = ParametersPrior(par_name_list)
        logL = ParametersLogLikelihood(y, vehicle, par_name_list)
        super(ParametersPosterior,self).__init__(logL, prior)