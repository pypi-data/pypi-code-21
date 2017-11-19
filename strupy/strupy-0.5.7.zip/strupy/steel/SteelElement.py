'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 (alpha) date 2017-11-17

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://struthon.org/

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

import strupy.units as u

from SteelSection import SteelSection

import element_resistance as element_resistance

class SteelElement(SteelSection):

    def __init__(self):
        print ('SteelElement init')
        SteelSection.__init__(self)   
        #---
        self.Mark = 'Nonamed'     
        #---
        self.L = 10.5*u.m
        self.k_ycr = 1.0 # -effective length factors for y buckling
        self.k_zcr = 1.0 # -effective length factors for z buckling
        self.k_LT = 1.0 # -effective length factors for lateral-torsional buckling
        #---
        self.comment = 'No commenent'
        #---
        self.set_sectionfrombase()
    
    #----------------------------------------------

    @property
    def L_ycr(self): # -effective length for y buckling
        return self.k_ycr * self.L
    @property
    def L_zcr(self): # -effective length for z buckling
        return self.k_zcr * self.L
    @property
    def L_LT(self): # -effective length for lateral-torsional buckling
        return self.k_LT * self.L

    #----------------------------------------------
    @property
    def curve(self): # - buckling imperfection curve
        return element_resistance.curve()
    @property
    def curve_LT(self): # - lateral-torsional buckling imperfection curve
        return element_resistance.curve_LT()
    
    @property
    def alpha(self): # - buckling imperfection factor
        return element_resistance.alpha(self.curve)
    @property
    def alpha_LT(self): # - lateral-torsional buckling imperfection factor
        return element_resistance.alpha_LT(self.curve_LT)
        
    #----------------------------------------------
    
    @property
    def lambda_y(self): # - buckling imperfection factor for y
        return self.L_ycr / self.i_y
    @property
    def lambda_z(self): # - buckling imperfection factor for z
        return self.L_zcr / self.i_z

    #----------------------------------------------
    
    @property
    def lambda_l(self): # - slenderness value to determine the relative slendemcss
        return element_resistance.lambda_l(self.f_y, self.E)

    #----------------------------------------------

    @property
    def lambda_yrel(self): # - relative slendemcss for y buckling
        return element_resistance.lambda_rel(self.L_ycr, self.i_y, self.class_comp)
    @property
    def lambda_zrel(self): # - relative slendemcss for z buckling
        return element_resistance.lambda_rel(self.L_zcr, self.i_z, self.class_comp)
    @property
    def lambda_relLT(self): # - relative slenderness for lateral-torsional buckling
        return element_resistance.lambda_relLT(self.M_cr, self.W_ply, self.W_ely, self.f_y, self.class_bend_y)

    #----------------------------------------------
        
    @property
    def hi_y(self): # - buckling reduction factor for y
        hi_y = element_resistance.hi(self.lambda_yrel, self.alpha)
        #return round(hi_y.asNumber(), 2)
        return hi_y
    @property
    def hi_z(self): # - buckling reduction factor for z
        hi_z = element_resistance.hi(self.lambda_zrel, self.alpha)
        #return round(hi_z.asNumber(), 2)
        return hi_z 
    @property
    def hi_LT(self): # - reduction factor for lateral-torsional buckling
        hi_LT = element_resistance.hi_LT(self.lambda_relLT, self.alpha_LT)
        #return round(hi_LT.asNumber(), 2) 
        return hi_LT

    #----------------------------------------------

    @property
    def N_ycr(self): # - buckling force for y
        return element_resistance.N_cr(self.I_y, self.L_ycr, self.E, self.class_comp)
    @property
    def N_zcr(self): # - buckling force for z
        return element_resistance.N_cr(self.I_z, self.L_zcr, self.E, self.class_comp) 
    @property
    def M_cr(self): # - lateral-torsional buckling moment
        return element_resistance.M_cr(self.figuregroup_id, self.I_z, self.I_t, self.I_w, L_LT=self.L_LT, E=self.E, G=self.G)
        
    #----------------------------------------------

    @property
    def N_ybRd(self): # - buckling resistance for y
        return element_resistance.N_bRd(self.A, self.f_y, self.hi_y, self.class_comp)  
    @property
    def N_zbRd(self): # - buckling resistance for z
        return element_resistance.N_bRd(self.A, self.f_y, self.hi_z, self.class_comp)
    @property
    def N_bRd(self): # - minimun od buckling resistance for z and y
        return min(self.N_ybRd, self.N_zbRd)
    
    @property
    def M_bRd(self): # - lateral torsional buckling resistance of bending member
        return element_resistance.M_bRd(self.W_ply, self.W_ely, self.hi_LT, self.f_y, self.class_bend_y)
        
    #----------------------------------------------        
    
    def __str__(self):
        return 'element string .......'
        
# Test if main
if __name__ == '__main__':
    print ('test SteelElement')
    element=SteelElement()
    element.set_sectionfrombase('HE 240 B')
    element.set_steelgrade('S355')
    element.L = 6.3*u.m
    #-----------
    print element.sectname
    print element.steelgrade
    print ('---------Element buckling --------')
    print 'L_ycr =', element.L_ycr
    print 'curve =', element.curve
    print 'alpha =', element.alpha
    print 'lambda_y =', element.lambda_y
    print 'L_zcr =', element.L_zcr
    print 'lambda_z =', element.lambda_z
    print 'lambda_l =', element.lambda_l
    print 'lambda_yrel =', element.lambda_yrel
    print 'lambda_zrel =', element.lambda_zrel
    print 'hi_yrel =', element.hi_y
    print 'hi_zrel =', element.hi_z
    print 'N_cRd =', element.N_cRd 
    print 'N_ycr =', element.N_ycr
    print 'N_zcr =', element.N_zcr
    print 'N_ybRd =', element.N_ybRd  
    print 'N_zbRd =', element.N_zbRd
    print 'N_bRd =', element.N_bRd    
    print ('---------Element lateral-torsional buckling --------')
    print 'L_LT =', element.L_LT
    print 'curve_LT =', element.curve_LT
    print 'alpha_LT =', element.alpha_LT
    print 'M_ycRd =', element.M_ycRd 
    print 'M_cr =', element.M_cr
    print 'lambda_relLT =', element.lambda_relLT
    print 'hi_LT =', element.hi_LT
    print 'M_bRd =', element.M_bRd