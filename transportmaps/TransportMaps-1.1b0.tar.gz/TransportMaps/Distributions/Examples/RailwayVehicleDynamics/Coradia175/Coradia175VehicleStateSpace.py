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
import scipy.linalg as scila
import scipy.integrate as sciint

import SpectralToolbox.Spectral1D as S1D

from TransportMaps.Maps.MapBase import Map, ConstantMap
from TransportMaps.Distributions import \
    GaussianDistribution, ConditionallyGaussianDistribution
from TransportMaps.Distributions.Decomposable.LinearGaussianSequentialInferenceDistributions import \
    ConditionallyLinearGaussianAR1TransitionDistribution
from TransportMaps.Likelihoods import \
    AdditiveConditionallyLinearGaussianLogLikelihood

__all__ = ['DEFAULTS',
           'Coradia175Vehicle',
           'DynamicsMap', 'NoiseDynamicsMap', 'ObservationSystemMap',
           'ParametersPrior', 'StateSpacePrior', 'StateSpaceTransition',
           'StateSpaceLogLikelihood', 'generate_data',
           'Yw1', 'Yw1dot',
           'Pw1', 'Pw1dot', 
           'Yw2', 'Yw2dot', 
           'Pw2', 'Pw2dot', 
           'Yb', 'Ybdot',
           'Pb', 'Pbdot',  
           'Yc', 'Ycdot',  
           'D1', 'D2']

nax = np.newaxis

# Position of degrees of freedom
NDOFS  = 0
Yw1    = NDOFS; NDOFS += 1;
Yw1dot = NDOFS; NDOFS += 1;
Pw1    = NDOFS; NDOFS += 1;
Pw1dot = NDOFS; NDOFS += 1;
Yw2    = NDOFS; NDOFS += 1;
Yw2dot = NDOFS; NDOFS += 1;
Pw2    = NDOFS; NDOFS += 1;
Pw2dot = NDOFS; NDOFS += 1;
Yb     = NDOFS; NDOFS += 1;
Ybdot  = NDOFS; NDOFS += 1;
Pb     = NDOFS; NDOFS += 1;
Pbdot  = NDOFS; NDOFS += 1;
Yc     = NDOFS; NDOFS += 1;
Ycdot  = NDOFS; NDOFS += 1;
D1     = NDOFS; NDOFS += 1;
D2     = NDOFS; NDOFS += 1;

# Default values
DEFAULTS = {
    'L_Ky':   (4000.)*10**3,   # Leading primary spring lateral (kN/m)
    'T_Ky':   (4000.)*10**3,   # Trailing primary spring lateral (kN/m)
    'L_KPsi': (4000.)*10**3,   # Primary yaw stiffness (kN/rad)
    'T_KPsi': (4000.)*10**3,   # Primary yaw stiffness (kN/rad)
    'Kyb':    (160.)*10**3,    # Secondary lateral stiffness (kN/m)
    'Cyb':    (16.)*10**3,     # Secondary lateral damping (kN s/m)
    'CPb':    (500.)*10**3,    # Secondary anti-yaw damping (kN s/rad)
    'f11':    7.4*10**6,       # Longitudinal creep coeff (MN)
    'f22':    6.2*10**6,       # Lateral creep coeff (MN)
}


