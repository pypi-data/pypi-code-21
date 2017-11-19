'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-03-06

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://strupy.org/

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

from math import sqrt, pow

import strupy.units as u

def _findclass (value = 20, maxclassvalues=[20, 40, 50]):
    classlist = [1, 2, 3, 4]
    #print value
    #print maxclassvalues
    if (value <= maxclassvalues[0]):
        return classlist[0]
    if (maxclassvalues[0] < value <= maxclassvalues[1]):
        return classlist[1]
    if (maxclassvalues[1] < value <= maxclassvalues[2]):
        return classlist[2]
    if (maxclassvalues[2] < value):
        return classlist[3]

def get_parameters (figuregroup_id, f_y=230.0*u.MPa, h=100.0*u.mm, b=100.0*u.mm, t_w=20.0*u.mm, t_f=10.0*u.mm, r_a=5.0*u.mm, r_s=5.0*u.mm):
    epsilon = (235.0*u.MPa / f_y)**0.5
    if figuregroup_id == 10:
        return _group_10_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----I-beam
    if figuregroup_id == 10:
        return _group_10_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Double I-beam'
    if figuregroup_id == 11: 
        return _group_11_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Channel
    if figuregroup_id == 20:
        return _group_20_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Double channel flanges to flanges
    if figuregroup_id == 21:
        return _group_21_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Double angles legs back to back
    if figuregroup_id == 22:
        return _group_22_parameters(epsilon, h, b, t_w, t_f, r_a)   
    #----Angel
    if figuregroup_id == 30:
        return _group_30_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----#Double  angles in cruciform-like shape
    if figuregroup_id == 31:
        return _group_31_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Double angles legs back to back
    if figuregroup_id == 32:
        return _group_32_parameters(epsilon, h, b, t_w, t_f, r_a)   
    #----Rectangular bar
    if figuregroup_id == 40:
        return _group_40_parameters()
    #----Round bar
    if figuregroup_id == 41:
        return _group_41_parameters()
    #----Flat bar
    if figuregroup_id == 50:
        return _group_50_parameters(epsilon, h, b)
    #----Round hollow tube
    if figuregroup_id == 60:
        return _group_60_parameters(epsilon, h, t_f)
    #----Hexagonal hollow tube
    if figuregroup_id == 61:
        return _group_61_parameters(epsilon, h, t_f)
    #----Rectangular hollow tube
    if figuregroup_id == 62:
        return _group_62_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Structural tee
    if figuregroup_id == 70:
        return _group_70_parameters(epsilon, h, b, t_w, t_f, r_a)
    #----Tee cut from I-beam
    if figuregroup_id == 71:
        return _group_71_parameters(epsilon, h, b, t_w, t_f, r_a)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------Classification of cross sections acc 5.5 EN 1993-1-1---------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#----I-beam
def _group_10_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0 * r_a - 2*t_f # web
    c_f = b/2 - 0.5*t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(1)
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#----Double I-beam'
def _group_11_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0 * r_a - 2*t_f # web
    c_f = b/2 - 0.5*t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------    
#----Channel
def _group_20_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0 * r_a - 2*t_f # web
    c_f = b - t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------  
#----Double channel flanges to flanges
def _group_21_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0 * r_a - 2*t_f # web
    c_f = b/2 - t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------    
#----Double channel back to back
def _group_22_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm) :
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0 * r_a - 2*t_f # web
    c_f = b/2 - t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33*epsilon, 38*epsilon, 42*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72*epsilon, 83*epsilon, 124*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(1)
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#----Angel<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_30_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - r_a - t_f # web
    c_f = b - t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------   
