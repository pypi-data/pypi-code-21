from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class ShellSemiGaussAnaDC(Model):
    '''
    Semi-gaussian shell distribution - analytical equation
    by DC : 22/06/2009
    '''
    
    def ShellGauss_ana_DC(self,q,par):
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
        prefactor = 1e-48*8./9.*numpy.pi**2*n*(rho1-rho2)**2/q**6
        fconst = t1**4+6.*t1**2*t2**2+3.*t2**4
        fcos = (fconst-24.*t2**4*(t1**2+t2**2)+16.*t2**8)*numpy.cos(2.*t1)
        fsin = 8.*t1*t2**2*(t1**2-4.*t2**4+3.*t2**2)*numpy.sin(2.*t1)
        f = fconst-numpy.exp(-2.*t2**2)*(fcos+fsin)
        return prefactor*f
    
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
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.ShellGauss_ana_DC #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[250.,10.,1.5e14,2e11,1e10]            #list of parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False,False]    #list of boolean for fitting
        self.name="DC- Shells: semi-gaussian distribution"          #name of the model
        self.Doc=["Mean (A)",\
             "Polydispersity ",\
             "number density",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)"] #list of description for parameters
        self.Description="Shells: semi-gaussian distribution"  # description of model
        self.Author="David Carriere"       #name of Author
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=ShellSemiGaussAnaDC()
    #plot the model
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    gp("set logscale xy")
    c=Gnuplot.Data(modl.q,modl.getIntensity(),with_='points')
    gp.plot(c)
    raw_input("enter") 
    #plot and fit the noisy model
    yn=modl.getNoisy(0.8)
    cn=Gnuplot.Data(modl.q,yn,with_='points')
    res=modl.fit(yn) 
    cf=Gnuplot.Data(modl.q,modl.IntensityFunc(modl.q,res),with_='lines')
    gp.plot(c,cn,cf)
    raw_input("enter")    
    #plot and fit the noisy model with fitBounds
    bounds=modl.getBoundsFromParam() #[250.0,2e11,1e10,1.5e15]
    res2=modl.fitBounds(yn,bounds)
    print res2
    raw_input("enter")  
    
