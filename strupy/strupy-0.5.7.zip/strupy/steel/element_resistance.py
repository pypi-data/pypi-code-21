'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 (alpha) date 2017-11-19

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

import math

import strupy.units as u

gamm_M1=1.0
    
'''
------------------------------------------------------------------------------
------------------------------------------------------------------------------
----------------- UNIFORM MEMBER IN COMPRSSION acc. 6.3.1 EC3 ----------------
------------------------------------------------------------------------------
------------------------------------------------------------------------------
'''

'''
Buckling curve type - acc. Table 6.2 EC3
'''
def curve():
    return 'a'

'''
Buckling imperfection factor - acc. Table 6.1 EC3
'''
def alpha(curve=curve()):
    if curve == 'a0':
        return 0.13
    if curve == 'a':
        return 0.21
    if curve == 'b':
        return 0.34
    if curve == 'c':
        return 0.49
    if curve == 'd':
        return 0.76
        
'''
Slenderness value to determine the relative slendemcss - acc. (6.51) EC3
'''
def lambda_l(f_y=355.0*u.MPa, E=210.0*u.GPa):
    return math.pi * (E / f_y)**0.5

'''
Elastic buckling load of undeflected compression member
(class 4 is not supported)
'''
def N_cr (I=300.0*u.cm4, L_cr=4.0*u.m, E=210.0*u.GPa, compressionclass=3):
    if compressionclass in [1, 2, 3]:
        N_cr = math.pi**2 * E * I / L_cr**2
    if compressionclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        I_ceff = rho * I
        N_cr = math.pi**2 * E * I_ceff / L_cr**2
    return N_cr.asUnit(u.kN)

'''
Relative slenderness - acc. (6.51) EC3
(class 4 is not supported)
'''
def lambda_rel(L_cr=1.0*u.m, i=45.0*u.mm, compressionclass=3): 
    if compressionclass in [1, 2, 3]:
        lambda_rel = (L_cr / i) / lambda_l() #!!!!!!! lambda() zalezy od fd poprawic
    if compressionclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        #A_ceff = rho * A
        #lambda_rel = (A_ceff / A)**0.5 * (L_cr / i) / lambda_l()
        lambda_rel = (L_cr / i) / lambda_l() * rho**-1 #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return lambda_rel

'''
Reduction factor for relevant buckling mode - acc. (6.49) EC3
'''
def hi(lambda_rel=lambda_rel(), alpha=alpha()): # - buckling reduction factor for y
    phi = 0.5 * (1.0 + alpha * (lambda_rel - 0.2) + lambda_rel**2)
    hi = 1.0 / (phi + (phi**2 - lambda_rel**2)**0.5)
    hi = min(hi, 1.0)
    return hi

'''
Buckling resistance of compression member  - acc. (6.48) EC3
(class 4 is not supported)
'''
def N_bRd (A=10.0*u.cm2, f_y=355*u.MPa, hi=hi(), compressionclass=3):
    if compressionclass in [1, 2, 3]:
        N_bRd = hi * A * f_y / gamm_M1
    if compressionclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        A_ceff = rho * A
        N_bRd = hi * A_ceff * f_y / gamm_M1
    return N_bRd.asUnit(u.kN)
    
    
'''
------------------------------------------------------------------------------
------------------------------------------------------------------------------
----------------- UNIFORM MEMBER IN BENDING acc. 6.3.2 EC3 -------------------
------------------------------------------------------------------------------
------------------------------------------------------------------------------
'''

'''
Lateral torsional buckling curve type - acc. Table 6.4 EC3
'''
def curve_LT():
    return 'a'

'''
Lateral torsional buckling imperfection factor - acc. Table 6.3 EC3
'''
def alpha_LT(curve_LT=curve_LT()):
    if curve_LT == 'a':
        return 0.21
    if curve_LT == 'b':
        return 0.34
    if curve_LT == 'c':
        return 0.49
    if curve_LT == 'd':
        return 0.76

