'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1(alpha) date 2017-11-17

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
from SteelSectionSolver import SteelSectionSolver

class SteelElementSolver(SteelSectionSolver):

    import section_capacity_conditions as __section_conditions
    import element_capacity_conditions as __element_conditions

    def __init__(self):
        print "SteelElementSolver init"
        SteelSectionSolver.__init__(self)

    def check_element_for_forces(self, element, M_yEd=40*u.kNm, M_zEd=5*u.kNm, T_Ed=0*u.kNm, N_Ed=125*u.kN, V_yEd=40*u.kN, V_zEd=120*u.kN, stabilitycheck=True):
        #---Cheking section
        section_check_result = self.check_section_for_forces(element, M_yEd=M_yEd, M_zEd=M_zEd, T_Ed=T_Ed, N_Ed=N_Ed, V_yEd=V_yEd, V_zEd=V_zEd)
        failure = section_check_result[0]
        resultcomment  = '-------Section check-----------\n'
        resultcomment += section_check_result[1]
        condition_value = section_check_result[2]
        #---Cheking element
        if stabilitycheck and (N_Ed < 0*u.kN or  M_yEd != 0*u.kNm) :
            #---
            if M_yEd == 0*u.kNm and M_zEd == 0*u.kNm: # Uniform members in compression
                element_check_result = self.__element_conditions.condition_N(N_Ed, element.N_bRd)
            elif  N_Ed == 0*u.kN and M_zEd == 0*u.kNm: # Uniform members in y bending
                element_check_result = self.__element_conditions.condition_M(M_yEd, element.M_bRd)
            elif  N_Ed <= 0*u.kN and (M_yEd != 0*u.kNm or M_zEd != 0*u.kNm): # Uniform members in bending and compresion
                element_check_result = self.__element_conditions.condition_Nc_Mx_My (   N_Ed, element.N_cRk, element.hi_y, element.hi_z,
                                                                                        M_yEd, element.M_yRk, element.hi_LT, 
                                                                                        M_zEd, element.M_zRk,
                                                                                        gamma_M1=1.0)
            elif  N_Ed > 0*u.kN and (M_yEd != 0*u.kNm or M_zEd != 0*u.kNm): # Uniform members in bending and tension
                element_check_result = self.__element_conditions.condition_Nt_Mx_My (   N_Ed, element.N_tRk,
                                                                                        M_yEd, element.M_yRk, element.hi_LT, 
                                                                                        M_zEd, element.M_zRk,
                                                                                        gamma_M1=1.0)
            if element_check_result[1] > 0: # Uniform members in bending and tension
                resultcomment += '\n------Stability check------------\n'
                resultcomment += element_check_result[2]
            #---
            failure = min(failure, element_check_result[0])
            condition_value = max(condition_value, element_check_result[1])
        return [failure, resultcomment, condition_value] 

    def check_element_for_load(self, element, load):
        capacity_is_true = False
        loadcase = []
        resultcomment = []
        failure = []
        condition_value = []
        #------------
        for i in range(len(load.Name)):
            if load.caseactiv[i]:                
                loadcase_result = self.check_element_for_forces(element, 
                                                                M_yEd = load.M_yEd[i], 
                                                                M_zEd = load.M_zEd[i], 
                                                                T_Ed = load.T_Ed[i], 
                                                                N_Ed = load.N_Ed[i], 
                                                                V_yEd = load.V_yEd[i], 
                                                                V_zEd = load.V_zEd[i],
                                                                stabilitycheck = load.stabilitycheck[i])
                #------------
                loadcase.append(i)
                failure.append(loadcase_result[0])
                resultcomment.append(loadcase_result[1])
                condition_value.append(loadcase_result[2])
        #------------
        if not False in failure:
            capacity_is_true = True
        return [capacity_is_true, loadcase, failure, resultcomment, condition_value]
    
# Test if main
if __name__ == '__main__':
    import strupy.units as u
    from SteelElement import SteelElement
    from SteelElementLoad import SteelElementLoad
    print ('SteelelementSolver')
    element=SteelElement()
    element.L = 8.6*u.m
    element.set_sectionfrombase('HE 200 A')
    element.set_steelgrade('S355')
    solver=SteelElementSolver()
    load=SteelElementLoad()
    load.delete_loadcase(0)
    load.add_loadcase({"Name": 'ULS_case1', "M_yEd": 50*u.kNm, "M_zEd": 0*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 100*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN, "stabilitycheck": True})
    #load.add_loadcase({"Name": 'ULS_case2', "M_yEd": 20*u.kNm, "M_zEd": 20*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 200*u.kN, "V_yEd": 9*u.kN, "V_zEd": 8*u.kN, "stabilitycheck": False})
    #load.add_loadcase({"Name": 'ULS_case3', "M_yEd": 120*u.kNm, "M_zEd": 80*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 300*u.kN, "V_yEd": 9*u.kN, "V_zEd": 5000*u.kN, "stabilitycheck": True})
    print '-----------------1-------------------'
    print load.get_loadcases()
    print '-----------------2-------------------'
    print element
    print '-----------------2-------------------'
    #element.set_sectionfrombase('IPE 240')
    print element
    print '-----------------4-------------------'
    result = solver.check_element_for_load(element, load)
    print result
    print '-----Raprot-----'
    print result[4]
    print '>>>>>>> ' + str(result[0]) + ' <<<<<<<'
    for i in range(len(result[1])):
        print'loadcase no. ' + str(result[1][i]) + ' -> ' +  str(result[2][i]) + str(result[4][i])  + '\n' + str(result[3][i])
    print result[1]
    #--------------------
    print '========================'
    print result
    
    #print ('######################################################################################')
    #print solver.check_element_for_forces(element)[0]
    #print solver.check_element_for_forces(element)[1]
    #print solver.check_element_for_forces(element)[2]
    #result = solver.check_element_for_load(element, load)
    #print result[0]
    