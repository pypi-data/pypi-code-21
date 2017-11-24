"""
pySAXS python routines for small angle xray scattering.
This is the core of pySAXS
containing usefull function for SAXS data treatment,
tested and optimized amplitude and form factor

"""
import sys
from string import *
from math import *
import numpy
from numpy import *
from scipy import special as SPspecial
from scipy import stats as SPstats
from scipy import integrate as SPintegrate
from scipy import optimize as SPoptimize

##
##Utility functions
##

def Q(n,wave_length,pixel_size,detector_to_sample):
    '''
    calculate q in Angstrom -1
    '''
    return ((4*pi)/wave_length)*sin(arctan((pixel_size*n)/detector_to_sample)/2)

def Qlogspace(qmin,qmax,np):
    """
    This function returns an array of np q values evenlly separated in
    log scale between qmin and qmax
    """
    return numpy.logspace(log10(qmin),log10(qmax),np)

def getV(R):
    """
    This function returns a the volume of a sphere with radius r
    """
    return (4./3.)*numpy.pi*R*R*R

def getVelli(R,e):
    """
    This function returns a the volume of a sphere with radius r
    """
    return (4./3.)*numpy.pi*R*R*R*e

def SS(f,p):
    """
    This function returns the specific surface of a distribution of
    spheres
    f function to compute the distribution
    p array of parameter
    """
    r=arange(p[0]/100.,p[0]+6.*p[1],p[1]/10.)
    S=sum(f(r,p[0],p[1])*r**2)
    V=sum(f(r,p[0],p[1])*r**3/3.)
    surfacespecifique=S/V*1.e10
    return surfacespecifique,S,V

##
## Basic functions
##

def Guinier(q,I0,Rg):
    '''
    Guinier function
    '''
    #G=I0*exp((q0**2*Rg**2)/3.0)*exp(-q**2*Rg**2/3)
    G=I0*numpy.exp(-q**2*Rg**2/3.0)
    
    return G

def Porod(q,B):
    '''
    Porod function
    q**-4*B*1e-32
    '''
    return q**-4.0*B*1e-32



def Dgauss(par):
    """
    This function returns a gaussian distribution for the array r with an
    averaga size rm and a standard deviation sigma.
    """
    if len(par) != 3:
        sys.stderr.write("This function takes a list of 3 parameter")
        return -1.
    f=SPstats.norm.pdf(par[0],par[1],par[2])
    return f,SPstats.mean(f*par[0])/SPstats.mean(f)

def Dlognormal(par):
    """
    This function returns a modified lognormal distribution for the
    array r with an averaga size rm and a standard deviation sigma
    """
    if len(par) != 3:
        sys.stderr.write("This function takes a list of 3 parameter")
        return -1.
    f=numpy.where(par[0]>0.0,par[1]*SPstats.lognorm.pdf(par[1]/par[0],par[2])/par[0]**2.,0.0)
    return f,SPstats.mean(f*par[0])/SPstats.mean(f)

def Dexpon(par):
    """
    This function returns a modified lognormal distribution for the
    array r with an averaga size rm and a standard deviation sigma
    """
    if len(par) != 3:
        sys.stderr.write("This function takes a list of 3 parameter")
        return -1.
    f=numpy.where(r>=0.0,SPstats.expon.pdf(par[0],par[1],par[2]),0.0)
    return f,SPstats.mean(f*par[0])/SPstats.mean(f)

def Dalpha(par):
    """
    This function returns a modified lognormal distribution for the
    array r with an averaga size rm and a standard deviation sigma
    """
    if len(par) != 4:
        sys.stderr.write("This function takes a list of 4 parameter")
        return -1.
    f=numpy.where(par[0]>=0.0,SPstats.alpha.pdf(par[0],par[1],par[2],par[3]),0.0)
    return f,SPstats.mean(f*par[0])/SPstats.mean(f)



def Dshultz(r,rav,z):
    """
    This function returns a shultz distribution for the array r with rav,
    z as parameter
    """
    f=numpy.zeros(len(r),float)
    f=(((z+1.0)/rav)**(z+1.0)*(r**z/(numpy.exp(SPspecial.gammaln(z+1))))*numpy.exp(-r*(z+1.0)/rav))
    return f,numpy.mean(f*r)/numpy.mean(f)



def getRmoydist(R,D):
    """
    This function returns the form factor of a dsitribution of spheres of
    radius R for q
    """
    f1=SPintegrate.trapz(R*D,R)
    f2=SPintegrate.trapz(D,R)
    return(f1/f2)


##
##Amplitude factor (pedersen notations) F1,F2 etc..
##


def F1(q,R):
    """
    This function returns a scattering amplitude of a sphere of radius R for q
    """
    return (3.0*(numpy.sin(q*R)-q*R*numpy.cos(q*R)))/(q*R)**3.0

def F2(q,R1,R2):
    """
    This function returns a scattering amplitude of an empty shell of internal
    radius R2 and external radius R2 for q
    """
    return (getV(R1)*F1(q,R1)-getV(R2)*F1(q,R2))/(getV(R1)-getV(R2))

def F3(q,R,rho):
    """
    This function returns the scattering amplitude of spherically symetric
    shells of internal radius Ri and scattering length density rhoi for q
    """
    if len(R)==len(rho):

        rho2=numpy.zeros(len(rho),float)
        rho2[1:]=rho[0:len(rho)-1]
        rho=rho-rho2
        #M3=sum(rho*getV(R))

        if numpy.isscalar(q):
            F3=0.0
            M3=0.0
        else:
            F3=numpy.zeros(len(q),float)
            M3=0.0

        for i in numpy.arange(len(R)):
            F3=F3+rho[i]*getV(R[i])*F1(q,R[i])
            M3=M3+rho[i]*getV(R[i])
        return F3/M3,M3
    else:
        sys.stderr.write("radius and contrast length does not match")
        return -1.,-1.

def F3elli(q,R,e,rho):
    if len(R)==len(rho):
        rho2=numpy.zeros(len(rho),float)
        rho2[1:]=rho[0:len(rho)-1]
        rho=rho-rho2
        M3=sum(rho*getVelli(R,e))
        if numpy.isscalar(q):
            F3=0.0
        else:
            F3=numpy.zeros(len(q),float)
        for i in range(len(R)):
            F3=F3+rho[i]*getVelli(R[i],e)*F1(q,R[i])
        return F3/M3,M3
    else:
        sys.stderr.write("radius and contrast length does not match")
        return -1.,-1.


def fP5_int(x,q,R,e):
    return sin(x)*F1(q,R*sqrt(numpy.sin(x)*numpy.sin(x)+e*e*numpy.cos(x)*numpy.cos(x)))**2.

def P5_int(q,R,e):
    return SPintegrate.quad(fP5_int,0.0,numpy.pi/2.,(q,R,e))[0]
def fP5_conc_int(x,q,R,e,rho):
    return numpy.sin(x)*F3elli(q,R*numpy.sqrt(numpy.sin(x)*numpy.sin(x)+e*e*numpy.cos(x)*numpy.cos(x)),e,rho)[0]**2.

def P5_conc_int(q,R,e,rho):
    return SPintegrate.quad(fP5_conc_int,0.0,numpy.pi/2.,(q,R,e,rho))[0]

def fP11_int(x,q,R,L):
    return numpy.sin(x)*((2.0*SPspecial.j1(q*R*numpy.sin(x))*numpy.sin(q*L*numpy.cos(x)/2.))/(q*R*numpy.sin(x)*q*L*numpy.cos(x)/2.))**2.

def P11_int(q,R,L):
    return SPintegrate.quad(fP11_int,0.0,numpy.pi/2.,(q,R,L))[0]



##
## Form factor (Pedersen notations) P1,P2, etc...
## These are the normalized P ie P(0)=1.
##

def P1(q,R):
    """
    This function returns the form factor of a sphere of radius R for q
    """
    if numpy.min(R)<=0.0:
        sys.stderr.write('can not compute for nul or negative sizes\n')
        return 1.0
    return F1(q,R)*F1(q,R)

def P2(q,R1,R2):
    """
    This function returns the form factor of an empty shell of internal radius
    R2 and external radius R2 for q
    """
    return F2(q,R1,R2)*F2(q,R1,R2)

def P3(q,R,rho):
    """
    This function returns the form factor of spherically symetric shells of
    internal radius Ri and scattering length density rhoi for q
    """
    P,M=F3(q,R,rho)[0],F3(q,R,rho)[1]
    return P*P,M*M

def P3elli(q,R,e,rho):
    """
    This function returns the form factor of spherically symetric shells of
    internal radius Ri and scattering length density rhoi for q
    """
    P,M=F3elli(q,R,e,rho)
    return P*P,M*M

def P5(q,R,e):
    """
    This function returns the form factor of an ellipsoid of revolution with
    semi-axes R, R and e*R for q
    """
    P5=numpy.zeros(len(q),dtype='float')
    for i in numpy.arange(len(q)):
        P5[i]=P5_int(q[i],R,e)
    return P5

