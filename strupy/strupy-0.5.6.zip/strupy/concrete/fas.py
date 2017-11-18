'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2016-01-13

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

import ascomp as ascomp
import astens as astens

def calc (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, ap=5*u.cm, an=5*u.cm, fip=20*u.mm, fin=20*u.mm, rysAp=1.0, rysAn=1.0, wlimp=0.3*u.mm, wlimn=0.3*u.mm, fcd=16.7E6*u.Pa, fctm=2.2*u.MPa, fyd=420*u.MPa):

    OUT={"Ap":0*u.m2, "An":0*u.m2, "ksieff":0, "mimos":0, "rys":0*u.m}

    #-------- tens ------------------
    if Nsd>0*u.N and Msd>0*u.Nm :
        
        tmp=astens.astens (abs(Nsd), abs(Msd), h, b, an, ap, rysAn, rysAp, fin, fip, wlimn, wlimp, fcd, fctm, fyd)
        
        OUT['Ap']=tmp ['A2']
        OUT['An']=tmp ['A1']
        OUT['rys']=tmp ['rys']
        OUT['mimos']=tmp ['mimos']
        OUT['ksieff']=tmp ['ksieff']

    if Nsd>0*u.N and Msd<=0*u.Nm :
        
        tmp=astens.astens (abs(Nsd), abs(Msd), h, b, ap, an, rysAp, rysAn, fip, fin, wlimp, wlimn, fcd, fctm, fyd)
        
        OUT['Ap']=tmp ['A1']
        OUT['An']=tmp ['A2']
        OUT['rys']=tmp ['rys']
        OUT['mimos']=tmp ['mimos']
        OUT['ksieff']=tmp ['ksieff']
        
    #-------- comp ------------------
    if Nsd<=0*u.N and Msd>0*u.Nm :
        
        tmp=ascomp.ascomp (abs(Nsd), abs(Msd), h, b, an, ap, rysAn, rysAp, fin, fip, wlimn, wlimp, fcd, fctm, fyd)
        
        OUT['Ap']=tmp ['A2']
        OUT['An']=tmp ['A1']
        OUT['rys']=tmp ['rys']
        OUT['mimos']=tmp ['mimos']
        OUT['ksieff']=tmp ['ksieff']
        
    if Nsd<=0*u.N and Msd<=0*u.Nm :
        
        tmp=ascomp.ascomp (abs(Nsd), abs(Msd), h, b, ap, an, rysAp, rysAn, fip, fin, wlimp, wlimn, fcd, fctm, fyd)

        OUT['Ap']=tmp ['A1']
        OUT['An']=tmp ['A2']
        OUT['rys']=tmp ['rys']
        OUT['mimos']=tmp ['mimos']
        OUT['ksieff']=tmp ['ksieff']
    
    return OUT

# Test if main
if __name__ == '__main__':
    print ('test Fas')
    print (calc())