class Coradia175Vehicle(object):
    r"""
    Args:
      v (float): Longitudinal vehicle velocity (m/s)
    """
    mw     = 1000.     # Wheel set mass (kg)
    Iw     = 600.      # Wheel set yaw inertia (kg * m^2)
    mb     = 2000.     # Bogie mass (kg)
    Ib     = 2300.     # Bogie yaw inertia (kg * m^2)
    mc     = 8720.     # Half vehicle mass (kg)
    a      = 1.05      # Semi wheel-wheel spacing (m)
    l      = 0.75      # Half gauge (m)
    lmb    = 0.15      # Conicity
    r0     = 0.37      # Wheelset radius (m)
    
    def __init__(self, v,
                 observables=[Ybdot, Pb, Ycdot],
                 dt = 1e-2,                        # Discretization time
                 # Ar = 2 * 0.33 * 1e-3 # Original
                 Ar = 2 * 0.33 * 1e-6,             # Track roughness - reduced
                 # Noises
                 init_noise = 1e-6,
                 # obs_noise = {'Yw1dot': 1e-4 * 1e2,
                 #              'Yw2dot': 1e-4 * 1e2,
                 #              'Ybdot':  4.11 * 1e-4 * 1e2,
                 #              'Pb':     3.75 * 1e-7 * 1e2,
                 #              'Ycdot':  7.62 * 1e-3 * 1e2}
                 obs_noise = {'Yw1dot': 1e-4 * 1e1,
                              'Yw2dot': 1e-4 * 1e1,
                              'Ybdot':  4.11 * 1e-4 * 1e1,
                              'Pb':     3.75 * 1e-7 * 1e1,
                              'Ycdot':  7.62 * 1e-3 * 1e1}
                 # obs_noise = {'Yw1dot': 1e-4,
                 #              'Yw2dot': 1e-4,
                 #              'Ybdot':  4.11 * 1e-4,
                 #              'Pb':     3.75 * 1e-7,
                 #              'Ycdot':  7.62 * 1e-3}
             ):
        self.v      = v         # Vehicle forward velocity (m/s)
        self.observables = observables
        self.dt = dt
        self.Ar = Ar
        self.init_noise = init_noise
        self.obs_noise = obs_noise

    def get_system_matrix(
            self,
            L_Ky   = DEFAULTS['L_Ky'],     # Leading primary spring lateral (kN/m)
            T_Ky   = DEFAULTS['T_Ky'],     # Trailing primary spring lateral (kN/m)
            L_KPsi = DEFAULTS['L_KPsi'],   # Primary yaw stiffness (kN/rad)
            T_KPsi = DEFAULTS['T_KPsi'],   # Primary yaw stiffness (kN/rad)
            Kyb    = DEFAULTS['Kyb'],      # Secondary lateral stiffness (kN/m)
            Cyb    = DEFAULTS['Cyb'],      # Secondary lateral damping (kN s/m)
            CPb    = DEFAULTS['CPb'],      # Secondary anti-yaw damping (kN s/rad)
            f11    = DEFAULTS['f11'],      # Longitudinal creep coeff (MN)
            f22    = DEFAULTS['f22'],      # Lateral creep coeff (MN)
    ):
        ###################
        # System dynamics #
        ###################
        A = np.zeros((NDOFS,NDOFS))
        # Lateral displacement front wheelset
        A[Yw1,Yw1dot]    = 1.
        A[Yw1dot,Yw1]    = - L_Ky
        A[Yw1dot,Yw1dot] = - 2. * f22 / self.v
        A[Yw1dot,Pw1]    = 2. * f22 
        A[Yw1dot,Yb]     = L_Ky 
        A[Yw1dot,Pb]     = self.a * L_Ky 
        A[Yw1dot,:]     /= self.mw
        # Yaw front wheelset
        A[Pw1,Pw1dot]    = 1.
        A[Pw1dot,Pw1dot] = - 2. * f11 * self.l**2 / self.v
        A[Pw1dot,Pw1]    = - L_KPsi
        A[Pw1dot,Pb]     = L_KPsi
        A[Pw1dot,D1]     = - 2. * f11 * self.lmb * self.l / self.r0
        A[Pw1dot,:]     /= self.Iw
        # Lateral displacement trailing wheelset
        A[Yw2,Yw2dot]    = 1.
        A[Yw2dot,Yw2]    = - T_Ky
        A[Yw2dot,Yw2dot] = - 2. * f22 / self.v
        A[Yw2dot,Pw2]    = 2. * f22 
        A[Yw2dot,Yb]     = T_Ky 
        A[Yw2dot,Pb]     = self.a * T_Ky 
        A[Yw2dot,:]     /= self.mw
        # Yaw trailing wheelset
        A[Pw2,Pw2dot]    = 1.
        A[Pw2dot,Pw2dot] = - 2. * f11 * self.l**2 / self.v
        A[Pw2dot,Pw2]    = - T_KPsi
        A[Pw2dot,Pb]     = T_KPsi
        A[Pw2dot,D2]     = - 2. * f11 * self.lmb * self.l / self.r0
        A[Pw2dot,:]     /= self.Iw
        # Lateral displacement bogie frame
        A[Yb,Ybdot]      = 1.
        A[Ybdot,Yw1]     = L_Ky
        A[Ybdot,Yw2]     = T_Ky
        A[Ybdot,Ybdot]   = - Cyb
        A[Ybdot,Yb]      = - (L_Ky + T_Ky + Kyb)
        A[Ybdot,Ycdot]   = Cyb
        A[Ybdot,Yc]      = Kyb
        A[Ybdot,:]      /= self.mb
        # Yaw bogie frame
        A[Pb,Pbdot]      = 1.
        A[Pbdot,Yw1]     = self.a * L_Ky
        A[Pbdot,Pw1]     = L_KPsi
        A[Pbdot,Yw2]     = - self.a * T_Ky 
        A[Pbdot,Pw2]     = T_KPsi
        A[Pbdot,Pbdot]   = - CPb
        A[Pbdot,Pb]      = - (L_Ky + T_Ky) * self.a**2 \
                                - (L_KPsi + T_KPsi)
        A[Pbdot,:]      /= self.Ib
        # Lateral displacement car body (MODIFIED!)
        A[Yc,Ycdot]      = 1.
        A[Ycdot,Ybdot]   = Cyb
        A[Ycdot,Yb]      = Kyb
        A[Ycdot,Ycdot]   = -Cyb
        A[Ycdot,Yc]      = - Kyb
        A[Ycdot,:]      /= self.mc
        # Lateral track displacement (leading wheelset)
        A[D1,Yw1dot]     = 1.
        A[D2,Yw2dot]     = 1.
        return A

    def get_grad_system_matrix(
            self,
            par_name_list,  # List of parameters over which to compute the gradient
            L_Ky   = DEFAULTS['L_Ky'],     # Leading primary spring lateral (kN/m)
            T_Ky   = DEFAULTS['T_Ky'],     # Trailing primary spring lateral (kN/m)
            L_KPsi = DEFAULTS['L_KPsi'],   # Primary yaw stiffness (kN/rad)
            T_KPsi = DEFAULTS['T_KPsi'],   # Primary yaw stiffness (kN/rad)
            Kyb    = DEFAULTS['Kyb'],      # Secondary lateral stiffness (kN/m)
            Cyb    = DEFAULTS['Cyb'],      # Secondary lateral damping (kN s/m)
            CPb    = DEFAULTS['CPb'],      # Secondary anti-yaw damping (kN s/rad)
            f11    = DEFAULTS['f11'],      # Longitudinal creep coeff (MN)
            f22    = DEFAULTS['f22'],      # Lateral creep coeff (MN)
    ):
        gA = np.zeros((NDOFS,NDOFS,len(par_name_list)))
        cntr = 0 # Counter for free parameters
        if 'L_Ky' in par_name_list:
            # Lateral displacement front wheelset
            gA[Yw1dot,Yw1,cntr]    = - 1.
            gA[Yw1dot,Yb,cntr]     = 1.
            gA[Yw1dot,Pb,cntr]     = self.a
            gA[Yw1dot,:,cntr]     /= self.mw
            # Lateral displacement bogie frame
            gA[Ybdot,Yw1,cntr]     = 1.
            gA[Ybdot,Yb,cntr]      = - 1.
            gA[Ybdot,:,cntr]      /= self.mb
            # Yaw bogie frame
            gA[Pbdot,Yw1,cntr]     = self.a 
            gA[Pbdot,Pb,cntr]      = - self.a**2 
            gA[Pbdot,:,cntr]      /= self.Ib
            # Update counter
            cntr += 1
        if 'T_Ky' in par_name_list:
            # Lateral displacement trailing wheelset
            gA[Yw2dot,Yw2,cntr]    = - 1.
            gA[Yw2dot,Yb,cntr]     = 1.
            gA[Yw2dot,Pb,cntr]     = self.a 
            gA[Yw2dot,:,cntr]     /= self.mw
            # Lateral displacement bogie frame
            gA[Ybdot,Yw2,cntr]     = 1.
            gA[Ybdot,Yb,cntr]      = - 1.
            gA[Ybdot,:,cntr]      /= self.mb
            # Yaw bogie frame
            gA[Pbdot,Yw2,cntr]     = - self.a 
            gA[Pbdot,Pb,cntr]      = - self.a**2 
            gA[Pbdot,:,cntr]      /= self.Ib
            # Update counter
            cntr += 1
        if 'L_KPsi' in par_name_list:
            # Yaw front wheelset
            gA[Pw1dot,Pw1,cntr]    = - 1.
            gA[Pw1dot,Pb,cntr]     = 1.
            gA[Pw1dot,:,cntr]     /= self.Iw
            # Yaw bogie frame
            gA[Pbdot,Pw1,cntr]     = 1.
            gA[Pbdot,Pb,cntr]      = - 1.
            gA[Pbdot,:,cntr]      /= self.Ib
            # Update counter
            cntr += 1
        if 'T_KPsi' in par_name_list:
            # Yaw trailing wheelset
            gA[Pw2dot,Pw2,cntr]    = - 1.
            gA[Pw2dot,Pb,cntr]     = 1.
            gA[Pw2dot,:,cntr]     /= self.Iw
            # Yaw bogie frame
            gA[Pbdot,Pw2,cntr]     = 1.
            gA[Pbdot,Pb,cntr]      = - 1.
            gA[Pbdot,:,cntr]      /= self.Ib
            # Update counter
            cntr += 1
        if 'Kyb' in par_name_list:
            # Lateral displacement bogie frame
            gA[Ybdot,Yb,cntr]      = - 1.
            gA[Ybdot,Yc,cntr]      = 1.
            gA[Ybdot,:,cntr]      /= self.mb
            # Lateral displacement car body (MODIFIED!)
            gA[Ycdot,Yb,cntr]      = 1.
            gA[Ycdot,Yc,cntr]      = - 1.
            gA[Ycdot,:,cntr]      /= self.mc
            # Update counter
            cntr += 1
        if 'Cyb' in par_name_list:
            # Lateral displacement bogie frame
            gA[Ybdot,Ybdot,cntr]   = - 1.
            gA[Ybdot,Ycdot,cntr]   = 1.
            gA[Ybdot,:,cntr]      /= self.mb
            # Lateral displacement car body (MODIFIED!)
            gA[Ycdot,Ybdot,cntr]   = 1.
            gA[Ycdot,Ycdot,cntr]   = - 1.
            gA[Ycdot,:,cntr]      /= self.mc
            # Update counter
            cntr += 1
        if 'CPb' in par_name_list:
            # Yaw bogie frame
            gA[Pbdot,Pbdot,cntr]   = - 1.
            gA[Pbdot,:,cntr]      /= self.Ib
            # Update counter
            cntr += 1
        if 'f11' in par_name_list:
            # Yaw front wheelset
            gA[Pw1dot,Pw1dot,cntr] = - 2. * self.l**2 / self.v
            gA[Pw1dot,D1,cntr]     = - 2. * self.lmb * self.l / self.r0
            gA[Pw1dot,:,cntr]     /= self.Iw
            # Yaw trailing wheelset
            gA[Pw2dot,Pw2dot,cntr] = - 2. * self.l**2 / self.v
            gA[Pw2dot,D2,cntr]     = - 2. * self.lmb * self.l / self.r0
            gA[Pw2dot,:,cntr]     /= self.Iw
            # Update counter
            cntr += 1
        if 'f22' in par_name_list:
            # Lateral displacement front wheelset
            gA[Yw1dot,Yw1dot,cntr] = - 2. / self.v
            gA[Yw1dot,Pw1,cntr]    = 2.
            gA[Yw1dot,:,cntr]     /= self.mw
            # Lateral displacement trailing wheelset
            gA[Yw2dot,Yw2dot,cntr] = - 2. / self.v
            gA[Yw2dot,Pw2,cntr]    = 2. 
            gA[Yw2dot,:,cntr]     /= self.mw
            # Update counter
            cntr += 1
        return gA
        
    def get_track_matrix(self):
        #################
        # Track control #
        #################
        G = np.zeros((NDOFS,NDOFS))
        G[D1,D1] = -1.
        G[D2,D2] = -1.
        return G

    def get_grad_track_matrix(self, par_name_list):
        dG = np.zeros((NDOFS,NDOFS,len(par_name_list)))
        return dG

    def get_observation_matrix(
            self,
            L_Ky   = DEFAULTS['L_Ky'],     # Leading primary spring lateral (kN/m)
            T_Ky   = DEFAULTS['T_Ky'],     # Trailing primary spring lateral (kN/m)
            L_KPsi = DEFAULTS['L_KPsi'],   # Primary yaw stiffness (kN/rad)
            T_KPsi = DEFAULTS['T_KPsi'],   # Primary yaw stiffness (kN/rad)
            Kyb    = DEFAULTS['Kyb'],      # Secondary lateral stiffness (kN/m)
            Cyb    = DEFAULTS['Cyb'],      # Secondary lateral damping (kN s/m)
            CPb    = DEFAULTS['CPb'],      # Secondary anti-yaw damping (kN s/rad)
            f11    = DEFAULTS['f11'],      # Longitudinal creep coeff (MN)
            f22    = DEFAULTS['f22'],      # Lateral creep coeff (MN)
    ):
        A = self.get_system_matrix(L_Ky, T_Ky, L_KPsi, T_KPsi,
                                   Kyb, Cyb, CPb, f11, f22)
        ################
        # Observations #
        ################
        H = A[self.observables, :]
        return H

    def get_grad_observation_matrix(
            self,
            par_name_list,
            L_Ky   = DEFAULTS['L_Ky'],     # Leading primary spring lateral (kN/m)
            T_Ky   = DEFAULTS['T_Ky'],     # Trailing primary spring lateral (kN/m)
            L_KPsi = DEFAULTS['L_KPsi'],   # Primary yaw stiffness (kN/rad)
            T_KPsi = DEFAULTS['T_KPsi'],   # Primary yaw stiffness (kN/rad)
            Kyb    = DEFAULTS['Kyb'],      # Secondary lateral stiffness (kN/m)
            Cyb    = DEFAULTS['Cyb'],      # Secondary lateral damping (kN s/m)
            CPb    = DEFAULTS['CPb'],      # Secondary anti-yaw damping (kN s/rad)
            f11    = DEFAULTS['f11'],      # Longitudinal creep coeff (MN)
            f22    = DEFAULTS['f22'],      # Lateral creep coeff (MN)
    ):
        gA = self.get_grad_system_matrix(
            par_name_list,
            L_Ky, T_Ky, L_KPsi, T_KPsi, Kyb, Cyb, CPb, f11, f22)
        gH = gA[self.observables, :, :]
        return gH
        
    def get_matrices(
            self,
            L_Ky   = DEFAULTS['L_Ky'],     # Leading primary spring lateral (kN/m)
            T_Ky   = DEFAULTS['T_Ky'],     # Trailing primary spring lateral (kN/m)
            L_KPsi = DEFAULTS['L_KPsi'],   # Primary yaw stiffness (kN/rad)
            T_KPsi = DEFAULTS['T_KPsi'],   # Primary yaw stiffness (kN/rad)
            Kyb    = DEFAULTS['Kyb'],      # Secondary lateral stiffness (kN/m)
            Cyb    = DEFAULTS['Cyb'],      # Secondary lateral damping (kN s/m)
            CPb    = DEFAULTS['CPb'],      # Secondary anti-yaw damping (kN s/rad)
            f11    = DEFAULTS['f11'],      # Longitudinal creep coeff (MN)
            f22    = DEFAULTS['f22'],      # Lateral creep coeff (MN)
    ):
        A = self.get_system_matrix(L_Ky, T_Ky, L_KPsi, T_KPsi,
                                   Kyb, Cyb, CPb, f11, f22)
        G = self.get_track_matrix()
        H = self.get_observation_matrix(L_Ky, T_Ky, L_KPsi, T_KPsi,
                                        Kyb, Cyb, CPb, f11, f22)
        return (A, G, H)

