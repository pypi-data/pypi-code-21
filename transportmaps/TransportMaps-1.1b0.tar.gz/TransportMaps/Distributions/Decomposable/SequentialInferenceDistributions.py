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

from TransportMaps.Distributions.DistributionBase import *
from TransportMaps.Distributions.Inference.InferenceBase import BayesPosteriorDistribution
from TransportMaps.Distributions.FrozenDistributions import StandardNormalDistribution
from TransportMaps.Likelihoods.LikelihoodBase import IndependentLogLikelihood

__all__ = ['AR1TransitionDistribution',
           'MarkovChainDistribution',
           'SequentialHiddenMarkovChainDistribution',
           'MarkovComponentDistribution']

nax = np.newaxis

class AR1TransitionDistribution(ConditionalDistribution):
    r""" Transition probability for an auto-regressive (1) process (possibly with hyper-parameters)

    Defines the probability distribution
    :math:`\pi({\bf Z}_{k+1}\vert {\bf Z}_{k}, \Theta)=\pi({\bf Z}_{k+1} - T({\bf Z}_{k},\Theta) \vert \Theta)`
    for the auto-regressive (1) process

    .. math::

       {\bf Z}_{k+1} = T({\bf Z}_k, \Theta) + \varepsilon
       \;, \quad
       \varepsilon \sim \nu_\pi

    Args:
      pi (:class:`Distribution<TransportMaps.Distributions.ConditionalDistribution`):
        distribution :math:`\pi:\mathbb{R}^d\times\mathbb{R}^{d_\theta}\rightarrow\mathbb{R}`
      T (:class:`Map<TransportMaps.Maps.Map>`): map
        :math:`T:\mathbb{R}^{d+d_\theta}\rightarrow\mathbb{R}^d`
    """
    def __init__(self, pi, T):
        if pi.dim != T.dim_out:
            raise ValueError("The dimension of pi must match the output " + \
                             "dimension of T.")
        self._pi = pi
        if issubclass(type(pi), ConditionalDistribution):
            self._isPiCond = True
        else:
            self._isPiCond = False
        self._T = T
        self._state_dim = pi.dim
        self._hyper_dim = T.dim_in - T.dim_out
        super(AR1TransitionDistribution, self).__init__(pi.dim, T.dim_in)

    @property
    def T(self):
        return self._T

    @property
    def pi(self):
        return self._pi

    @property
    def isPiCond(self):
        return self._isPiCond

    @property
    def state_dim(self):
        return self._state_dim

    @property
    def hyper_dim(self):
        return self._hyper_dim
        
    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        frw = self.T.evaluate(y, params, idxs_slice)
        if self.isPiCond:
            return self.pi.log_pdf(x - frw, y[:,self.dim:])
        else:
            return self.pi.log_pdf(x - frw)

    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        frw = self.T.evaluate(y, params,idxs_slice)
        gx_frw = self.T.grad_x(y, params, idxs_slice)
        if self.isPiCond:
            gxlpdf = self.pi.grad_x_log_pdf(x - frw, y[:,self.dim:])
        else:
            gxlpdf = self.pi.grad_x_log_pdf(x - frw)
        out = np.zeros((x.shape[0], self.dim + self.dim_y))
        out[:,:self.dim] = gxlpdf
        out[:,self.dim:] = - np.einsum('...i,...ij->...j', gxlpdf, gx_frw)
        return out

    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        m = x.shape[0]
        dx = self.dim
        dy = self.dim_y
        frw = self.T.evaluate(y, params,idxs_slice)
        gx_frw = self.T.grad_x(y, params, idxs_slice)
        hx_frw = self.T.hess_x(y, params, idxs_slice)
        if self.isPiCond:
            gx_lpdf = self.pi.grad_x_log_pdf(x - frw, y[:,dx:])
            hx_lpdf = self.pi.hess_x_log_pdf(x - frw, y[:,dx:])
        else:
            gx_lpdf = self.pi.grad_x_log_pdf(x - frw)
            hx_lpdf = self.pi.hess_x_log_pdf(x - frw)
        out = np.zeros((m, dx+dy, dx+dy))
        out[:,:dx,:dx] = hx_lpdf
        out[:,:dx,dx:] = - np.einsum('...ij,...ik->...jk', hx_lpdf, gx_frw)
        out[:,dx:,:dx] = out[:,:dx,dx:].transpose((0,2,1))
        tmp = - out[:,:dx,dx:] # m x dx x dy
        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_frw)
        tmp -= np.einsum('...i,...ijk->...jk', gx_lpdf, hx_frw)
        out[:,dx:,dx:] = tmp
        return out

