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

import TransportMaps as TM

__all__ = ['Sampler']

class Sampler(TM.TMO):
    r""" Generic sampler of distribution ``d``

    This main class just mirrors all the sampling methods provided by the distribution ``d``.

    Args:
      d (Distributions.Distribution): distribution to sample from.
    """
    def __init__(self, d):
        super(Sampler, self).__init__()
        self.distribution = d

    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples and weights from the distribution

        Args:
          m (int): number of samples to generate

        Returns:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`], :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of points and weights
        """
        return (self.distribution.rvs(m, *args, **kwargs), np.ones(m)/float(m))
    