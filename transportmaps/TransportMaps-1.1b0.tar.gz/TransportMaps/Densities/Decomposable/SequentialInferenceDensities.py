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

from TransportMaps import deprecate
from TransportMaps.Distributions.Decomposable import *

__all__ = ['MarkovChainDensity',
           'SequentialHiddenMarkovChainDensity',
           'MarkovComponentDensity']

class MarkovChainDensity(MarkovChainDistribution):
    def __init__(self, *args, **kwargs):
        deprecate(
            "TransportMaps.Densities.Decomposable.MarkovChainDensity", "1.0",
            "Use TransportMaps.Distributions.Decomposable.MarkovChainDistribution instead")
        super(MarkovChainDensity, self).__init__(*args, **kwargs)

class SequentialHiddenMarkovChainDensity(
        SequentialHiddenMarkovChainDistribution):
    def __init__(self, *args, **kwargs):
        deprecate(
            "TransportMaps.Densities.Decomposable.SequentialHiddenMarkovChainDensity",
            "1.0",
            "Use TransportMaps.Distributions.Decomposable.SequentialHiddenMarkovChainDistribution instead")
        super(SequentialHiddenMarkovChainDensity, self).__init__(*args, **kwargs)

class MarkovComponentDensity(MarkovComponentDistribution):
    def __init__(self, *args, **kwargs):
        deprecate(
            "TransportMaps.Densities.Decomposable.MarkovComponentDensity", "1.0",
            "Use TransportMaps.Distributions.Decomposable.MarkovComponentDistribution instead")
        super(MarkovComponentDensity, self).__init__(*args, **kwargs)
