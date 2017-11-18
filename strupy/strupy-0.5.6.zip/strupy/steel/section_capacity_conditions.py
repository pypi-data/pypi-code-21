'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-11-17

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
import strupy.units as u

def condition_Nt(N_Ed=1.0*u.kN, N_tRd=5.0*u.kN):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_tRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='N_Ed / N_tRd  = %s/%s = %s' % (abs(N_Ed), N_tRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.5) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_Nc(N_Ed=1.0*u.kN, N_cRd=5.0*u.kN):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_cRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='N_Ed / N_cRd  = %s/%s = %s' % (abs(N_Ed), N_cRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.9) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_My(M_yEd=1.0*u.kNm, M_yRd=5.0*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*M_yEd) / (1.0*M_yRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='M_yEd / M_yRd = %s/%s = %s' %(abs(M_yEd), M_yRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.12) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_Mz(M_zEd=1.0*u.kNm, M_zRd=5.0*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*M_zEd) / (1.0*M_zRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='M_zEd / M_zRd = %s/%s = %s' %(abs(M_zEd), M_zRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.12) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_My_Mz(M_yEd=1*u.kNm, M_yRd=1*u.kNm, M_zEd=1*u.kNm, M_zRd=1*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*M_yEd) / (1.0*M_yRd) + abs(1.0*M_zEd) / (1.0*M_zRd)
    condition_text='M_yEd / M_yRd + M_zEd / M_zRd = %s/%s + %s/%s = %s' % (abs(M_yEd), M_yRd, abs(M_zEd), M_zRd, condition_value)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text += warning_text
    condition_is_from = '(6.3) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)
    
def condition_Nc_My_Mz(N_Ed=1*u.kN, N_cRd=0.9*u.kN, M_yEd=1*u.kNm, M_yRd=1*u.kNm, M_zEd=1*u.kNm, M_zRd=1*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_cRd) + abs(1.0*M_yEd) / (1.0*M_yRd) + abs(1.0*M_zEd) / (1.0*M_zRd)
    condition_text='N_Ed / N_cRd + M_yEd / M_yRd + M_zEd / M_zRd = %s/%s + %s/%s + %s/%s = %s' % (abs(N_Ed), N_cRd, abs(M_yEd), M_yRd, abs(M_zEd), M_zRd, condition_value)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text += warning_text
    condition_is_from = '(6.3) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_Nt_My_Mz(N_Ed=1*u.kN, N_tRd=0.9*u.kN, M_yEd=1*u.kNm, M_yRd=1*u.kNm, M_zEd=1*u.kNm, M_zRd=1*u.kNm):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_tRd) + abs(1.0*M_yEd) / (1.0*M_yRd) + abs(1.0*M_zEd) / (1.0*M_zRd)
    condition_text='N_Ed / N_tRd + M_yEd / M_yRd + M_zEd / M_zRd = %s/%s + %s/%s + %s/%s = %s' % (abs(N_Ed), N_tRd, abs(M_yEd), M_yRd, abs(M_zEd), M_zRd, condition_value)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text += warning_text
    condition_is_from = '(6.3) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)
    
def condition_V(V_Ed=1*u.kN, V_cRd=1*u.kN, shear_axis_sign=''):
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
    condition_text='V_%sEd / V_c%sRd = %s/%s = %s' % (shear_axis_sign, shear_axis_sign, abs(V_Ed), V_cRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.17) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

# Test if main
if __name__ == '__main__':
    print 'section_capacity_conditions test'
    print '--------condition_N_My_Mz ()-----------'
    print condition_Nt()
    print condition_Nc()
    print condition_My()
    print condition_Mz()
    print condition_My_Mz()
    print condition_Nt_My_Mz (10*u.kN, 50*u.kN, 10*u.kNm, 80*u.kNm, 10*u.kNm, 125*u.kNm)
    print condition_Nc_My_Mz (10*u.kN, 50*u.kN, 10*u.kNm, 80*u.kNm, 10*u.kNm, 125*u.kNm)
    #print condition_N_My_Mz()[2] + ' from ' + condition_N_My_Mz()[3]
    print '--------condition_V ()-----------'
    print condition_V (0*u.kN, 0*u.kN)
    print condition_V()[2] + ' from ' + condition_V()[3]