def P5conc(q,R,e,rho):
    """
    This function returns the form factor of an concentric ellipsoid
    of revolutions with semi-axes R, R and e*R for q
    """
    P5conc=numpy.zeros(len(q),dtype='float')
    for i in numpy.arange(len(q)):
        P5conc[i]=P5_conc_int(q[i],R,e,rho)
    return P5conc

def P11(q,R,L):
    P11=numpy.zeros(len(q),dtype='float')
    x=0.0
    for i in numpy.arange(len(q)):
        P11[i]=P11_int(q[i],R,L)
    return P11

def Pcylcos(q,R,L):
    """
    Optimized version of P11 OS
    This function calculates the P(q) of a cylinder of length L and radius R
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        dPcyl0=numpy.sin(alpha0)*(2.*SPspecial.j1(q[i]*R*numpy.sin(alpha0))*numpy.sin(q[i]*L*numpy.cos(alpha0)/2.)/(q[i]*R*numpy.sin(alpha0)*q[i]*L*numpy.cos(alpha0)/2.))**2
        dPcylN=numpy.sin(alphaN)*(2.*SPspecial.j1(q[i]*R*numpy.sin(alphaN))*numpy.sin(q[i]*L*numpy.cos(alphaN)/2.)/(q[i]*R*numpy.sin(alphaN)*q[i]*L*numpy.cos(alphaN)/2.))**2
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dcosalpha=1./N
            cosalpha=numpy.arange(dcosalpha,1.,2.*dcosalpha)
            sinalpha=(1.-cosalpha**2)**(0.5)
            dPcyl=(2.*SPspecial.j1(q[i]*R*sinalpha)*numpy.sin(q[i]*L*cosalpha/2.)/(q[i]*R*sinalpha*q[i]*L*cosalpha/2.))**2
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dcosalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold

def Pcyl(q,R,L):
    """
    Optimized version of P11 OS
    This function calculates the P(q) of a cylinder of length L and radius R
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        dPcyl0=numpy.sin(alpha0)*(2.*SPspecial.j1(q[i]*R*numpy.sin(alpha0))*numpy.sin(q[i]*L*numpy.cos(alpha0)/2.)/(q[i]*R*numpy.sin(alpha0)*q[i]*L*numpy.cos(alpha0)/2.))**2
        dPcylN=numpy.sin(alphaN)*(2.*SPspecial.j1(q[i]*R*numpy.sin(alphaN))*numpy.sin(q[i]*L*numpy.cos(alphaN)/2.)/(q[i]*R*numpy.sin(alphaN)*q[i]*L*numpy.cos(alphaN)/2.))**2
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            dPcyl=numpy.sin(alpha)*(2.*SPspecial.j1(q[i]*R*numpy.sin(alpha))*numpy.sin(q[i]*L*numpy.cos(alpha)/2.)/(q[i]*R*numpy.sin(alpha)*q[i]*L*numpy.cos(alpha)/2.))**2
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold

def Pcylmulti(q,R,rho,L,rhos):
    """
    This function calculates at the absolute scale the P(q) of a cylinder of length L and and multilayers R of density Rho the last one being solvent
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        
        #----------------------------------------------------------------------------------------------------       
        """Somme sur les ecorces"""
        dPeco=0.
        for j in range(len(R)):
            dPeco=dPeco+(rho[j]-rho[j+1])*(2.*R[j]*SPspecial.j1(q[i]*R[j]*numpy.sin(alpha0))/(q[i]*numpy.sin(alpha0)))     
        dPcyl0=numpy.sin(alpha0)*(numpy.sin(q[i]*L*numpy.cos(alpha0)/2.)/(q[i]*L*numpy.cos(alpha0)/2.)*dPeco)**2

        #----------------------------------------------------------------------------------------------------        
        dPeco=0.
        for k in range(len(R)):
            dPeco=dPeco+(rho[k]-rho[k+1])*(2.*R[k]*SPspecial.j1(q[i]*R[k]*numpy.sin(alphaN))/(q[i]*numpy.sin(alphaN)))            
        dPcylN=numpy.sin(alphaN)*(numpy.sin(q[i]*L*numpy.cos(alphaN)/2.)/(q[i]*L*numpy.cos(alphaN)/2.)*dPeco)**2
        #----------------------------------------------------------------------------------------------------
        
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            #----------------------------------------------------------------------------------------------------
            dPeco=0.*alpha
            for l in range(len(R)):
                dPeco=dPeco+(rho[l]-rho[l+1])*(2.*R[l]*SPspecial.j1(q[i]*R[l]*numpy.sin(alpha))/(q[i]*numpy.sin(alpha)))      
            dPcyl=numpy.sin(alpha)*(numpy.sin(q[i]*L*numpy.cos(alpha)/2.)/(q[i]*L*numpy.cos(alpha)/2.)*dPeco)**2            
            #----------------------------------------------------------------------------------------------------         
            dPcylnew=sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i] 
    return Pcylold*numpy.pi**2*L**2*1e-48*rhos

def f(x,y):
    f=2.*SPspecial.j1(x)/x*numpy.sin(y)/y
    return f

def Pcylvb(q,R,L):
    """
    This function calculates the P(q) normalized to one at q=0 of a cylinder of length L and radius R
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        x=q[i]*R*numpy.sin(alpha0)
        y=q[i]*L/2.*numpy.cos(alpha0)
        dPcyl0=numpy.sin(alpha0)*f(x,y)**2
        x=q[i]*R*numpy.sin(alphaN)
        y=q[i]*L/2.*numpy.cos(alphaN)        
        dPcylN=numpy.sin(alphaN)*f(x,y)**2
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            x=q[i]*R*numpy.sin(alpha)
            y=q[i]*L/2.*numpy.cos(alpha)
            dPcyl=numpy.sin(alpha)*f(x,y)**2
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold


def dPpara(q,a,b,c,beta):
    """Side function of Ppara"""
    a=a/2.
    b=b/2.
    c=c/2.
    dPparanew=1.*q
    dPparaold=1.*q
    N=1.
    alpha0=1e-12
    alphaN=pi/2
    x=q*a*numpy.sin(alpha0)*numpy.cos(beta)
    y=q*b*numpy.sin(alpha0)*numpy.sin(beta)
    z=q*c*numpy.cos(alpha0)        
    ddPpara0=numpy.sin(alpha0)*(numpy.sin(x)*numpy.sin(y)*numpy.sin(z)/(x*y*z))**2
        
    x=q*a*numpy.sin(alphaN)*numpy.cos(beta)
    y=q*b*numpy.sin(alphaN)*numpy.sin(beta)
    z=q*c*numpy.cos(alphaN)               
    ddPparaN=numpy.sin(alphaN)*(numpy.sin(x)*numpy.sin(y)*numpy.sin(z)/(x*y*z))**2
        
    ddPparaold=(ddPpara0+ddPparaN)/2.
    dPparaold=pi/2*ddPparaold
    test1=1.
    while(abs(test1)>1e-3):
        N=2.*N
        dalpha=(pi/2.-alpha0)/N
        alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
        x=q*a*numpy.sin(alpha)*numpy.cos(beta)
        y=q*b*numpy.sin(alpha)*numpy.sin(beta)
        z=q*c*numpy.cos(alpha)            
        ddPpara=numpy.sin(alpha)*(numpy.sin(x)*numpy.sin(y)*numpy.sin(z)/(x*y*z))**2
            
        ddPparanew=numpy.sum(ddPpara)+ddPparaold
        ddPparaold=ddPparanew
        dPparanew=dalpha*ddPparanew
        test1=(dPparanew-dPparaold)/dPparaold
        dPparaold=dPparanew
    return dPparaold

def Ppara(q,a,b,c):
    """
    This function calculates the P(q) normalized to one at q=0 of a parallelepiped a,b,c (not finished 21/10/2009. this function makes use of dPpara
    which makes the integral over alpha
    """
    Pparanew=0.*q
    Pparaold=0.*q
    for i in range(len(q)):
        N=1
        beta0=1e-12
        betaN=pi/2       
        dPpara0=dPpara(q[i],a,b,c,beta0)               
        dPparaN=dPpara(q[i],a,b,c,betaN)
        
        dPparaold=(dPpara0+dPparaN)/2.
        Pparaold[i]=dPparaold
        test=1.
        while(abs(test)>1e-3):
            N=2.*N
            dbeta=(pi/2.-beta0)/N
            beta=numpy.arange(dbeta,pi/2.,2.*dbeta)
            dPparanew=0.
            for j in range(len(beta)):                     
                dPparanew=dPpara(q[i],a,b,c,beta[j])+dPparanew
            dPparanew=dPparaold+dPparanew
            dPparaold=dPparanew
            Pparanew[i]=dbeta*dPparanew
            test=(Pparanew[i]-Pparaold[i])/Pparaold[i]
            Pparaold[i]=Pparanew[i]
    return 2.*Pparaold/pi

