'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-11-15
This file is part of Struthon.
Struthon is a range of free open source structural engineering design 
Python applications.
http://struthon.org/

Struthon is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Struthon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''
import copy

available_languages = ['EN', 'PL']

def ElementnPropertiesReport(element, language='EN'):
    reports = {}
    reports['EN'] = '''Section %(sectname)s properties
==============================================================
Section dimencion: b=%(b)s, h=%(h)s
Section properties: A=%(A)s, I_y=%(I_y)s, I_z=%(I_z)s
--------------------------------------------------------------
Element lenght: L=%(L)s
Length for y buckling: k_ycr = %(k_ycr)s, L_ycr = %(L_ycr)s
Length for y buckling: k_zcr = %(k_zcr)s, L_zcr = %(L_zcr)s
Length for lateral-torsional buckling: k_LT = %(k_LT)s, L_LT = %(L_LT)s
--------------------------------------------------------------
Steelgrade: %(steelgrade)s, f_y=%(f_y)s, f_u=%(f_u)s
'''
    reports['PL'] = '''Parametry przekroju %(sectname)s
--------------------------------------------------------------
Wymiary: b = %(b)s, h=%(h)s
Parametry: A = %(A)s, I_y=%(I_y)s, I_z=%(I_z)s
--------------------------------------------------------------
Dlugosc: L=%(L)s
Dlugosc przy wyboczeniu wzgl. osi y: k_ycr = %(k_ycr)s, L_ycr = %(L_ycr)s
Dlugosc przy wyboczeniu wzgl. osi z: k_zcr = %(k_zcr)s, L_zcr = %(L_zcr)s
Dlugosc przy zwichrzeniu: k_LT = %(k_LT)s, L_LT = %(L_LT)s
--------------------------------------------------------------
Gatunek stali: %(steelgrade)s
'''
    out = reports[language]%element_var_dict(element)
    return out.replace('[]', '')


def SectionResistanceReport(element, language='EN'):
    reports = {}
    reports['EN'] = '''Section %(sectname)s resistance
==============================================================
N_tRd = %(N_tRd)s - design tension resistance
--------------------------------------------------------------
N_cRd = %(N_cRd)s (class %(class_comp)s) - design compression resistance
--------------------------------------------------------------
M_ycRd = %(M_ycRd)s (class %(class_bend_y)s) - design resistance for y bending
M_zcRd = %(M_zcRd)s (class %(class_bend_z)s) - design resistance for z bending
--------------------------------------------------------------
V_ycRd = %(V_ycRd)s - design plastic y shear resistance
V_zcRd = %(V_zcRd)s - design plastic z shear resistance
--------------------------------------------------------------
'''
    reports['PL'] = '''Nosnosc przekroju %(sectname)s
==============================================================
N_tRd = %(N_tRd)s - obliczeniowa nosnosc na rozciaganie
--------------------------------------------------------------
N_cRd = %(N_cRd)s (class %(class_comp)s) - obliczeniowa nosnosc na sciskanie
--------------------------------------------------------------
M_ycRd = %(M_ycRd)s (class %(class_bend_y)s) - obliczeniowa nosnosc na zginanie wzgl. osi y
M_zcRd = %(M_zcRd)s (class %(class_bend_z)s) - obliczeniowa nosnosc na zginanie wzgl. osi z
--------------------------------------------------------------
V_ycRd = %(V_ycRd)s - obliczeniowa nosnosc na scinanie w kier. osi y
V_zcRd = %(V_zcRd)s - obliczeniowa nosnosc na scinanie w kier. osi z
--------------------------------------------------------------
'''
    out = reports[language]%element_var_dict(element)
    return out.replace('[]', '')

