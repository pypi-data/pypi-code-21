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

from TransportMaps.ObjectBase import TMO
from TransportMaps.Misc import deprecate
from TransportMaps.Distributions.Decomposable import \
    SequentialHiddenMarkovChainDistribution
from TransportMaps.Maps.TriangularTransportMapBase import \
    TriangularTransportMap, TriangularListStackedTransportMap
from TransportMaps.Maps.TransportMapBase import ListCompositeTransportMap

__all__ = ['Filter', 'Smoother']

class Filter(TMO):
    r""" Perform the on-line filtering of a sequential Hidded Markov chain.

    Given the prior distribution on the hyper-parameters :math:`\pi(\Theta)`,
    provides the functions neccessary to assimilate new pieces of data or
    missing data 
    (defined in terms of transition densities
    :math:`\pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right)`
    and log-likelihoods
    :math:`\log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right)`),
    to return the maps pushing forward :math:`\mathcal{N}(0,{\bf I})`
    to the filtering/forecast distributions
    :math:`\{\pi\left(\Theta, {\bf Z}_k \middle\vert {\bf y}_{0:k} \right)\}_k`.

    For more details see also :cite:`Spantini2017` and the
    `tutorial <example-sequential-stocvol-6d.html>`_.

    Args:
      pi_hyper (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior distribution on the hyper-parameters :math:`\pi(\Theta)`

    .. note:: This is a super-class. Part of its methods need to be implemented
      by sub-classes.
    """
    def __init__(self, pi_hyper=None):
        super(Filter,self).__init__()
        self._pi = SequentialHiddenMarkovChainDistribution([], [], pi_hyper)
        self._nsteps = -1
        self.F_list = [] # List of filtering maps

    @property
    def pi(self):
        return self._pi

    @property
    def nsteps(self):
        return self._nsteps

    @property
    def filtering_map_list(self):
        r""" Returns the maps :math:`\{ \widetilde{\mathfrak{M}}_k({\bf x}_\theta, {\bf x}_{k+1}) \}_{i=0}^{k-1}` pushing forward :math:`\mathcal{N}(0,{\bf I})` to the filtering/forecast distributions :math:`\{\pi\left(\Theta, {\bf Z}_k \middle\vert {\bf y}_{0:k} \right)\}_k`.

        The maps :math:`\widetilde{\mathfrak{M}}_k({\bf x}_\theta, {\bf x}_{k+1})`
        are defined as follows:

        .. math::

           \widetilde{\mathfrak{M}}_k({\bf x}_\theta, {\bf x}_{k+1}) = 
           \left[\begin{array}{l}
           \mathfrak{M}_0^\Theta \circ \cdots \circ \mathfrak{M}_{k}^\Theta ({\bf x}_\theta) \\
           \mathfrak{M}_k^1\left({\bf x}_\theta, {\bf x}_{k+1}\right)
           \end{array}\right] =
           \left[\begin{array}{l}
           \mathfrak{H}_{k}({\bf x}_\theta) \\
           \mathfrak{M}_k^1\left({\bf x}_\theta, {\bf x}_{k+1}\right)
           \end{array}\right]

        Returns:
          (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`) -- list of transport maps :math:`\widetilde{\mathfrak{M}}_k({\bf x}_\theta, {\bf x}_{k+1})`
        """
        return self.F_list
        
    def assimilate(self, pi, ll, *args, **kwargs):
        r""" Assimilate one piece of data :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`.

        Given the new piece of data
        :math:`\left( \pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right), \log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right) \right)`,
        determine the maps pushing forward :math:`\mathcal{N}(0,{\bf I})`
        to the filtering/forecast distributions
        :math:`\{\pi\left(\Theta, {\bf Z}_k \middle\vert {\bf y}_{0:k} \right)\}_k`.
        
        Args:
          pi (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            transition distribution
            :math:`\pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right)`
          ll (:class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
            log-likelihood
            :math:`\log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right)`. The value ``None`` stands for missing observation.
          *args, **kwargs: arguments required by the particular sub-classes implementations
            of :func:`_assimilation_step`.

        .. note:: This method requires the implementation of the function
           :func:`_assimilation_step` in sub-classes
        """
        # Append transition and log-likelihood in self.pi
        self._pi.append(pi, ll)
        self._nsteps += 1
        # Approximation
        self._assimilation_step(*args, **kwargs)

    def _assimilation_step(self, *args, **kwargs):
        r""" [Abstract] Implements the map approximation for one step in the sequential inference.

        .. raises:: NotImplementedError
        """
        raise NotImplementedError("To be implemented in sub-classes.")

    def get_filtering_map_list(self):
        r"""
        .. deprecated:: Use :attr:`filtering_map_list` instead
        """
        deprecate("filtering_map_list", "1.0b3",
                  "Use property filtering_map_list instead")
        return self.filtering_map_list

class Smoother(Filter):
    r""" Perform the on-line smoothing and filtering of a sequential Hidded Markov chain.

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

    .. note:: This is a super-class. Part of its methods need to be implemented
      by sub-classes.
    """
    def __init__(self, pi_hyper=None):
        super(Smoother,self).__init__(pi_hyper)
        self.L_list = []

    @property
    def smoothing_map(self):
        r""" Returns the map :math:`\mathfrak{T}` pushing forward :math:`\mathcal{N}(0,{\bf I})` to the smoothing distribution :math:`\pi\left(\Theta, {\bf Z}_\Lambda \middle\vert {\bf y}_\Xi\right)`.

        The map :math:`\mathfrak{T}` is given by the composition
        :math:`T_0 \circ \cdots \circ T_{k-1}` maps constructed in
        :math:`k` assimilation steps.

        Returns:
          (:class:`TransportMap<TransportMaps.Maps.TransportMap>`) -- the map :math:`\mathfrak{T}`
        """
        if self.nsteps >= 0:
            return ListCompositeTransportMap( self.L_list )
        else:
            raise RuntimeError("No step assimilated yet!")
        
    def assimilate(self, pi, ll, *args, **kwargs):
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
        
        Args:
          pi (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
            transition distribution
            :math:`\pi\left({\bf Z}_{k+1} \middle\vert {\bf Z}_k, \Theta \right)`
          ll (:class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
            log-likelihood
            :math:`\log \mathcal{L}\left({\bf y}_{k+1}\middle\vert {\bf Z}_{k+1}, \Theta\right)`. The value ``None`` stands for missing observation.
          *args, **kwargs: arguments required by the particular sub-classes implementations
            of :func:`_assimilation_step`.

        .. note:: This method requires the implementation of the function
           :func:`_assimilation_step` in sub-classes
        """
        super(Smoother, self).assimilate(pi, ll, *args, **kwargs)

    def get_smoothing_map(self):
        r"""
        .. deprecated:: Use :attr:`filtering_map_list` instead
        """
        deprecate("get_smoothing_map", "1.0b3",
                  "Use property smoothing_map instead")
        return self.smoothing_map