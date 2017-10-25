'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-03-06

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

class MaterialSteel:
    
    __SteelGrades=[]
    __SteelGrades.append({'steelgrade':'S235', 'steelstandard':'EN 10025-1', 'f_y_range':[235*u.MPa, 215*u.MPa], 'f_u_range':[360*u.MPa, 360*u.MPa]})
    __SteelGrades.append({'steelgrade':'S275', 'steelstandard':'EN 10025-1', 'f_y_range':[275*u.MPa, 255*u.MPa], 'f_u_range':[430*u.MPa, 410*u.MPa]})
    __SteelGrades.append({'steelgrade':'S355', 'steelstandard':'EN 10025-1', 'f_y_range':[355*u.MPa, 335*u.MPa], 'f_u_range':[490*u.MPa, 470*u.MPa]})
    __SteelGrades.append({'steelgrade':'S450', 'steelstandard':'EN 10025-1', 'f_y_range':[440*u.MPa, 410*u.MPa], 'f_u_range':[550*u.MPa, 550*u.MPa]})
    #..........

    def __init__(self):
        print 'MaterialSteel init'
        self.steelgrade = 'none'
        self.steelstandard = 'none'
        self.__f_y_range = [0*u.MPa, 0*u.MPa]
        self.__f_u_range = [0*u.MPa, 0*u.MPa]
        self.set_steelgrade('S235')
        self.E = 210.0*u.GPa
        self.G = 80.0*u.GPa
        nu = 0.3
        
    def set_steelgrade(self, newgrade):
        for i in MaterialSteel.__SteelGrades:
            if newgrade==i['steelgrade']:
                self.steelgrade = i['steelgrade']
                self.steelstandard = i['steelstandard']
                self.__f_y_range = i['f_y_range']
                self.__f_u_range = i['f_u_range']
                
    def get_steelinfo(self):
        return {'steelgrade':self.steelgrade, 'steelstandard':self.steelstandard, 'fyrange':self.__f_y_range, 'furange':self.__f_u_range, 'E':self.E}
        
    def get_availablesteelgrade(self):
        return [i['steelgrade'] for i in MaterialSteel.__SteelGrades]
        
    def f_u(self, thickness=50*u.mm):
        if thickness <= 40*u.mm:
            return self. __f_u_range[0]
        if thickness > 40*u.mm:
            return self. __f_u_range[1]
            
    def f_y(self, thickness=50*u.mm):
        if thickness <= 40*u.mm:
            return self. __f_y_range[0]
        if thickness > 40*u.mm:
            return self. __f_y_range[1]
        
# Test if main
if __name__ == '__main__':
    print ('test MaterialSteel')
    a=MaterialSteel()
    print a.get_steelinfo()
    a.set_steelgrade('S355')
    print a.get_steelinfo()
    print a.get_availablesteelgrade()
    print a.f_u(10*u.mm)
    print a.f_u(50*u.mm)
    print a.f_y(10*u.mm)
    print a.f_y(50*u.mm)