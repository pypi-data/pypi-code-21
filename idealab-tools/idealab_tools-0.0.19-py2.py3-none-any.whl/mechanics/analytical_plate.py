# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

import numpy
import matplotlib.pyplot as plt
from math import pi

#millimeters=1/1000
#
#GPa = 1e9
#kPa = 1e3

E = 12
t = 1
nu = 0

D = E*t**3/(12*(1-nu**2))
q = -1

a = 1
b = 1
x = .5*a
y = .5*b

mm = numpy.r_[1:101:2]
nn = numpy.r_[1:101:2]
mmm,nnn = numpy.meshgrid(mm,nn)

xx = numpy.r_[0:a:31j]
yy = numpy.r_[0:b:31j]
xy = numpy.array(numpy.meshgrid(xx,yy)).T

ww = (xy*0)[:,:,0]

amn = 16*q/mmm/nnn/pi**2
w1 = amn/pi**4/D
w2 = (mmm**2/a**2+nnn**2/b**2)**-2
for ii in range(xy.shape[0]):
    for jj in range(xy.shape[1]):
        x=xy[ii,jj,0]
        y=xy[ii,jj,1]
        w3 = numpy.sin(mmm*pi*x/a)
        w4 = numpy.sin(nnn*pi*y/b)  
        w = w1*w2*w3*w4
        ww[ii,jj]=w.sum()
        
#ww = ww*100

xyz = numpy.array([xy[:,:,0],xy[:,:,1],ww]).transpose(1,2,0).reshape(-1,3)
fig = plt.figure(figsize=(10,8))

import idealab_tools.mechanics.functions
idealab_tools.mechanics.functions.plot_xyz(xyz,fig)

#plt.figure()
#plt.contourf(xy[:,:,0],xy[:,:,1],ww)
#plt.axis('equal')
#plt.plot(xy[:,:,0],ww)

#w_max=4*q/(pi**4*D*(1/a**2+1/b**2)**2)
print(ww.min())


plt.savefig('analytical.png')