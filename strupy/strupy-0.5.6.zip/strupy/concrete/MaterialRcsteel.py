'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2015-11-28

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
File version 0.2 changes:
- RcSteelClass data structure changed
- get_availablercsteelclass() added
'''

import strupy.units as u

class MaterialRcsteel :
    
    __RcSteelClass=[]
    __RcSteelClass.append({"rcsteelname":'B400', "fyd":350*u.MPa, "ksiefflim":0.53})
    __RcSteelClass.append({"rcsteelname":'B450', "fyd":375*u.MPa, "ksiefflim":0.53})
    __RcSteelClass.append({"rcsteelname":'B500', "fyd":420*u.MPa, "ksiefflim":0.5})

    def __init__(self):
        print "MaterialRcsteel init"
        self.rcsteelname = 'B500'
        self.fyd = 420*u.MPa
        self.ksiefflim = 0.5

    def get_rcsteelinfo(self):
        return {"rcsteelname":self.rcsteelname, "fyd":self.fyd, "ksiefflim":self.ksiefflim}

    def set_rcsteelclass(self, newsteel):
        for i in MaterialRcsteel.__RcSteelClass:
            if newsteel==i['rcsteelname']:
                self.rcsteelname = i['rcsteelname']
                self.fyd = i['fyd']
                self.ksiefflim = i['ksiefflim']

    def get_availablercsteelclass(self):
        return [i['rcsteelname'] for i in MaterialRcsteel.__RcSteelClass] 

# Test if main
if __name__ == '__main__':
    print ('test MaterialRcsteell')
    a=MaterialRcsteel()
    print a.get_rcsteelinfo()
    a.set_rcsteelclass('B450')
    print a.get_rcsteelinfo()
    print a.get_availablercsteelclass()
