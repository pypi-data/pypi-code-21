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

def condition_N (N_Ed=1*u.kN, N_bRd=1*u.kN):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*N_Ed) / (1.0*N_bRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='N_Ed / N_bRd = %s/%s = %s' % (abs(N_Ed), N_bRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.46) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_M (M_Ed=1*u.kN, M_bRd=1*u.kN):
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value = abs(1.0*M_Ed) / (1.0*M_bRd)
    #------------
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
        warning_text = ''
    #------------
    condition_text='M_Ed / M_bRd = %s/%s = %s' % (abs(M_Ed), M_bRd, condition_value)
    condition_text += warning_text
    condition_is_from = '(6.54) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_Nc_Mx_My ( N_Ed=1.0*u.kN, N_Rk=20.0*u.kN, hi_y=0.15, hi_z=0.80,
                        M_yEd=4.0*u.kNm, M_yRk=10.0*u.kNm, hi_LT=0.8, 
                        M_zEd=3.0*u.kNm, M_zRk=10.0*u.kNm,
                        gamma_M1=1.0):
    k_yy=1.0
    k_yz=1.0
    k_zy=1.0
    k_zz=1.0
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value_1 = abs(N_Ed) / (hi_y*N_Rk/gamma_M1) + k_yy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1) + k_yz*abs(M_zEd)/(M_zRk/gamma_M1)
    condition_value_2 = abs(N_Ed) / (hi_z*N_Rk/gamma_M1) + k_zy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1) + k_zz*abs(M_zEd)/(M_zRk/gamma_M1)
    condition_value = max(condition_value_1, condition_value_2)
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
    #------------
    if 0 <= condition_value_1 < 1.0 :
        warning_text_1 = ''
    else: warning_text_1 = warning_text
    #------------
    if 0 <= condition_value_2 < 1.0 :
        warning_text_2 = ''
    else: warning_text_2 = warning_text
    #------------
    condition_text = ''
    #------------
    if condition_value_1 >= condition_value_2:
        condition_text += 'for y axis buckling: \n'
        condition_text += 'N_Ed /(hi_y*N_cRk/gamma_M1) + k_yy*M_yEd/ (hi_LT*M_yRk/gamma_M1) + k_yz*M_zEd/(M_zRk/gamma_M1) ='
        condition_text += '\n= %s /(%s*%s/%s) + %s*%s/ (%s*%s/%s) + %s*%s/(%s/%s) =' \
        % (N_Ed, hi_y, N_Rk, gamma_M1, k_yy, M_yEd, hi_LT, M_yRk, gamma_M1, k_yz, M_zEd, M_zRk, gamma_M1)
        condition_text += '\n= %s + %s + %s = %s' \
        % (abs(N_Ed) / (hi_y*N_Rk/gamma_M1), k_yy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1), k_yz*abs(M_zEd)/(M_zRk/gamma_M1), condition_value_1)
        condition_text += warning_text_1
    #-----------
    if condition_value_2 > condition_value_1:
        condition_text += 'for z axis buckling: \n'
        condition_text += 'N_Ed /(hi_z*N_cRk/gamma_M1) + k_zy*M_yEd/ (hi_LT*M_yRk/gamma_M1) + k_zz*M_zEd/(M_zRk/gamma_M1) ='
        condition_text += '\n= %s /(%s*%s/%s) + %s*%s/ (%s*%s/%s) + %s*%s/(%s/%s) =' \
        % (N_Ed, hi_z, N_Rk, gamma_M1, k_zy, M_yEd, hi_LT, M_yRk, gamma_M1, k_zz, M_zEd, M_zRk, gamma_M1)
        condition_text += '\n= %s + %s + %s = %s' \
        % (abs(N_Ed) / (hi_z*N_Rk/gamma_M1), k_zy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1), k_zz*abs(M_zEd)/(M_zRk/gamma_M1), condition_value_2)
        condition_text += warning_text_2
    #------------
    condition_is_from = '(6.61 & 6.62) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)

