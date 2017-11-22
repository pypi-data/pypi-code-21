#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.

# References : https://www.deming.org/
# http://www.contesolutions.com/Western_Electric_SQC_Handbook.pdf
# http://www.fr-deming.org/WECSQ.pdf

"""
p.185
Correction factors
"""

def c1(n):
    """
    modal root square deviation = c1 * standard deviation
    """
    return math.sqrt((n-2)/n)
    
def c2(n):
    """
    mean root square deviation = c2 * standard deviation
    """
    a = math.sqrt((2/n))
    b = math.gamma(((n-2)/2)+1)
    c = math.gamma(((n-3)/2)+1)
    return a * (b/c)
    
"""
p.90
Table A
Values of F1(z) = (1 / sqrt(2*pi))*INTEGRAL[0-z]e^(-1/2 * z^2)dz
"""
import scipy.integrate as integrate
import math
import numpy as np

def F1(z):
    a = 1 / (math.sqrt(2 * math.pi))
    def integrand(z):
        return np.exp(-0.5*(z**2))
    result = integrate.quad(integrand, 0, z)
    return result[0] * a
    
"""
p.91
Table B
Values of F2(z) = (1 / 6 * sqrt(2*pi))*(1 - (1 - z**2)e^-0.5z**2)
"""
def F2(z):
    a = 1 / (6 * (math.sqrt(2 * math.pi)))
    b = 1 - (1 - z**2)*np.exp(-0.5*(z**2))
    return a * b

"""
p. 189
Ratio z
deviation from the mean vs sigma
"""

"""
Tables
"""
TABLE_A2_D3_D4 = { '2' : {'A2' : 1.88, 'D3' : 0, 'D4' : 3.27},
            '3' : {'A2' : 1.02, 'D3' : 0, 'D4' : 2.57},
            '4' : {'A2' : 0.73, 'D3' : 0, 'D4' : 2.28},
            '5' : {'A2' : 0.58, 'D3' : 0, 'D4' : 2.11},
            '6' : {'A2' : 0.48, 'D3' : 0, 'D4' : 2.00},
            '7' : {'A2' : 0.42, 'D3' : 0.08, 'D4' : 1.92},
            '8' : {'A2' : 0.37, 'D3' : 0.14, 'D4' : 1.86},
            '9' : {'A2' : 0.34, 'D3' : 0.18, 'D4' : 1.82},
            '10' : {'A2' : 0.31, 'D3' : 0.22, 'D4' : 1.78},
            '11' : {'A2' : 0.29, 'D3' : 0.26, 'D4' : 1.74},
            '12' : {'A2' : 0.27, 'D3' : 0.28, 'D4' : 1.72},
            '13' : {'A2' : 0.25, 'D3' : 0.31, 'D4' : 1.69},
            '14' : {'A2' : 0.24, 'D3' : 0.33, 'D4' : 1.67},
            '15' : {'A2' : 0.22, 'D3' : 0.35, 'D4' : 1.65},
            '16' : {'A2' : 0.21, 'D3' : 0.36, 'D4' : 1.64},
            '17' : {'A2' : 0.20, 'D3' : 0.38, 'D4' : 1.62},
            '18' : {'A2' : 0.19, 'D3' : 0.39, 'D4' : 1.61},
            '19' : {'A2' : 0.19, 'D3' : 0.40, 'D4' : 1.60},
            '20' : {'A2' : 0.18, 'D3' : 0.41, 'D4' : 1.59}
        }