def Pcylcreux(q,Ri,Ro,L):
    """
    This function calculates the P(q) normalized to one at q=0 of an hollow cylinder of length L inner radius Ri and outer radius Ro
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        xo=q[i]*Ro*numpy.sin(alpha0)
        xi=q[i]*Ri*numpy.sin(alpha0)
        y=q[i]*L/2.*numpy.cos(alpha0)
        dPcyl0=numpy.sin(alpha0)*(pi*L*Ro**2*f(xo,y)-pi*L*Ri**2*f(xi,y))**2
        xo=q[i]*Ro*numpy.sin(alphaN)
        xi=q[i]*Ri*numpy.sin(alphaN)
        y=q[i]*L/2.*numpy.cos(alphaN)        
        dPcylN=numpy.sin(alphaN)*(pi*L*Ro**2*f(xo,y)-pi*L*Ri**2*f(xi,y))**2
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            xo=q[i]*Ro*numpy.sin(alpha)
            xi=q[i]*Ri*numpy.sin(alpha)
            y=q[i]*L/2.*numpy.cos(alpha)
            dPcyl=numpy.sin(alpha)*(pi*L*Ro**2*f(xo,y)-pi*L*Ri**2*f(xi,y))**2
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold/(pi*L*(Ro**2-Ri**2))**2

def fcan(x,y,z):
    f=4.*SPspecial.j1(x)/x*numpy.cos(z)*numpy.sin(y)
    return f

def fcanb(x,y,z):
    f=4.*SPspecial.j1(x)/x*numpy.sin(z)*numpy.sin(y)
    return f

        
def Pcylcreuxcan(q,a,Ri,Ro,L):
    Pcylnew=1.*q
    Pcylold=1.*q    
    for i in range(len(q)):
        dPcyl=numpy.zeros(len(a))
        dPcylb=numpy.zeros(len(a))
        Pcylold[i]=0.
        N=1.
        alpha0=1e-120
        alphaN=pi/2.

        dPcyl0=0.*a        
        for j in range(len(a)):
            xo=q[i]*Ro[j]*numpy.sin(alpha0)
            xi=q[i]*Ri[j]*numpy.sin(alpha0)
            z=q[i]*a[j]*numpy.cos(alpha0)
            y=q[i]*L[j]/2.*numpy.cos(alpha0)            
            dPcyl[j]=pi/(q[i]*numpy.cos(alpha0))*(Ro[j]**2*fcan(xo,y,z)-Ri[j]**2*fcan(xi,y,z))
            dPcylb[j]=pi/(q[i]*numpy.cos(alpha0))*(Ro[j]**2*fcanb(xo,y,z)-Ri[j]**2*fcanb(xi,y,z))
        dPcyl0=numpy.sin(alpha0)*(numpy.sum(dPcyl)**2+numpy.sum(dPcylb)**2)

        dPcylN=0.*a
        for j in range(len(a)):
            xo=q[i]*Ro[j]*numpy.sin(alphaN)
            xi=q[i]*Ri[j]*numpy.sin(alphaN)
            z=q[i]*a[j]*numpy.cos(alphaN)
            y=q[i]*L[j]/2.*numpy.cos(alphaN)
            dPcyl[j]=pi/(q[i]*numpy.cos(alphaN))*(Ro[j]**2*fcan(xo,y,z)-Ri[j]**2*fcan(xi,y,z))
            dPcylb[j]=pi/(q[i]*numpy.cos(alphaN))*(Ro[j]**2*fcanb(xo,y,z)-Ri[j]**2*fcanb(xi,y,z))
        dPcylN=numpy.sin(alphaN)*(numpy.sum(dPcyl)**2+numpy.sum(dPcylb)**2)
        
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi*dPcylold/2.
        
        test=1.       
        while(abs(test)>1e-5):
            N=2.*N
            dalpha=pi/2./float(N)
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            dPcyl=0.*alpha
            dPcylb=0.*alpha
            for j in range(len(a)):
                xo=q[i]*Ro[j]*numpy.sin(alpha)
                xi=q[i]*Ri[j]*numpy.sin(alpha)
                z=q[i]*a[j]*numpy.cos(alpha)
                y=q[i]*L[j]/2.*numpy.cos(alpha)
                dPcyl=dPcyl+pi/(q[i]*numpy.cos(alpha))*(Ro[j]**2*fcan(xo,y,z)-Ri[j]**2*fcan(xi,y,z))
                dPcylb=dPcylb+pi/(q[i]*numpy.cos(alpha))*(Ro[j]**2*fcanb(xo,y,z)-Ri[j]**2*fcanb(xi,y,z))
            dPcylnew=numpy.sum((dPcyl**2+dPcylb**2)*numpy.sin(alpha))+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylnew[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold/Vcylcreuxcan(a,Ri,Ro,L)**2



def R(R,L,x,alp,b,x0):
    p=R*(1.+alp*(numpy.cos(b*2.*pi*(x-x0)/L)))
    N=int(pi/numpy.arcsin(2.125/p))
    p1=2.125/numpy.sin(pi/float(N))
    return p
    
def Vcylcreuxqcq(Ri,L,alp,b,x0,delt):
    V=0.
    dx=L/100.
    x=-L/2.
    while (x<=L/2.):
        Rint=R(Ri,L,x,alp,b,x0)
        Rout=Rint+delt
        V=V+pi*(Rout**2-Rint**2)*dx
        x=x+dx
    return V

def Pcylcouche(q,rho,R,L):
    """
    This function calculates the scaled by volume square and scattering length density P(q)
    of a cylinder of inner length L1 and radius R1 and outer length L2 and radius R2.
    It is thus more versatile than Pcylcreux
    """

    rho0=rho[0]
    rho1=rho[1]
    rho2=rho[2]
    R0=R[0]
    R1=R[1]
    L0=L[0]
    L1=L[1]

    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=numpy.pi/2
        dPcyl0=numpy.sin(alpha0)*((rho2-rho1)*numpy.pi*R1**2*L1*2.*SPspecial.j1(q[i]*R1*numpy.sin(alpha0))*numpy.sin(q[i]*L1*numpy.cos(alpha0)/2.)/(q[i]*R1*numpy.sin(alpha0)*q[i]*L1*numpy.cos(alpha0)/2.)-(-rho1+rho0)*numpy.pi*R0**2*L0*2.*SPspecial.j1(q[i]*R0*numpy.sin(alpha0))*numpy.sin(q[i]*L0*numpy.cos(alpha0)/2.)/(q[i]*R0*numpy.sin(alpha0)*q[i]*L0*numpy.cos(alpha0)/2.))**2

        dPcylN=numpy.sin(alphaN)*((rho2-rho1)*numpy.pi*R1**2*L1*2.*SPspecial.j1(q[i]*R1*numpy.sin(alphaN))*numpy.sin(q[i]*L1*numpy.cos(alphaN)/2.)/(q[i]*R1*numpy.sin(alphaN)*q[i]*L1*numpy.cos(alphaN)/2.)-(-rho1+rho0)*numpy.pi*R0**2*L0*2.*SPspecial.j1(q[i]*R0*numpy.sin(alphaN))*numpy.sin(q[i]*L0*numpy.cos(alphaN)/2.)/(q[i]*R0*numpy.sin(alphaN)*q[i]*L0*numpy.cos(alphaN)/2.))**2

        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(numpy.pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            dPcyl=(rho2-rho1)*numpy.pi*R1*R1*L1*2.*SPspecial.j1(q[i]*R[1]*numpy.sin(alpha))*numpy.sin(q[i]*L1*numpy.cos(alpha)/2.)/(q[i]*R1*numpy.sin(alpha)*q[i]*L[1]*numpy.cos(alpha)/2.)
            dPcyl=dPcyl-(-rho1+rho0)*numpy.pi*R0*R0*L0*2.*SPspecial.j1(q[i]*R0*numpy.sin(alpha))*numpy.sin(q[i]*L0*numpy.cos(alpha)/2.)/(q[i]*R0*numpy.sin(alpha)*q[i]*L0*numpy.cos(alpha)/2.) 
            dPcyl=numpy.sin(alpha)*dPcyl*dPcyl
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]       
    return Pcylold



def Pcylcreuxqcq(q,Ri,L,alp,b,x0,delt):
    """
    contient une erreur en date du 30 avril 2009 connue mais a corriger
    This function calculates the P(q) normalized to one at q=0 of an hollow cylinder of length L inner radius Ri and outer radius Ro
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    Npts=100.
    for i in range(len(q)):
        N=1.
        alpha0=1e-12
        alphaN=pi/2
        
