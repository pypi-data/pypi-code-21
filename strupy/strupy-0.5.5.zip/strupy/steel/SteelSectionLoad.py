'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-08-xx 

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

class SteelSectionLoad():

    def __init__(self):
        self.Name=['Noname']
        self.M_yEd=[0*u.kNm]
        self.M_zEd=[0*u.kNm]
        self.T_Ed=[0*u.kNm]
        self.N_Ed=[0*u.kN]
        self.V_yEd=[0*u.kN]
        self.V_zEd=[0*u.kN]
        self.caseactiv=[True]
        
    def add_loadcase(self, casevalue={"Name": 'Noname', "M_yEd": 0*u.kNm, "M_zEd": 0*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN, "caseactiv": True}):
        self.Name.append(casevalue["Name"])
        self.M_yEd.append(casevalue["M_yEd"])
        self.M_zEd.append(casevalue["M_zEd"])
        self.T_Ed.append(casevalue["T_Ed"])
        self.N_Ed.append(casevalue["N_Ed"])
        self.V_yEd.append(casevalue["V_yEd"])
        self.V_zEd.append(casevalue["V_zEd"])
        #---
        if casevalue.has_key("caseactiv"):
            self.caseactiv.append(casevalue["caseactiv"])
        else:
            self.caseactiv.append(True)
            
    def edit_loadcase(self, casenumber, newcasevalue={"Name": 'Noname', "M_yEd": 0*u.kNm, "M_zEd": 0*u.kNm, "T_Ed": 0*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 0*u.kN, "V_zEd": 0*u.kN, "caseactiv": True}):
        self.Name[casenumber]=newcasevalue["Name"]
        self.M_yEd[casenumber]=newcasevalue["M_yEd"]
        self.M_zEd[casenumber]=newcasevalue["M_zEd"]
        self.T_Ed[casenumber]=newcasevalue["T_Ed"]
        self.N_Ed[casenumber]=newcasevalue["N_Ed"]
        self.V_yEd[casenumber]=newcasevalue["V_yEd"]
        self.V_zEd[casenumber]=newcasevalue["V_zEd"]
        #---
        if newcasevalue.has_key("caseactiv"):
            self.caseactiv[casenumber]=newcasevalue["caseactiv"]
        
    def delete_loadcase(self, casenumber):
        self.Name.pop(casenumber)
        self.M_yEd.pop(casenumber)
        self.M_zEd.pop(casenumber)
        self.T_Ed.pop(casenumber)
        self.N_Ed.pop(casenumber)
        self.V_yEd.pop(casenumber)
        self.V_zEd.pop(casenumber)
        self.caseactiv.pop(casenumber)
        
    def caseactiv_all(self):
        for i in xrange(0, len(self.caseactiv)):
            self.caseactiv[i]=True

    def caseactiv_any(self):
        for i in xrange(0, len(self.caseactiv)):
            self.caseactiv[i]=False
            
    def caseactiv_oncase(self, casenumber):
        self.caseactiv[casenumber]=True
        
    def caseactiv_offcase(self, casenumber):
        self.caseactiv[casenumber]=False
   
    def get_loadcases(self):
        return {"Name": self.Name, "M_yEd":self.M_yEd, "M_zEd":self.M_zEd, "T_Ed":self.T_Ed, "N_Ed":self.N_Ed, "V_yEd":self.V_yEd, "V_zEd":self.V_zEd, "caseactiv":self.caseactiv}
        
    def clear_loadcase(self):
        self.__init__()    

# Test if main
if __name__ == '__main__':
    print ('test SteelSectionLoad')
    # creating SteelSectionLoad object
    a=SteelSectionLoad()
    print a.get_loadcases()
    # adding lodacase to SteelSectionLoad object
    a.add_loadcase({"Name": 'ULS_case1', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN})
    a.add_loadcase({"Name": 'ULS_case2', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN})
    print a.get_loadcases()
    # deleting lodacase number 0 from SteelSectionLoad object
    a.delete_loadcase(2)
    print a.get_loadcases()
    # editing lodacase values number 0 in SteelSectionLoad object
    a.edit_loadcase(0, {"Name": 'ULS_changed', "M_yEd": 10*u.kNm, "M_zEd": 10*u.kNm, "T_Ed": 2*u.kNm, "N_Ed": 0*u.kN, "V_yEd": 9*u.kN, "V_zEd": 9*u.kN})
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