def condition_Nt_Mx_My ( N_Ed=1.0*u.kN, N_tRk=20.0*u.kN,
                        M_yEd=4.0*u.kNm, M_yRk=10.0*u.kNm, hi_LT=0.8, 
                        M_zEd=3.0*u.kNm, M_zRk=10.0*u.kNm,
                        gamma_M1=1.0):
    k_yy=1.0
    k_yz=1.0
    k_zy=1.0
    k_zz=1.0
    condition_is_true = False
    warning_text = ' (!!!!!!!!)'
    #------------
    condition_value_1 = abs(N_Ed) / (N_tRk/gamma_M1) + k_yy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1) + k_yz*abs(M_zEd)/(M_zRk/gamma_M1)
    condition_value_2 = abs(N_Ed) / (N_tRk/gamma_M1) + k_zy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1) + k_zz*abs(M_zEd)/(M_zRk/gamma_M1)
    condition_value = max(condition_value_1, condition_value_2)
    if 0 <= condition_value < 1.0 :
        condition_is_true = True
    #------------
    if 0 <= condition_value_1 < 1.0 :
        warning_text_1 = ''
    else: warning_text_1 = warning_text
    #------------
    if 0 <= condition_value_2 < 1.0 :
        warning_text_2 = ''
    else: warning_text_2 = warning_text
    #------------
    condition_text = ''
    #-----------
    if condition_value_1 >= condition_value_2:
        condition_text += 'N_Ed /(N_tRk/gamma_M1) + k_yy*M_yEd/ (hi_LT*M_yRk/gamma_M1) + k_yz*M_zEd/(M_zRk/gamma_M1) ='
        condition_text += '\n= %s /(%s/%s) + %s*%s/ (%s*%s/%s) + %s*%s/(%s/%s) =' \
        % (N_Ed, N_tRk, gamma_M1, k_yy, M_yEd, hi_LT, M_yRk, gamma_M1, k_yz, M_zEd, M_zRk, gamma_M1)
        condition_text += '\n= %s + %s + %s = %s' \
        % (abs(N_Ed) / (N_tRk/gamma_M1), k_yy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1), k_yz*abs(M_zEd)/(M_zRk/gamma_M1), condition_value_1)
        condition_text += warning_text_1
    #-----------
    if condition_value_2 > condition_value_1:
        condition_text += 'N_Ed /(N_tRk/gamma_M1) + k_zy*M_yEd/ (hi_LT*M_yRk/gamma_M1) + k_zz*M_zEd/(M_zRk/gamma_M1) ='
        condition_text += '\n= %s /(%s/%s) + %s*%s/ (%s*%s/%s) + %s*%s/(%s/%s) =' \
        % (N_Ed, N_tRk, gamma_M1, k_zy, M_yEd, hi_LT, M_yRk, gamma_M1, k_zz, M_zEd, M_zRk, gamma_M1)
        condition_text += '\n= %s + %s + %s = %s' \
        % (abs(N_Ed) / (N_tRk/gamma_M1), k_zy*abs(M_yEd) / (hi_LT*M_yRk/gamma_M1), k_zz*abs(M_zEd)/(M_zRk/gamma_M1), condition_value_2)
        condition_text += warning_text_2
    #------------
    condition_is_from = '(6.61 & 6.62) acc. EC3 EN 1993-1-1'
    return (condition_is_true, condition_value, condition_text, condition_is_from)


# Test if main
if __name__ == '__main__':
    print 'element_capacity_conditions test'
    print '--------condition_N()-----------'
    print condition_N (10*u.kN, 50*u.kN)
    print '--------condition_M()-----------'
    print condition_M (10*u.kNm, 50*u.kNm)    
    print '--------condition_N_Mx_My()-----------'   
    print condition_Nc_Mx_My()[2]
    print condition_Nt_Mx_My()[2]