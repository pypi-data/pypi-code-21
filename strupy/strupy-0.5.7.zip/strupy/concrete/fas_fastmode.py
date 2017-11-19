'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

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

import strupy.units as u

import fas_pure as fas_clon

def calc (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, ap=5*u.cm, an=5*u.cm, fip=20*u.mm, fin=20*u.mm, rysAp=1.0, rysAn=1.0, wlimp=0.3*u.mm, wlimn=0.3*u.mm, fcd=16.7E6*u.Pa, fctm=2.2*u.MPa, fyd=420*u.MPa):
    
    OUT = fas_clon.calc (Nsd.asUnit(u.N).asNumber(), Msd.asUnit(u.Nm).asNumber(), h.asUnit(u.m).asNumber(), b.asUnit(u.m).asNumber(), ap.asUnit(u.m).asNumber(), an.asUnit(u.m).asNumber(), fip.asUnit(u.m).asNumber(), fin.asUnit(u.m).asNumber(), rysAp, rysAn, wlimp.asUnit(u.m).asNumber(), wlimn.asUnit(u.m).asNumber(), fcd.asUnit(u.Pa).asNumber(), fctm.asUnit(u.Pa).asNumber(), fyd.asUnit(u.Pa).asNumber())
    
    OUT['Ap']=OUT ['Ap'] * u.m2
    OUT['An']=OUT ['An'] * u.m2
    
    return OUT

# Test if main
if __name__ == '__main__':
    print ('test Fas')
    print (calc())