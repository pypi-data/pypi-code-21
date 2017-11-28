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

import collections
import numpy as np
import scipy.linalg as scila

from .SequentialInferenceBase import *

from TransportMaps.Distributions import GaussianDistribution
from TransportMaps.Likelihoods import AdditiveLinearGaussianLogLikelihood
from TransportMaps.Maps import LinearTransportMap, PermutationTransportMap, \
    ListCompositeTransportMap
from TransportMaps.Maps.Decomposable import LiftedTransportMap

__all__ = ['LinearFilter',
           'LinearSmoother']

class LinearFilter(Filter):
    r""" Perform the on-line filtering of a sequential linear Gaussian Hidden Markov chain.

    Aka: Kalman filter.

    If the linear state-space model is parametric, i.e.

    .. math::

       {\bf Z}_{k+1} = {\bf c}_k(\theta) + {\bf F}_k(\theta){\bf Z}_k + {\bf w}_k(\theta) \\
       {\bf Y}_{k} = {\bf H}_k(\theta){\bf Z}_k + {\bf v}_k(\theta)

    then one can optionally compute the gradient
    (with respect to the parameters) of the filter.

    Args:
      ders (int): ``0`` no gradient is computed, ``1`` compute gradient
      pi_hyper (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior distribution on the hyper-parameters :math:`\pi(\Theta)`
    
    .. todo:: Square-root filter
    """
    def __init__(self, ders=0, pi_hyper=None):
        super(LinearFilter, self).__init__(pi_hyper)
        self._marg_log_lklhood = 0.
        self._filt_mean_list = []
        self._filt_cov_list = []
        self._ders = ders
        if ders > 0:
            self._filt_grad_mean_list = []
            self._filt_grad_cov_list = []
            self._grad_marg_log_lklhood = 0.

    @property
    def marginal_log_likelihood(self):
        r""" Returns the marginal log-likelihood :math:`\log\pi\left({\bf Y}_{\Xi\leq k}\right)`

        Returns:
          (:class:`float`) -- current marginal likelihood
        """
        return self._marg_log_lklhood
        
    @property
    def filtering_mean_list(self):
        r""" Returns the means of all the filtering distributions

        Returns:
          (:class:`list` of :class:`float`) -- means of
            :math:`\pi\left({\bf Z}_k\middle\vert{\bf Y}_{\Xi\leq k}\right)`
            for :math:`k\in \Lambda=0,\ldots,n`.
        """
        return self._filt_mean_list

    @property
    def filtering_covariance_list(self):
        r""" Returns the covariances of all the filtering distributions

        Returns:
          (:class:`list` of :class:`ndarray<numpy.ndarray>`) -- covariances of
            :math:`\pi\left({\bf Z}_k\middle\vert{\bf Y}_{\Xi\leq k}\right)`
            for :math:`k\in \Lambda=0,\ldots,n`.
        """
        return self._filt_cov_list

    @property
    def grad_marginal_log_likelihood(self):
        r""" Returns the gradient of the marginal log-likelihood :math:`\nabla_\theta\log\pi\left({\bf Y}_{\Xi\leq k}\right)`

        Returns:
          (:class:`float`) -- current marginal likelihood
        """
        return self._grad_marg_log_lklhood
        
    @property
    def filtering_grad_mean_list(self):
        r""" Returns the gradient of the means of all the filtering distributions

        Returns:
          (:class:`list` of :class:`float`) -- gradient of the means of
            :math:`\pi\left({\bf Z}_k\middle\vert{\bf Y}_{\Xi\leq k}\right)`
            for :math:`k\in \Lambda=0,\ldots,n`.
        """
        return self._filt_grad_mean_list

    @property
    def filtering_grad_covariance_list(self):
        r""" Returns the gradient of the covariances of all the filtering distributions

        Returns:
          (:class:`list` of :class:`ndarray<numpy.ndarray>`) --
            gradient of the covariances of
            :math:`\pi\left({\bf Z}_k\middle\vert{\bf Y}_{\Xi\leq k}\right)`
            for :math:`k\in \Lambda=0,\ldots,n`.
        """
        return self._filt_grad_cov_list


    def _assimilation_step(self):
        r""" Assimilate one piece of Gaussian data :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}\right) \right)`.
        """
        pi = self.pi.pi_list[-1]
        ll = self.pi.ll_list[-1]

        # PRECIDTION STEP
        if self.nsteps == 0:
            # Load initial conditions x_{0|-1} and P_{0|-1}
            pred_x = pi.mu
            pred_P = pi.sigma
        else:
            # Load former state and covariance
            x = self._filt_mean_list[-1]
            P = self._filt_cov_list[-1]
            # Load transition system
            c = pi.T.c
            F = pi.T.T
            b = pi.pi.mu
            Q = pi.pi.sigma
            # Predict
            pred_x = c + F.dot(x) + b
            pred_P = F.dot(P.dot(F.T)) + Q
            
        # Gradient recursion
        if self._ders > 0:
            # Prediction step
            if self.nsteps == 0:
                pred_ga_x = pi.grad_a_mu
                pred_ga_P = pi.grad_a_sigma
            else:
                # Load former gradient state and gradient covariance
                ga_x = self._filt_grad_mean_list[-1]
                ga_P = self._filt_grad_cov_list[-1]
                # Load transition derivatives
                ga_c = pi.T.grad_a_c
                ga_F = pi.T.grad_a_T
                ga_b = pi.pi.grad_a_mu
                ga_Q = pi.pi.grad_a_sigma
                # Predict
                pred_ga_x = ga_c + np.einsum('ijk,j->ik', ga_F, x) + \
                            np.einsum('ij,jk->ik', F, ga_x) + ga_b
                # gF P F^T + F gP F^T + F P gF^T
                pred_ga_P = np.einsum('ijk,jl,ml->imk', ga_F, P, F) + \
                            np.einsum('ij,jkl,mk->iml', F, ga_P, F) + \
                            np.einsum('ij,jk,lkm->ilm', F, P, ga_F) + \
                            ga_Q

        # State and convariance after prediction
        x = pred_x
        P = pred_P
        if self._ders > 0:
            ga_x = pred_ga_x
            ga_P = pred_ga_P
            
        # Perform update if necessary
        up_x = x
        up_P = P
        if ll is not None:
            # Load observation system
            z = ll.y
            a = ll.T.c
            H = ll.T.T
            b = ll.pi.mu
            R = ll.pi.sigma
            # Compute update recursions
            y = z - a - b - np.dot(H, x) # Mesurament residual
            S = R + np.dot(H, np.dot(P, H.T)) # Innovation
            S12_factors = scila.cho_factor(S, True)
            S1y = scila.cho_solve(S12_factors, y)
            S1H = scila.cho_solve(S12_factors, H)
            KS = np.dot(P, H.T)
            Ky = np.dot(KS, S1y)
            KH = np.dot(KS, S1H)
            ImKH = np.eye(pi.dim) - KH
            # Upadtes (state, covariance, marginal likelihood)
            up_x = x + Ky
            up_P = np.dot(ImKH, P)
            self._marg_log_lklhood -= .5 * (np.dot(y, S1y) + \
                                            2 * np.sum(np.log(np.diag(S12_factors[0]))) + \
                                            y.shape[0] * np.log(2*np.pi))

        # Gradient recursion
        if ll is not None and self._ders > 0:
            # Load gradients of observation system
            ga_a = ll.T.grad_a_c
            ga_H = ll.T.grad_a_T
            ga_b = ll.pi.grad_a_mu
            ga_R = ll.pi.grad_a_sigma
            ncoeffs = ga_a.shape[1]
            # Compute update recursions
            ga_y = - (ga_a + ga_b + np.einsum('ijk,j->ik', ga_H, x) + \
                      np.einsum('ij,jk->ik', H, ga_x) )
            ga_S = ga_R + \
                   np.einsum('ijk,jl,ml->imk', ga_H, P, H) + \
                   np.einsum('ij,jkl,mk->iml', H, ga_P, H) + \
                   np.einsum('ij,jk,lkm->ilm', H, P, ga_H)
            S1gaS = np.zeros( ga_S.shape )
            for nc in range(ncoeffs):
                S1gaS[:,:,nc] = scila.cho_solve(S12_factors, ga_S[:,:,nc])
            ga_KS = np.einsum('ijk,lj->ilk', ga_P, H) + \
                    np.einsum('ij,kjl->ikl', P, ga_H) + \
                    np.einsum('ij,kj,klm->ilm', P, H, - S1gaS)
            S1gay = np.zeros( ga_y.shape )
            for nc in range(ncoeffs):
                S1gay[:,nc] = scila.cho_solve(S12_factors, ga_y[:,nc])
            S1gaH = np.zeros( ga_H.shape )
            for nc in range(ncoeffs):
                S1gaH[:,:,nc] = scila.cho_solve(S12_factors, ga_H[:,:,nc])
            Kgay = np.dot(KS, S1gay)
            gaKy = np.einsum('ijk,j->ik', ga_KS, S1y)
            gaKH = np.einsum('ijk,jl->ilk', ga_KS, S1H)
            KgaH = np.einsum('ij,jkl->ikl', KS, S1gaH)
            # Upadtes (state, covariance)
            up_ga_x = ga_x + gaKy + Kgay
            up_ga_P = - np.einsum('ijk,jl->ilk', gaKH + KgaH, P) \
                      + np.einsum('ij,jkl->ikl', ImKH, ga_P)
            # Update marginal likelihood
            tr_S1gaS = np.einsum('iik->k', S1gaS) # Trace for each parameter
            ga_mll = .5 * (np.dot(ga_y.T, S1y) + \
                           np.einsum('i,ijk,j->k', y, -S1gaS, S1y) + \
                           np.dot(y, S1gay) + \
                           tr_S1gaS)
            self._grad_marg_log_lklhood -= ga_mll
            
        # State and convariance after update
        x = up_x
        P = up_P
        if self._ders > 0:
            ga_x = up_ga_x
            ga_P = up_ga_P
            
        # Append new filtering map
        try:
            L = scila.cholesky(P, True)
        except scila.LinAlgError:
            U,S,V = scila.svd(P)
            L = U * np.sqrt(S)
        M = LinearTransportMap(x, L)
        self.F_list.append(M)

        # Update filtering mean and covariance
        self._filt_mean_list.append(x)
        self._filt_cov_list.append( np.dot(L, L.T) )
        if self._ders > 0:
            self._filt_grad_mean_list.append( ga_x )
            self._filt_grad_cov_list.append( ga_P )

