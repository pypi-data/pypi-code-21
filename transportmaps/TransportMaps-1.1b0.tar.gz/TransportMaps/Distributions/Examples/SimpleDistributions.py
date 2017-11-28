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
from TransportMaps.Distributions.FrozenDistributions import StandardNormalDistribution

__all__ = ['FactorizedBananaDistribution']

class SquaredAvgNormalDistribution(ConditionalDistribution):
    r"""
    Conditional distribution :math:`x_1 | x_0 \sim \mathcal{N}(x_0^2, 1)`
    """
    def __init__(self):
        super(SquaredAvgNormalDistribution, self).__init__(1,1)
    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        return -.5 * (x[:,0] - y[:,0]**2)**2 -.5 * np.log(2 * np.pi)
    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        out = np.zeros((x.shape[0],2))
        out[:,0] = - x[:,0] + y[:,0]**2
        out[:,1] = 2 * x[:,0] * y[:,0] - 2 * y[:,0]**3
        return out
    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        out = np.zeros((x.shape[0],2,2))
        out[:,0,0] = -1.
        out[:,0,1] = 2 * y[:,0]
        out[:,1,0] = out[:,0,1]
        out[:,1,1] = 2 * x[:,0] - 6 * y[:,0]**2
        return out

class FactorizedBananaDistribution(FactorizedDistribution):
    r"""
    Joint distribution :math:`\pi(x_0,x_1)=\pi_1(x_1|x_0)\pi_2(x_0)` defined by

    .. math::

       x_0 \sim \mathcal{N}(0,1) \\
       x_1 | x_0 \sim \mathcal{N}(x_0^2, 1)

    """
    def __init__(self):
        p1 = SquaredAvgNormalDistribution()
        p2 = StandardNormalDistribution(1)
        factors = [(p1, (1,), (0,)),
                   (p2, (0,), ()  )]
        super(FactorizedBananaDistribution,self).__init__(factors)


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    d = FactorizedBananaDistribution()
    x = np.linspace(-4,4,30)
    X,Y = np.meshgrid(x,x)
    xx = np.vstack((X.flatten(),Y.flatten())).T
    Z = d.pdf(xx).reshape(X.shape)
    plt.figure()
    plt.contour(X,Y,Z)
    plt.show(False)