#       dx=L/Npts
        dx=3.7
        x=-L/2.+dx/2.
        ddPcyl0=0.
        while(x<=L/2.):
            Rif=R(Ri,L,x,alp,b,x0)
            Rof=Rif+delt
            xo=q[i]*Rof*numpy.sin(alpha0)
            xi=q[i]*Rif*numpy.sin(alpha0)
            y=q[i]*x*numpy.cos(alpha0)
            ddPcyl0=ddPcyl0+(2.*pi*(Rof**2*SPspecial.j1(xo)/xo-Rif**2*SPspecial.j1(xi)/xi)*numpy.cos(y)*dx)
            x=x+dx      
        dPcyl0=numpy.sin(alpha0)*ddPcyl0**2
        
        x=-L/2.+dx/2.
        ddPcylN=0.
        while(x<=L/2.):
            Rif=R(Ri,L,x,alp,b,x0)
            Rof=Rif+delt
            xo=q[i]*Rof*numpy.sin(alphaN)
            xi=q[i]*Rif*numpy.sin(alphaN)
            y=q[i]*x*numpy.cos(alphaN)
            ddPcylN=ddPcylN+(2.*pi*(Rof**2*SPspecial.j1(xo)/xo-Rif**2*SPspecial.j1(xi)/xi)*numpy.cos(y)*dx)
            x=x+dx       
        dPcylN=numpy.sin(alphaN)*ddPcylN**2
        
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0)/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            x=-L/2.+dx/2.
            ddPcyl=0.*alpha
            while(x<=L/2.):
                Rif=R(Ri,L,x,alp,b,x0)
                Rof=Rif+delt
                xo=q[i]*Rof*numpy.sin(alpha)
                xi=q[i]*Rif*numpy.sin(alpha)
                y=q[i]*x*numpy.cos(alpha)
                ddPcyl=ddPcyl+(2.*pi*(Rof**2*SPspecial.j1(xo)/xo-Rif**2*SPspecial.j1(xi)/xi)*numpy.cos(y)*dx)
                x=x+dx      
            dPcyl=numpy.sin(alpha)*ddPcyl**2
            
            dPcylnew=numpy.sum(dPcyl)+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
    return Pcylold/Vcylcreuxqcq(Ri,L,alp,b,x0,delt)**2

def Vcylcreuxcan(a,Ri,Ro,L):
    return pi*sum(L*(Ro**2-Ri**2))

def dPcylb(qi,R,L,al):
    dPcylb=numpy.sin(al)*(2.*SPspecial.j1(qi*R*numpy.sin(al))*numpy.sin(qi*L*numpy.cos(al)/2.)/(q[i]*R*numpy.sin(al)*qi*L*numpy.cos(al)/2.))**2
    return dPcylb

def Pcylh(q,R,L):
    """
    Optimized version of P11 OS
    This function calculates the P(q) of a cylinder of length L and radius R with two hemispheres of redaisu R as cap ends
    is associated with dPcylh
    """
    Pcylnew=1.*q
    Pcylold=1.*q
    for i in range(len(q)):
        N=1.
        alpha0=numpy.array([1e-12])
        alphaN=numpy.array([pi/2])
        dPcyl0=dPcylh(q[i],R,L,alpha0)
        dPcylN=dPcylh(q[i],R,L,alphaN)
        dPcylold=(dPcyl0+dPcylN)/2.
        Pcylold[i]=pi/2*dPcylold
        test=1.
        qi=q[i]
        while(abs(test)>1e-4):
            N=2.*N
            dalpha=(pi/2.-alpha0[0])/N
            alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
            dPcyl=dPcylh(qi,R,L,alpha)
            dPcylnew=dPcyl+dPcylold
            dPcylold=dPcylnew
            Pcylnew[i]=dalpha*dPcylnew
            test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
            Pcylold[i]=Pcylnew[i]
        Pcylold[i]=Pcylold[i]/(1.+4./3.*R/L)**2
    return Pcylold

def dPcylh(qi,R,L,al):
    """
    Subfunction of Pcylh
    """
    dPcylh=0.
    dPcylh1=0.*al
    for j in range(len(al)):        
        dPcylh1[j]=2.*SPspecial.j1(qi*R*numpy.sin(al[j]))*numpy.sin(qi*L*numpy.cos(al[j])/2.)/(qi*R*numpy.sin(al[j])*qi*L*numpy.cos(al[j])/2.)
        dPcylh1[j]=dPcylh1[j]+4.*R/L*numpy.cos(qi*L/2.*cos(al[j]))*(numpy.sin(qi*R)-qi*R*numpy.cos(qi*R))/(qi*R)**3
        dPcylh1[j]=dPcylh1[j]-4.*R/L*numpy.sin(qi*L/2.*cos(al[j]))*ddPcylh(qi,R,al[j])/(qi*R*numpy.sin(al[j]))
        dPcylh=dPcylh+dPcylh1[j]**2*numpy.sin(al[j])        
    return dPcylh

def ddPcylh(qi,R,al):
    """
    Sub-sub-function of dPcylh
    """
    N=1
    t0=0.
    t1=1.
    d3Pcylh0=numpy.sin(qi*R*t0*numpy.cos(al))*SPspecial.j1(qi*R*numpy.sin(al)*(1.-t0**2)**(0.5))*(1.-t0**2)**(0.5)
    d3Pcylh1=numpy.sin(qi*R*t1*numpy.cos(al))*SPspecial.j1(qi*R*numpy.sin(al)*(1.-t1**2)**(0.5))*(1.-t1**2)**(0.5)
    d3Pcylhold=(d3Pcylh0+d3Pcylh1)/2.
    ddPcylhold=d3Pcylhold
    test=1.
    while(abs(test)>0.01):
        N=2.*N
        dt=1./N
        t=numpy.arange(dt,1.,2.*dt)
        d3Pcylhnew=d3Pcylhold+numpy.sum(numpy.sin(qi*R*t*numpy.cos(al))*SPspecial.j1(qi*R*numpy.sin(al)*(1.-t**2)**(0.5))*(1.-t**2)**(0.5))
        d3Pcylhold=d3Pcylhnew
        ddPcylhnew=dt*d3Pcylhnew
        test=(ddPcylhnew-ddPcylhold)/ddPcylhold
        ddPcylhold=ddPcylhnew
    return ddPcylhold

###################################################################################################################
################################                    POLYEDRES                   ###################################
###################################################################################################################
#Toutes les fonctions annexes liees au calcul du Pdq du polyedre
###################################################################################################################

def pente(Sommets):
    S=numpy.array(Sommets)
    a=0.*S[:,0]
    b=0.*S[:,1]
    for i in range(len(S)-1):
        dx=S[i+1,0]-S[i,0]
        dy=S[i+1,1]-S[i,1]
        if dy!=0.:
            if dx!=0.:
                a[i]=dx/dy
                b[i]=S[i,0]-a[i]*S[i,1]
            else:
                a[i]=0.
                b[i]=S[i,0]
        else:
            b[i]=0.
            a[i]=1.e300
    return a,b


def TFS(Sommets,a,b,qx,qy):
    "returns the ff of polygon for a matrix qx,qy"
    S=numpy.array(Sommets)
    TFS=numpy.zeros((len(qx),len(qy)),complex)
    for i in range(len(a)-1):
        if a[i]!=1.e300:
            for k in range(len(qx)):
                tet=b[i]*qx[k]
                pr=complex(numpy.cos(tet),numpy.sin(tet))
                for l in range(len(qy)):
                    II=numpy.sinc((qy[l]+a[i]*qx[k])*S[i+1,1]/pi)*S[i+1,1]-numpy.sinc((qy[l]+a[i]*qx[k])*S[i,1]/pi)*S[i,1]
                    I=-2*numpy.sinc(0.5*(qy[l]+a[i]*qx[k])*(S[i+1,1]-S[i,1])/pi)*(0.5*(S[i+1,1]-S[i,1]))*numpy.sin(0.5*(qy[l]+a[i]*qx[k])*(S[i+1,1]+S[i,1]))
                    add=pr*complex(I,II)/qx[k]                    
                    TFS[k,l]=TFS[k,l]-add
    return TFS

def TFSpi(Sommets,a,b,qx,qy):
    "returns the ff of polygon for a matrix qx,qy"
    S=numpy.array(Sommets)
    TFS=numpy.zeros((len(qx)),complex)
    for i in range(len(a)-1):
        if a[i]!=1.e300:
            for k in range(len(qx)):
                tet=b[i]*qx[k]
                pr=complex(numpy.cos(tet),numpy.sin(tet))
                II=numpy.sinc((qy[k]+a[i]*qx[k])*S[i+1,1]/pi)*S[i+1,1]-numpy.sinc((qy[k]+a[i]*qx[k])*S[i,1]/pi)*S[i,1]
                I=-2*numpy.sinc(0.5*(qy[k]+a[i]*qx[k])*(S[i+1,1]-S[i,1])/pi)*(0.5*(S[i+1,1]-S[i,1]))*numpy.sin(0.5*(qy[k]+a[i]*qx[k])*(S[i+1,1]+S[i,1]))
                add=pr*complex(I,II)/qx[k]                    
                TFS[k]=TFS[k]-add
    return TFS

def TFSs(Sommets,a,b,qx,qy):
    "returns the ff of polygon for a scalar qx qy"
    S=numpy.array(Sommets)
    TFS=0.+0.j
    for i in range(len(a)-1):
        if a[i]!=1.e300:
            tet=b[i]*qx
            pr=complex(numpy.cos(tet),numpy.sin(tet))
            II=numpy.sinc((qy+a[i]*qx)*S[i+1,1]/pi)*S[i+1,1]-numpy.sinc((qy+a[i]*qx)*S[i,1]/pi)*S[i,1]
            I=-2*numpy.sinc(0.5*(qy+a[i]*qx)*(S[i+1,1]-S[i,1])/pi)*(0.5*(S[i+1,1]-S[i,1]))*numpy.sin(0.5*(qy+a[i]*qx)*(S[i+1,1]+S[i,1]))
            add=pr*complex(I,II)/qx
            TFS=TFS-add
    return TFS


