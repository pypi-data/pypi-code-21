# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import pynamics
pynamics.script_mode = False

from pynamics.frame import Frame
from pynamics.variable_types import Differentiable,Constant
from pynamics.system import System
from pynamics.body import Body
from pynamics.dyadic import Dyadic
from pynamics.output import Output
from pynamics.particle import Particle
import pynamics.integration

import numpy
import matplotlib.pyplot as plt
plt.ion()
from math import pi
system = System()

lA = Constant(1,'lA',system)

mA = Constant(1,'mA',system)

g = Constant(9.81,'g',system)
#b = Constant(1e0,'b',system)
k = Constant(3e2,'k',system)

Ixx_A = Constant(1,'Ixx_A',system)
Iyy_A = Constant(1,'Iyy_A',system)
Izz_A = Constant(.3,'Izz_A',system)


tinitial = 0
tfinal = 10
tstep = .001
t = numpy.r_[tinitial:tfinal:tstep]

preload1 = Constant(0*pi/180,'preload1',system)

q,q_d,q_dd = Differentiable('q',system)
x,x_d,x_dd = Differentiable('x',system)

initialvalues = {}
initialvalues[q]=30*pi/180
initialvalues[q_d]=0*pi/180
initialvalues[x]=1
initialvalues[x_d]=0

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

N = Frame('N')
A = Frame('A')

system.set_newtonian(N)
A.rotate_fixed_axis_directed(N,[0,0,1],q,system)

pNA=0*N.x
pAB=pNA-x*A.y
vNA=pNA.time_derivative(N,system)
vAB=pAB.time_derivative(N,system)
aAB = vAB.time_derivative(N,system)

#ParticleA = Particle(pAB,mA,'ParticleA',system)
IA = Dyadic.build(A,Ixx_A,Iyy_A,Izz_A)
BodyA = Body('BodyA',A,pAB,mA,IA,system)

stretch = x-lA
direction = -A.y
#system.addforce(-b*vAB,vAB)
system.addforce(-k*stretch*A.y,vNA)
system.addforce(k*stretch*A.y,vAB)
#system.add_springforce(k*stretch*A.y,vAB)
#system.addforce(b*x_d*A.y,vAB)
system.addforcegravity(-g*N.y)

x1 = BodyA.pCM.dot(N.x)
y1 = BodyA.pCM.dot(N.y)

f,ma = system.getdynamics()
func = system.state_space_post_invert(f,ma)
#from pynamics.integrator import RK4,DoPri
#integrator = RK4(func,ini,t)
#integrator = DoPri(func,ini,t)
#states = integrator.run()
states=pynamics.integration.integrate_odeint(func,ini,t,rtol=1e-12,atol=1e-12,hmin=1e-14, args=({'constants':system.constant_values},))


KE = system.get_KE()
PE = system.getPEGravity(pNA) - system.getPESprings() - 1/2* k*(stretch)**2
    
output = Output([x1,y1,q,KE-PE],system)
y = output.calc(states)

plt.figure(1)
plt.plot(y[:,0],y[:,1])
plt.axis('equal')

plt.figure(2)
plt.plot(y[:,3])

#plt.figure(3)
#plt.plot(t,y[:,0])
#plt.show()
