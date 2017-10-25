'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2016-01-13

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
'''

from math import sqrt

import strupy.units as u
  
def sigmacs (Ms=10.0*u.kNm, Ns=10.0*u.kN, h=1.0*u.m, b=1.0*u.m, y=0.5*u.m):
    W=(b*h**2)/6
    Ac=h*b
    Sigma2= -Ns/Ac - Ms/W
    Sigma1= -Ns/Ac + Ms/W
    SigmaceOUT = (Sigma2 - Sigma1)/h*y + Sigma1
    return SigmaceOUT
   
def K2(Ms=10.0*u.Nm, Ns=10.0*u.N, h=1.0*u.m, b=1.0*u.m):
    Wy=(b*h**2)/6
    Ac=h*b
    eps1= (Ns/Ac-Ms/Wy)/u.Pa
    eps2= (Ns/Ac+Ms/Wy)/u.Pa
    if min(eps1,eps2)>0:
        epsmin=min(eps1,eps2)
    else:
        epsmin=0
    if max(eps1,eps2)>0:
        epsmax=min(eps1,eps2)
    else:
        epsmax=0
    if epsmax==0:
        K2OUT=0
    else:
        K2OUT=(epsmax+epsmin)/(2*epsmax)
    return K2OUT

def astens (Nsd=10.0*u.kN, Msd=200.0*u.kNm, h=0.8*u.m, b=0.4*u.m, a1=5*u.cm ,a2=5*u.cm ,rysA1=1.0 ,rysA2=1.0 ,fi1=20*u.mm ,fi2=20*u.mm ,wlim1=0.3*u.mm ,wlim2=0.3*u.mm, fcd=16.7*u.MPa, fctm=2.2*u.MPa, fyd=420*u.MPa):
    
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
    
    if Nsd<1*u.N :
        Nsd = 1*u.N

    es=Msd/Nsd
    d=h-a1
    es1=h/2-a1-es
    es2=h/2-a2+es
    Msd1=Nsd*(es-h/2+a1)

    if Msd1>0*u.Nm :
        A2=(Msd1-ksiefflim*(1-0.5*ksiefflim)*d**2*b*fcd)/((d-a2)*fyd)
        if A2<0*u.m2 :
            A2=0*u.m2
        ksieff=1-sqrt(1 - 2*(-Nsd*es1-A2*(d-a2)*fyd)/(b*d**2*fcd))
        A1=(ksieff*b*fcd*d+A2*fyd+Nsd)/fyd
        mimos=1
        if A1>0*u.m2 and A2>0*u.m2 :
            mimos=11

    if Msd1<=0*u.Nm  :
        A1=(Nsd*es2)/(fyd*(d-a2))
        A2=(Nsd*es1)/(fyd*(d-a2))
        mimos=2
        ksieff=0
        
    sigmas=0*u.Pa
    srm=0*u.m
    ror=0.0
    w=0.0*u.m
    Ncr=0.0*u.N
    rys=0.0

    if rysA1==1 and sigmacs(1/Gamma*Msd, -1/Gamma*Nsd,h,b,0.0*u.m)>fctm and A1>0*u.m2 :
        
        As=A1
        Wc=b*h**2/6
        w=0.5*u.mm
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
            if  mimos==1 or mimos==11 :
                ror=As/min(2.5*a1,(h-d*ksieff)/3)/b
            if  mimos==2 :
                ror=As/min(2.5*a1,h/2)/b

            k2=K2(1/Gamma*Msd,1/Gamma*Nsd,h,b)
            srm=0.05*u.m+0.25*k1*k2*fi1/ror
            sigmas=1/Gamma*fyd*A1/As
            epssm=sigmas/Es*(1-Beta1*Beta2*(Ncr/(1/Gamma*Nsd))**2)
            w=Beta*srm*epssm
            
        A1=As
        
        if n>0 :
            rys=1

    if rysA2==1 and sigmacs(1/Gamma*Msd, -1/Gamma*Nsd, h, b, 0*u.m)>fctm and A2>0*u.m2 and Msd1<0*u.Nm :
        
        As=A2
        Wc=b*h**2/6
        w=1*u.mm
        Ac=h*b
        n=-1
        Ncr=fctm/(es/Wc+1/Ac)
        
        while w > wlim2 :
            n=n+1
            if n :
                if (As * delta) < 0.5*u.cm2:
                    As=As + 0.5*u.cm2
                else:
                    As=As * (1+delta)
            ror=As/min(2.5*a2,h/2)/b
            k2=K2(1/Gamma*Msd,1/Gamma*Nsd,h,b)
            srm=0.05*u.m+0.25*k1*k2*fi2/ror
            sigmas=1/Gamma*fyd*A2/As
            epssm=sigmas/Es*(1-Beta1*Beta2*(Ncr/(1/Gamma*Nsd))**2)
            w=Beta*srm*epssm
            
        A2=As
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
    print ('test sigmacs')
    print (sigmacs(10.0*u.kNm, 10.0*u.kN, 1.0*u.m, 1.0*u.m, 0.5*u.m))
    print (sigmacs())
    print ('test k2')
    print (K2(10.0*u.Nm, 10.0*u.N, 1.0*u.m, 1.0*u.m))
    print (K2())
    print ('test astens')
    print (astens())