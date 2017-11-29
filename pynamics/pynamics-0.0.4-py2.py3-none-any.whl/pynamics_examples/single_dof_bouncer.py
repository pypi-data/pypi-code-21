# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import pynamics

from pynamics.frame import Frame
from pynamics.variable_types import Differentiable,Constant
from pynamics.system import System
from pynamics.body import Body
from pynamics.dyadic import Dyadic
from pynamics.output import Output
from pynamics.particle import Particle
import pynamics.integration

#import sympy
import numpy
import matplotlib.pyplot as plt
plt.ion()
from math import pi
system = System()

mA = Constant(1,'mA',system)

g = Constant(9.81,'g',system)
b = Constant(1e0,'b',system)
k = Constant(1e5,'k',system)

tinitial = 0
tfinal = 5
tstep = .001
t = numpy.r_[tinitial:tfinal:tstep]

x,x_d,x_dd = Differentiable('x',system)
y,y_d,y_dd = Differentiable('y',system)

initialvalues = {}
initialvalues[x]=0
initialvalues[x_d]=.1
initialvalues[y]=.1
initialvalues[y_d]=0

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

N = Frame('N')

system.set_newtonian(N)

pNA=0*N.x

pAcm=pNA+x*N.x+y*N.y
vAcm = pAcm.time_derivative(N,system)

ParticleA = Particle(pAcm,mA,'ParticleA',system)

system.addforce(-b*vAcm,vAcm)

stretch = y
stretched1 = (stretch+abs(stretch))/2
stretched2 = -(-stretch+abs(-stretch))/2

#system.add_spring_force1(k,(stretched1)*N.y,vAcm) 
system.add_spring_force1(k,(stretched2)*N.y,vAcm) 

system.addforcegravity(-g*N.y)

x1 = ParticleA.pCM.dot(N.x)
y1 = ParticleA.pCM.dot(N.y)
    
f,ma = system.getdynamics()
func1 = system.state_space_post_invert(f,ma)
states=pynamics.integration.integrate_odeint(func1,ini,t,rtol=1e-12,atol=1e-12,hmin=1e-14, args=({'constants':system.constant_values},))

KE = system.get_KE()
PE = system.getPEGravity(pNA)-system.getPESprings()

output = Output([x1,y1,KE-PE,x,y],system)
y = output.calc(states)

plt.figure(1)
plt.plot(y[:,0],y[:,1])
plt.axis('equal')

plt.figure(2)
plt.plot(y[:,2])

plt.figure(3)
plt.plot(t,y[:,4])
plt.show()
