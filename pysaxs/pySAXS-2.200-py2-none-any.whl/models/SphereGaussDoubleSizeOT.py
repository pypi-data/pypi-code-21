from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class SphereGaussDoubleSizeOT(Model):
    '''
    Spheres polydisperses distribution semi-Gaussienne analytique
    by DC : 18/06/2009
    adapted by OT 02/02/15
    '''
    
    def SphereGauss_ana_DS_OT(self,q,par):
        """
        q array of q (A-1)
        par[0] Mean radius(A) no 1
        par[1] Mean radius(A) no 2
        par[2] Gaussian standard deviation (A) no1
        par[3] Gaussian standard deviation (A) no2
        par[4] concentration of spheres (cm-3) no1
        par[5] concentration of spheres (cm-3) no2
        par[6] scattering length density of spheres (cm-2)
        par[7] scattering length density of outside (cm-2)
        par[8] background
        """
        R = par[0]
        R2=par[1]
        s = par[2]
        s2 = par[3]
        n = par[4]
        n2=par[5]
        rho1 = par[6]
        rho2 = par[7]
        
        t1 = q*R
        t2 = q*s
        prefactor1 = 1e-48*8.*numpy.pi**2.*n*(rho1-rho2)**2./q**6.
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        
        prefactor2 = 1e-48*8.*numpy.pi**2.*n2*(rho1-rho2)**2./q**6.
        t1 = q*R2
        t2 = q*s2
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f2 = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        
        return prefactor1*f+prefactor2*f2+par[8]
    
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
    IntensityFunc=SphereGauss_ana_DS_OT #function
    N=0
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.SphereGauss_ana_DS_OT #function
        self.N=0
        self.q=Qlogspace(1e-4,1,500.)      #q range(x scale)
        self.Arg=[250.,150,10.,10,1.5e14,1.5e14,2e11,1e10,0.0]            #list of parameters
        self.Format=["%f","%f","%f","%f","%1.3e","%1.3e","%1.3e","%1.3e","%f"]      #list of c format
        self.istofit=[True,True,True,True,True,True,False,False,True]    #list of boolean for fitting
        self.name="Spheres polydisperses with two sizes: Semi-Gaussian distribution"          #name of the model
        self.Doc=["Mean radius(A) for sphere 1",\
             "Mean radius(A) for sphere 2",\
             "Gaussian standard deviation 1(A) ",\
             "Gaussian standard deviation 2(A) ",\
             "concentration of spheres 1 (cm-3)",\
             "concentration of spheres 2 (cm-3)",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "background"] #list of description for parameters
        self.Description="Spheres : Semi-Gaussian distribution, two sizes"  # description of model
        self.Author="David Carriere, Olivier Tache"       #name of Author
        self.WarningForCalculationTime=False
    
