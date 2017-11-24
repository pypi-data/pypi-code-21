from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import SqSticky
import numpy
#from pySAXS.models.SphereGaussAnaDC import SphereGaussAnaDC

class StickyHS(Model):
    '''
    Multiplication simple du facteur de forme Sphere polydisperse par sq hard sphere collante
    A verifier
    31/03/2015
    '''
    def SqStickyModel(self,q,par):
        R=par[0]
        eta=par[1]
        tao=par[2]
        f1=SqSticky(q, R, eta, tao)
        f2=self.SphereGauss_ana_DC(q,[par[3],par[4],par[5],par[6],par[7]])
        return f1*f2
    
    def SphereGauss_ana_DC(self,q,par):
        """
        q array of q (A-1)
        par[0] Mean radius(A)
        par[1] Gaussian standard deviation (A)
        par[2] concentration of spheres (cm-3)
        par[3] scattering length density of spheres (cm-2)
        par[4] scattering length density of outside (cm-2)
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
        return prefactor*f
    
    
    def __init__(self):
        Model.__init__(self)
    
        self.IntensityFunc=self.SqStickyModel #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[30.,0.1,5.,25,10.,1.5e14,2e11,1e10]           #list of parameters
        self.Format=["%f","%f","%f","%f","%f","%f","%f","%f"]      #list of c format
        self.istofit=[True,True,True,True,True,True,True,True]    #list of boolean for fitting
        self.name="StickyHardSphere"          #name of the model
        self.Doc=["interaction radius(A)",\
             "ETA",\
             "TAO",\
             "Mean radius(A)",\
             "Gaussian standard deviation (A) ",\
             "concentration of spheres (cm-3)",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)"]          #list of description for parameters
        self.Description="Sticky Hard Sphere"  # description of model
        self.Author="Olivier Spalla, Olivier Tache"       #name of Author
        self.WarningForCalculationTime=False
    
if __name__=="__main__":
    '''
    test code
    '''
    print "toto"
    
