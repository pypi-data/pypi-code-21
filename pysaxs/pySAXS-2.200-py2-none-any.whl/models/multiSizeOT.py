from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class MultiSize(Model):
    '''
    Spheres polydisperses distribution semi-Gaussienne analytique
    by DC : 18/06/2009
    adapted by OT 02/02/15
    '''
    def Sphere(self,q,R,s,n,rho1,rho2):
        """
        q array of q (A-1)
        R Mean radius(A)
        s Gaussian standard deviation (A)
        n concentration of spheres (cm-3)
        rho1 scattering length density of spheres (cm-2)
        rho2 scattering length density of outside (cm-2)
        """
        #print "tzeriuzetr",q
        test=0
        t1 = q*R
        t2 = q*s
        prefactor = 1e-48*8.*numpy.pi**2.*n*(rho1-rho2)**2./q**6.
        fcos = ((1+2.*t2**2.)**2.-t1**2.-t2**2.)*numpy.cos(2.*t1)
        fsin = 2.*t1*(1.+2.*t2**2.)*numpy.sin(2.*t1)
        f = 1.+t1**2.+t2**2.-numpy.exp(-2.*t2**2)*(fcos+fsin)
        return prefactor*f
    
    def MyFunct(self,q,par):
        print "hello"
        n1=par[0]
        n2=par[1]
        n3=par[2]
        n4=par[3]
        n5=par[4]
        R1=100
        R2=200
        R3=300
        R4=400
        R5=500
        s = 10
        rho1 = par[5]
        rho2 = par[6]
        print par
        #print q
        r=self.Sphere(q,R1,s,n1,rho1,rho2)
        r+=self.Sphere(q,R2,s,n2,rho1,rho2)
        r+=self.Sphere(q,R3,s,n3,rho1,rho2)
        r+=self.Sphere(q,R4,s,n4,rho1,rho2)
        r+=self.Sphere(q,R5,s,n5,rho1,rho2)
        return r+par[7]
    
    
    def GaussianFunction(self,q,par):
        """
        Gaussian model to fit the peak to get exact zero position
        par[0] : height of gaussian
        par[1] : is related to the FWHM
        par[2] : center of gaussian
        par[3] : background
        """
        sigm=par[1]*((2*numpy.log(2))**0.5)/2
        return (par[0]-par[3])*numpy.exp(-((q-par[2])**2)/sigm**2)+par[3]
    
    IntensityFunc=MyFunct #function
    N=0
    q=Qlogspace(1e-2,1,500.)      #q range(x scale)
    name="test"          #name of the model
    Description="testOT"  # description of model
    Author="Olivier Tache"       #name of Author
    WarningForCalculationTime=False
    
    def __init__(self):
        #super(MultiSize,self).__init__()
        Model.__init__(self)
        #print self.Arg
        self.Arg=[]
        
        self.addParameter("R1",100,dataformat='%e')
        self.addParameter("n1",1e14,dataformat='%e')
        self.addParameter("R2",200,dataformat='%e')
        self.addParameter("n2",1e14,dataformat='%e')
        self.addParameter("rho1",1e11,istofit=False)
        self.addParameter("rho2",9e10,istofit=False,dataformat='%e')#,bound=(-1,1))
        self.addParameter("back",0,istofit=True,dataformat='%e',bound=(0,1))
        #print self.Arg
        
if __name__=="__main__":
    '''
    test code
    '''
    g=MultiSize()
    #y= g.Sphere(g.q,300,20,1e14,1e11,9e10)
    y= g.getIntensity()
    from pylab import *
    print y
    plot(g.q,y)
    loglog()
    show()