def grad_exp_integrand(xx, A, gA):
    out = np.zeros((xx.shape[0],) + gA.shape)
    for i, x in enumerate(xx):
        out[i] = np.einsum('ij,jk...->ik...', scila.expm(x*A),
                           np.einsum('ij...,jk->ik...', gA, scila.expm((1.-x)*A)) )
    return out

def chebnorm(A):
    return np.max(np.abs(A))

def grad_exp(A, gA, rtol=1e-10, atol=1e-16, maxord=100, startord=-1, noit=False):
    P = S1D.JacobiPolynomial(0.,0.)
    order = startord
    old = np.zeros(gA.shape)
    new = np.inf * np.ones(gA.shape)
    nrm = [chebnorm(old - new)]
    stop = False
    while not stop and order < maxord and \
          nrm[-1] > rtol * min(chebnorm(old),chebnorm(new)) + atol:
        order += 1
        old = new
        (x, w) = P.Quadrature(order)
        x = (x+1)/2.
        w /= 2.
        new = np.einsum('i,i...->...', w, grad_exp_integrand(x, A, gA))
        nrm.append( chebnorm(old - new) )
        stop = noit
    if order == maxord:
        raise RuntimeError("Quadrature did not converge")
    return new

class ParametersPrior(GaussianDistribution):
    def __init__(self, par_name_list):
        self.par_name_list = par_name_list
        dim = len(par_name_list)
        mu = np.zeros(dim)
        sigma2 = np.zeros((dim,dim))
        for i, par_name in enumerate(par_name_list):
            mu[i] = DEFAULTS[par_name]
            std = 0.05 * mu[i]
            sigma2[i,i] = std**2
        super(ParametersPrior,self).__init__(mu, sigma2)
    
