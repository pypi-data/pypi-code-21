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

#import sympy
import numpy
import matplotlib.pyplot as plt
plt.ion()
from math import pi
system = System()

error = 1e-12

lA = Constant(7.5/100,'lA',system)
lB = Constant(20/100,'lB',system)

mA = Constant(10/1000,'mA',system)
mB = Constant(100/1000,'mB',system)

g = Constant(9.81,'g',system)

tinitial = 0
tfinal = 10
tstep = .001
t = numpy.r_[tinitial:tfinal:tstep]


Ixx_A = Constant(50/1000/100/100,'Ixx_A',system)
Iyy_A = Variable('Iyy_A')
Izz_A = Variable('Izz_A')
Ixx_B = Constant(2500/1000/100/100,'Ixx_B',system)
Iyy_B = Constant(500/1000/100/100,'Iyy_B',system)
Izz_B = Constant(2000/1000/100/100,'Izz_B',system)

qA,qA_d,qA_dd = Differentiable('qA',system)
qB,qB_d,qB_dd = Differentiable('qB',system)

initialvalues = {}
initialvalues[qA]=90*pi/180
initialvalues[qA_d]=0*pi/180
initialvalues[qB]=.5*pi/180
initialvalues[qB_d]=0*pi/180

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

N = Frame('N')
A = Frame('A')
B = Frame('B')

system.set_newtonian(N)
A.rotate_fixed_axis_directed(N,[1,0,0],qA,system)
B.rotate_fixed_axis_directed(A,[0,0,1],qB,system)

pNA=0*N.x

pAcm=pNA-lA*A.y
pBcm=pNA-lB*A.y

wNA = N.getw_(A)
wAB = A.getw_(B)

IA = Dyadic.build(A,Ixx_A,Iyy_A,Izz_A)
IB = Dyadic.build(B,Ixx_B,Iyy_B,Izz_B)

BodyA = Body('BodyA',A,pAcm,mA,IA,system)
BodyB = Body('BodyB',B,pBcm,mB,IB,system)

#ParticleA = Particle(pAcm,mA,'ParticleA',system)
#ParticleB = Particle(pBcm,mB,'ParticleB',system)
#ParticleC = Particle(pCcm,mC,'ParticleC',system)

system.addforcegravity(-g*N.y)

x1 = BodyA.pCM.dot(N.x)
y1 = BodyA.pCM.dot(N.y)
x2 = BodyB.pCM.dot(N.x)
y2 = BodyB.pCM.dot(N.y)
    
f,ma = system.getdynamics()

#import sympy
#eq = sympy.Matrix(f)-sympy.Matrix(ma)
#sol = sympy.solve(eq,(qA_dd,qB_dd))
#
#qadd = sol[qA_dd]
#qbdd = sol[qB_dd]
#
#(Ixx_B*qA_d*qB_d*sin(2*qB) - Iyy_B*qA_d*qB_d*sin(2*qB) - g*lA*mA*sin(qA) - g*lB*mB*sin(qA))/(Ixx_A - Ixx_B*sin(qB)**2 + Ixx_B + Iyy_B*sin(qB)**2 + lA**2*mA + lB**2*mB)
func1 = system.state_space_post_invert(f,ma)
states=pynamics.integration.integrate_odeint(func1,ini,t,rtol=error,atol=error, args=({'constants':system.constant_values},))

KE = system.get_KE()
PE = system.getPEGravity(pNA) - system.getPESprings()

output = Output([x1,y1,x2,y2,KE-PE,qA,qB],system)
y = output.calc(states)

plt.figure(1)
plt.plot(y[:,0],y[:,1])
plt.plot(y[:,2],y[:,3])
plt.axis('equal')

plt.figure(2)
plt.plot(y[:,4])

plt.figure(3)
plt.plot(t,y[:,6:]*180/pi)
plt.show()
