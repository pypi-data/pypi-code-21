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

import numpy as np
import scipy.special
from TransportMaps.Distributions.DistributionBase import Distribution

__all__ = ['BODjoint']

class BODjoint(Distribution):
    def __init__(self, numY, sigma = np.sqrt(1e-3) ):
        timeY=np.arange(numY)+1.
        dimDistribution = numY+2
        super(BODjoint,self).__init__(dimDistribution)
        self.numY = numY
        self.timeY  = timeY
        self.sigma = sigma
    def pdf(self, x, params=None):
        return np.exp(self.log_pdf(x, params))
    def log_pdf(self, x, params=None):
        # x is a 2-d array of points. The first dimension corresponds to the number of points.
        #The first numY columns of x refer to the data
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + scipy.special.erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + scipy.special.erf( theta2/np.sqrt(2) )  )
        return -1.0/(2*self.sigma**2) * \
            np.sum( (Y - a[:,np.newaxis] * \
                     ( 1 - np.exp( -np.outer(b, self.timeY) ) ) )**2 , axis=1) + \
            -.5*( theta1**2 + theta2**2 )
    def grad_x_log_pdf(self, x, params=None):
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + scipy.special.erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + scipy.special.erf( theta2/np.sqrt(2) )  )
        da_theta1 = .4*np.sqrt(2/np.pi)*np.exp( -theta1**2/2.)
        db_theta2 = .15*np.sqrt(2/np.pi)*np.exp( -theta2**2/2.)
        grad = np.zeros( x.shape )
        for jj in np.arange(numY):
            grad[:,numY] -= -da_theta1/(self.sigma**2) * \
                            ( 1 - np.exp( - b*self.timeY[jj])  ) * \
                            ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) )
            grad[:,numY+1] -= -1.0/(self.sigma**2)*self.timeY[jj]*db_theta2*a * \
                              np.exp(-b*self.timeY[jj]) * \
                              ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) )
            grad[:,jj] = -1.0/self.sigma**2 * \
                         ( Y[:,jj] - a*(1-np.exp(-b*self.timeY[jj])) )
        grad[:,-2] -=  theta1
        grad[:,-1] -=  theta2
        return grad
    def hess_x_log_pdf(self, x, params=None):
        numY = self.numY
        Y = x[:,0:numY]
        theta1=x[:,numY] #The last two components refer to the parameters
        theta2=x[:,numY+1]
        a = .4  + .4*( 1 + scipy.special.erf( theta1/np.sqrt(2) )  )
        b = .01 + .15*( 1 + scipy.special.erf( theta2/np.sqrt(2) )  )
        da_theta1 = .4*np.sqrt(2/np.pi)*np.exp( -theta1**2/2.)
        db_theta2 = .15*np.sqrt(2/np.pi)*np.exp( -theta2**2/2.)
        d2a_theta1 = -theta1*da_theta1
        d2b_theta2 = -theta2*db_theta2
        Hess_x = np.zeros( (x.shape[0], x.shape[1],  x.shape[1]) )
        for jj in np.arange(numY):
            Hess_x[:,numY,numY]-= \
                -(1-np.exp(-b*self.timeY[jj]))/(self.sigma**2) * \
                ( d2a_theta1*( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) ) - \
                  da_theta1**2*(1-np.exp(-b*self.timeY[jj]))  )
            Hess_x[:,numY+1,numY]-= \
                -da_theta1/(self.sigma**2) * \
                ( db_theta2*self.timeY[jj]*np.exp(-b*self.timeY[jj]) * \
                  (Y[:,jj]-a+a*np.exp(-b*self.timeY[jj])) + \
                  (1-np.exp(-b*self.timeY[jj])) * \
                  (-a*self.timeY[jj]*db_theta2*np.exp(-b*self.timeY[jj])))
            Hess_x[:,numY+1,numY+1]-= \
                -self.timeY[jj]*a/(self.sigma**2) * \
                np.exp(-b*self.timeY[jj]) * \
                ( ( Y[:,jj] - a*(1- np.exp(-b*self.timeY[jj])) ) * \
                  ( d2b_theta2 - self.timeY[jj]*db_theta2**2 ) - \
                  db_theta2**2 *self.timeY[jj]*a*np.exp(-b*self.timeY[jj]))
            Hess_x[:,numY,jj] = da_theta1/(self.sigma**2)*(1-np.exp(-b*self.timeY[jj]))
            Hess_x[:,numY+1,jj] = 1/(self.sigma**2)*self.timeY[jj] * \
                                  db_theta2*a*np.exp(-b*self.timeY[jj])
            Hess_x[:,jj, numY] = Hess_x[:,numY,jj]
            Hess_x[:,jj, numY+1] = Hess_x[:,numY+1, jj]
        Hess_x[:,numY, numY+1] = Hess_x[:,numY+1, numY]
        Hess_x[:,numY,numY]-=1
        Hess_x[:,numY+1,numY+1]-=1
        for kk in np.arange(x.shape[0]):
            for jj in np.arange(numY):
                Hess_x[ kk , jj, jj]  = -1/(self.sigma**2)
        return Hess_x