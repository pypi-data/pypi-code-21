'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2015-07-01

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

class SectLoad:

    def __init__(self):
        self.Name=['Noname']
        self.Msd=[0*u.kNm]
        self.MTsd=[0*u.kNm]
        self.Nsd=[0*u.kN]
        self.Vsd=[0*u.kN]
        self.caseactiv=[True]
        
    def add_loadcase(self, casevalue={"Name": 'Noname', "Msd": 0*u.kNm, "MTsd": 0*u.kNm, "Nsd": 0*u.kN, "Vsd": 0*u.kN}):
        self.Name.append(casevalue["Name"])
        self.Msd.append(casevalue["Msd"])
        self.MTsd.append(casevalue["MTsd"])
        self.Nsd.append(casevalue["Nsd"])
        self.Vsd.append(casevalue["Vsd"])
        self.caseactiv.append(True)

    def edit_loadcase(self, casenumber, newcasevalue={"Name": 'Noname', "Msd": 5*u.kNm, "MTsd": 5*u.kNm, "Nsd": 5*u.kN, "Vsd": 5*u.kN}):
        self.Name[casenumber]=newcasevalue["Name"]
        self.Msd[casenumber]=newcasevalue["Msd"]
        self.MTsd[casenumber]=newcasevalue["MTsd"]
        self.Nsd[casenumber]=newcasevalue["Nsd"]
        self.Vsd[casenumber]=newcasevalue["Vsd"]
        
    def delete_loadcase(self, casenumber):
        self.Name.pop(casenumber)
        self.Msd.pop(casenumber)
        self.MTsd.pop(casenumber)
        self.Nsd.pop(casenumber)
        self.Vsd.pop(casenumber)
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
        return {"Name": self.Name, "Msd":self.Msd, "MTsd":self.MTsd, "Nsd":self.Nsd, "Vsd":self.Vsd, "caseactiv":self.caseactiv}
        
    def clear_loadcase(self):
        self.__init__()    

# Test if main
if __name__ == '__main__':
    print ('test SectLoad')
    # creating SectLoad object
    a=SectLoad()
    print a.get_loadcases()
    # adding lodacase to SectLoad object
    a.add_loadcase({"Name": 'ULS_case1', "Msd": 10*u.kNm, "MTsd": 2*u.kNm, "Nsd": 0*u.kN, "Vsd": 9*u.kN})
    a.add_loadcase({"Name": 'ULS_case2', "Msd": 10*u.kNm, "MTsd": 2*u.kNm, "Nsd": 0*u.kN, "Vsd": 5*u.kN})
    print a.get_loadcases()
    # deleting lodacase number 0 from SectLoad object
    a.delete_loadcase(2)
    print a.get_loadcases()
    # editing lodacase values number 0 in SectLoad object
    a.edit_loadcase(0, {"Name": 'ULS_changed', "Msd": 1200*u.kNm, "MTsd": 2*u.kNm, "Nsd": 0*u.kN, "Vsd": 9*u.kN})
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
    # clearing lodacase in SectLoad object
    a.clear_loadcase()
    print a.get_loadcases()