def PS(a,b):
    "return the scalar product of two vetors"
    return sum(a*b)

def PV(u,v):
    "return the vector orthogonal to u and v"
    return numpy.array([u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]])

def Normale(Face):
    "returns the oriented and normalized normal to the face"
    u=0.5*(Face[0]-Face[1])
    u=u/sqrt(PS(u,u))
    v=0.5*(Face[1]-Face[2])
    s=PV(u,v)
    w=s/sqrt(PS(s,s))
    psign=PS(s,Face[0])
    sign=abs(psign)/psign
    w=w*sign
    v=PV(w,u)
    return u,v,w

def ProjSommets(Face):
    PFace=numpy.zeros((len(Face)+1,3),float)
    for i in range(len(Face)):
        PFace[i][0]=PS(Face[i],Normale(Face)[0])
        PFace[i][1]=PS(Face[i],Normale(Face)[1])
        PFace[i][2]=PS(Face[i],Normale(Face)[2])
    PFace[-1][0]=PFace[0][0]
    PFace[-1][1]=PFace[0][1]
    PFace[-1][2]=PFace[0][2]   
    return PFace


def qvectors(q,teta,phi):
    qv=numpy.zeros((3),float)
    qv[0]=q*numpy.cos(teta)*numpy.sin(phi)
    qv[1]=q*numpy.cos(teta)*numpy.cos(phi)
    qv[2]=q*numpy.sin(teta)
    return qv

def angle(teta,phi):
    qv=numpy.zeros((3),float)
    qv[0]=numpy.cos(teta)*numpy.sin(phi)
    qv[1]=numpy.cos(teta)*numpy.cos(phi)
    qv[2]=numpy.sin(teta)
    return qv

def qvectorspi(q,teta,phi):
    qv0=q*numpy.cos(teta)*numpy.sin(phi)
    qv1=q*numpy.cos(teta)*numpy.cos(phi)
    qv2=q*numpy.sin(teta)
    return qv0,qv1,qv2

def Surf(S):
    Surf=0.
    for i in range(len(S)-1):
        Surf=Surf+(S[i+1,0]-S[i,0])*(S[i+1,1]+S[i,1])
    return 0.5*Surf    


#############################
#Les solides de Platon
#############################
def Tetraedre(a):
    "returns the 3D coordinates of the 4 summits of a tetraedreof side length a"
    R=numpy.array([[0.,numpy.sqrt(3.)/3.,-0.5],[0.5,-numpy.sqrt(3.)/6.,-0.5],[-0.5,-numpy.sqrt(3.)/6.,-0.5],[0.,0.,numpy.sqrt(2./3.)-0.5]])
    R=a*R
    return R

def FacesTetraedre(R):
    "returns the faces of the tetraedre"
    F1=(R[0],R[1],R[2])
    F2=(R[1],R[2],R[3])
    F3=(R[2],R[0],R[3])
    F4=(R[3],R[1],R[0])
    Faces=(F1,F2,F3,F4)
    return Faces

def Pdqtetra(q,a,N):
    sign=numpy.array([1.,1.,1.,1.])
    R=Tetraedre(a)
    Facepoly=FacesTetraedre(R)
    return Pdqpoly(q,Facepoly,sign,N)

def Hexaedre(a):
    "returns the 3D coordinates of the 8 summits of an hexaedre side length a"
    R=numpy.array([[1.,1.,1.],[1.,-1.,1.],[1.,1.,-1.],[1.,-1.,-1.],[-1.,1.,1.],[-1.,-1.,1.],[-1.,1.,-1.],[-1.,-1.,-1.]])
    R=a/2.*R
    return R

def Faceshexaedre(R):
    "returns the 6 faces of the hexaedre"
    F1=(R[0],R[1],R[3],R[2])
    F2=(R[0],R[4],R[6],R[2])
    F3=(R[0],R[4],R[5],R[1])
    F4=(R[7],R[5],R[1],R[3])
    F5=(R[7],R[6],R[2],R[3])
    F6=(R[7],R[5],R[4],R[6])    
    Faces=(F1,F2,F3,F4,F5,F6)
    return Faces

def Pdqhexa(q,a,N):
    sign=numpy.array([1.,1.,1.,1.,1.,1.])
    R=Hexaedre(a)
    Facepoly=Faceshexaedre(R)
    return Pdqpoly1(q,Facepoly,sign,N)

def Octaedre(a):
    "returns the 3D coordinates of the 6 summits of a octaaedre of side length a"
    R=numpy.array([[1.,0.,0.],[0.,1.,0.],[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.],[0.,0.,-1.]])
    R=a/numpy.sqrt(2.)*R
    return R

def Facesoctaedre(R):
    "returns the faces of the octaedre"
    F1=(R[0],R[1],R[4])
    F2=(R[1],R[2],R[4])
    F3=(R[2],R[3],R[4])
    F4=(R[3],R[0],R[4])    
    F5=(R[0],R[1],R[5])
    F6=(R[1],R[2],R[5])
    F7=(R[2],R[3],R[5])
    F8=(R[3],R[0],R[5])    
    Faces=(F1,F2,F3,F4,F5,F6,F7,F8)
    return Faces

def Pdqocta(q,a,N):
    sign=numpy.array([1.,1.,1.,1.,1.,1.,1.,1.])
    R=Octaedre(a)
    Facepoly=Facesoctaedre(R)
    return Pdqpoly1(q,Facepoly,sign,N)

#############################
#Manque le dodecaedre et licosaedre si quelqu un a le courage d'entrer les coordonnees des sommets et la liste des faces
#############################

###############################################
# Polyedres de longueur L et de section variable
###############################################


def Hexaedre_cyl(a,L):
    "return the 3D coordinates of the 12 submits of an hexaedre_cyl"
    P=numpy.array([[a,0.,-L/2.],[a/2.,a*sqrt(3.)/2.,-L/2.],[-a/2.,a*sqrt(3.)/2.,-L/2],[-a,0.,-L/2.],[-a/2.,-a*sqrt(3.)/2.,-L/2],[a/2.,-a*sqrt(3.)/2,-L/2.]])
    Q=P+numpy.array([0,0,L])
    R=numpy.array([P,Q])
    return R

def Hexaedre_def(a,b,L):
    "return the 3D coordinates of the 12 submits of an hexaedre_cyl deforme (a,b) au lieu de (a,a)"
    P=numpy.array([[a+b/2.,0.,-L/2.],[a/2.+b/2.,a*sqrt(3.)/2.,-L/2.],[-a/2.-b/2.,a*sqrt(3.)/2.,-L/2],[-a-b/2.,0.,-L/2.],[-a/2.-b/2.,-a*sqrt(3.)/2.,-L/2],[a/2.+b/2.,-a*sqrt(3.)/2,-L/2.]])
    Q=P+numpy.array([0,0,L])
    R=numpy.array([P,Q])
    return R

def FacesHexa(R):
    "return the faces of the hexaedre_cyl R, fonctionne pour le deforme egalement"
    F1=(R[0][0],R[0][1],R[0][2],R[0][3],R[0][4],R[0][5])
    F2=(R[1][0],R[1][1],R[1][2],R[1][3],R[1][4],R[1][5])
    F3=(R[0][0],R[0][1],R[1][1],R[1][0])
    F4=(R[0][1],R[0][2],R[1][2],R[1][1])
    F5=(R[0][2],R[0][3],R[1][3],R[1][2])
    F6=(R[0][3],R[0][4],R[1][4],R[1][3])
    F7=(R[0][4],R[0][5],R[1][5],R[1][4])
    F8=(R[0][5],R[0][0],R[1][0],R[1][5])
    Faces=(F1,F2,F3,F4,F5,F6,F7,F8)    
    return Faces

def FacesHexa_creux_def(R,Rin):
    "return the faces of the hexaedre_cyl R"
    F1=(R[0][0],R[0][1],R[0][2],R[0][3],R[0][4],R[0][5])
    F2=(R[1][0],R[1][1],R[1][2],R[1][3],R[1][4],R[1][5])
    F3=(R[0][0],R[0][1],R[1][1],R[1][0])
    F4=(R[0][1],R[0][2],R[1][2],R[1][1])
    F5=(R[0][2],R[0][3],R[1][3],R[1][2])
    F6=(R[0][3],R[0][4],R[1][4],R[1][3])
    F7=(R[0][4],R[0][5],R[1][5],R[1][4])
    F8=(R[0][5],R[0][0],R[1][0],R[1][5])
    F9=(Rin[0][0],Rin[0][1],Rin[0][2],Rin[0][3],Rin[0][4],Rin[0][5])
    F10=(Rin[1][0],Rin[1][1],Rin[1][2],Rin[1][3],Rin[1][4],Rin[1][5])
    F11=(Rin[0][0],Rin[0][1],Rin[1][1],Rin[1][0])
    F12=(Rin[0][1],Rin[0][2],Rin[1][2],Rin[1][1])
    F13=(Rin[0][2],Rin[0][3],Rin[1][3],Rin[1][2])
    F14=(Rin[0][3],Rin[0][4],Rin[1][4],Rin[1][3])
    F15=(Rin[0][4],Rin[0][5],Rin[1][5],Rin[1][4])
    F16=(Rin[0][5],Rin[0][0],Rin[1][0],Rin[1][5])    
    Faces=(F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13,F14,F15,F16)    
    return Faces