class StateSpacePrior(ConditionallyGaussianDistribution):
    def __init__(self, vehicle, par_name_list=[], init_coeffs=None):
        mu = np.zeros(NDOFS)
        Q0 = vehicle.init_noise * np.eye(NDOFS)
        muMap = ConstantMap(len(par_name_list), mu)
        Q0Map = ConstantMap(len(par_name_list), Q0)
        super(StateSpacePrior,self).__init__(
            muMap, sigma=Q0Map, coeffs=init_coeffs)

class DynamicsMap(Map): # Generates matrix Phi
    def __init__(self, vehicle, par_name_list=[]):
        self._vehicle = vehicle
        self._par_name_list = par_name_list
        super(DynamicsMap, self).__init__(
            len(par_name_list), NDOFS**2)
    def evaluate(self, x, *args, **kwargs):
        m = x.shape[0]
        Phi = np.zeros((m, NDOFS, NDOFS))
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            A = self._vehicle.get_system_matrix(**kwargs)
            dt = self._vehicle.dt
            Phi[i,:,:] = scila.expm(dt * A)
        return Phi
    def grad_x(self, x, *args, **kwargs):
        m = x.shape[0]
        gPhi = np.zeros((m, NDOFS, NDOFS, len(self._par_name_list)))
        if len(self._par_name_list) == 0:
            return gPhi
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            A = self._vehicle.get_system_matrix(**kwargs)
            kwargs.update({'par_name_list': self._par_name_list})
            gA = self._vehicle.get_grad_system_matrix(**kwargs)
            dt = self._vehicle.dt
            gPhi[i] = grad_exp(dt*A, dt*gA, startord=50, noit=True)
        return gPhi