class MarkovChainDistribution(FactorizedDistribution):
    r""" Distribution of a Markov process (optionally with hyper-parameters)

    For the index set :math:`A=[t_0,\ldots,t_k]` with :math:`t_0<t_1<\ldots <t_k`,
    and the user defined distributions
    :math:`\pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta)`,
    :math:`\pi({\bf Z}_{t_0} \vert \Theta)` and :math:`\pi(\Theta)`
    defines the distribution

    .. math::

       \pi(\Theta, {\bf Z}_A) = \left( \prod_{i=1}^k \pi({\bf Z}_{t_i} \vert {\bf Z}_{t_{i-1}}, \Theta) \right) \pi({\bf Z}_{t_0} \vert \Theta) \pi(\Theta)

    associated to the process :math:`{\bf Z}_A`.

    Args:
      pi_list (:class:`list` of :class:`ConditionalDistribution`):
        list of transition distributions
        :math:`\{\pi({\bf Z}_{t_0} \vert \Theta), \pi({\bf Z}_{t_1}\vert {\bf Z}_{t_{0}},\Theta), \ldots \}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(self, pi_list, pi_hyper=None):
        factors = []
        # Figure out dimension hyper-parameters
        if pi_hyper is None:
            hdim = 0
        else:
            hdim = pi_hyper.dim
            factors.append( (pi_hyper, list(range(hdim)), []) )
        # Check consistency
        dim = hdim
        sdim = None
        for i, pi in enumerate(pi_list):
            if i == 0:
                if issubclass(type(pi), ConditionalDistribution):
                    if pi.dim_y != hdim:
                        raise ValueError("The dimension of the %d component " % i + \
                                         "is not consistent")
                elif hdim != 0:
                    raise ValueError("The dimension of the %d component " % i + \
                                     "is not consistent")
                sdim = pi.dim
                factors.append( (pi, list(range(dim,dim+sdim)), list(range(hdim))) )
            else:
                if pi.dim != sdim or pi.dim_y != sdim + hdim:
                    raise ValueError("The dimension of the %d component " % i + \
                                     "is not consistent")
                factors.append( (pi, list(range(dim,dim+sdim)),
                                 list(range(dim-sdim,dim)) + list(range(hdim))) )
            dim += sdim
        # Init
        super(MarkovChainDistribution, self).__init__(factors)
        self.pi_list = pi_list
        self.pi_hyper = pi_hyper
        self.state_dim = sdim
        self.hyper_dim = hdim

    @property
    def nsteps(self):
        r""" Returns the number of steps (time indices) :math:`\sharp A`.
        """
        return len(self.pi_list)

    def append(self, pi):
        r""" Append a new transition distribution :math:`\pi({\bf Z}_{t_{k+1}}\vert {\bf Z}_{t_{k}},\Theta)`

        Args:
          pi (:class:`Distribution` or :class:`ConditionaDistribution`):
            transition distribution
            :math:`\pi({\bf Z}_{t_{k+1}}\vert {\bf Z}_{t_{k}},\Theta)`
        """
        # Check consistency
        if len(self.pi_list) == 0:
            if issubclass(type(pi), ConditionalDistribution):
                if pi.dim_y != self.hyper_dim:
                    raise ValueError("The dimension of the new component is not consistent")
            elif self.hyper_dim != 0:
                raise ValueError("The initial conditon prior must be conditional on " + \
                                 "the hyper parameters.")
            self.state_dim = pi.dim
            # Prepare factor
            factor = (pi, list(range(self.dim,self.dim+self.state_dim)),
                      list(range(self.hyper_dim)))
        else:
            if pi.dim != self.state_dim or pi.dim_y != self.state_dim + self.hyper_dim:
                raise ValueError("The dimension of the new component is not consistent")
            # Prepare factor
            factor = (pi, list(range(self.dim,self.dim+self.state_dim)),
                      list(range(self.dim-self.state_dim,self.dim)) + list(range(self.hyper_dim)))
        super(MarkovChainDistribution, self).append(factor)
        self.pi_list.append( pi )

class SequentialHiddenMarkovChainDistribution(BayesPosteriorDistribution):
    r""" Distribution of a sequential Hidden Markov chain model (optionally with hyper-parameters)

    For the index sets :math:`A=[t_0,\ldots,t_k]` with :math:`t_0<t_1<\ldots <t_k`, 
    :math:`B \subseteq A`, 
    the user defined transition densities (:class:`Distribution`)
    :math:`\{\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{1}\vert{\bf Z}_{t_{0}},\Theta), \ldots \}`,
    the prior :math:`\pi(\Theta)` and 
    the log-likelihoods (:class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`)
    :math:`\{\log\mathcal{L}({\bf y}_t \vert{\bf Z}_t,\Theta)\}_{t\in B}`, defines the distribution

    .. math::

       \pi(\Theta, {\bf Z}_A \vert {\bf y}_B) =
         \left( \prod_{t\in B} \mathcal{L}({\bf y}_t \vert {\bf Z}_t, \Theta) \right)
         \left( \prod_{i=1}^k \pi({\bf Z}_{t_i}\vert{\bf Z}_{t_{i-1}},\Theta) \right)
         \pi({\bf Z}_{t_0},\Theta) \pi(\Theta)

    associated to the process :math:`{\bf Z}_A`
    
    .. note:: Each of the log-likelihoods already embed its own data :math:`{\bf y}_t`.
       The list of log-likelihoods must be of the same length of the list of
       transitions. Missing data are simulated by setting the corresponding
       entry in the list of log-likelihood to ``None``.

    Args:
      pi_list (:class:`list` of :class:`ConditionalDistribution`): list of transition densities
        :math:`[\pi({\bf Z}_{t_0}\vert\Theta), \pi({\bf Z}_{t_1}\vert{\bf Z}_{t_{0}},\Theta), \ldots ]`
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
        list of log-likelihoods
        :math:`\{\log\mathcal{L}({\bf y}_t \vert {\bf Z}_t,\Theta)\}_{t\in B}`
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
    """
    def __init__(self, pi_list, ll_list, pi_hyper=None):
        if len(pi_list) != len(ll_list):
            raise ValueError("Length of list of transition must be the same of " + \
                             "the list of log-likelihoods")
        prior = MarkovChainDistribution(pi_list, pi_hyper)
        # Prepare likelihood factors and check consistency
        ll_factors = []
        sdim = prior.state_dim
        hdim = prior.hyper_dim
        dim = hdim
        for i, ll in enumerate(ll_list):
            if ll is not None and ll.dim != sdim + hdim:
                raise ValueError("Dimension of log-likelihood %d is not consistent" % i)
            ll_factors.append( (ll, list(range(dim,dim+sdim)) + list(range(hdim))) )
            dim += sdim
        logL = IndependentLogLikelihood( ll_factors )
        # Init
        super(SequentialHiddenMarkovChainDistribution, self).__init__(logL, prior)

    @property
    def state_dim(self):
        return self.prior.state_dim

    @property
    def hyper_dim(self):
        return self.prior.hyper_dim

    @property
    def pi_hyper(self):
        return self.prior.pi_hyper

    @property
    def pi_list(self):
        return self.prior.pi_list

    @property
    def ll_list(self):
        return [ll for ll,_ in self.logL.factors]

    @property
    def nsteps(self):
        return self.prior.nsteps

    def append(self, pi, ll=None):
        r""" Append a new transition distribution :math:`\pi({\bf Z}_{t_{k+1}}\vert\Theta, {\bf Z}_{t_{k}})` and the corresponding log-likelihood :math:`\log\mathcal{L}({\bf y}_{t_k} \vert \Theta, {\bf Z}_{t_k})` if any.

        Args:
          pi (:class:`ConditionalDistribution`): transition distribution
            :math:`\pi({\bf Z}_{t_{k+1}}\vert\Theta, {\bf Z}_{t_{k}})`
          ll (:class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
            log-likelihood
            :math:`\log\mathcal{L}({\bf y}_{t_k} \vert \Theta, {\bf Z}_{t_k})`.
            Missing data are represented by ``None``.
        """
        self.prior.append( pi )
        # Prepare likelihood factor and check consistency
        sdim = self.state_dim
        hdim = self.hyper_dim
        if ll is not None and ll.dim != sdim + hdim:
            raise ValueError("Dimension of log-likelihood is not consistent")
        self.logL.append( (ll, list(range(self.dim,self.dim+sdim)) + list(range(hdim))) )
        # Append
        self.dim = self.prior.dim

    def get_MarkovComponent(self, i, n=1, state_map=None, hyper_map=None):
        r""" Extract the (:math:`n\geq 1` steps) :math:`i`-th Markov component from the distribution

        If :math:`i=0` the Markov component is given by

        .. math::

           \pi^{0:n}(\Theta, {\bf Z}_{t_0}, \ldots, {\bf Z}_{t_n}) :=
             \left( \prod_{t \in \{t_0,\ldots,t_n\} \cap B}
                \mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t) \right)
             \left( \prod_{i=1}^n \pi({\bf Z}_{t_i}\vert \Theta, {\bf Z}_{t_{i-1}}) \right)
             \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta) \;.

        If :math:`i>0` then the Markov component is

        .. math::

           \pi^{i:i+n}\left(\Theta, {\bf Z}_{t_i}, \ldots, {\bf Z}_{t_{i+n}}\right) :=
             \eta(\Theta, {\bf Z}_{t_i}) 
             \left( \prod_{t \in \left\{t_{i+1},\ldots,t_{i+n}\right\} \cap B}
                \mathcal{L}\left({\bf y}_t \vert
                  \mathfrak{T}_{i-1}^{\Theta}(\Theta), {\bf Z}_t\right) \right)
             \left( \prod_{k=i+1}^{i+n-1}
                \pi\left({\bf Z}_{t_k+1}\vert {\bf Z}_{t_{k}},
                   \mathfrak{T}_{i-1}^{\Theta}(\Theta) \right) \right)
             \pi\left({\bf Z}_{t_{i+1}} \vert
                \mathfrak{M}_{i-1}^{1}(\Theta, {\bf Z}_{t_i}),
                \mathfrak{T}_{i-1}^{\Theta}(\Theta)
             \right) \;,

        where :math:`\mathfrak{T}_{i-1}^{\Theta}` and
        :math:`\mathfrak{M}_{i-1}^{1}` are the hyper-parameter and forecast
        components of the map computed at step :math:`i-1`, using the
        sequential algorithm described in :cite:`Spantini2017`.

        Args:
          i (int): index :math:`i` of the Markov component
          n (int): number of steps :math:`n`
          state_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            forecast map :math:`\mathfrak{M}_{i-1}^{1}` from step :math:`i-1`.
          hyper_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
            hyper-parameter map :math:`\mathfrak{T}_{i-1}^{\Theta}`
            from step :math:`i-1`.

        Returns:
          (:class:`Distribution<TransportMaps.Distributions.Distribution>`) --
            Markov component :math:`\pi^{i:i+n}`.
        """
        if i == 0:
            out = MarkovComponentDistribution(
                i, self.pi_list[:n+1], self.ll_list[:n+1],
                self.state_dim, self.hyper_dim,
                self.pi_hyper)
        elif i > 0:
            out = MarkovComponentDistribution(
                i, self.pi_list[i+1:i+n+1], self.ll_list[i+1:i+n+1],
                self.state_dim, self.hyper_dim,
                self.pi_hyper,
                state_map, hyper_map)
        else:
            raise AttributeError("Index must be i >= 0")
        return out

    def trim(self, nsteps):
        r""" Trim the Markov chain to the first ``nsteps``

        Args:
          (int) nsteps: number of steps in the Markov chain of the returned
             distribution
        Returns:
          (:class:`SequentialHiddenMarkovChainDistribution`) -- trimmed distribution
        """
        return SequentialHiddenMarkovChainDistribution(
            self.pi_list[:nsteps],
            self.ll_list[:nsteps],
            self.pi_hyper)
        
class MarkovComponentDistribution(Distribution):
    r""" :math:`i`-th Markov component of a :class:`SequentialHiddenMarkovChainDistribution`

    If :math:`i=0` the Markov component is given by

    .. math::

       \pi^{0:n}(\Theta, {\bf Z}_{t_0}, \ldots, {\bf Z}_{t_n}) :=
         \left( \prod_{t \in \{t_0,\ldots,t_n\} \cap B}
            \mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t) \right)
         \left( \prod_{i=1}^n \pi({\bf Z}_{t_i}\vert \Theta, {\bf Z}_{t_{i-1}}) \right)
         \pi({\bf Z}_{t_0}\vert\Theta) \pi(\Theta) \;.

    If :math:`i>0` then the Markov component is

    .. math::

       \pi^{i:i+n}\left(\Theta, {\bf Z}_{t_i}, \ldots, {\bf Z}_{t_{i+n}}\right) :=
         \eta(\Theta, {\bf Z}_{t_i}) 
         \left( \prod_{t \in \left\{t_{i+1},\ldots,t_{i+n}\right\} \cap B}
            \mathcal{L}\left({\bf y}_t \vert
              \mathfrak{T}_{i-1}^{\Theta}(\Theta), {\bf Z}_t\right) \right)
         \left( \prod_{k=i+1}^{i+n-1}
            \pi\left({\bf Z}_{t_k+1}\vert {\bf Z}_{t_{k}},
               \mathfrak{T}_{i-1}^{\Theta}(\Theta) \right) \right)
         \pi\left({\bf Z}_{t_{i+1}} \vert
            \mathfrak{M}_{i-1}^{1}(\Theta, {\bf Z}_{t_i}),
            \mathfrak{T}_{i-1}^{\Theta}(\Theta)
         \right) \;,

    where :math:`\mathfrak{T}_{i-1}^{\Theta}` and
    :math:`\mathfrak{M}_{i-1}^{1}` are the hyper-parameter and forecast
    components of the map computed at step :math:`i-1`, using the
    sequential algorithm described in :cite:`Spantini2017`.

    Args:
      idx0 (int): index :math:`i` of the Markov component
      pi_list (:class:`list` of :class:`Distribution`): list of :math:`n`
        transition densities
      ll_list (:class:`list` of :class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
        list of :math:`n` log-likelihoods (``None`` for missing data)
        :math:`\{\log\mathcal{L}({\bf y}_t \vert \Theta, {\bf Z}_t)\}_{t\in B}`
      state_dim (int): dimension of the state-space
      hyper_dim (int): dimension of the parameter-space
      pi_hyper (:class:`Distribution`): prior on hyper-parameters :math:`h(\Theta)`
      state_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        forecast map :math:`\mathfrak{M}_{i-1}^{1}` from step :math:`i-1`.
      hyper_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        hyper-parameter map :math:`\mathfrak{T}_{i-1}^{\Theta}`
        from step :math:`i-1`.
    """
    def __init__(self, idx0, pi_list, ll_list,
                 state_dim, hyper_dim,
                 pi_hyper=None,
                 state_map=None, hyper_map=None):
        # Figure out dimension and check correct arguments are provided
        self.idx0 = idx0
        self.state_dim = state_dim
        self.hyper_dim = hyper_dim
        if idx0 == 0:
            if pi_hyper is not None and pi_hyper.dim != hyper_dim:
                raise AttributeError(
                    "Dimension of prior of hyper-paramenter not consistent")
            self.pi_hyper = pi_hyper
        elif idx0 > 0:
            if state_map is None:
                raise AttributeError(
                    "The state_map parameter must be provided for idx0>0")
            if state_map.dim_in != hyper_dim + state_dim:
                raise AttributeError(
                    "Dimension of state_map not consistent")
            if self.hyper_dim > 0 and hyper_map is None:
                raise AttributeError(
                    "The hyper_map parameter must be provided for hyper_dim>0")
            if self.hyper_dim > 0 and hyper_map.dim != hyper_dim:
                raise AttributeError(
                    "Dimension of hyper_map not consistent")
            self.state_map = state_map
            self.hyper_map = hyper_map
            self.pi_hyper = StandardNormalDistribution(hyper_dim + state_dim)
        else:
            raise AttributeError("Onli idx0>=0 admitted")
        if len(pi_list) != len(ll_list):
            raise AttributeError("Length of list of transition must be the same of " + \
                                 "the list of log-likelihoods")
        if idx0 == 0 and len(pi_list) < 2:
            raise AttributeError("The 0-th Markov component must be composed " + \
                                 "by at least two transition densities")
        if idx0 > 0 and len(pi_list) < 1:
            raise AttributeError("The (i>0)-th Markov component must be composed " + \
                                 "by at least one transition distribution")
        if idx0 == 0: # We can get away with a SequentialInferenceDistribution
            self.seqinfdens = SequentialHiddenMarkovChainDistribution(
                pi_list, ll_list, pi_hyper)
            dim = self.seqinfdens.dim
        else:
            dim = hyper_dim + state_dim
            for i, (pi, ll) in enumerate(zip(pi_list,ll_list)):
                if pi.dim != state_dim or pi.dim_y != hyper_dim + state_dim:
                    raise AttributeError(
                        "The dimension of the %d transition is not consistent" % i)
                if ll is not None and ll.dim != hyper_dim + state_dim:
                    raise AttributeError(
                        "The dimension of the %d log-likelihood is not consistent" % i)
                dim += state_dim
        self.pi_list = pi_list
        self.ll_list = ll_list
        super(MarkovComponentDistribution, self).__init__(dim)

    def log_pdf(self, x, *args, **kwargs):
        if self.idx0 == 0:
            out = self.seqinfdens.log_pdf(x, *args, **kwargs)
        else:
            xtr = x.copy() # Transformed
            hdim = self.hyper_dim
            sdim = self.state_dim
            # Apply hyper and component maps to obtain transformed inputs
            if hdim > 0:
                xtr[:,:hdim] = self.hyper_map.evaluate(x[:,:hdim], *args, **kwargs)
            xtr[:,hdim:hdim+sdim] = self.state_map.evaluate(
                x[:,:hdim+sdim], *args, **kwargs)
            # Evaluate pi_hyper
            out = self.pi_hyper.log_pdf(x[:,:hdim+sdim], *args, **kwargs)
            # Evaluate transitions and likelihoods
            for i, (pi, ll) in enumerate(zip(self.pi_list, self.ll_list)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                out += pi.log_pdf(xin, yin, *args, **kwargs)
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    out += ll.evaluate(xin, *args, **kwargs)
        return out

    def grad_x_log_pdf(self, x, *args, **kwargs):
        if self.idx0 == 0:
            out = self.seqinfdens.grad_x_log_pdf(x, *args, **kwargs)
        else:
            xtr = x.copy() # Transformed input
            hdim = self.hyper_dim
            sdim = self.state_dim
            # Apply hyper and component maps to obtain transformed inputs and
            # compute gradients of the maps
            if hdim > 0:
                xtr[:,:hdim] = self.hyper_map.evaluate(x[:,:hdim], *args, **kwargs)
                gx_hyper = self.hyper_map.grad_x(x[:,:hdim], *args, **kwargs)
            xtr[:,hdim:hdim+sdim] = self.state_map.evaluate(
                x[:,:hdim+sdim], *args, **kwargs)
            gx_comp = self.state_map.grad_x(x[:,:hdim+sdim], *args, **kwargs)
            # Evaluate
            out = np.zeros((x.shape[0], self.dim))
            # Evaluate pi_hyper
            out[:,:hdim+sdim] += self.pi_hyper.grad_x_log_pdf(
                x[:,:hdim+sdim], *args, **kwargs)
            # Evaluate transitions and likelihoods
            perm_pi = list(range(2*sdim,2*sdim+hdim)) + \
                      list(range(sdim,2*sdim)) + \
                      list(range(0, sdim))
            perm_ll = list(range(sdim, sdim+hdim)) + \
                      list(range(0, sdim))
            for i, (pi, ll) in enumerate(zip(self.pi_list, self.ll_list)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                # Transition
                gxlpdf = pi.grad_x_log_pdf(xin, yin, *args, **kwargs)[:,perm_pi]
                gxlpdfinner = np.zeros(gxlpdf.shape)
                gxlpdfinner[:,hdim+sdim:] = gxlpdf[:,hdim+sdim:]
                if hdim > 0: # Apply gradient hyper map
                    gxlpdfinner[:,:hdim] += np.einsum(
                        '...i,...ij->...j', gxlpdf[:,:hdim], gx_hyper)
                if i == 0: # Apply gradient component map
                    gxlpdfinner[:,:hdim+sdim] += np.einsum(
                        '...i,...ij->...j', gxlpdf[:,hdim:hdim+sdim], gx_comp)
                else:
                    gxlpdfinner[:,hdim:hdim+sdim] = gxlpdf[:,hdim:hdim+sdim]
                out[:,:hdim] += gxlpdfinner[:,:hdim]
                out[:,s1:s3] += gxlpdfinner[:,hdim:]
                # Likelihood
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    gxll = ll.grad_x(xin, *args, **kwargs)[:,perm_ll]
                    if hdim > 0:
                        gxll[:,:hdim] = np.einsum(
                            '...i,...ij->...j', gxll[:,:hdim], gx_hyper)
                    out[:,:hdim] += gxll[:,:hdim]
                    out[:,s2:s3] += gxll[:,hdim:]
        return out

    def hess_x_log_pdf(self, x, *args, **kwargs):
        if self.idx0 == 0:
            out = self.seqinfdens.hess_x_log_pdf(x, *args, **kwargs)
        else:
            xtr = x.copy() # Transformed input
            hdim = self.hyper_dim
            sdim = self.state_dim
            # Apply hyper and component maps to obtain transformed inputs and
            # compute gradients and Hessians of the maps
            xtr[:,hdim:hdim+sdim] = self.state_map.evaluate(
                x[:,:hdim+sdim], *args, **kwargs)
            gx_comp = self.state_map.grad_x(x[:,:hdim+sdim], *args, **kwargs)
            hx_comp = self.state_map.hess_x(x[:,:hdim+sdim], *args, **kwargs)
            if hdim > 0:
                xtr[:,:hdim] = self.hyper_map.evaluate(x[:,:hdim], *args, **kwargs)
                gx_hyper = self.hyper_map.grad_x(x[:,:hdim], *args, **kwargs)
                hx_hyper = self.hyper_map.hess_x(x[:,:hdim], *args, **kwargs)
            # Evaluate
            m = x.shape[0]
            out = np.zeros((x.shape[0], self.dim, self.dim))
            # Evaluate pi_hyper
            out[:,:hdim+sdim,:hdim+sdim] += self.pi_hyper.hess_x_log_pdf(
                x[:,:hdim+sdim], *args, **kwargs)
            # Evaluate transitions and likelihoods
            perm_pi = list(range(2*sdim,2*sdim+hdim)) + \
                      list(range(sdim,2*sdim)) + \
                      list(range(0, sdim))
            perm_ll = list(range(sdim, sdim+hdim)) + \
                      list(range(0, sdim))
            for i, (pi, ll) in enumerate(zip(self.pi_list, self.ll_list)):
                s1 = hdim + i*sdim
                s2 = s1 + sdim
                s3 = s2 + sdim
                xin = xtr[:,s2:s3]
                yin = np.hstack( (xtr[:,s1:s2], xtr[:,:hdim]) )
                #############
                # Transition
                c1 = hdim
                c2 = c1 + sdim
                hxlpdf = pi.hess_x_log_pdf(
                    xin, yin, *args, **kwargs)[np.ix_(range(m),perm_pi,perm_pi)]
                gxlpdf = pi.grad_x_log_pdf(xin, yin, *args, **kwargs)[:,perm_pi]
                hx = np.zeros(hxlpdf.shape)

                # H_th (logpi(T(th), M(th,y), x))
                if hdim > 0: # Apply hyper map
                    # <H_th logpi, (d_th T)(d_th T)^T>
                    tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,:c1], gx_hyper)
                    tmp = np.einsum('...ij,...ik->...jk', tmp, gx_hyper)
                    hx[:,:c1,:c1] += tmp
                    if i == 0:
                        # <H_{th,y} logpi, (d_th T)(d_th M)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,:c1])
                        hx[:,:c1,:c1] += tmp + tmp.transpose((0,2,1)) # Symmetry
                        # <H_{y} logpi, (d_th M)(d_th M)^T>
                        tmp = np.einsum('...ij,...ik->...jk',
                                        hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,:c1])
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,:c1])
                        hx[:,:c1,:c1] += tmp
                    # <d_th logpi, H_th T>
                    tmp = np.einsum('...i,...ijk->...jk', gxlpdf[:,:c1], hx_hyper)
                    hx[:,:c1,:c1] += tmp
                    if i == 0:
                        # <d_y logpi, H_th M>
                        tmp = np.einsum('...i,...ijk->...jk',
                                        gxlpdf[:,c1:c2], hx_comp[:,:,:c1,:c1])
                        hx[:,:c1,:c1] += tmp

                # H_y (logpi(T(th), M(th,y), x))
                if i == 0:
                    # <H_y logpi, (d_y M)(d_y M)^T>
                    tmp = np.einsum('...ij,...ik->...jk',
                                    hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,c1:])
                    tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                    hx[:,c1:c2,c1:c2] += tmp
                    # <d_y logpi, H_y M>
                    tmp = np.einsum('...i,...ijk->...jk',
                                    gxlpdf[:,c1:c2], hx_comp[:,:,c1:,c1:])
                    hx[:,c1:c2,c1:c2] += tmp
                else:
                    hx[:,c1:c2,c1:c2] += hxlpdf[:,c1:c2,c1:c2]

                # H_x (logpi(T(th), M(th,y), x))
                hx[:,c2:,c2:] += hxlpdf[:,c2:,c2:] # Identity

                # H_{th,y} (logpi(T(th), M(th,y), x))
                if hdim > 0:
                    if i == 0:
                        # <H_{th,y} logpi, (d_th T)(d_y M)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                        hx[:,:c1,c1:c2] += tmp
                        # <H_y logpi, (d_th M)(d_y M)^T>
                        tmp = np.einsum('...ij,...ik->...jk',
                                        hxlpdf[:,c1:c2,c1:c2], gx_comp[:,:,:c1])
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_comp[:,:,c1:])
                        hx[:,:c1,c1:c2] += tmp
                        # <d_y logpi, H_{th,y} M>
                        tmp = np.einsum('...i,...ijk->...jk',
                                        gxlpdf[:,c1:c2], hx_comp[:,:,:c1,c1:])
                        hx[:,:c1,c1:c2] += tmp
                    else:
                        # <H_{th,y} logpi, (d_th T) I^T>
                        tmp = np.einsum('...ij,...ik->...kj', hxlpdf[:,:c1,c1:c2], gx_hyper)
                        hx[:,:c1,c1:c2] += tmp

                # H_{y,th} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c1:c2,:c1] += hx[:,:c1,c1:c2].transpose((0,2,1))

                # H_{th,x} (logpi(T(th), M(th,y), x))
                if hdim > 0:
                    # <H_{th,x} logpi, (d_th T) I^T>
                    tmp = np.einsum('...ij,...ik->...kj', hxlpdf[:,:c1,c2:], gx_hyper)
                    hx[:,:c1,c2:] += tmp
                    if i == 0:
                        tmp = np.einsum('...ij,...ik->...kj',
                                        hxlpdf[:,c1:c2,c2:], gx_comp[:,:,:c1])
                        hx[:,:c1,c2:] += tmp

                # H_{x,th} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c2:,:c1] += hx[:,:c1,c2:].transpose((0,2,1))

                # H_{y,x} (logpi(T(th), M(th,y), x))
                if i == 0:
                    # <H_{y,x} logpi, (d_y M) I^T>
                    tmp = np.einsum('...ij,...ik->...kj',
                                    hxlpdf[:,c1:c2,c2:], gx_comp[:,:,c1:])
                    hx[:,c1:c2,c2:] += tmp
                else:
                    hx[:,c1:c2,c2:] += hxlpdf[:,c1:c2,c2:]

                # H_{x,y} (logpi(T(th), M(th,y), x)) -- symmetry
                hx[:,c2:,c1:c2] = hx[:,c1:c2,c2:].transpose((0,2,1))

                # Update out
                out[:,:hdim,:hdim] += hx[:,:hdim,:hdim]
                out[:,:hdim,s1:s3] += hx[:,:hdim,hdim:]
                out[:,s1:s3,:hdim] += hx[:,hdim:,:hdim]
                out[:,s1:s3,s1:s3] += hx[:,hdim:,hdim:]
                
                #############
                # Likelihood
                if ll is not None:
                    xin = np.hstack( (xtr[:,s2:s3], xtr[:,:hdim]) )
                    hxll = ll.hess_x(
                        xin, *args, **kwargs)[np.ix_(range(m),perm_ll,perm_ll)]
                    gxll = ll.grad_x(xin, *args, **kwargs)[:,perm_ll]
                    hx = np.zeros(hxll.shape)

                    # H_th (logL(T(th),x))
                    if hdim > 0:
                        # <H_th logL, (d_th T)(d_th T)^T>
                        tmp = np.einsum('...ij,...ik->...jk', hxll[:,:hdim,:hdim], gx_hyper)
                        tmp = np.einsum('...ij,...ik->...jk', tmp, gx_hyper)
                        hx[:,:hdim,:hdim] += tmp
                        # <d_th logL, H_th T>
                        tmp = np.einsum('...i,...ijk->...jk', gxll[:,:hdim], hx_hyper)
                        hx[:,:hdim,:hdim] += tmp

                    # H_x (logL(T(th),x))
                    hx[:,hdim:,hdim:] += hxll[:,hdim:,hdim:]

                    # H_{th,x} (logL(T(th),x))
                    if hdim > 0:
                        # <H_{th,x} logL, (d_th T) I^T>
                        tmp = np.einsum('...ij,...ik->...kj', hxll[:,:hdim,hdim:], gx_hyper)
                        hx[:,:hdim,hdim:] += tmp

                    # H_{th,x} (logL(T(th),x)) -- symmetry
                    hx[:,hdim:,:hdim] += hx[:,:hdim,hdim:].transpose((0,2,1))

                    # Update out
                    out[:,:hdim,:hdim] += hx[:,:hdim,:hdim]
                    out[:,:hdim,s2:s3] += hx[:,:hdim,hdim:]
                    out[:,s2:s3,:hdim] += hx[:,hdim:,:hdim]
                    out[:,s2:s3,s2:s3] += hx[:,hdim:,hdim:]
        return out