def Cubedre(a,L):
    "return the 3D coordinates of the 6 submits of a cube"
    P=numpy.array([[a/2,-a/2,-L/2.],[a/2.,a/2.,-L/2.],[-a/2.,a/2.,-L/2],[-a/2,-a/2,-L/2.]])
    Q=P+numpy.array([0,0,L])
    R=numpy.array([P,Q])
    return R

def Decaedre(a,b):
    "returne the 3D cartesian coordinates of the seven sumits of decahedra"
    R=numpy.array([[a,0.,0],[a*cos(2.*pi/5.),a*sin(2.*pi/5.),0. ],[a*cos(4.*pi/5.),a*sin(4.*pi/5.),0. ],[a*cos(6.*pi/5.),a*sin(6.*pi/5.),0. ],[a*cos(8.*pi/5.),a*sin(8.*pi/5.),0.],[0,0.,b],[0,0.,-b]])
    return R
    
def FacesDeca(R):
    "return the faces of the decaedra R"
    F1=(R[0],R[5],R[1])
    F2=(R[0],R[6],R[1])
    F3=(R[1],R[5],R[2])
    F4=(R[1],R[6],R[2])
    F5=(R[2],R[5],R[3])
    F6=(R[2],R[6],R[3])
    F7=(R[3],R[5],R[4])
    F8=(R[3],R[6],R[4])
    F9=(R[4],R[5],R[0])
    F10=(R[4],R[6],R[0])
    Faces=(F1,F2,F3,F4,F5,F6,F7,F8,F9,F10)
    sign=(1,1,1,1,1,1,1,1,1,1)
    return Faces,sign

def Triedre(a,L):
    "return the 3D coordinates of the 6 submits of a triedre"
    P=numpy.array([[a/2,-a/2/numpy.sqrt(3),-L/2.],[0.,a/numpy.sqrt(3.),-L/2.],[-a/2.,-a/2/numpy.sqrt(3),-L/2]])
    Q=P+numpy.array([0,0,L])
    R=numpy.array([P,Q])
    return R


def Facescube(R):
    "return the 6 faces of the Cubedre "
    F1=(R[0][0],R[0][1],R[0][2],R[0][3])
    F2=(R[1][0],R[1][1],R[1][2],R[1][3])
    F3=(R[0][0],R[0][1],R[1][1],R[1][0])
    F4=(R[0][1],R[0][2],R[1][2],R[1][1])
    F5=(R[0][2],R[0][3],R[1][3],R[1][2])
    F6=(R[0][3],R[0][0],R[1][0],R[1][3])
    Faces=(F1,F2,F3,F4,F5,F6)    
    return Faces

def FaceTri(R):
    "return the 5 faces of the triedre"
    F1=(R[0][0],R[0][1],R[0][2])
    F2=(R[1][0],R[1][1],R[1][2])
    F3=(R[0][0],R[0][1],R[1][1],R[1][0])
    F4=(R[0][1],R[0][2],R[1][2],R[1][1])
    F5=(R[0][2],R[0][0],R[1][0],R[1][2])
    Faces=(F1,F2,F3,F4,F5)    
    return Faces


            
def PdqHexa3(q,R,L,N):
    Poly=Hexaedre(R,L)
    FacePoly1=FacesHexa(Poly)
    FacePoly=(FacePoly1[0],FacePoly1[2],FacePoly1[3],FacePoly1[4])    
# Cette partie est commune a tout polyedre mais  integre  la symetries de faces    
    PPoly=[]
    A=[]
    B=[]
    U=[]
    V=[]
    W=[]
    Sign0=[]   
    for j in range(len(FacePoly)):
        Ppoly0=ProjSommets(FacePoly[j])
        PPoly.append(Ppoly0)
        A.append(pente(Ppoly0)[0])
        B.append(pente(Ppoly0)[1])
        U.append(Normale(FacePoly[j])[0])
        V.append(Normale(FacePoly[j])[1])
        W.append(Normale(FacePoly[j])[2])
        Sign0.append(abs(Surf(Ppoly0))/Surf(Ppoly0))
    
    eps=1e-5
    N2=N
    N1=3*N2
    dteta=pi/2./float(N1)
    dphi=pi/3./float(N2)
    
    Pdq=0.*q
#On passe par chaque norme de vecteur de diffusion
    for i in range(len(q)):
        #On commence a faire tourner teta et phi
        teta=-pi/2.+dteta/2.
        while teta<0.:
            phi=dphi/2.+eps
            while phi<pi/3.:
                qv=qvectors(q[i],teta,phi)
                fdqij=complex(0.,0.)
                for j in range(len(FacePoly)):                    
                    Ppoly=numpy.array(PPoly[j])
                    a=numpy.array(A[j])
                    b=numpy.array(B[j])
                    sign0=Sign0[j]
                    u=numpy.array(U[j])
                    v=numpy.array(V[j])
                    w=numpy.array(W[j])
                    
#coeur du calcul par lequel toute boucle doit passer                    
                    qn=PS(qv,w)
                    qx=PS(qv,u)
                    qy=PS(qv,v)                    
                    fdqij1=complex(0.,-qn/q[i]**2)
                    
# Le facteur 2 de fdqij2 vient de la symetrie des faces de l hexaedre, il doit etre supprime dans le cas general                    
                    fdqij2=2.*numpy.sin(PS(qn*w,FacePoly[j][0]))                  
                    fdqij3=TFSs(Ppoly,a,b,qx,qy)                   
                    fdqij=fdqij+fdqij1*fdqij2*fdqij3*sign0
   

                Pdq[i]=Pdq[i]+(numpy.imag(fdqij)**2+numpy.real(fdqij)**2)*numpy.cos(teta)
                phi=phi+dphi
            teta=teta+dteta   
        Pdq[i]=Pdq[i]*dteta*dphi
    return 12.*Pdq/(4.*pi)/(R**2*L*1.5*sqrt(3.))**2
            
def PdqHexacoq(q,Ri,Ro,L,N):
    Polyi=Hexaedre(Ri,L)
    Polyo=Hexaedre(Ro,L)
    FacePolyi1=FacesHexa(Polyi)
    FacePolyo1=FacesHexa(Polyo)
    FacePolyi=(FacePolyi1[0],FacePolyi1[2],FacePolyi1[3],FacePolyi1[4])
    FacePolyo=(FacePolyo1[0],FacePolyo1[2],FacePolyo1[3],FacePolyo1[4])
    
#Cette partie est commune a tout polyedre mais n integre pas les symetries de faces    
    PPolyi=[]
    Ai=[]
    Bi=[]
    Ui=[]
    Vi=[]
    Wi=[]
    Sign0i=[]
    
    PPolyo=[]
    Ao=[]
    Bo=[]
    Uo=[]
    Vo=[]
    Wo=[]
    Sign0o=[]
    
    for j in range(len(FacePolyi)):
        Ppoly0i=ProjSommets(FacePolyi[j])
        PPolyi.append(Ppoly0i)
        Ai.append(pente(Ppoly0i)[0])
        Bi.append(pente(Ppoly0i)[1])
        Ui.append(Normale(FacePolyi[j])[0])
        Vi.append(Normale(FacePolyi[j])[1])
        Wi.append(Normale(FacePolyi[j])[2])
        Sign0i.append(abs(Surf(Ppoly0i))/Surf(Ppoly0i))

    for j in range(len(FacePolyo)):
        Ppoly0o=ProjSommets(FacePolyo[j])
        PPolyo.append(Ppoly0o)
        Ao.append(pente(Ppoly0o)[0])
        Bo.append(pente(Ppoly0o)[1])
        Uo.append(Normale(FacePolyo[j])[0])
        Vo.append(Normale(FacePolyo[j])[1])
        Wo.append(Normale(FacePolyo[j])[2])
        Sign0o.append(abs(Surf(Ppoly0o))/Surf(Ppoly0o))
        
    eps=1e-3
    N2=N
    N1=3*N2
    dteta=pi/2./float(N1)
    dphi=pi/3./float(N2)
    
    Pdq=0.*q
#On passe par chaque norme de vecteur de diffusion
    for i in range(len(q)):
        #On commence a faire tourner teta et phi
        teta=-pi/2.+dteta/2.
        while teta<0.:
            phi=dphi/2.+eps
            while phi<pi/3.:
                qv=qvectors(q[i],teta,phi)
                fdqiji=complex(0.,0.)
                fdqijo=complex(0.,0.)
                for j in range(len(FacePolyi)):                    
                    Ppolyi=numpy.array(PPolyi[j])
                    ai=numpy.array(Ai[j])
                    bi=numpy.array(Bi[j])
                    sign0i=Sign0i[j]
                    ui=numpy.array(Ui[j])
                    vi=numpy.array(Vi[j])
                    wi=numpy.array(Wi[j])
                    
                    Ppolyo=numpy.array(PPolyo[j])
                    ao=numpy.array(Ao[j])
                    bo=numpy.array(Bo[j])
                    sign0o=Sign0o[j]
                    uo=numpy.array(Uo[j])
                    vo=numpy.array(Vo[j])
                    wo=numpy.array(Wo[j])
                    
