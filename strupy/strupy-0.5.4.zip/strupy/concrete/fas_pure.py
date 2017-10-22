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
'''

import fas as fas_clon
import ascomp_pure
import astens_pure

import strupy.units_pure as u

fas_clon.u = u
fas_clon.ascomp = ascomp_pure
fas_clon.astens = astens_pure

def calc (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, ap=5*u.cm, an=5*u.cm, fip=20*u.mm, fin=20*u.mm, rysAp=1.0, rysAn=1.0, wlimp=0.3*u.mm, wlimn=0.3*u.mm, fcd=16.7E6*u.Pa, fctm=2.2*u.MPa, fyd=420*u.MPa):
    return fas_clon.calc (Nsd, Msd, h, b, ap, an, fip, fin, rysAp, rysAn, wlimp, wlimn, fcd, fctm, fyd)
    
# Test if main
if __name__ == '__main__':
    print ('test Fas')
    print (calc())