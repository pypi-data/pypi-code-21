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

from TransportMaps import deprecate
from TransportMaps.Distributions import *

__all__ = ["Density", "ParametricDensity",
           "TransportMapDensity",
           "PushForwardTransportMapDensity",
           "PullBackTransportMapDensity",
           'FrozenDensity_1d',
           'GaussianDensity', 'StandardNormalDensity',
           'LogNormalDensity', 'LogisticDensity',
           'GammaDensity', 'BetaDensity',
           'WeibullDensity',
           'GumbelDensity', 'BananaDensity']

class Density(Distribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.Density", "1.0",
                  "Use TransportMaps.Distributions.Distribution instead")
        super(Density, self).__init__(*args, **kwargs)

class ParametricDensity(ParametricDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.ParametricDensity", "1.0",
                  "Use TransportMaps.Distributions.ParametricDistribution instead")
        super(ParametricDensity, self).__init__(*args, **kwargs)

class TransportMapDensity(TransportMapDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.TransportMapDensity", "1.0",
                  "Use TransportMaps.Distributions.TransportMapDistribution instead")
        super(TransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

class PushForwardTransportMapDensity(PushForwardTransportMapDistribution):
    def __init__(self, *args, **kwargs):
        deprecate(
            "TransportMaps.Densities.PushForwardTransportMapDensity", "1.0",
            "Use TransportMaps.Distributions.PushForwardTransportMapDistribution instead")
        super(PushForwardTransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

class PullBackTransportMapDensity(PullBackTransportMapDistribution):
    def __init__(self, *args, **kwargs):
        deprecate(
            "TransportMaps.Densities.PullBackTransportMapDensity", "1.0",
            "Use TransportMaps.Distributions.PullBackTransportMapDistribution instead")
        super(PullBackTransportMapDensity, self).__init__(*args, **kwargs)

    @property
    def base_density(self):
        return self.base_distribution

    @base_density.setter
    def base_density(self, value):
        self.base_distribution = value

# FROZEN DISTRIBUTIONS
class FrozenDensity_1d(FrozenDistribution_1d):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.FrozenDensity_1d", "1.0",
                  "Use TransportMaps.Distributions.FrozenDistribution_1d instead")
        super(FrozenDensity_1d, self).__init__(*args, **kwargs)

class GaussianDensity(GaussianDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.GaussianDensity", "1.0",
                  "Use TransportMaps.Distributions.GaussianDistribution instead")
        super(GaussianDensity, self).__init__(*args, **kwargs)

class StandardNormalDensity(StandardNormalDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.StandardNormalDensity", "1.0",
                  "Use TransportMaps.Distributions.StandardNormalDistribution instead")
        super(StandardNormalDensity, self).__init__(*args, **kwargs)

class LogNormalDensity(LogNormalDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.LogNormalDensity", "1.0",
                  "Use TransportMaps.Distributions.LogNormalDistribution instead")
        super(LogNormalDensity, self).__init__(*args, **kwargs)

class LogisticDensity(LogisticDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.LogisticDensity", "1.0",
                  "Use TransportMaps.Distributions.LogisticDistribution instead")
        super(LogisticDensity, self).__init__(*args, **kwargs)

class GammaDensity(GammaDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.GammaDensity", "1.0",
                  "Use TransportMaps.Distributions.GammaDistribution instead")
        super(GammaDensity, self).__init__(*args, **kwargs)

class BetaDensity(BetaDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.BetaDensity", "1.0",
                  "Use TransportMaps.Distributions.BetaDistribution instead")
        super(BetaDensity, self).__init__(*args, **kwargs)

class WeibullDensity(WeibullDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.WeibullDensity", "1.0",
                  "Use TransportMaps.Distributions.WeibullDistribution instead")
        super(WeibullDensity, self).__init__(*args, **kwargs)

class GumbelDensity(GumbelDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.GumbelDensity", "1.0",
                  "Use TransportMaps.Distributions.GumbelDistribution instead")
        super(GumbelDensity, self).__init__(*args, **kwargs)

class BananaDensity(BananaDistribution):
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Densities.BananaDensity", "1.0",
                  "Use TransportMaps.Distributions.BananaDistribution instead")
        super(BananaDensity, self).__init__(*args, **kwargs)