#coeur du calcul par lequel toute boucle doit passer                    
                    qni=PS(qv,wi)
                    qxi=PS(qv,ui)
                    qyi=PS(qv,vi)
                    
                    qno=PS(qv,wo)
                    qxo=PS(qv,uo)
                    qyo=PS(qv,vo)
                    
                    fdqiji1=complex(0.,-qni/q[i]**2)
# Le facteur 2 de fdqij2 vient de la symetrie des faces de l hexaedre, il doit etre supprime dans le cas general
                    fdqiji2=2.*numpy.sin(PS(qni*wi,FacePolyi[j][1]))                  
                    fdqiji3=TFSs(Ppolyi,ai,bi,qxi,qyi)                   
                    fdqiji=fdqiji+fdqiji1*fdqiji2*fdqiji3*sign0i
   
                    fdqijo1=complex(0.,-qno/q[i]**2)
                    fdqijo2=2.*numpy.sin(PS(qno*wo,FacePolyo[j][1]))                  
                    fdqijo3=TFSs(Ppolyo,ao,bo,qxo,qyo)                   
                    fdqijo=fdqijo+fdqijo1*fdqijo2*fdqijo3*sign0o

                    fdqij=fdqijo-fdqiji
                    
                Pdq[i]=Pdq[i]+(numpy.numpy.imag(fdqij)**2+numpy.real(fdqij)**2)*numpy.cos(teta)
                phi=phi+dphi
            teta=teta+dteta   
        Pdq[i]=Pdq[i]*dteta*dphi
    return 12.*Pdq/(4.*pi)/((Ro**2-Ri**2)*L*1.5*sqrt(3.))**2

def SHexa(R,L):
    return 3.*sqrt(3)*R**2+6*R*L

def Scyl(R,L):
    return 2.*pi*R**2+2*pi*R*L

def VHexa(R,L):
    return 1.5*sqrt(3)*R**2*L

def Vcyl(R,L):
    return pi*R**2*L

#################################################################################################################################
#################################################################################################################################
def Pdqpoly(q1,FacePoly,sign,N):
#Ce programme calcul le Pdq d'un polyedre quelconque definie par ces faces et le signe (+1 pour outer, -1 pour inner de celles-ci)    
#On commence par ajouter a la fin une petite valeur de q pour normer au volume carre"""
    q=[]
    for i in range(len(q1)):
           q.append(q1[i])
    q.append(1.e-8)               
    q=numpy.array(q)
    q[-1]=1e-8
    PPoly=[]
    A=[]
    B=[]
    U=[]
    V=[]
    W=[]
    Sign0=[]   
    for j in range(len(FacePoly)):
        Ppoly0=ProjSommets(FacePoly[j])
        PPoly.append(Ppoly0)
        A.append(pente(Ppoly0)[0])
        B.append(pente(Ppoly0)[1])
        U.append(Normale(FacePoly[j])[0])
        V.append(Normale(FacePoly[j])[1])
        W.append(Normale(FacePoly[j])[2])
        Sign0.append(abs(Surf(Ppoly0))/Surf(Ppoly0))
    
    eps=1e-5
#Il est possible d'ameliorer l'integration en faisant des pas en d(cos(teta)) mais c'est plus lours a programmer
    N2=N
    N1=N2
    dteta=pi/2./float(N1)
    dsinteta=1./float(N1)
    dphi=2.*pi/float(N2)
    
    Pdq=0.*q
#On passe par chaque norme de vecteur de diffusion
    for i in range(len(q)):
        #On commence a faire tourner teta et phi
        teta=-pi/2.+dteta/2.
        sinteta=-1
        while sinteta<0.:
            teta=arcsin(sinteta)
            phi=dphi/2.+eps
            while phi<2.*pi:
                qv=qvectors(q[i],teta,phi)
                fdqij=complex(0.,0.)
                for j in range(len(FacePoly)):                    
                    Ppoly=numpy.array(PPoly[j])
                    a=numpy.array(A[j])
                    b=numpy.array(B[j])
                    sign0=Sign0[j]
                    u=numpy.array(U[j])
                    v=numpy.array(V[j])
                    w=numpy.array(W[j])
                    
#coeur du calcul par lequel toute boucle doit passer                    
                    qn=PS(qv,w)
                    qx=PS(qv,u)
                    qy=PS(qv,v)                    
                    fdqij1=complex(0.,-qn/q[i]**2)
                    
# Le facteur 2 de fdqij2 vient de la symetrie des faces de l hexaedre, il doit etre supprime dans le cas general                    
                    fdqij2=complex(numpy.cos(PS(qn*w,FacePoly[j][0])),numpy.sin(PS(qn*w,FacePoly[j][0])))                 
                    fdqij3=TFSs(Ppoly,a,b,qx,qy)                   
                    fdqij=fdqij+fdqij1*fdqij2*fdqij3*sign0*sign[j]
   

                Pdq[i]=Pdq[i]+(numpy.imag(fdqij)**2+numpy.real(fdqij)**2)*dsinteta
                phi=phi+dphi
            sinteta=sinteta+dsinteta  
        Pdq[i]=Pdq[i]*dphi
    """On normalise au dernier point"""
    Pdq1=0.*q1
    Pdq1=Pdq/Pdq[-1]    
    return Pdq1



##
##Form factor obtained from size distributions
##


def fPolySphere_int(R,q,Dfunc,Arg):
    par=(R,Arg[1],Arg[2])
    return Dfunc(par)*getV(R)*getV(R)*P1(q,R)

def PolySphere_int(q,Dfunc,par):
    return SPintegrate.quad(fPolySphere_int,par[0][0],par[0][len(par[0])-1],(q,Dfunc,par))[0]


def P1dist(q,Dfunc,par):
    """
    This function returns the form factor of a dsitribution of spheres of
    radius R for q
    """
    P=numpy.zeros(len(q),float)

    D=Dfunc(par)[0]
    f2=SPintegrate.trapz(D,par[0])
    for i in numpy.arange(len(q)):
        P[i]=SPintegrate.trapz(P1(q[i],par[0])*D*getV(par[0])*getV(par[0]),par[0])
    return P,P/f2


def P5dist(q,type,rm,sigma,e):
    """
    This function returns the form factor of a dsitribution of ellipses with
    semi-axes R, R and e*R for q
    """
    P=numpy.zeros(len(q),float)
    P=asarray(P)
    R=arange(100)
    R=R+1
    R=asarray(R)
    R=(R*(rm+5.*sigma))/100.0
    if type == 1:
        D=Dgauss(R,rm,sigma)
    elif type == 2:
        D=Dlognormal(R,rm,sigma)
    elif type == 3:
        D=Dshultz(R,rm,sigma)
    else :
        D=Dgauss(R,rm,sigma)
    f2=Trapz(D*getV(R),R)
    for tq in q:
        f1=Trapz(P5(tq,R,e)*D*getV(R)*getV(R),R)
        P[sum(where(q==tq,arange(len(q)),numpy.zeros(len(q))))]=f1/f2

    return P,R,D




def P1Sqdist(q,type,rm,sigma,eta,tao):
    """
    This function returns the form factor of a dsitribution of spheres of
    radius R for q
    """
    P=numpy.zeros(len(q),float)
    P=asarray(P)
    R=arange(100)
    R=R+1
    R=asarray(R)
    R=(R*(rm+5.*sigma))/100.0
    if type == 1:
        D=Dgauss(R,rm,sigma)
    elif type == 2:
        D=Dlognormal(R,rm,sigma)
    elif type == 3:
        D=Dshultz(R,rm,sigma)
    else :
        D=Dgauss(R,rm,sigma)
    f2=Trapz(D*getV(R),R)
    for tq in q:
        f1=Trapz(P1(tq,R)*D*getV(R)*getV(R)*SqSticky(tq,R,eta,tao),R)
        P[sum(where(q==tq,arange(len(q)),numpy.zeros(len(q))))]=f1/f2

    return P,R,D



