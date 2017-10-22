'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2015-11-23

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
    
def condition_N_Mx_My (N_Ed=1*u.kN, N_Rd=1*u.kN, M_yEd=1*u.kNm, M_yRd=1*u.kNm, M_zEd=1*u.kNm, M_zRd=1*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_Rd) + abs(1.0*M_yEd) / (1.0*M_yRd) + abs(1.0*M_zEd) / (1.0*M_zRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='N_Ed / N_Rd + M_yEd / M_yRd + M_zEd / M_zRd = %s/%s + %s/%s + %s/%s = %s' % (abs(N_Ed), N_Rd, abs(M_yEd), M_yRd, abs(M_zEd), M_zRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.3) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)
    
def condition_V (V_Ed=1*u.kN, V_cRd=1*u.kN):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    try:
        condition_value = abs(1.0*V_Ed) / (1.0*V_cRd)
    except ZeroDivisionError:
        if abs(1.0*V_Ed) > 0*u.kN:
            condition_value = float('+inf')
        if abs(1.0*V_Ed) == 0*u.kN:
            condition_value = 0
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='V_Ed / V_cRd = %s/%s = %s' % (abs(V_Ed), V_cRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.17) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

# Test if main
if __name__ == '__main__':
    print 'section_capacity_conditions test'
    print '--------condition_N_Mx_My ()-----------'
    print condition_N_Mx_My (10*u.kN, 50*u.kN, 10*u.kNm, 80*u.kNm, 10*u.kNm, 125*u.kNm)
    print condition_N_Mx_My()[2] + ' from ' + condition_N_Mx_My()[3]
    print '--------condition_V ()-----------'
    print condition_V (0*u.kN, 0*u.kN)
    print condition_V()[2] + ' from ' + condition_V()[3]

