# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""
import matplotlib.pyplot as plt
import sympy
import numpy
from sympy import pi
b,h,theta,P,l,E,I,x,w,M=sympy.symbols('b,h,theta,P,l,E,I,x,w,M')

#constant cross-sectional area
b = (l-x)**2
#b = (l-x)
I = b*h**3/12

#loading = 'point'
#loading = 'moment'
#loading = 'distributed'
loading = 'distributed'

if loading=='point':
    #point load at the end
    M = P*(l-x)

elif loading=='moment':
    #Moment applied to the end
    M = M

elif loading=='distributed':
    #distributed load
    M = sympy.integrate(w*x,(x,0,l-x))

elif loading=='function':
    #distributed load
    w = -sympy.sin(pi*x/l)
    M = sympy.integrate(w*x,(x,0,l-x))

dtheta = M/(E*I)
theta = sympy.integrate(dtheta,(x,0,x))
y = sympy.integrate(theta,(x,0,x))
y_max = sympy.integrate(theta,(x,0,l))
print(y_max)

# plot with real values

subs = {}
#subs[b]=1
subs[h]=1
#subs[I]=subs[b]*subs[h]**3/12
subs[l]=1
subs[E]=1
subs[P]=.1
if loading=='moment':
    subs[M]=1
if loading=='distributed':
    subs[w]=-.1
x2 = numpy.r_[0:subs[l]:100j]

y2 = y.subs(subs)
fy = sympy.lambdify(x,y2)
y3 = numpy.r_[[fy(item) for item in x2]]
plt.plot(x2,y3)

if loading == 'function':
    w2 = w.subs(subs)
    fw = sympy.lambdify(x,w2)
    w3 = numpy.r_[[fw(item) for item in x2]]
    plt.plot(x2,w3)
#
#
plt.axis('equal')

#
b = b.subs(subs)
fp = sympy.lambdify(x,b)
pn = numpy.r_[[fp(item) for item in x2]]
f = plt.figure()
##

profile_x = numpy.r_[x2,x2[::-1],x2[0:1]]
profile_y = numpy.r_[pn/2,-(pn/2)[::-1],pn[0:1]/2]
plt.plot(profile_x,profile_y)
##