'''
Elastic critical moment for lateral-torsional buckling
(class 4 is not supported)
'''
def M_cr(figuregroup_id=10, I_z=100.0*u.cm4, I_t=100.0*u.cm4, I_w=100.0*u.cm**6, L_LT=3.0*u.m, E=210.0*u.GPa, G=210.0*u.GPa):
    '''   
    if figuregroup_id == 10:
        z_g=20.0*u.cm,
        k_z=1.0
        k_w=1.0
        C_1=1.127
        C_2=0.454           
        B = ( (k_z/k_w)**2*I_w/I_z + (k_z*L_LT)**2*G*I_t/(math.pi**2*E*I_z) + (C_2*z_g)**2 )**0.5
        M_cr = ( C_1*(math.pi**2 * E * I_z)/(k_z * L_LT)**2 * (B - C_2*z_g) ).asUnit(u.kNm)
        Mcr = math.pi/(L_LT) * (E*I_z*G*I_t)**0.5 * (1 + (math.pi**2*E*I_w)/(L_LT**2*G*I_t))**0.5 * 1.0 / 1.0
        print '\n',Mcr.asUnit(u.kNm), '<<<<<<222'
    else:
        M_cr = 0.0*u.kNm
    '''
    m = 0.9
    M_cr = math.pi/(L_LT) * (E*I_z*G*I_t)**0.5 * (1 + (math.pi**2*E*I_w)/(L_LT**2*G*I_t))**0.5 * 1.0 / m
    return M_cr.asUnit(u.kNm)

'''
Relative slenderness - acc. (6.56) EC3
(class 4 is not supported)
'''
def lambda_relLT(M_cr=M_cr(), W_pl=10.0*u.cm3, W_el=5.0*u.cm3, f_y=355*u.MPa, bendingclass=3):
    if bendingclass in [1, 2]:
        lambda_relLT = (W_pl * f_y / M_cr )**0.5
    if bendingclass in [3]:
        lambda_relLT = (W_el * f_y / M_cr )**0.5
    if bendingclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        W_ceff = rho * W_el
        lambda_relLT = (W_ceff * f_y / M_cr )**0.5
    return lambda_relLT

'''
Reduction factor for lateral-torsional buckling - acc. (6.56) EC3
'''
def hi_LT(lambda_relLT=lambda_relLT(), alpha_LT=alpha_LT()):
    phi_LT= 0.5 * (1.0 + alpha_LT * (lambda_relLT - 0.2) + lambda_relLT**2)
    hi_LT = 1.0 / (phi_LT + (phi_LT**2 - lambda_relLT**2)**0.5)
    hi_LT = min(hi_LT, 1.0)
    return hi_LT

'''
Lateral torsional buckling resistance of bending member  - acc. (6.55) EC3
(class 4 is not supported)
'''   
def M_bRd (W_pl=10.0*u.cm3, W_el=5.0*u.cm3, hi_LT=hi_LT(), f_y=355*u.MPa, bendingclass=3):
    if bendingclass in [1, 2]:
        M_bRd = hi_LT * W_pl * f_y / gamm_M1
    if bendingclass in [3]:
        M_bRd = hi_LT * W_el * f_y / gamm_M1
    if bendingclass in [4]:
        print '!!!! class 4 !!!!!'
        rho = 0.5 #<<<<<<<<<<<<!!!!!!!!!!
        W_eff = rho * W_el
        M_bRd = hi_LT * W_eff * f_y / gamm_M1
    return M_bRd.asUnit(u.kNm)

# Test if main
if __name__ == '__main__':
    print ('test elementresistance')
    print '------UNIFORM MEMBER IN COMPRSSION acc. 6.3.1 EC3-----------------'
    print (curve())
    print (alpha())
    print (lambda_l())
    print (N_cr())
    print (lambda_rel())
    print (hi())
    print (N_bRd())
    print '-------UNIFORM MEMBER IN BENDING acc. 6.3.2 EC3----------------'
    print (curve_LT())
    print (alpha_LT())
    print (M_cr())
    print (lambda_relLT())
    print (hi_LT())
    print (M_bRd())