class NoiseDynamicsMap(Map): # Generates matrix Q
    def __init__(self, vehicle, par_name_list=[]):
        self._vehicle = vehicle
        self._par_name_list = par_name_list
        super(NoiseDynamicsMap, self).__init__(
            len(par_name_list), NDOFS**2)
    def evaluate(self, x, *args, **kwargs):
        m = x.shape[0]
        Q = np.zeros((m, NDOFS, NDOFS))
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            A = self._vehicle.get_system_matrix(**kwargs)
            G = self._vehicle.get_track_matrix()
            # Dynamic noise
            v = self._vehicle.v
            Ar = self._vehicle.Ar
            dt = self._vehicle.dt
            sigma = np.sqrt( 4 * np.pi**2 * Ar * v**2 * dt)
            W = sigma * np.eye(NDOFS)
            # Pade approximations
            GWG = np.dot(G, np.dot(W, G.T))
            A1 = np.zeros((2*NDOFS,2*NDOFS))
            A1[:NDOFS,:NDOFS] = - A
            A1[:NDOFS,NDOFS:] = GWG
            A1[NDOFS:,NDOFS:] = A.T
            B = scila.expm(dt * A1)
            Phi = B[NDOFS:,NDOFS:].T
            Q[i,:,:] = np.dot(Phi, B[:NDOFS,NDOFS:])
        return Q
    def grad_x(self, x, *args, **kwargs):
        m = x.shape[0]
        dQ = np.zeros((m, NDOFS, NDOFS, len(self._par_name_list)))
        if len(self._par_name_list) == 0:
            return dQ
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            A = self._vehicle.get_system_matrix(**kwargs)
            G = self._vehicle.get_track_matrix()
            kwargs.update({'par_name_list': self._par_name_list})
            dA = self._vehicle.get_grad_system_matrix(**kwargs)
            # Dynamic noise
            v = self._vehicle.v
            Ar = self._vehicle.Ar
            dt = self._vehicle.dt
            sigma = np.sqrt( 4 * np.pi**2 * Ar * v**2 * dt )
            W = sigma * np.eye(NDOFS)
            GWG = np.dot(G, np.dot(W, G.T))
            # Pade approximations Phi, Phi1Q
            A1 = np.zeros((2*NDOFS,2*NDOFS))
            A1[:NDOFS,:NDOFS] = - A
            A1[:NDOFS,NDOFS:] = GWG
            A1[NDOFS:,NDOFS:] = A.T
            B = scila.expm(dt * A1)
            Phi = B[NDOFS:,NDOFS:].T
            Phi1Q = B[:NDOFS,NDOFS:]
            # Pade approximation dPhi
            dPhi = grad_exp(dt*A, dt*dA, startord=50, noit=True)
            # Pade approximation dPhi1Q
            dA1 = np.zeros((2*NDOFS,2*NDOFS,len(self._par_name_list)))
            dA1[:NDOFS,:NDOFS,:] = - dA
            dA1[NDOFS:,NDOFS:,:] = dA.transpose((1,0,2))
            dB = grad_exp(dt*A1, dt*dA1, startord=50, noit=True)
            dPhi1Q = dB[:NDOFS,NDOFS:,:]
            # Compute gradient
            dQ[i] = np.einsum('ijk,jl->ilk', dPhi, Phi1Q) + \
                    np.einsum('ij,jkl->ikl', Phi, dPhi1Q)
        return dQ
        
