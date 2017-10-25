'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.4 date 2017-03-06

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
- crack control algorithm optimized
File version 0.4 changes:
- python3  compatibility cheked
'''

from math import sqrt

import strupy.units as u

from astens import sigmacs

def ascomp (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, a1=5*u.cm ,a2=5*u.cm ,rysA1=1.0 ,rysA2=1.0 ,fi1=20*u.mm ,fi2=20*u.mm ,wlim1=0.3*u.mm ,wlim2=0.3*u.mm, fcd=16.7*u.MPa, fctm=2.2*u.MPa, fyd=420*u.MPa):
    
    k1=0.8
    k2=0.5
    Beta1=1.0
    Beta2=0.5
    Beta=1.7
    Asmin=0*u.cm2
    Es=200*u.GPa
    Gamma=1.25
    delta=0.05

    ksiefflim=0.8*0.0035/(0.0035+fyd/Es)

    if Nsd<1*u.N:
        Nsd = 1*u.N
        
    es=Msd/Nsd
    d=h-a1
    es1=d-h/2+es
    es2=h/2-a2-es
    Msd1=Nsd*(es-h/2+a1)
    A2=(Nsd*es1-ksiefflim*(1-0.5*ksiefflim)*b*d**2*fcd)/(d-a2)/fyd
    A2=max(A2,0*u.m**2)
    ksieff=1-sqrt(1-2*(Nsd*es1-A2*(d-a2)*fyd)/(b*d**2*fcd))
    A1=(ksieff*b*fcd*d+A2*fyd-Nsd)/fyd
    mimos=-1

    if A1<0*u.m2 :   
        A1=0*u.m2
        B=a1/d-(2*A1*fyd*(d-a2))/(1-ksiefflim)/(b*d**2*fcd)
        ksieff=B+sqrt(B**2+2*((1-ksiefflim)*Nsd*es2+(1-ksiefflim)*A1*(d-a2)*fyd)/(1-ksiefflim)/(b*d**2*fcd))
        ksieff=abs(ksieff)
        if ksieff<1 :
            A2=(Nsd*es1-ksieff*(1-0.5*ksieff)*b*d**2*fcd)/(d-a2)/fyd
        A2=max(A2,0*u.m2)
        mimos=-2
        if A2>0*u.m2 :
            mimos=-22
        if ksieff>=1 :
            ksieff=1
            A1=(Nsd*es2-0.5*b*d**2*fcd)/(d-a2)/fyd
            A2=(Nsd*es1-1*(1-0.5*1)*b*d**2*fcd)/(d-a2)/fyd
            A1=max(A1,0*u.m2)
            A2=max(A2,0*u.m2)
            mimos=-3
            if A1>0*u.m2 :
                mimos=-33

    sigmas=0*u.Pa
    srm=0*u.m
    ror=0.0
    w=0.0*u.m
    Ncr=0.0*u.N
    rys=0.0

    if rysA1==1 and sigmacs(1/Gamma*Msd, 1/Gamma*Nsd, h, b, 0.0*u.m)>fctm and A1>0*u.m2 :
        
        As=A1
        Wc=b*h**2/6
        w=1*u.mm
        Ac=h*b
        n=-1
        Ncr=fctm/(es/Wc+1/Ac)
        
        while w > wlim1 :
            n=n+1
            if n :
                if (As * delta) < 0.5*u.cm2:
                    As=As + 0.5*u.cm2
                else:
                    As=As * (1+delta)
            ror=As/min(2.5*a1,(h-d*ksieff)/3)/b
            srm=0.05*u.m+0.25*k1*k2*fi1/ror
            sigmas=1/Gamma*fyd*A1/As
            epssm=sigmas/Es*(1-Beta1*Beta2*(Ncr/(1/Gamma*Nsd))**2)
            w=Beta*srm*epssm
            
        A1=As
        
        if n>0 :
            rys=1
            
    if A1<Asmin :
        A1=Asmin
    if A2<Asmin :
        A2=Asmin
        
    OUT={"A1": A1, "A2": A2, "ksieff": ksieff, "mimos": mimos, "rys": rys, "w": w, "sigmas": sigmas, "srm": srm, "ror": ror, "Ncr": Ncr}
    
    return OUT

# Test if main
if __name__ == '__main__':
    
    print ('test ascomp')
    print (ascomp())
