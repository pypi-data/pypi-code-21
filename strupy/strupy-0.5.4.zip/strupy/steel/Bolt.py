'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-02-04

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

class Bolt() :
    
    __BoltGradeList=[]
    __BoltGradeList.append({"grade":'3.6', "Rm":330.0*u.MPa, "Re":190.0*u.MPa})
    __BoltGradeList.append({"grade":'4.6', "Rm":400.0*u.MPa, "Re":240.0*u.MPa})
    __BoltGradeList.append({"grade":'4.8', "Rm":420.0*u.MPa, "Re":340.0*u.MPa})
    __BoltGradeList.append({"grade":'5.6', "Rm":500.0*u.MPa, "Re":300.0*u.MPa})
    __BoltGradeList.append({"grade":'5.8', "Rm":520.0*u.MPa, "Re":420.0*u.MPa})
    __BoltGradeList.append({"grade":'6.6', "Rm":600.0*u.MPa, "Re":360.0*u.MPa})
    __BoltGradeList.append({"grade":'6.8', "Rm":600.0*u.MPa, "Re":480.0*u.MPa})
    __BoltGradeList.append({"grade":'8.8', "Rm":800.0*u.MPa, "Re":640.0*u.MPa, "Rm_1":830.0*u.MPa, "Re_1":660.0*u.MPa})
    __BoltGradeList.append({"grade":'10.9', "Rm":1040.0*u.MPa, "Re":940.0*u.MPa})
    __BoltGradeList.append({"grade":'12.9', "Rm":1220.0*u.MPa, "Re":1100.0*u.MPa})
    
    __BoltDimList=[]
    __BoltDimList.append({"dim":'M10', "d":10.0*u.mm, "As":58.0*u.mm2})
    __BoltDimList.append({"dim":'M12', "d":12.0*u.mm, "As":84.3*u.mm2})
    __BoltDimList.append({"dim":'M16', "d":16.0*u.mm, "As":157.0*u.mm2})
    __BoltDimList.append({"dim":'M20', "d":20.0*u.mm, "As":245.0*u.mm2})
    __BoltDimList.append({"dim":'M24', "d":24.0*u.mm, "As":353.0*u.mm2})
    __BoltDimList.append({"dim":'M30', "d":30.0*u.mm, "As":561.0*u.mm2})

    def __init__(self):
        print "Bolt init"
        self.Grade = ''
        self.Dim = ''
        self.m = 1.0
        #---
        self.d = 0 * u.mm
        self.As = 0 * u.mm2
        self.Rm = 0 * u.MPa
        self.Re = 0 * u.MPa
        #---
        self.SRt = 0 * u.kN
        self.SRv = 0 * u.kN
        self.SRr = 0 * u.kN
        self.SRrdyn = 0 * u.kN
        #---
        self.set_BoltGrade()
        self.set_BoltDim()
    
    def get_AvailableBoltGrade(self):
        return [i['grade'] for i in Bolt.__BoltGradeList]

    def get_AvailableBoltDim(self):
        return [i['dim'] for i in Bolt.__BoltDimList]

    def set_BoltGrade(self, newgrade = '8.8'):
        for i in Bolt.__BoltGradeList:
            if newgrade==i['grade']:
                self.Grade = i['grade']
                self.Rm = i['Rm']
                self.Re = i['Re']
                if self.Grade=='8.8' and self.d > 16*u.mm :
                        self.Rm = i['Rm_1']
                        self.Re = i['Re_1']
        self.calculatebolt()
        print 'Bolt grade changed on ' + str(self.Grade)

    def set_BoltDim(self, newdim = 'M12'):
        for i in Bolt.__BoltDimList:
            if newdim==i['dim']:
                self.Dim = i['dim']
                self.As = i['As']
                self.d = i['d']
        #---
        curent_grade = self.Grade
        self.set_BoltGrade(curent_grade)
        #---
        self.calculatebolt()
        print 'Bolt dim changed on ' + str(self.Dim)
    
    def calculatebolt(self):
        #---SRt
        self.SRt = min (0.65 * self.Rm * self.As, 0.85 * self.Re * self.As)
        self.SRt = self.SRt.asUnit(u.kN)
        #---SRr    
        self.SRr = 0.8 * self.SRt
        self.SRr = self.SRr.asUnit(u.kN)
        #---SRrdyn
        self.SRrdyn = 0.6 * self.SRt
        self.SRrdyn = self.SRrdyn.asUnit(u.kN)
        #---SRv
        Av = 3.14 * self.d**2 / 4
        self.SRv = 0.45 * self.Rm * Av * self.m
        self.SRv = self.SRv.asUnit(u.kN)

# Test if main
if __name__ == '__main__':
    print ('test Bolt')
    bolt=Bolt()
    print bolt.get_AvailableBoltGrade()
    print bolt.get_AvailableBoltDim()
    bolt.set_BoltDim('M12')
    bolt.set_BoltGrade('8.8')
    print 'SRt =' + str(bolt.SRt)
    print 'SRv =' + str(bolt.SRv)
    print 'SRr =' + str(bolt.SRr)
    print 'SRrdyn =' + str(bolt.SRrdyn)