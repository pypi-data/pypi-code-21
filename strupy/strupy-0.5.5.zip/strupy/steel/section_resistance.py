'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

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

gamm_M0=1.0

def paraminfo ():
    print gamm_M0
    
'''
The design tension resistance
'''
def N_tRd (A=10.0*u.cm2, f_y=355*u.MPa):
    N_tRd = A * f_y / gamm_M0
    return N_tRd.asUnit(u.kN)

'''
The design compression resistance
(class 4 is not supported)
'''
def N_cRd (A=10.0*u.cm2, f_y=355*u.MPa, compressionclass=3):
    if compressionclass in [1, 2, 3]:
        N_cRd = A * f_y / gamm_M0
    if compressionclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        A_ceff = rho * A
        N_cRd = A_ceff * f_y / gamm_M0
    return N_cRd.asUnit(u.kN)

def N_Rk (A=10.0*u.cm2, f_y=355*u.MPa, compressionclass=3):
    N_Rk = N_cRd (A, f_y, compressionclass) * gamm_M0 
    return N_Rk
       
'''
The design rcsistance for bending about one axis with the absence of shear
(class 4 is not supported)
'''   
def M_cRd (W_pl=10.0*u.cm3, W_el=5.0*u.cm3, f_y=355*u.MPa, bendingclass=3):
    if bendingclass in [1, 2]:
        M_cRd = W_pl * f_y / gamm_M0
    if bendingclass in [3]:
        M_cRd = W_el * f_y / gamm_M0
    if bendingclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        W_eff = rho * W_el
        M_cRd = W_eff * f_y / gamm_M0
    return M_cRd.asUnit(u.kNm)

def M_Rk (W_pl=10.0*u.cm3, W_el=5.0*u.cm3, f_y=355*u.MPa, bendingclass=3):
    M_Rk = M_cRd(W_pl, W_el, f_y, bendingclass) * gamm_M0
    return M_Rk
        
'''
The design plastic shear resistance
'''   
def V_cRd (A_v=10.0*u.cm2, chi_w=1.0, f_y=355*u.MPa):
    V_cRd = chi_w * A_v * (f_y / pow(3.0, 0.5)) / gamm_M0
    return V_cRd.asUnit(u.kN)

# Test if main
if __name__ == '__main__':
    print ('test sectionresistance')
    paraminfo()
    print (N_tRd())
    print (N_cRd())
    print (N_Rk())
    print (M_cRd())
    print (M_Rk())
    print (V_cRd())