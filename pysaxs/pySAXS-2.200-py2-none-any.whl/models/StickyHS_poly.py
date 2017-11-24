from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import SqSticky
import numpy
#from pySAXS.models.SphereGaussAnaDC import SphereGaussAnaDC

class StickyHS_poly(Model):
    '''
    Multiplication simple du facteur de forme Sphere polydisperse par sq hard sphere collante
    dans l approximation d interaction localement monodisperse
    31/03/2015
    '''
    def SqStickyModel(self,q,par):
        R=par[0]
        eta=par[1]
        tao=par[2]
        f1=SqSticky(q, R, eta, tao)
        f2=self.SphereGauss_ana_DC(q,[par[3],par[4],par[5],par[6],par[7]])
        f3=self.SphereGauss_ana_OS(q,[par[3],par[4],par[5],par[6],par[7]])
        return f2-(1.-f1)*f3

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
    
    def SphereGauss_ana_OS(self,q,par):
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
        prefactor = 1e-24*4.*numpy.pi*(rho1-rho2)/q**3.
        fcos = t1*numpy.cos(t1)
        fsin = (1.+t2**2.)*numpy.sin(t1)
        f = numpy.exp(-0.5*t2**2)*(fsin-fcos)
        return n*(prefactor*f)**2
    
    def __init__(self):
        #super(MultiSize,self).__init__()
        Model.__init__(self)
        #print self.Arg
        self.IntensityFunc=self.SqStickyModel #function
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.name="StickyHardSphere polydisperse"          #name of the model
        self.Description="Sticky Hard Sphere Polydisperse"  # description of model
        self.Author="Olivier Spalla, Olivier Tache"       #name of Author
        self.WarningForCalculationTime=False
        self.Arg=[]
        self.addParameter("interaction radius(A)",30,dataformat='%g')
        self.addParameter("ETA",0.1,dataformat='%g')
        self.addParameter("ETO",5.,dataformat='%g')
        self.addParameter("Mean radius(A)",25,dataformat='%g')
        self.addParameter("Gaussian standard deviation (A) ",10,dataformat='%g')
        self.addParameter("concentration of spheres (cm-3)",1.5e14,dataformat='%e')
        self.addParameter("scattering length density of sphere (cm-2)",2e11,dataformat='%e')
        self.addParameter("scattering length density of medium (cm-2)",1e10,dataformat='%e')
    
    
if __name__=="__main__":
    '''
    test code
    '''
    print "toto"
    