#----#Double  angles in cruciform-like shape<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_31_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    return _group_30_parameters(epsilon, h/2, b/2, t_w, t_f, r_a)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------  
#----Double angles legs back to back<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_32_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    return _group_30_parameters(epsilon, h, b/2, t_w, t_f, r_a)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Rectangular bar<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_40_parameters():
    class_comp = 1
    class_bend_y = 1
    class_bend_z = 1
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Round bar<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_41_parameters():
    class_comp = 1
    class_bend_y = 1
    class_bend_z = 1
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Flat bar<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_50_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    h = h
    t = b
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---wall class
    class_comp.append(_findclass(h/t, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    alpha = 0.5
    #---wall class
    class_bend_y.append(_findclass(h/t, [9/alpha*epsilon, 10/alpha*epsilon, 21*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---wall class
    class_bend_z.append(1)
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------     
#----Round hollow tube
def _group_60_parameters(epsilon = 1.0, h=300*u.mm, t_f=10*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    d = h # tube diameter
    t = t_f # tube wall thickness
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---wall class
    class_comp.append(_findclass(d/t, [50*epsilon**2, 70*epsilon**2, 90*epsilon**2]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = class_comp
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = class_comp
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Hexagonal hollow tube<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Need to be checked
def _group_61_parameters(epsilon = 1.0, h=300*u.mm, t_f=10*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    b_s = h/2 # tube wall segment width 
    t = t_f # tube wall thickness
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---wall class
    class_comp.append(_findclass(b_s/t, [33*epsilon, 38*epsilon, 42*epsilon**2]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = class_comp
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = class_comp
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------    
#----Rectangular hollow tube
def _group_62_parameters(epsilon = 1.0, h=300.0*u.mm, b=100.0*u.mm, t_w=8.0*u.mm, t_f=10.0*u.mm, r_a=5.0*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - 2.0*t_f - 2.0*r_a # web
    c_f = b - 2.0*t_w - 2.0*r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [33.0*epsilon, 38.0*epsilon, 42.0*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [33.0*epsilon, 38.0*epsilon, 42.0*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [72.0*epsilon, 83.0*epsilon, 124.0*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [33.0*epsilon, 38.0*epsilon, 42.0*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(_findclass(c_w/t_w, [33.0*epsilon, 38.0*epsilon, 42.0*epsilon]))
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [72.0*epsilon, 83.0*epsilon, 124.0*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Structural tee
def _group_70_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    #---------------------------------------------------------------
    #-----------------------part dimension--------------------------
    #---------------------------------------------------------------    
    c_w = h - r_a - t_f # web
    c_f = b/2 - 0.5*t_w - r_a # flage
    #---------------------------------------------------------------
    #------------------compresion - x axis--------------------------
    #---------------------------------------------------------------
    class_comp = []
    #---web class
    class_comp.append(_findclass(c_w/t_w, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---flage class
    class_comp.append( _findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_comp = max(class_comp)
    #--------------------------------------------------------------
    #------------------bending - y axis----------------------------
    #---------------------------------------------------------------
    class_bend_y = []
    #---web class
    class_bend_y.append(_findclass(c_w/t_w, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---flage class
    class_bend_y.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_y = max(class_bend_y)
    #--------------------------------------------------------------
    #------------------bending - z axis----------------------------
    #---------------------------------------------------------------
    class_bend_z = []
    #---web class
    class_bend_z.append(1)
    #---flage class
    class_bend_z.append(_findclass(c_f/t_f, [9*epsilon, 10*epsilon, 14*epsilon]))
    #---geting max
    class_bend_z = max(class_bend_z)    
    #-----------------------
    return {'class_comp':class_comp, 'class_bend_y':class_bend_y, 'class_bend_z':class_bend_z, 'chi_wy':1.0 , 'chi_wz':1.0}
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------      
#----Tee cut from I-beam
def _group_71_parameters(epsilon = 1.0, h=300*u.mm, b=100*u.mm, t_w=8*u.mm, t_f=10*u.mm, r_a=5*u.mm):
    return _group_70_parameters(epsilon, h, b, t_w, t_f, r_a)
#------------------------------------------------------------------------------   
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------  
    
# Test if main
if __name__ == '__main__':
    print 'section_parameters test'
    print '-------------_group_id_parameters() test--------------------------'
    print 'IPE240', _group_10_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=120.0*u.mm, t_w=6.0*u.mm, t_f=9.8*u.mm, r_a=15.0*u.mm)
    print 'doubleIPE240', _group_11_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=120.0*u.mm, t_w=6.0*u.mm, t_f=9.8*u.mm, r_a=15.0*u.mm)
    print '---------------------------------------'
    print 'UPE240', _group_20_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=90.0*u.mm, t_w=7.0*u.mm, t_f=12.5*u.mm, r_a=15.0*u.mm)
    print 'doubleUPE240 flage to flage', _group_21_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=180.0*u.mm, t_w=7.0*u.mm, t_f=12.5*u.mm, r_a=15.0*u.mm)
    print 'doubleUPE240 back to back', _group_22_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=180.0*u.mm, t_w=7.0*u.mm, t_f=12.5*u.mm, r_a=15.0*u.mm)
    print '---------------------------------------'
    print 'angel L60x60x5 ', _group_30_parameters(epsilon = (235.0/355.0)**0.5, h=60.0*u.mm, b=60.0*u.mm, t_w=5.0*u.mm, t_f=5.0*u.mm, r_a=8.0*u.mm)
    print 'double L60x60x5 angles in cruciform-like shape ', _group_31_parameters(epsilon = (235.0/355.0)**0.5, h=120.0*u.mm, b=120.0*u.mm, t_w=5.0*u.mm, t_f=5.0*u.mm, r_a=8.0*u.mm)
    print 'double L60x60x5 angles Back to Back ', _group_32_parameters(epsilon = (235.0/355.0)**0.5, h=60.0*u.mm, b=120.0*u.mm, t_w=5.0*u.mm, t_f=5.0*u.mm, r_a=8.0*u.mm)
    print '---------------------------------------'
    print 'Rectangular bar ', _group_40_parameters()
    print 'Round bar ', _group_41_parameters()
    print '---------------------------------------'
    print 'flat bar ', _group_50_parameters(epsilon = (235.0/355.0)**0.5, h=50.0*u.mm, b=5.0*u.mm)
    print '---------------------------------------'
    print 'hollow tube  ', _group_60_parameters(epsilon = (235.0/355.0)**0.5, h=300*u.mm, t_f=7*u.mm)
    print 'hexagonal tube  ', _group_61_parameters(epsilon = (235.0/355.0)**0.5, h=300.0*u.mm, t_f=7.0*u.mm)
    print 'Rectangular hollow tube', _group_62_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=250.0*u.mm, t_w=7.0*u.mm, t_f=7.0*u.mm, r_a=15.0*u.mm)
    print '---------------------------------------'
    print 'Structural tee', _group_70_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=250.0*u.mm, t_w=7.0*u.mm, t_f=7.0*u.mm, r_a=15.0*u.mm)
    print 'Tee cut from I-beam', _group_71_parameters(epsilon = (235.0/355.0)**0.5, h=240.0*u.mm, b=250.0*u.mm, t_w=7.0*u.mm, t_f=7.0*u.mm, r_a=15.0*u.mm)
    print '----------------get_parameters(id) test-----------------------'
    print get_parameters(10)
    print get_parameters(11)
    print '---------------------------------------'
    print get_parameters(20)
    print get_parameters(21)
    print get_parameters(22)
    print '---------------------------------------'
    print get_parameters(30)
    print get_parameters(31)
    print get_parameters(32)
    print '---------------------------------------'
    print get_parameters(40)
    print get_parameters(41)
    print '---------------------------------------'
    print get_parameters(50)
    print '---------------------------------------'
    print get_parameters(60)
    print get_parameters(61)
    print get_parameters(62)
    print '---------------------------------------'
    print get_parameters(70)
    print get_parameters(71)
    print '---------------------------------------'
    print 'Test all from datatabase'
    from SteelSection import SteelSection
    sec = SteelSection()
    databasetest = True
    if databasetest:
        for i in sec._SteelSection__base.get_database_sectionlist():
            sec.set_sectionfrombase(i)
            print i, sec._parameters_data, sec.steelgrade
    print '---------------------------------------'
    print 'Test one from datatabase'
    steel = 'S235'
    sectname = 'IPE A 300'
    sec.set_sectionfrombase(sectname)
    sec.set_steelgrade(steel)
    print sec.sectname, sec._parameters_data, sec.steelgrade
    print '---------------------------------------'