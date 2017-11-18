'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.4 date 2017-11-17

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

class SteelSectionSolver():
    
    import section_capacity_conditions as __conditions

    def __init__(self):
        print "SteelSectionSolver init"

    def check_section_for_forces(self, section, M_yEd=100.*u.kNm, M_zEd=56.*u.kNm, T_Ed=20.*u.kNm, N_Ed=40.*u.kN, V_yEd=10.*u.kN, V_zEd=50.*u.kN):
        failure = None
        resultcomment = None
        condition_value = None
        #------
        if M_yEd == 0*u.kNm and M_zEd == 0*u.kNm and N_Ed >= 0*u.kN: # section in tension
            condition_N_My_Mz = self.__conditions.condition_Nt(N_Ed, section.N_tRd)
        elif M_yEd == 0*u.kNm and M_zEd == 0*u.kNm and N_Ed < 0*u.kN: # section in compresion
            condition_N_My_Mz = self.__conditions.condition_Nc(N_Ed, section.N_cRd)
        elif M_yEd != 0*u.kNm and M_zEd == 0*u.kNm and N_Ed == 0*u.kN: # section in y bending
            condition_N_My_Mz = self.__conditions.condition_My(M_yEd, section.M_ycRd)                 
        elif M_yEd == 0*u.kNm and M_zEd != 0*u.kNm and N_Ed == 0*u.kN: # section in z bending
            condition_N_My_Mz = self.__conditions.condition_Mz(M_zEd, section.M_zcRd)
        elif M_yEd != 0*u.kNm and M_zEd != 0*u.kNm and N_Ed == 0*u.kN: # section in y z bending
            condition_N_My_Mz = self.__conditions.condition_My_Mz(M_yEd, section.M_ycRd, M_zEd, section.M_zcRd)              
        elif (M_yEd != 0*u.kNm or M_zEd != 0*u.kNm) and N_Ed > 0*u.kN: # section in y z bending and tension
            condition_N_My_Mz = self.__conditions.condition_Nt_My_Mz(N_Ed, section.N_tRd, M_yEd, section.M_ycRd, M_zEd, section.M_zcRd)      
        elif (M_yEd != 0*u.kNm or M_zEd != 0*u.kNm) and N_Ed < 0*u.kN: # section in y z bending and compresion
            condition_N_My_Mz = self.__conditions.condition_Nc_My_Mz(N_Ed, section.N_cRd, M_yEd, section.M_ycRd, M_zEd, section.M_zcRd)
        #-------
        condition_Vz = self.__conditions.condition_V(V_zEd, section.V_zcRd, 'z')
        condition_Vy = self.__conditions.condition_V(V_yEd, section.V_ycRd, 'y') 
        #------
        failure = min(condition_N_My_Mz[0], condition_Vz[0], condition_Vy[0])
        #------
        resultcomment = ''
        if condition_N_My_Mz[1] > 0 :resultcomment += condition_N_My_Mz[2]
        if condition_Vz[1]      > 0 :resultcomment += condition_Vz[2]
        if condition_Vy[1]      > 0 :resultcomment += condition_Vy[2]
        if not resultcomment: resultcomment = '(0.0)'
        #------
        condition_value = max(condition_N_My_Mz[1], condition_Vz[1], condition_Vy[1])
        #------
        return [failure, resultcomment, condition_value]   
    
    def check_section_for_load(self, section, load):
        capacity_is_true = False
        loadcase = []
        resultcomment = []
        failure = []
        condition_value = []
        #------------
        for i in range(len(load.Name)):
            if load.caseactiv[i]:                
                loadcase_result = self.check_section_for_forces(section, 
                                                                M_yEd = load.M_yEd[i], 
                                                                M_zEd = load.M_zEd[i], 
                                                                T_Ed = load.T_Ed[i], 
                                                                N_Ed = load.N_Ed[i], 
                                                                V_yEd = load.V_yEd[i], 
                                                                V_zEd = load.V_zEd[i])
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
    from SteelSection import SteelSection
    from SteelSectionLoad import SteelSectionLoad
    print ('SteelSectionSolver')
    section=SteelSection()
    solver=SteelSectionSolver()
    load=SteelSectionLoad()
    #-------------
    print solver.check_section_for_forces(section)
    #-------------
    load.add_loadcase({"Name": 'ULS_case1', "M_yEd": 0*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 10*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN})
    #load.add_loadcase({"Name": 'ULS_case2', "M_yEd": 20*u.kNm, "M_zEd": 20*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 8*u.kN})
    #load.add_loadcase({"Name": 'ULS_case3', "M_yEd": 120*u.kNm, "M_zEd": 80*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 5000*u.kN})
    print '-----------------1-------------------'
    print load.get_loadcases()
    print '-----------------2-------------------'
    print section
    print '-----------------2-------------------'
    section.set_sectionfrombase('IPE 300')
    print section
    print '-----------------4-------------------'
    result = solver.check_section_for_load(section, load)
    print result
    print '-----Raprot-----'
    print result[4]
    print '>>>>>>> ' + str(result[0]) + ' <<<<<<<'
    for i in range(len(result[1])):
        print'loadcase no. ' + str(result[1][i]) + ' -> ' +  str(result[2][i]) + '\n' + str(result[3][i])
    print result[1]