def ElementResistanceReport(element, language='EN'):
    reports = {}
    reports['EN'] = '''Element %(Mark)s - %(sectname)s resistance (L=%(L)s)
==============================================================
                         General results
==============================================================
Buckling
hi_y = %(hi_y)s, hi_z = %(hi_z)s - buckling reduction factors
N_bRd = %(N_bRd)s - minimum buckling resistances
Lateral torsional buckling
hi_LT = %(hi_LT)s - reduction factor for lateral-torsional buckling
M_bRd = %(M_bRd)s - lateral torsional buckling resistance of bending member
==============================================================
                         Details of calculations
==============================================================
Buckling resistance 
L_ycr = %(L_ycr)s, L_zcr = %(L_zcr)s - effective lengths for buckling
alph = %(alpha)s - buckling imperfection factor
lambda_y = %(lambda_y)s, lambda_z = %(lambda_z)s - relative slendemcss
hi_y = %(hi_y)s, hi_z = %(hi_z)s - buckling reduction factors
N_ycr = %(N_ycr)s, N_zcr = %(N_zcr)s - buckling forces
N_ybRd = %(N_ybRd)s, N_zbRd = %(N_zbRd)s - buckling resistances
==============================================================
Lateral torsional buckling resistance
L_LT = %(L_LT)s - effective length for lateral-torsional buckling
alph_LT = %(alpha_LT)s - lateral-torsional buckling imperfection factor
M_cr = %(M_cr)s - lateral-torsional buckling moment
lambda_relLT = %(lambda_relLT)s - relative slenderness for lateral-torsional buckling
hi_LT = %(hi_LT)s - reduction factor for lateral-torsional buckling
M_bRd = %(M_bRd)s - lateral torsional buckling resistance of bending member
==============================================================
'''
    reports['PL'] = '''Element %(Mark)s - %(sectname)s resistance (L=%(L)s)
==============================================================
                         Wyniki obliczen
==============================================================
Wyboczenie
hi_y = %(hi_y)s, hi_z = %(hi_z)s - wspolczynniki wyboczenia 
N_bRd = %(N_bRd)s - nosnosc na wyboczenie
Zwichrzenie
hi_LT = %(hi_LT)s - wspolczynnik zwichrzenia
M_bRd = %(M_bRd)s - nosnosc na zwichrzenie
==============================================================
                         Szczegoly obliczen
==============================================================
Nosnosc na wyboczenie 
L_ycr = %(L_ycr)s, L_zcr = %(L_zcr)s - dlugosci wyboczeniowe
alph = %(alpha)s - parametr imperfekcji
lambda_y = %(lambda_y)s, lambda_z = %(lambda_z)s - smuklosc wzgledna
hi_y = %(hi_y)s, hi_z = %(hi_z)s - wspolczynniki wyboczenia
N_ycr = %(N_ycr)s, N_zcr = %(N_zcr)s - sily krytyczne
N_ybRd = %(N_ybRd)s, N_zbRd = %(N_zbRd)s - nosnosci na wyboczenie
==============================================================
Nosnosc na zwichrzenie
L_LT = %(L_LT)s - dlugosc zwichrzeniowa
alph_LT = %(alpha_LT)s - parametr imperfekcji
M_cr = %(M_cr)s - moment krytyczny przy zwichrzeniu sprezystym
lambda_relLT = %(lambda_relLT)s - smuklosc wzgledna
hi_LT = %(hi_LT)s - wspolczynnik zwichrzenia
M_bRd = %(M_bRd)s - nosnosc na zwichrzenie
==============================================================
'''
    out = reports[language]%element_var_dict(element)
    return out.replace('[]', '')

def OneLineResistanceReport(element, language='EN'):
    reports = {}
    reports['EN'] = '| N_bRd = %(N_bRd)s (hi_y = %(hi_y)s, hi_z = %(hi_z)s)  |  M_bRd = %(M_bRd)s (hi_LT = %(hi_LT)s) |'
    reports['PL'] =  reports['EN']
    out = reports[language]%element_var_dict(element)
    return out.replace('[]', '')

