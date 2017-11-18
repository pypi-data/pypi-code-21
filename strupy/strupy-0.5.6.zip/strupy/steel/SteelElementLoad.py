'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1(alpha) date 2017-11-27

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
from SteelSectionLoad import SteelSectionLoad

class SteelElementLoad(SteelSectionLoad):

    def __init__(self):
        SteelSectionLoad.__init__(self)
        self.stabilitycheck=[True]

    def add_loadcase(self, casevalue={  "Name": 'Noname', 
                                        "M_yEd": 0*u.kNm, "M_zEd": 0*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN, 
                                        "caseactiv": True, "stabilitycheck": True}):
        SteelSectionLoad.add_loadcase(self, casevalue)
        #---
        if casevalue.has_key("stabilitycheck"):
            self.stabilitycheck.append(casevalue["stabilitycheck"])
        else:
            self.stabilitycheck.append(True)

    def edit_loadcase(self, casenumber, newcasevalue={  "Name": 'Noname', 
                                                        "M_yEd": 0*u.kNm, "M_zEd": 0*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN, 
                                                        "caseactiv": True, "stabilitycheck": True}):
        SteelSectionLoad.edit_loadcase(self, casenumber, newcasevalue)
        #---
        if newcasevalue.has_key("stabilitycheck"):
            self.stabilitycheck[casenumber]=newcasevalue["stabilitycheck"]

    def delete_loadcase(self, casenumber):
        SteelSectionLoad.delete_loadcase(self, casenumber)
        self.stabilitycheck.pop(casenumber)

    def get_loadcases(self):
        out = SteelSectionLoad.get_loadcases(self)
        out["stabilitycheck"] = self.stabilitycheck
        return out
        
# Test if main
if __name__ == '__main__':
    print ('test SteelElementLoad')
    # creating SteelSectionLoad object
    a=SteelElementLoad()
    print a.get_loadcases()
    # adding lodacase to SteelSectionLoad object
    a.add_loadcase({"Name": 'ULS_case1', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN})
    a.add_loadcase({"Name": 'ULS_case2', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN, "caseactiv": True, "stabilitycheck": True})
    print a.get_loadcases()
    # deleting lodacase number 0 from SteelSectionLoad object
    a.delete_loadcase(2)
    print a.get_loadcases()
    # editing lodacase values number 0 in SteelSectionLoad object
    a.edit_loadcase(0, {"Name": 'ULS_changed', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN})
    a.edit_loadcase(1, {"Name": 'ULS_case2', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN, "caseactiv": False, "stabilitycheck": False})    
    print a.get_loadcases()
    # deactivating all load cases
    a.caseactiv_all()
    print a.get_loadcases()
    # activating all load cases
    a.caseactiv_any()
    print a.get_loadcases()
    # deactivating loadcase 0
    a.caseactiv_offcase(0)
    print a.get_loadcases()
    # activating loadcase 0
    a.caseactiv_oncase(0)
    print a.get_loadcases()
    # clearing lodacase in SteelSectionLoad object
    a.clear_loadcase()
    print a.get_loadcases()