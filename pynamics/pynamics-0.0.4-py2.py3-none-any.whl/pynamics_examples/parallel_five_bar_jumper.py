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

lO = Constant(.5,'lO',system)
lA = Constant(1,'lA',system)
lB = Constant(1,'lB',system)
lC = Constant(1,'lC',system)
lD = Constant(1,'lD',system)

mO = Constant(10,'mO',system)
mA = Constant(1,'mA',system)
mB = Constant(1,'mB',system)
mC = Constant(1,'mC',system)
mD = Constant(1,'mD',system)

I_xx = Constant(1,'I_xx',system)
I_yy = Constant(1,'I_yy',system)
I_zz = Constant(1,'I_zz',system)

g = Constant(9.81,'g',system)
b = Constant(1e0,'b',system)
k = Constant(1e3,'k',system)

tinitial = 0
tfinal = 10
tstep = .01
t = numpy.r_[tinitial:tfinal:tstep]

preload1 = Constant(0*pi/180,'preload1',system)
preload2 = Constant(0*pi/180,'preload2',system)
preload3 = Constant(-180*pi/180,'preload3',system)
preload4 = Constant(0*pi/180,'preload4',system)
preload5 = Constant(180*pi/180,'preload5',system)

x,x_d,x_dd = Differentiable('x',system)
y,y_d,y_dd = Differentiable('y',system)
qO,qO_d,qO_dd = Differentiable('qO',system)
qA,qA_d,qA_dd = Differentiable('qA',system)
qB,qB_d,qB_dd = Differentiable('qB',system)
qC,qC_d,qC_dd = Differentiable('qC',system)
qD,qD_d,qD_dd = Differentiable('qD',system)

initialvalues = {}
initialvalues[x]=0
initialvalues[x_d]=0
initialvalues[y]=20
initialvalues[y_d]=0
initialvalues[qO]=0*pi/180
initialvalues[qO_d]=0*pi/180
initialvalues[qA]=-60*pi/180
initialvalues[qA_d]=0*pi/180
initialvalues[qB]=-150*pi/180
initialvalues[qB_d]=0*pi/180
initialvalues[qC]=-120*pi/180
initialvalues[qC_d]=0*pi/180
initialvalues[qD]=-30*pi/180
initialvalues[qD_d]=0*pi/180

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

N = Frame('N')
O = Frame('O')
A = Frame('A')
B = Frame('B')
C = Frame('C')
D = Frame('D')

system.set_newtonian(N)
O.rotate_fixed_axis_directed(N,[0,0,1],qO,system)
A.rotate_fixed_axis_directed(N,[0,0,1],qA,system)
B.rotate_fixed_axis_directed(N,[0,0,1],qB,system)
C.rotate_fixed_axis_directed(N,[0,0,1],qC,system)
D.rotate_fixed_axis_directed(N,[0,0,1],qD,system)

pOcm=x*N.x+y*N.y
pOA = pOcm+lO/2*O.x
pOC = pOcm-lO/2*O.x
pAB = pOA+lA*A.x
pBtip = pAB + lB*B.x
vBtip = pBtip.time_derivative(N,system)

pCD = pOC + lC*C.x
pDtip = pCD + lD*D.x
vDtip = pDtip.time_derivative(N,system)

pAcm=pOA+lA/2*A.x
pBcm=pAB+lB/2*B.x
pCcm=pOC+lC/2*C.x
pDcm=pCD+lD/2*D.x

wOA = O.getw_(A)
wAB = A.getw_(B)
wOC = O.getw_(C)
wCD = C.getw_(D)
wBD = B.getw_(D)

I = Dyadic.build(A,I_xx,I_yy,I_zz)

BodyO = Body('BodyO',O,pOcm,mO,I,system)
BodyA = Body('BodyA',A,pAcm,mA,I,system)
BodyB = Body('BodyB',B,pBcm,mB,I,system)
BodyC = Body('BodyC',C,pCcm,mC,I,system)
BodyD = Body('BodyD',D,pDcm,mD,I,system)

#ParticleO = Particle(pOcm,mO,'ParticleO',system)
#ParticleA = Particle(pAcm,mA,'ParticleA',system)
#ParticleB = Particle(pBcm,mB,'ParticleB',system)
#ParticleC = Particle(pCcm,mC,'ParticleC',system)
#ParticleD = Particle(pDcm,mD,'ParticleD',system)

system.addforce(-b*wOA,wOA)
system.addforce(-b*wAB,wAB)
system.addforce(-b*wOC,wOC)
system.addforce(-b*wCD,wCD)
system.addforce(-b*wBD,wBD)

