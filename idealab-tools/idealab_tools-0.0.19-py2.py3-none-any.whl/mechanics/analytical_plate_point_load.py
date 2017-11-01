# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

import numpy
import matplotlib.pyplot as plt
from math import pi
from numpy import sin,cos,tanh,sinh,cosh
#millimeters=1/1000
#
#GPa = 1e9
#kPa = 1e3

E = 12
t = 1
nu = 0

D = E*t**3/(12*(1-nu**2))
P = -1


a = 1
b = 1
x = .5*a
y = .5*b
e1 = .5*a
e2 = .5*b

mm = numpy.r_[1:501:2]
nn = numpy.r_[1:501:2]
mmm,nnn = numpy.meshgrid(mm,nn)

xx = numpy.r_[0:a:31j]
yy = numpy.r_[0:b:31j]
xy = numpy.array(numpy.meshgrid(xx,yy)).T

ww = (xy*0)[:,:,0]

w0 = 4*P*b**3/(pi**4*a*D)
for ii in range(xy.shape[0]):
    for jj in range(xy.shape[1]):
        x=xy[ii,jj,0]
        y=xy[ii,jj,1]

        w1 = sin(nnn*pi*e2/b)*sin(nnn*pi*y/b)/(mmm**2*b**2/a**2+nnn**2)**2
        w2 = sin(mmm*pi*e1/a)*sin(mmm*pi*x/a)
        
        w = w0*w1*w2
        ww[ii,jj]=w.sum()

xyz = numpy.array([xy[:,:,0],xy[:,:,1],ww]).transpose(1,2,0).reshape(-1,3)
import idealab_tools.mechanics.functions
idealab_tools.mechanics.functions.plot_xyz(xyz)

#plt.figure()
#plt.contourf(xy[:,:,0],xy[:,:,1],ww)
#plt.axis('equal')
#plt.plot(xy[:,:,0],ww)

#w_max=4*q/(pi**4*D*(1/a**2+1/b**2)**2)
print(ww.min())


