# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import sympy
from sympy import cos, sin
from pynamics.vector import Vector
import pynamics

def build_fixed_axis(axis,q,frame,sys = None):
    sys = sys or pynamics.get_system()

    axis = sympy.Matrix(axis)
    l_2 = axis.dot(axis)
    axis = axis/(l_2**.5)
    
    e0 = axis[0]        
    e1 = axis[1]        
    e2 = axis[2]        
    
    c = axis * axis.T
    a = (sympy.Matrix.eye(3) - c) * cos(q)
    b = sympy.Matrix([[0, -e2, e1], [e2, 0, -e0],[-e1, e0, 0]]) * sin(q)
    R = a + b + c 
    R = R.T

    w = sys.derivative(q)
    w_ = w*Vector({frame:axis})
    return R,w_,axis

def w_from_der(R,f,sys):
    
    Rxx = R[0,0]
    Rxy = R[0,1]
    Rxz = R[0,2]

    Ryx = R[1,0]
    Ryy = R[1,1]
    Ryz = R[1,2]

    Rzx = R[2,0]
    Rzy = R[2,1]
    Rzz = R[2,2]
    
    Rxx_d = sys.derivative(R[0,0])
    Rxy_d = sys.derivative(R[0,1])
    Rxz_d = sys.derivative(R[0,2])

    Ryx_d = sys.derivative(R[1,0])
    Ryy_d = sys.derivative(R[1,1])
    Ryz_d = sys.derivative(R[1,2])

    Rzx_d = sys.derivative(R[2,0])
    Rzy_d = sys.derivative(R[2,1])
    Rzz_d = sys.derivative(R[2,2])
    
    wx = Rxz*Rxy_d + Ryz*Ryy_d + Rzz*Rzy_d
    wy = Rxx*Rxz_d + Ryx*Ryz_d + Rzx*Rzz_d
    wz = Rxy*Rxx_d + Ryy*Ryx_d + Rzy*Rzx_d
    
    w = wx*f.x + wy*f.y + wz*f.z
    return w

class Rotation(object):
    def __init__(self,f1,f2,R,w_):
        self.f1 = f1
        self.f2 = f2
        self._R = R
        self.w_ = w_
 
    def to_other(self,f):
        if f==self.f1:
            return self._R
        elif f==self.f2:
            return self._R.T
        else:
            raise(Exception('frame not in this rotation'))

    def w__from(self,f):
        if f==self.f1:
            return self.w_
        elif f==self.f2:
            return -self.w_
        else:
            raise(Exception('frame not in this rotation'))

    def other(self,f):
        if f==self.f1:
            return self.f2
        elif f==self.f2:
            return self.f1
        else:
            raise(Exception('frame not in this rotation'))
            
    @classmethod
    def build_fixed_axis(cls,f1,f2,axis,q,sys = None):
        R,w,fixedaxis = build_fixed_axis(axis,q,f1,sys)
        return cls(f1,f2,R,w)
        
    def w_from_der(self,sys):
        return w_from_der(self.R.T,self.f2,sys)

        