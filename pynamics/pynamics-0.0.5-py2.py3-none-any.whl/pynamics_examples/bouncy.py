# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import pynamics
from pynamics.frame import Frame
from pynamics.variable_types import Differentiable,Constant,Variable
from pynamics.system import System
from pynamics.body import Body
from pynamics.dyadic import Dyadic
from pynamics.output import Output
from pynamics.particle import Particle
import pynamics.integration

import sympy
import numpy
import matplotlib.pyplot as plt
plt.ion()
from math import pi
system = System()

error = 1e-4
error_tol = 1e-10

alpha = 1e6
beta = 1e5

#preload1 = Constant('preload1',0*pi/180,system)
l1 = Constant(1,'l1',system)
m1 = Constant(1e1,'m1',system)
m2 = Constant(1e0,'m2',system)
k = Constant(1e4,'k',system)
l0 = Constant(1,'l0',system)
b = Constant(5e0,'b',system)
g = Constant(9.81,'g',system)

tinitial = 0
tfinal = 10
tstep = .01
t = numpy.r_[tinitial:tfinal:tstep]

x1,x1_d,x1_dd = Differentiable('x1',system)
x2,x2_d,x2_dd = Differentiable('x2',system)

initialvalues = {}
initialvalues[x1]=2
initialvalues[x1_d]=0
initialvalues[x2]=1
initialvalues[x2_d]=0

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

N = Frame('N')
system.set_newtonian(N)

pNA=0*N.x
pm1 = x1*N.y
pm2 = pm1 - x2*N.y

#BodyA = Body('BodyA',A,pm1,m1,IA,system)
Particle1 = Particle(pm1,m1,'Particle1',system)
Particle2 = Particle(pm2,m2,'Particle2',system)

vpm1 = pm1.time_derivative(N,system)
vpm2 = pm2.time_derivative(N,system)

l_ = pm1-pm2
l = (l_.dot(l_))**.5
l_d =system.derivative(l)
stretch = l - l0
ul_ = l_*((l+error_tol)**-1)
vl = l_.time_derivative(N,system)

system.add_spring_force1(k,stretch*ul_,vl)
#system.addforce(-k*stretch*ul_,vpm1)
#system.addforce(k*stretch*ul_,vpm2)

system.addforce(-b*l_d*ul_,vpm1)
system.addforce(b*l_d*ul_,vpm2)

#system.addforce(k*l*ul_,vpm2)
#system.addforce(-b*vl,vl)
#system.addforce(-b*vl,vl)
#system.addforce(-b*vl,vl)



system.addforcegravity(-g*N.y)

#system.addforcegravity(-g*N.y)
#system.addforcegravity(-g*N.y)


eq1 = [pm2.dot(N.y)-0]
eq1_d=[system.derivative(item) for item in eq1]
eq1_dd=[system.derivative(system.derivative(item)) for item in eq1]

a = [0-pm2.dot(N.y)]
b = [(item+abs(item)) for item in a]

x1 = Particle1.pCM.dot(N.y)
x2 = Particle2.pCM.dot(N.y)

f,ma = system.getdynamics()
#func = system.state_space_post_invert(f,ma,eq)
func = system.state_space_post_invert2(f,ma,eq1_dd,eq1_d,eq1,eq_active = b)
states=pynamics.integration.integrate_odeint(func,ini,t,rtol = error, atol = error, args=({'alpha':alpha,'beta':beta, 'constants':system.constant_values},),full_output = 1,mxstep = int(1e5))
states = states[0]

KE = system.get_KE()
PE = system.getPEGravity(pNA) - system.getPESprings()

output = Output([x1,x2,l, KE-PE],system)
y = output.calc(states)
pynamics.toc()

plt.figure(0)
plt.plot(t,y[:,0])
plt.plot(t,y[:,1])
plt.axis('equal')

plt.figure(1)
plt.plot(t,y[:,2])
plt.axis('equal')

plt.figure(2)
plt.plot(t,y[:,3])
#plt.axis('equal')
