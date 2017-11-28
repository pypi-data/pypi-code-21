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

from . import SequentialInference
from . import Adaptivity

__all__ = []
__all__ += ['SequentialInference']
__all__ += ['Adaptivity']

# Back-compatibility interface
from TransportMaps import deprecate
__all__ += ['SequentialHiddenMarkovChainIntegrator']
class SequentialHiddenMarkovChainIntegrator(
        SequentialInference.TransportMapsSmoother):
    r""" Deprecated. Use :class:`TransportMapsSmoother<TransportMaps.Algorithms.SequentialInference.TransportMapsSmoother>`.
    """
    def __init__(self, *args, **kwargs):
        deprecate("TransportMaps.Algorithms.SequentialHiddenMarkovChainIntegrator",
                  "1.1",
                  "Use TransportMaps.Algorithms.SequentialInference.TransportMapsSmoother instead")
        super(SequentialHiddenMarkovChainIntegrator, self).__init__(*args, **kwargs)