class LinearSmoother(LinearFilter,Smoother):
    r""" Perform the on-line assimilation of a sequential linear Gaussian Hidden Markov chain.

    Args:
      lag (:class:`numpy.float`): lag to be used in the backward updates of
        smoothing means and covariances. The default value ``None`` indicates
        infinite lag.
    
    .. todo:: no hyper-parameter admitted right now.
    """
    def __init__(self, lag=None):
        super(LinearSmoother,self).__init__()
        self._lag = lag
        self._smooth_mean_list = []
        self._smooth_cov_list = []
        # Data structures necessary for fast smoothing updates
        self._CB_queue = collections.deque(maxlen=lag)
        self._CB2_queue = collections.deque(maxlen=lag)

    @property
    def lag(self):
        return self._lag

    @property
    def smoothing_mean_list(self):
        return self._smooth_mean_list

    @property
    def smoothing_covariance_list(self):
        return self._smooth_cov_list

    def _assimilation_step(self):
        r""" Assimilate one piece of Gaussian data :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}\right) \right)`.
        """
        # Run the filter to get (c,L)
        LinearFilter._assimilation_step(self)
        c = self.F_list[-1].c
        C = self.F_list[-1].L
        a = None
        A = None
        B = None
        # Apply recursions
        if self.nsteps == 0: # At first step smoothing == filtering
            M = LinearTransportMap(c, C)
            L = LiftedTransportMap(-1, M, self.pi.dim, 0)
            self.L_list.append( L )
        else:
            cm1 = self.F_list[-2].c
            Cm1 = self.F_list[-2].L
            # Load transition system
            pi = self.pi.pi_list[-1]
            sdim = pi.dim
            F = pi.T.T
            Q12 = pi.pi.sampling_mat
            # Recursions
            Q12FCm1 = scila.solve_triangular(Q12, np.dot(F, Cm1), lower=True)
            Q1FCm1 = scila.solve_triangular(Q12, Q12FCm1, lower=True, trans='T')
            J = np.eye(pi.dim) + np.dot(Cm1.T, np.dot(F.T, Q1FCm1))
            J12 = scila.cholesky(J, lower=True)
            Cm1TFT = np.dot(Cm1.T, F.T)
            # A
            A = scila.solve_triangular(J12, np.eye(pi.dim), lower=True, trans='T')
            # B
            Q12C = scila.solve_triangular(Q12, C, lower=True)
            Q1C = scila.solve_triangular(Q12, Q12C, lower=True, trans='T')
            PC = - np.dot(Cm1TFT,Q1C)
            J12PC = scila.solve_triangular(J12, PC, lower=True)
            B = - scila.solve_triangular(J12, J12PC, lower=True, trans='T')
            # a
            Fcm1c = np.dot(F,cm1) - c
            Q12Fcm1c = scila.solve_triangular(Q12, Fcm1c, lower=True)
            Q1Fcm1c = scila.solve_triangular(Q12, Q12Fcm1c, lower=True, trans='T')
            PFcm1c = - np.dot(Cm1TFT, Q1Fcm1c)
            J12PFcm1c = scila.solve_triangular(J12, PFcm1c, lower=True)
            a = scila.solve_triangular(J12, J12PFcm1c, lower=True, trans='T')
            # Assemble smoothing map
            ac = np.hstack((a, c))
            ABC = np.zeros((2*sdim, 2*sdim)) # Matrix [[A,B],[0,C]]
            ABC[:sdim,:sdim] = A
            ABC[:sdim,sdim:] = B
            ABC[sdim:,sdim:] = C
            M = LinearTransportMap(ac, ABC)

            # Update all dimension of previous maps
            for L in self.L_list:
                L.dim = L.dim_in = L.dim_out = self.pi.dim
            # Append new map
            L = LiftedTransportMap(self.nsteps-1, M, self.pi.dim, 0)
            self.L_list.append(L)

        # Update smoothing means and covariances
        self._update_smoothing_mean_covariance_lists(
            self.nsteps, self.lag,
            self._smooth_mean_list, self._smooth_cov_list,
            self._CB_queue, self._CB2_queue,
            c, C, a, A, B)

    def _update_smoothing_mean_covariance_lists(
            self, nsteps, lag,
            smooth_mean_list, smooth_cov_list, CB_queue, CB2_queue,
            c, C, a=None, A=None, B=None):
        # (the lag is controlled by the length of CB_queue and CB2_queue)
        for i, (CB, CB2) in enumerate(zip(CB_queue, CB2_queue)):
            if lag is None:
                lag = nsteps
            idx = max(nsteps - lag, 0) + i
            # MEAN: Insert new term <CB,a>
            smooth_mean_list[idx] += np.dot(CB, a)
            # COV: Remove last <CB,CB.T> term introduced
            smooth_cov_list[idx] -= CB2
            # COV: Insert new term <CBA,CBA.T>
            CBA = np.dot(CB, A)
            CBA2 = np.dot(CBA, CBA.T)
            smooth_cov_list[idx] += CBA2
            # Update CB and CB2
            CBB = np.dot(CB, B)
            CB_queue[i] = CBB
            CBB2 = np.dot(CBB, CBB.T)
            CB2_queue[i] = CBB2
            # COV: Insert new term <CBB,CBB.T>
            smooth_cov_list[idx] += CBB2
        # Append new mean
        smooth_mean_list.append( c.copy() )
        # Append new covariance
        CB_queue.append( C )
        C2 = np.dot(C, C.T)
        CB2_queue.append( C2 )
        smooth_cov_list.append( C2.copy() )
            
    def offline_smoothing_mean_covariance_lists(self, lag=None):
        r""" Compute the mean and covariances with a fixed lag for a pre-assimilated density
        """
        sdim = self.pi.state_dim
        smooth_mean_list = []
        smooth_cov_list = []
        # Data structures necessary for fast smoothing updates
        CB_queue = collections.deque(maxlen=lag)
        CB2_queue = collections.deque(maxlen=lag)
        # Iterate over the available maps
        for nsteps, L in enumerate(self.L_list):
            M = L.tm
            if nsteps > 0:
                c = M.c[sdim:]
                C = M.L[sdim:,sdim:]
                a = M.c[:sdim]
                A = M.L[:sdim,:sdim]
                B = M.L[:sdim,sdim:]
            else:
                c = M.c[:sdim]
                C = M.L[:sdim,:sdim]
                a = None
                A = None
                B = None
            self._update_smoothing_mean_covariance_lists(
                nsteps, lag,
                smooth_mean_list, smooth_cov_list,
                CB_queue, CB2_queue,
                c, C, a, A, B)
        return (smooth_mean_list, smooth_cov_list)