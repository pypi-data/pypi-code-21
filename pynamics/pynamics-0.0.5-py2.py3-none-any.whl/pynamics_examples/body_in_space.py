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
from pynamics.output import Output,PointsOutput
from pynamics.particle import Particle
import pynamics.integration
pynamics.script_mode = True

#import logging
#pynamics.logger.setLevel(logging.ERROR)
#pynamics.system.logger.setLevel(logging.ERROR)

import numpy
import matplotlib.pyplot as plt
plt.ion()
from math import pi
system = System()

g = Constant(9.81,'g',system)

tinitial = 0
tfinal = 5
tstep = 1/30
t = numpy.r_[tinitial:tfinal:tstep]

Differentiable('qA')
Differentiable('qB')
Differentiable('qC')

Differentiable('x')
Differentiable('y')
Differentiable('z')

Constant(1,'mC')
Constant(2,'Ixx')
Constant(3,'Iyy')
Constant(1,'Izz')

initialvalues = {}
initialvalues[qA]=0*pi/180
initialvalues[qA_d]=7
initialvalues[qB]=0*pi/180
initialvalues[qB_d]=.2
initialvalues[qC]=0*pi/180
initialvalues[qC_d]=.2

initialvalues[x]=0
initialvalues[x_d]=0
initialvalues[y]=0
initialvalues[y_d]=0
initialvalues[z]=0
initialvalues[z_d]=0

statevariables = system.get_state_variables()
ini = [initialvalues[item] for item in statevariables]

Frame('N')
Frame('A')
Frame('B')
Frame('C')

system.set_newtonian(N)
A.rotate_fixed_axis_directed(N,[1,0,0],qA,system)
B.rotate_fixed_axis_directed(A,[0,1,0],qB,system)
C.rotate_fixed_axis_directed(B,[0,0,1],qC,system)

pCcm=x*N.x+y*N.y+z*N.z
wNC = N.getw_(C)

IC = Dyadic.build(C,Ixx,Iyy,Izz)

Body('BodyC',C,pCcm,mC,IC)

system.addforcegravity(-g*N.y)

points = [0*N.x,pCcm]

ang = [wNC.dot(C.x),wNC.dot(C.y),wNC.dot(C.z)]

f,ma = system.getdynamics()
func1 = system.state_space_post_invert(f,ma)
states=pynamics.integration.integrate_odeint(func1,ini,t, args=({'constants':system.constant_values},))

output = Output(ang,system)
output.calc(states)
output.plot_time()

po = PointsOutput(points,system)
po.calc(states)
