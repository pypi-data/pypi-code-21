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

__all__ = []

from ._version import __version__

# Transport map imports
from . import External
from .External import *

from . import ObjectBase
from .ObjectBase import *

from . import Misc
from .Misc import *

from . import XML

from . import FiniteDifference

from . import Distributions
from . import Functionals
from . import Maps
from . import Likelihoods

from . import Routines
from .Routines import *

from . import Defaults
from .Defaults import *

from . import Algorithms
# from . import Optimization
from . import Diagnostics
from . import Samplers
from . import CLI
from . import tests

__all__ += External.__all__
__all__ += ObjectBase.__all__
__all__ += Misc.__all__
__all__ += ['FiniteDifference']
__all__ += ['Distributions']
__all__ += ['Functionals']
__all__ += ['Likelihoods']
__all__ += ['Maps']
__all__ += Routines.__all__
__all__ += Defaults.__all__
__all__ += ['Algorithms']
# __all__ += ['Optimization']
__all__ += ['Diagnostics']
__all__ += ['Samplers']
__all__ += ['XML']
__all__ += ['CLI']
__all__ += ['tests']

############
# DEPRECATED
from . import Densities
__all__ += ['Densities']
############

XML_NAMESPACE = '{TransportMaps}'

__author__ = "Transport Map Team"
__copyright__ = """LGPLv3, Copyright (C) 2015-2017, Massachusetts Institute of Technology"""
__credits__ = ["Transport Map Team"]
__maintainer__ = "Transport Map Team"
__website__ = "transportmaps.mit.edu"
__status__ = "Development"


##############################
# Linking to SpectralToolbox
def linking():
    import os.path
    tm_dir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.islink(tm_dir + '/XML/schema/basis.xsd'):
        import warnings
        import os
        import SpectralToolbox.Spectral1D as S1D
        warnings.warn("Re-linking to SpectralToolbox. " + \
                      "This is done every time a new version of either " + \
                      "SpectralToolbox or TransportMaps are updated.",
                      UserWarning)
        s1d_dir = os.path.dirname(os.path.realpath(S1D.__file__))
        os.symlink(s1d_dir + '/XML/schema/basis.xsd',
                   tm_dir + '/XML/schema/basis.xsd')
linking()