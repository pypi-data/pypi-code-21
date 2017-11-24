from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class SphereOTBackgd(Model):
    '''
    Spheres polydisperses distribution semi-Gaussienne analytique
    by DC : 18/06/2009
    '''
    
    def fSphereOTBackgd(self,q,par):
        """
        q array of q (A-1)
        par[0] Mean radius(A)
        par[1] Gaussian standard deviation (A)
        par[2] concentration of spheres (cm-3)
        par[3] scattering length density of spheres (cm-2)
        par[4] scattering length density of outside (cm-2)
        par[5] background
        """
        R = par[0]
        s = par[1]
        n = par[2]
        rho1 = par[3]
        rho2 = par[4]
        t1 = q*R
        t2 = q*s
        prefactor = 1e-48*8.*numpy.pi**2.*n*(rho1-rho2)**2./q**6.
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        return prefactor*f+par[5]
    
    '''
    parameters definition
    
    Model(2,PolyGauss_ana_DC,Qlogspace(1e-4,1.,500.),
    ([250.,10.,1.5e14,2e11,1e10]),
    ("Mean (A)",
    "Polydispersity ","number density","scattering length density of sphere (cm-2)",
    "scattering length density of medium (cm-2)"),
    ("%f","%f","%1.3e","%1.3e","%1.3e"),
    (True,True,False,False,False)),
    
    
    '''
    IntensityFunc=fSphereOTBackgd #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[250.,10.,1.5e14,2e11,1e10,0]            #list of parameters
    Format=["%f","%f","%1.3e","%1.3e","%1.3e","%f"]      #list of c format
    istofit=[True,True,True,False,False,True]    #list of boolean for fitting
    name="Spheres polydisperses with background"          #name of the model
    Doc=["Mean radius(A)",\
         "Gaussian standard deviation (A) ",\
         "concentration of spheres (cm-3)",\
         "scattering length density of sphere (cm-2)",\
         "scattering length density of medium (cm-2)",\
         "background"] #list of description for parameters
    Description="Spheres with backgrnd"  # description of model
    Author="OT"       #name of Author
    WarningForCalculationTime=False
    