class StateSpaceTransition(ConditionallyLinearGaussianAR1TransitionDistribution):
    def __init__(self, vehicle, par_name_list=[], init_coeffs=None):
        self.vehicle = vehicle
        c = ConstantMap(len(par_name_list), np.zeros(NDOFS))
        PhiMap = DynamicsMap(vehicle, par_name_list)
        mu = ConstantMap(len(par_name_list), np.zeros(NDOFS))
        QMap = NoiseDynamicsMap(vehicle, par_name_list)
        # Init
        super(StateSpaceTransition,self).__init__(
            c, PhiMap, mu, sigma=QMap, coeffs=init_coeffs)

class ObservationSystemMap(Map): # Generates matrix H
    def __init__(self, vehicle, par_name_list=[]):
        self._vehicle = vehicle
        self._par_name_list = par_name_list
        super(ObservationSystemMap, self).__init__(
            len(par_name_list), len(vehicle.observables)*NDOFS)
    def evaluate(self, x, *args, **kwargs):
        m = x.shape[0]
        H = np.zeros((m, len(self._vehicle.observables), NDOFS))
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            H[i,:,:] = self._vehicle.get_observation_matrix(**kwargs)
        return H
    def grad_x(self, x, *args, **kwargs):
        m = x.shape[0]
        dH = np.zeros((m, len(self._vehicle.observables), NDOFS, len(self._par_name_list)))
        for i in range(m):
            kwargs = {par_name: x[i,p]
                      for p, par_name in enumerate(self._par_name_list)}
            kwargs.update({'par_name_list': self._par_name_list})
            dH[i,:,:,:] = self._vehicle.get_grad_observation_matrix(**kwargs)
        return dH
        