def SqSticky(q,R,eta,tao):
    """
    This function computes the Baxter structure factor
    eta is the volume fraction
    tao is the sticky factor
    R is the radius in A
    q is an array of scattering vectors A-1
    """
    temp0=(tao/eta) + ( 1./(1.- eta) )
    temp1 = 6.*temp0 + numpy.sqrt((36.*temp0*temp0)-((12.*(1.+eta/2.))/(eta*(1.-eta)*(1.-eta))))
    temp2 = 6.*temp0 - numpy.sqrt((36.*temp0*temp0)-((12.*(1.+eta/2.))/(eta*(1.-eta)*(1.-eta))))
    if  temp1 < temp2:
       lambd=temp1
    else:
       lambd=temp2
    mu=lambd*eta*(1. - eta)
    alpha= ( (1. + 2.* eta)- (lambd*eta*(1. - eta)) )/( (1.- eta)*(1. - eta) )
    beta=( -3.*eta + (lambd*eta*(1. - eta)))/( 2.*(1.-eta)*(1.- eta) )
    k=2.*q*R
    NSIN=numpy.sin(k)
    NCOS=numpy.cos(k)

    A=(1. + 12.*eta*( (( ( (1. + 2.* eta)- (lambd*eta*(1. - eta)) )/( (1.- eta)*(1. - eta) )))*( (NSIN-k*NCOS)/(k*k*k)) + (( ( -3.*eta + (lambd*eta*(1. - eta)))/( 2.*(1.-eta)*(1.- eta) )))*( (1.- NCOS)/(k*k) )-( lambd/12. )* ((NSIN)/k) ))
    B= 12.*eta*( alpha*( ( 0.5*k**2.0 - k*NSIN + 1.-NCOS )/k**3.0 ) + (beta)*( (k - NSIN)/k**2 )-(lambd/12.)*(1.-NCOS)/k )

    return 1. /(A*A+B*B)


def Idqc(q,rho1,rho2,rho3,al1,al2,al3,Phi1,Phi2,RG0,RGsig,R1,sigR1,R3,sigR3,taoL,taoS,scale,reduc):
    Npas=50
    deltaRG=RG0*(1.+7.*RGsig)/Npas
    Phi3=1.-Phi1-Phi2
    Phi3c=Phi3/(Phi3+Phi2)
    Phi2c=Phi2/(Phi3+Phi2)
    rhoc=(Phi2*rho2*al2+Phi3*rho3*al3)/(Phi2+Phi3)
    rhoG=Phi1*rho1*al1+Phi2*rho2*al2+Phi3*rho3*al3

    def Vol(r):
        V=getV(r)*1.e-30
        return V

    def Ilat(q,rm,sig,eta,tao):
        Np=50
        if rm-3.*sig<=0.0:
            rmin=1e-10
        else:
            rmin=rm-3.*sig
        r=rmin
        deltar=6.*sig/float(Np)
        I=numpy.zeros(len(q))
        VTot=0.
        for i in range (Np):
            arg=[r,rm,sig]
            Dgl=Dgauss(arg)[0]
            sql=SqSticky(q,r,eta,tao)
            I=I+Vol(r)*Vol(r)*P1(q,r)*sql*Dgl
            VTot=VTot+Vol(r)*Dgl
            r=r+deltar
        I=I/VTot
        return I

    def Isil(q,rm,sig,eta,tao):
        Np=50
        if rm-3.*sig<=0.0:
            rmin=1e-10
        else:
            rmin=rm-3.*sig
        r=rmin
        deltar=6.*sig/float(Np)
        I=numpy.zeros(len(q))
        VTot=0.
        for i in range (Np):
            sqS=SqSticky(q,r,eta,tao)
            arg=[r,rm,sig]
            Dgs=Dgauss(arg)[0]
            I=I+Vol(r)*Vol(r)*P1(q,r)*sqS*Dgs
            VTot=VTot+Vol(r)*Dgs
            r=r+deltar
        I=I/VTot
        return I
    I1c=numpy.zeros(len(q))
    I1b=numpy.zeros(len(q))
    VGTot=0.
    RG=1.
    Ilatex=Ilat(q,R1,sigR1,Phi1,taoL)
    Isilice=Isil(q,R3,sigR3,Phi2,taoS)
    if reduc=='False':
        Pphi=Phi2
    elif reduc=='True':
        Pphi=Phi3
    for i in range(Npas):
        VG=Vol(RG)
        arg=[RG,RG0,RGsig]
        Dgg=Dlognormal(arg)[0]
        #I1c=I1c+VG*(Phi1*(rho1*al1-rhoc)**2.*Ilatex+Phi3*(rho3*al3-rho2*al2)**2.*Isilice+VG*rhoG**2.*Pr(RG,q))*d_lognormal(RG,RG0,RGsig)
        I1c=I1c+VG*(Phi1*(rho1*al1-rhoc)**2.*Ilatex+Pphi*(rho3*al3-rho2*al2)**2.*Isilice+VG*rhoG**2.*P1(q,RG))*Dgg
        VGTot=VGTot+VG*Dgg
        RG=RG+deltaRG


    I1c=I1c/(VGTot*(Phi1*al1+Phi2*al2+Phi3*al3))

    return scale*I1c*1e-2

## Modele functions
## These functions should take only one parameter list and return the scattering intensity in cm-1
##
##

##def normf(a,s,x):
##    t1=(a**2.*s*(-8.*a**5.*numpy.e**((a**2. + x**2.)/ (a**2.*s**2.))*numpy.sqrt(numpy.pi)* SPspecial.erf((a - x)/(a*s)) - s*(2.*numpy.e**((2.*x)/(a*s**2.))* (a**5.*(4. + 28.*s**2. + 33.*s**4.) + a**4.*(4. + 24.*s**2. + 15.*s**4.)*x + 2.*a**3.*(2 + 9.*s**2.)*x**2. + 2.*a**2.*(2. + 5*s**2.)*x**3. + 4.*a*x**4. + 4.*x**5.) - 15.*a**5.*numpy.e**((a**2. + x**2.)/(a**2.*s**2.))* numpy.sqrt(numpy.pi)*s*(4 + 6.*s**2. + s**4.)* SPspecial.erf((-a + x)/(a*s)))))/ (16.*numpy.e**((a**2. + x**2.)/(a**2.*s**2)))
##    t2=-(a*numpy.sqrt(numpy.pi)*s*SPspecial.erf((a-x)/(a*s)))/2
##    return t1,t2


def PolyGauss_ana_Norm(q,par):
        """This fucntion calculates the normalized P(q) of a gaussian distribution of spheres centered in par[0] with an extension par[1]
        q array of q (A-1)
        par[0] Mean radius(A)
        par[1] Gaussian standard deviation (A)
        """
        qnorm=1./(100*par[0])
        t1 = qnorm*par[0]
        t2 = qnorm*par[1]
        prefactor =4.5/(qnorm*par[0])**6.
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        Norm=prefactor*f
        
        R = par[0]
        s = par[1]

        t1 = q*R
        t2 = q*s
        prefactor =4.5/(q*par[0])**6.
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        return prefactor*f,Norm
    
#########################################################
# Section sur les multiplets OS 11-11-2011
#########################################################

def distance(A,B):
    d=((A[0]-B[0])**2+(A[1]-B[1])**2+(A[2]-B[2])**2)**0.5
    return d

def amplitude_multiplet(q,L,rho,R):
    Iq=0.*q
    for i in range(len(L)):
        ri=distance(L[0],L[i])
        if ri==0:
            Iq=Iq+rho[i]*getV(R[i])*F1(q,R[i])
        else:
            Iq=Iq+rho[i]*sin(q*ri)/(q*ri)*getV(R[i])*F1(q,R[i])
    return Iq*1e-24

def Multiplet(q,L,rho,R):
    Iq=0.*q
    for i in range(len(L)):
        for j in range(len(L)):
            rij=distance(L[i],L[j])
            if rij==0:
               Iq=Iq+rho[i]*rho[j]*getV(R[i])*F1(q,R[i])*getV(R[j])*F1(q,R[j])
            else:
               Iq=Iq+rho[i]*rho[j]*sin(q*rij)/(q*rij)*getV(R[i])*F1(q,R[i])*getV(R[j])*F1(q,R[j])
    return Iq*1e-48

# Quelques multiplets

def Doublet_Multiplet(a):
    Pos1=a*array([-1,0.,0.])
    Pos2=a*array([1,0.,0.])
    Liste=[Pos1,Pos2]
    return Liste

def Triplet_Multiplet(a):
    Pos1=a*array([-1.,0.,0.])
    Pos2=a*array([1.,0.,0.])
    Pos3=a*array([0.,3.**0.5,0.])
    Liste=[Pos1,Pos2,Pos3]
    return Liste

def Tetra1_Multiplet(b):
    """b is the distance between spheres"""
    a=b/2.**0.5
    Pos1=a*array([1.,0.,0.])
    Pos2=a*array([0.,1.,0.])
    Pos3=a*array([0.,0.,1.])
    Pos4=a*array([1.,1.,1.])
    Liste=[Pos1,Pos2,Pos3,Pos4]
    return Liste

def Tetra2_Multiplet(c):
    """c is the distance between the core and the satellites"""
    a=c*2./(3.)**0.5
    Pos1=a*array([1.,0.,0.])
    Pos2=a*array([0.,1.,0.])
    Pos3=a*array([0.,0.,1.])
    Pos4=a*array([1.,1.,1.])
    Liste=[Pos1,Pos2,Pos3,Pos4]
    return Liste


def Tetra_Multiplet(a):
    """semble suspect"""
    Pos1=a*array([0.5,0.5,0.5])
    Pos2=a*array([1.,0.,0.])
    Pos3=a*array([0.,1.,0.])
    Pos4=a*array([0.,0.,1.])
    Pos5=a*array([1.,1.,1.])
    Liste=[Pos1,Pos2,Pos3,Pos4,Pos5]
    return Liste