def CheckSectionReport(sect, load, result, language='EN'):
    if language == 'EN':
        def true_false_text(i):
            if i==True:
                return 'correct'
            if i==False:
                return 'failure !!!!!!'
        max_value = max(result[4])
        at_position = result[4].index(max_value)
        text =  '==============================================================\n'
        text +=  '>>>>>>> Section is ' + true_false_text(result[0]) + ' <<<<<<<' + '\n'
        text +=  '>>>>>>> Max condition is %s for loadcase no. %s \n'%(max_value, at_position)
        text +=  '==============================================================\n'
        for i in range(len(result[1])):
            text += 'loadcase no. ' + str(result[1][i]) + '  ' +load.Name[result[1][i]] + ' -> ' +  true_false_text(result[2][i]) + ' - %s'%str(result[4][i]) + '\n' + str(result[3][i] + '\n')
            text +=  '==============================================================\n'
    if language == 'PL':
        def true_false_text(i):
            if i==True:
                return 'poprawny'
            if i==False:
                return 'niepoprawny !!!!!!'
        max_value = max(result[4])
        at_position = result[4].index(max_value)
        text =  '==============================================================\n'
        text +=  '>>>>>>> Przekroj jest ' + true_false_text(result[0]) + ' <<<<<<<' + '\n'
        text +=  '>>>>>>> Maks. wytezenie - %s dla przyp. obc. nr %s \n'%(max_value, at_position)
        text +=  '==============================================================\n'
        for i in range(len(result[1])):
            text += 'przyp. obc. nr ' + str(result[1][i]) + '  ' +load.Name[result[1][i]] + ' -> ' +  true_false_text(result[2][i]) + ' - %s'%str(result[4][i]) + '\n' + str(result[3][i] + '\n')
            text +=  '==============================================================\n'   
    return text.replace('[]', '')
    
def SummaryReport(element, load, result, language='EN'):
    reports = {}
    #---
    reports['PL']  = CheckSectionReport(element, load, result, language='PL')
    reports['PL'] += ElementnPropertiesReport(element, language='PL')
    reports['PL'] += ElementResistanceReport(element, language='PL')
    #---
    reports['EN']  = CheckSectionReport(element, load, result, language='EN')
    reports['EN'] += ElementnPropertiesReport(element, language='EN')
    reports['EN'] += ElementResistanceReport(element, language='EN')
    return reports[language]

def OneLineCheckSectionReport(sect, load, result, language='EN'):
    max_value = str(max(result[4])).replace('[]', '')
    if language == 'EN':
        def true_false_text(i):
            if i==True:
                return 'correct (%s)'%max_value
            if i==False:
                return 'failure (%s) !!'%max_value
        text =  'Section is ' + true_false_text(result[0])
    if language == 'PL':
        def true_false_text(i):
            if i==True:
                return 'poprawny (%s)'%max_value
            if i==False:
                return 'niepoprawny (%s) !!'%max_value
        text =  'Przekroj jest ' + true_false_text(result[0])
    return text

#-------------------------------------

def element_var_dict(element):
    section_prop_name = ['f_y', 'f_u', 'class_comp', 'class_bend_y', 'class_bend_z', 'N_tRd', 'N_cRd', 'N_cRk','N_tRk' , 'M_ycRd', 'M_yRk', 'M_zcRd', 'M_zRk', 'V_ycRd', 'V_zcRd']
    element_prop_name = [   'L_ycr', 'L_zcr', 'L_LT',
                            'curve', 'curve_LT', 'alpha', 'alpha_LT', 
                            'lambda_y', 'lambda_z', 'lambda_l', 'lambda_yrel', 'lambda_zrel', 'lambda_relLT', 
                            'hi_y', 'hi_z', 'hi_LT', 
                            'N_ycr', 'N_zcr', 'M_cr', 'N_ybRd', 'N_zbRd', 'N_bRd', 'M_bRd']
    element_val_dict = copy.copy(vars(element))
    for i in section_prop_name + element_prop_name:
        exec("element_val_dict['%s'] = element.%s"%(i,i))
    return element_val_dict


#Test if main
if __name__ == "__main__":
    from strupy.steel.SteelElement import SteelElement
    from strupy.steel. SteelElementSolver import SteelElementSolver
    from strupy.steel.SteelElementLoad import SteelElementLoad
    element = SteelElement()
    load = SteelElementLoad()
    solv = SteelElementSolver()
    result = solv.check_element_for_load(element, load)
    #-----------------------
    import strupy.units as u
    element.L = 4.3*u.m
    print '-------------------------'
    print ElementnPropertiesReport(element, 'PL')
    print '-------------------------'
    print SectionResistanceReport(element, 'PL')
    print '-------------------------'
    print ElementResistanceReport(element, 'EN')
    print '-------------------------'
    print SummaryReport(element, load, result, 'PL')