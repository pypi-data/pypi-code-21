# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:17:36 2017

@author: daukes
"""

def solid_parallelepiped(lx,ly=None,lz=None,density = 1,mass = None):

    ly = ly or lx
    lz = lz or lx
    
    volume = lx*ly*lz
    if not mass:
        mass = volume*density

    Ixx = mass*(ly**2+lz**2)/12
    Iyy = mass*(lx**2+lz**2)/12
    Izz = mass*(lx**2+ly**2)/12

    return (Ixx,Iyy,Izz),mass,volume

def solid_ellipsoid(lx,ly=None,lz=None,density = 1,mass = None):
    import math

    ly = ly or lx
    lz = lz or lx

    volume = 4/3*math.pi*lx*ly*lz
    if not mass:
        mass = volume*density

    Ixx = mass*(ly**2+lz**2)/5
    Iyy = mass*(lx**2+lz**2)/5
    Izz = mass*(lx**2+ly**2)/5

    return (Ixx,Iyy,Izz),mass,volume

def shift_from_cm(I_cm,cm,p,m,frame):
    import pynamics.dyadic
    unit_dyadic = pynamics.dyadic.Dyadic.unit(frame)
    rcmp = p-cm
    I = I_cm+m*(unit_dyadic*(rcmp.dot(rcmp)) - pynamics.dyadic.Dyad(rcmp,rcmp))

    return I