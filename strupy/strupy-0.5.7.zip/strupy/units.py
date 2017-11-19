'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-03-06

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
- kg units added
- m3, cm3, mm3, m4, cm4, mm4 units added
File version 0.3 changes:
- python3  compatibility cheked
- um, rad added

'''

# SI units system in StruPy package is based on Unum package
# To use strupy units system write "import strupy.units as u" to be able use u.m, u.mm, u.kN etc.
# To use strupy units system write "from strupy.units import *" to be able use m, mm, kN etc. 

from unum import Unum as __Unum

# Unum customization 
__Unum.UNIT_SEP = '.'
__Unum.UNIT_DIV_SEP = '/'
__Unum.UNIT_FORMAT = '[%s]'
__Unum.VALUE_FORMAT = '%5.2f'

#---------------------------------------------------------------------
# SI unit list used in StruPy pakage
from unum.units import m                       # [m] unit definition
from unum.units import cm                      # [cm] unit definition
from unum.units import mm                      # [mm] unit definition
from unum.units import um                      # [um] unit definition
from unum.units import kg                      # [kg] unit definition
from unum.units import rad                     # [rad] unit definition

m2=m**2                                        # [m2] unit definition
cm2=cm**2                                      # [cm2] unit definition
mm2=mm**2                                      # [mm2] unit definition

m3=m**3                                        # [m3] unit definition
cm3=cm**3                                      # [cm3] unit definition
mm3=mm**3                                      # [mm3] unit definition

m4=m**4                                        # [m4] unit definition
cm4=cm**4                                      # [cm4] unit definition
mm4=mm**4                                      # [mm4] unit definition
 
from unum.units import N                       # [N] unit definition
kN = __Unum.unit('kN', 1E3 * N)                # [kN] unit definition

Nm = __Unum.unit('Nm', N * m)                  # [Nm] unit definition
kNm = __Unum.unit('kNm', 1E3 * N * m)          # [kNm] unit definition
 
from unum.units import J                       # [J] unit definition

from unum.units import Pa as Pa                # [Pa] unit definition
kPa = __Unum.unit('kPa', 1E3 * Pa)             # [kPa] unit definition
MPa = __Unum.unit('MPa', 1E6 * Pa)             # [MPa] unit definition
GPa = __Unum.unit('GPa', 1E9 * Pa)             # [MPa] unit definition

from unum.units import s                       # [s] unit definition
#---------------------------------------------------------------------

# Extra useful function definition

def xvalueformat(format='%10.2f'):
    __Unum.VALUE_FORMAT=format

def xunumlistvalue(unumlist,unit=1):
    if type(unumlist[0]) is not type ([]):
        unumlist = [(i/unit).asNumber() for i in unumlist]
        return unumlist
    if type(unumlist[0]) is type ([]):
        for j in range(len(unumlist)):
            unumlist[j] = [(i/unit).asNumber() for i in unumlist[j]]
        return unumlist
        
# Test if main
if __name__ == '__main__':
    print ('units test') 
    print (3.7*m*s**2)
    print (23.7*kN/m)
    print (2*kN/m)
    a=10*m
    b=10*m
    c=a+b
    print (c)
    c=c**2
    print (c)
    print ('xunumlistvalue test')
    a=[1*m, 3*m]
    b=[1*m, 3*m]
    print (a)
    print (b)
    print ('_unumlistvalue --->')
    a=xunumlistvalue(a, 0.01*m)
    b=xunumlistvalue(b, 0.01*m)
    print (a)
    print (b)
    k=[[m, m], [m, m]]
    k=xunumlistvalue(k, 0.01*m)
    print (k)