class StateSpaceLogLikelihood(AdditiveConditionallyLinearGaussianLogLikelihood):
    def __init__(self, y, vehicle, par_name_list=[], init_coeffs=np.zeros(0)):
        HMap = ObservationSystemMap(vehicle, par_name_list)
        avars = list(range(len(par_name_list)))
        dy = y.shape[0]
        ###########
        # Original
        R = np.eye(NDOFS)
        R[Yw1dot,Yw1dot] = vehicle.obs_noise['Yw1dot']
        R[Yw2dot,Yw2dot] = vehicle.obs_noise['Yw2dot']
        R[Ybdot,Ybdot]   = vehicle.obs_noise['Ybdot']
        R[Pb,Pb]         = vehicle.obs_noise['Pb']
        R[Ycdot,Ycdot]   = vehicle.obs_noise['Ycdot']
        R = R[np.ix_(vehicle.observables, vehicle.observables)]
        # Prepare maps
        cMap = ConstantMap(len(par_name_list), np.zeros(dy))
        muMap = ConstantMap(len(par_name_list), np.zeros(dy))
        RMap = ConstantMap(len(par_name_list), R)
        super(StateSpaceLogLikelihood,self).__init__(
            y, cMap, HMap, muMap, RMap, coeffs=init_coeffs)

def generate_data(nsteps, vehicle, par_name_list=[], par_val_list=np.zeros(0)):
    prior = StateSpacePrior(vehicle, par_name_list, par_val_list)
    trans = StateSpaceTransition(vehicle, par_name_list, par_val_list)
    ll = StateSpaceLogLikelihood(
        np.zeros(len(vehicle.observables)), vehicle,
        par_name_list, par_val_list) # Just use to get handle on params
    # Generate dynamics
    T = np.zeros(nsteps+1)
    Z = np.zeros((nsteps+1, NDOFS))
    Z[0,:] = prior.rvs(1)[0,:]
    for i in range(nsteps):
        T[i+1] = T[i] + vehicle.dt
        Tin = np.hstack((Z[i,:], par_val_list))[nax,:]
        Z[i+1,:] = trans.T.evaluate(Tin)[0,:] + \
                   trans.pi.rvs(1,par_val_list)[0,:]
    # Generate observations
    Y = []
    for i in range(nsteps+1):
        Y.append( ll.T.evaluate(Z[[i],:])[0,:] + ll.pi.rvs(1)[0,:] )
    return (T,Z,Y)