stretch = -pBtip.dot(N.y)
stretch_s = (stretch+abs(stretch))
on = stretch_s/(2*stretch+1e-10)
system.add_spring_force1(1e4,-stretch_s*N.y,vBtip)
system.addforce(-1e2*vBtip*on,vBtip)

v = pBtip-pDtip
l = (v.dot(v))**.5
n = 1/l*v
system.add_spring_force1(1e5,l*n,vBtip)
system.add_spring_force1(1e5,-l*n,vDtip)
system.addforce(-b*(vBtip-vDtip),vBtip)
system.addforce(b*(vBtip-vDtip),vDtip)

system.add_spring_force1(k,(qA-qO-preload1)*N.z,wOA)
system.add_spring_force1(k,(qB-qA-preload2)*N.z,wAB)
system.add_spring_force1(k,(qC-qO-preload3)*N.z,wOC)
system.add_spring_force1(k,(qD-qC-preload4)*N.z,wCD)
system.add_spring_force1(k,(qD-qB-preload5)*N.z,wBD)

system.addforcegravity(-g*N.y)

eq = []
eq.append(pOcm.dot(N.y)-initialvalues[y])
eq.append(pOcm.dot(N.x)-initialvalues[x])
eq.append(qO-initialvalues[qO])
#eq.append((pBtip-pDtip).dot(N.x))
#eq.append((pBtip-pDtip).dot(N.y))


#eq.append(pBtip.dot(N.y))
#eq.append(pDtip.dot(N.y))

eq_d= [system.derivative(item) for item in eq]
eq_dd= [system.derivative(item) for item in eq_d]

f,ma = system.getdynamics()
func1 = system.state_space_post_invert2(f,ma,eq_dd,eq_d,eq,constants = system.constant_values)
states=pynamics.integration.integrate_odeint(func1,ini,t,rtol=1e-3,atol=1e-3,args=({'constants':{},'alpha':1e2,'beta':1e1},))

plt.plot()

KE = system.get_KE()
PE = system.getPEGravity(0*N.x) - system.getPESprings()


energy = Output([KE-PE])
energy.calc(states)
energy.plot_time()


points = [pDtip,pCD,pOC,pOA,pAB,pBtip]
points = [item2 for item in points for item2 in [item.dot(N.x),item.dot(N.y)]]
points = Output(points)
y = points.calc(states)
y = y.reshape((-1,6,2))
plt.figure()
for item in y[::30]:
    plt.plot(*(item.T))

#eq2 = []
#eq2.append((pBtip-pDtip).dot(N.x))
#eq2.append((pBtip-pDtip).dot(N.y))
#eq2.append((pBtip).dot(N.y))
#eq2.append((pBtip).dot(N.x))

#eq2_d= [system.derivative(item) for item in eq2]
#eq2_dd= [system.derivative(item) for item in eq2_d]

#eq2_active = []
#eq2_active.append(1)
#eq2_active.append(1)
#eq2_active.append(0-pBtip.dot(N.y))
#eq2_active.append(0-pBtip.dot(N.x))
#eq2_active = [(item+abs(item)) for item in eq2_active]
#
ini = states[-1]
ini[2] = 0
ini[7:] = 0
#ini[7] = 10
ini = list(ini)

func1 = system.state_space_post_invert(f,ma,constants = system.constant_values)
states2=pynamics.integration.integrate_odeint(func1,ini,numpy.r_[tinitial:tfinal:1/30],hmax = .01,rtol=1e-3,atol=1e-3,args=({'constants':{},'alpha':1e3,'beta':1e1},))
y = points.calc(states2)
y = y.reshape((-1,6,2))
plt.figure()
for item in y[::25]:
    plt.plot(*(item.T))
plt.axis('equal')

energy = Output([KE-PE])
energy.calc(states2)
energy.plot_time()

tip = Output([pBtip.dot(N.y),stretch])
tip.calc(states2)
tip.plot_time()

import os
import idealab_tools.makemovie
idealab_tools.makemovie.clear_folder()
folder = idealab_tools.makemovie.prep_folder()
f = plt.figure()
ax = f.add_subplot(1,1,1)
ax.axis('equal')

for ii,item in enumerate(y):
    [item.remove() for item in ax.lines]
    plt.plot(*(item.T),'ro-')
    ax.set_xlim((y[:,:,0].min(),y[:,:,0].max()))
    ax.set_ylim((y[:,:,1].min(),y[:,:,1].max()))
    plt.savefig(os.path.join(folder,'{0:04d}.png'.format(ii)))

idealab_tools.makemovie.render(image_name_format = '%04d.png')
idealab_tools.makemovie.clear_folder()
