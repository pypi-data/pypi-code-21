# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

import numpy
import matplotlib.pyplot as plt

num_div = 1000
ii_max = num_div+1

ii = numpy.r_[0:ii_max]
x = ii/ii_max

base=1

P = -1
F = -1
L = 1
a = .5*L
b = L-a

h = .2

E = 30
I = base*h**3/12

#Simply supported with asymmetric point Load
w1 = F*b*x*(L**2-b**2-x**2)/(6*L*E*I)
w2 = F*b*x*(L**2-b**2-x**2)/(6*L*E*I)+P*(x-a)**3/(6*E*I)
w = x*0

w[x<=a] = w1[x<=a]
w[x>a] = w2[x>a]
plt.plot(x,w)

#simply supported with distributed load
w= P*x*(L**3-2*L*x**2+x**3)/(24*E*I)
plt.figure()
plt.plot(x,w)

#cantilever with end load
w = F*x**2*(3*L-x)/(6*E*I)
plt.figure()
plt.plot(x,w)

#cantilever with distributed load
w = P*x**2*(6*L**2-4*L*x+x**2)/(24*E*I)
plt.figure()
plt.plot(x,w)

