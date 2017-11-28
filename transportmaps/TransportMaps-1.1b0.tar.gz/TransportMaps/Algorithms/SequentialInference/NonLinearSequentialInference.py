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

from TransportMaps.Algorithms.SequentialInference.SequentialInferenceBase import *
from TransportMaps.Algorithms.Adaptivity.KullbackLeiblerAdaptivity import KullbackLeiblerBuilder
from TransportMaps.Algorithms.Adaptivity.RegressionAdaptivity import L2RegressionBuilder
from TransportMaps.Distributions import StandardNormalDistribution, \
    PushForwardTransportMapDistribution, PullBackTransportMapDistribution
from TransportMaps.Maps import TransportMap, TriangularTransportMap, \
    CompositeTransportMap, ListCompositeTransportMap, PermutationTransportMap, \
    TriangularListStackedTransportMap
from TransportMaps.Maps.Decomposable import LiftedTransportMap
from TransportMaps.Diagnostics.Routines import variance_approx_kl
from TransportMaps.Routines import L2_misfit

__all__ = ['TransportMapsSmoother']

class TransportMapsSmoother(Smoother):
    r""" Perform the on-line assimilation of a sequential Hidded Markov chain.

    Given the prior distribution on the hyper-parameters :math:`\pi(\Theta)`,
    provides the functions neccessary to assimilate new pieces of data or
    missing data 
    (defined in terms of transition densities
    :math:`\pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right)`
    and log-likelihoods
    :math:`\log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right)`),
    to return the map pushing forward :math:`\mathcal{N}(0,{\bf I})`
    to the smoothing distribution
    :math:`\pi\left(\Theta, {\bf Z}_\Lambda \middle\vert {\bf y}_\Xi \right)`
    and to return the maps pushing forward :math:`\mathcal{N}(0,{\bf I})`
    to the filtering/forecast distributions
    :math:`\{\pi\left(\Theta, {\bf Z}_k \middle\vert {\bf y}_{0:k} \right)\}_k`.

    For more details see also :cite:`Spantini2017` and the
    `tutorial <example-sequential-stocvol-6d.html>`_.

    Args:
      pi_hyper (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior distribution on the hyper-parameters :math:`\pi(\Theta)`
    """
    def __init__(self, *args, **kwargs):
        super(TransportMapsSmoother, self).__init__(*args, **kwargs)
        self._var_diag_convergence = []
        self._regression_convergence = []

    @property
    def var_diag_convergence(self):
        return self._var_diag_convergence

    @property
    def regression_convergence(self):
        return self._regression_convergence
        
    def _assimilation_step(self, tm, solve_params, builder=None,
                           hyper_tm=None, regression_params=None,
                           hyper_builder=None,
                           skip_initial=False,
                           var_diag_convergence_params=None,
                           regression_convergence_params=None,
                           continue_on_error=True):
        r""" Assimilate one piece of data :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`.

        Given the new piece of data
        :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`,
        retrieve the :math:`k`-th Markov component :math:`\pi^k` of :math:`\pi`,
        determine the transport map

        .. math::

           \mathfrak{M}_k({\boldsymbol \theta}, {\bf z}_k, {\bf z}_{k+1}) = \left[
           \begin{array}{l}
           \mathfrak{M}^\Theta_k({\boldsymbol \theta}) \\
           \mathfrak{M}^0_k({\boldsymbol \theta}, {\bf z}_k, {\bf z}_{k+1}) \\
           \mathfrak{M}^1_k({\boldsymbol \theta}, {\bf z}_{k+1})
           \end{array}
           \right] = Q \circ R_k \circ Q

        that pushes forward :math:`\mathcal{N}(0,{\bf I})` to :math:`\pi^k`, and
        embed it into the linear map which will remove the desired conditional
        dependencies from :math:`\pi`.
        
        Optionally, it will also compress the maps
        :math:`\mathfrak{M}_{0}^\Theta \circ \ldots \circ \mathfrak{M}_{k-1}^\Theta`
        into the map :math:`\mathfrak{H}_{k-1}` in order to speed up the
        evaluation of the :math:`k`-th Markov component :math:`\pi^k`.

        Args:
          tm (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport map :math:`R_k`
          solve_params (dict): parameters to be passed to
            :func:`minimize_kl_divergence<TransportMaps.Maps.TransportMap.minimize_kl_divergence>`
          hyper_tm (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            transport map :math:`\mathfrak{H}_{k-1}`
          regression_params (dict): parameters to be passed to
            :func:`regression<TransportMaps.Maps.TransportMap.regression>` during
            the determination of :math:`\mathfrak{H}_{k-1}`
          skip_initial (bool): whether to skip the approximation of
            :math:`\pi\left(\Theta, {\bf Z}_0 \middle\vert {\bf y}_0 \right)` in the first step.
          var_diag_convergence_params (dict): parameters to be used to monitor the
            convergence of the map approximation. If ``None`` the conevergence is not monitored.
          regression_convergence_params (dict): parameters to be used to monitor the
            convergence of the regression step on the hyper-parameters map.
            If ``None`` the conevergence is not monitored.
          continue_on_error (bool): whether to continue when the KL-minimization step or the
            regression step fails with back-up plans

        Raises:
          RunTimeError: an convergence error occurred during the assimilation

        .. see:: :func:`Smoother.assimilate`
        """
        def terminate_kl(log, continue_on_error):
            if not log['success']:
                if continue_on_error:
                    self.logger.warning(
                        log['msg'] + \
                        "Reverted to last converged map. " + \
                        "This may lead to overall loss of accuracy.")
                else:
                    self.logger.error(
                        log['msg'] + " Terminating."
                    )
                    return True
            return False
        
        if builder is None:
            builder = KullbackLeiblerBuilder()
        if hyper_builder is None:
            hyper_builder = L2RegressionBuilder()
        # Approximation
        if not skip_initial and self.nsteps == 0:
            # If step zero, then just approximate self.pi
            rho = StandardNormalDistribution(self.pi.dim)
            builder.base_distribution = rho
            builder.target_distribution = self.pi
            tm, log = builder.solve(tm, **solve_params)
            if terminate_kl(log, continue_on_error):
                raise RuntimeError("KL-minimization did not converge. Terminating.")
            self.L_list.append( tm )
        elif self.nsteps == 1:
            # If step one, then approximate 0-th Markov component
            hdim = self.pi.hyper_dim
            sdim = self.pi.state_dim
            self._regression_convergence.append( None )
            pi0 = self.pi.get_MarkovComponent(0)
            self.rho_mk = StandardNormalDistribution(pi0.dim)
            self.Q = PermutationTransportMap(
                list(range(hdim)) + \
                list(range(hdim+sdim, hdim+2*sdim)) + \
                list(range(hdim, hdim+sdim)) )
            pull_Q_pi0 = PullBackTransportMapDistribution(self.Q, pi0)
            builder.base_distribution = self.rho_mk
            builder.target_distribution = pull_Q_pi0
            tm, log = builder.solve(tm, **solve_params)
            if terminate_kl(log, continue_on_error):
                raise RuntimeError(log['msg'] + " Terminating.")
            # H_list contains the hyper-parameters maps H
            # R_list contains the lower triangular maps R
            # M_list contains the generalized lower triangular maps M
            # L_list contains the lifted maps
            self.H_list = [
                TriangularTransportMap( tm.active_vars[:hdim],
                                        tm.approx_list[:hdim] )
                if hdim > 0 else None ]
            self.R_list = [ tm ]
            self.M_list = [ ListCompositeTransportMap([self.Q, tm, self.Q]) ]
            self.L_list[0] = LiftedTransportMap(0, self.M_list[0], self.pi.dim, hdim)
        elif self.nsteps > 1:
            # If step k, then approximate the (k-1)-th Markov component
            hdim = self.pi.hyper_dim
            sdim = self.pi.state_dim
            if self.nsteps > 2 and hyper_tm is not None:
                hyper_builder.target_map = self.H_list[-1]
                x0 = None
                if self.nsteps > 3 and isinstance(hyper_builder, L2RegressionBuilder):
                    x0 = self.H_list[-1].t1.coeffs
                hyper_tm, log_list = hyper_builder.solve(
                    hyper_tm, x0=x0, **regression_params)
                if not log_list[-1]['success']:
                    if not continue_on_error:
                        self.logger.error("Regression did not converge. Terminating.")
                        raise RuntimeError("KL-minimization did not converge. Terminating.")
                else:
                    if regression_convergence_params is not None:
                        self._regression_convergence.append(
                            L2_misfit(
                                self.H_list[-1], hyper_tm,
                                **regression_convergence_params) )
                    else:
                        self._regression_convergence.append( None )
                    self.H_list[-1] = hyper_tm
            else:
                self._regression_convergence.append( 0. )
            Mkm1 = TransportMap( self.R_list[-1].active_vars[hdim:hdim+sdim],
                                 self.R_list[-1].approx_list[hdim:hdim+sdim] )
            pik = self.pi.get_MarkovComponent(
                self.nsteps-1, state_map=Mkm1, hyper_map=self.H_list[-1] )
            pull_Q_pik = PullBackTransportMapDistribution(self.Q, pik)
            builder.base_distribution = self.rho_mk
            builder.target_distribution = pull_Q_pik
            tm, log = builder.solve(tm, **solve_params)
            if terminate_kl(log, continue_on_error):
                raise RuntimeError(log['msg'] + " Terminating.")
            self.R_list.append( tm )
            self.M_list.append( ListCompositeTransportMap([self.Q, tm, self.Q]) )
            # Update dimension of all lifted maps
            for L in self.L_list:
                L.dim = L.dim_in = L.dim_out = self.pi.dim
            L = LiftedTransportMap( self.nsteps-1, self.M_list[-1], self.pi.dim, hdim)
            self.L_list.append(L)
            # Store next hyper map composition
            self.H_list.append(
                CompositeTransportMap(
                    self.H_list[-1], TriangularTransportMap(
                        self.R_list[-1].active_vars[:hdim],
                        self.R_list[-1].approx_list[:hdim] ) )
                if hdim > 0 else None )

        # Prepare the filtering maps
        if self.nsteps == 0:
            F = self.L_list[0]
        else:
            hdim = self.pi.hyper_dim
            sdim = self.pi.state_dim
            H = self.H_list[-1]
            R = self.R_list[-1]
            Rkp1 = TriangularTransportMap( R.active_vars[hdim:hdim+sdim],
                                           R.approx_list[hdim:hdim+sdim] )
            if hdim > 0:
                F = TriangularListStackedTransportMap( [H, Rkp1] )
            else:
                F = Rkp1
        self.F_list.append( F )

        # Monitor kl convergence
        if var_diag_convergence_params is not None:
            pull_tar = PullBackTransportMapDistribution(
                tm, builder.target_distribution)
            var = variance_approx_kl(
                builder.base_distribution, pull_tar,
                **var_diag_convergence_params)
        else:
            var = None
                        
        if self.nsteps == 1:
            self._var_diag_convergence[0] = var
        else:
            self._var_diag_convergence.append( var )

    def trim(self, ntrim):
        r""" Trim the integrator to ``ntrim``
        """
        nback = self.nsteps - ntrim
        ns = TransportMapsSmoother(self.pi.pi_hyper)
        # Trim smoother lists
        ns.H_list = self.H_list[:ntrim-1]
        ns.R_list = self.R_list[:ntrim-1]
        ns.M_list = self.M_list[:ntrim-1]
        ns.L_list = self.L_list[:ntrim-1]
        for L in ns.L_list:
            L.dim = L.dim_in = L.dim_out = ntrim + self.pi.hyper_dim
        ns.F_list = self.F_list[:ntrim]
        ns._var_diag_convergence = self.var_diag_convergence[:ntrim-1]
        ns._regression_convergence = self.regression_convergence[:ntrim-1]
        # Trim target distribution
        for pi, ll in zip(self.pi.prior.pi_list[:ntrim], self.pi.ll_list[:ntrim]):
            ns.pi.append(pi, ll)
        # Update nsteps
        ns._nsteps = ntrim
        return ns