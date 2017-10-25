'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2016-01-13

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
- xxxxx
'''

import astens as astens_clon

import strupy.units_pure as u

astens_clon.u = u

def astens (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, a1=5*u.cm ,a2=5*u.cm ,rysA1=1.0 ,rysA2=1.0 ,fi1=20*u.mm ,fi2=20*u.mm ,wlim1=0.3*u.mm ,wlim2=0.3*u.mm, fcd=16.7*u.MPa, fctm=2.2*u.MPa, fyd=420*u.MPa):
    return astens_clon.astens(Nsd, Msd, h, b, a1, a2 ,rysA1, rysA2 ,fi1, fi2, wlim1, wlim2, fcd, fctm, fyd)

# Test if main
if __name__ == '__main__':

    print ('test astens_fastmode')
    print (astens())
