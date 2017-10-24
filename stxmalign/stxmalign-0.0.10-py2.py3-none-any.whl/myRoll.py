#!/usr/bin/python
"""
My np.rool function
"""

import numpy as np

class myRoll(object):

    def npRoll(self, array, shift, axis):
        array = np.roll(array, shift, axis)
        return array
        

    def transfRoll(self, array, shift, axis):
##        print "myroll", array.shape
##        for l in range(array.shape[0]):
##            print l
##            array[l,:] = np.roll(array[l,:], shift[l], axis)
        for l in range(array.shape[1]):
##            print l
            array[:,l] = np.roll(array[:,l], shift[l], axis)
        return array
