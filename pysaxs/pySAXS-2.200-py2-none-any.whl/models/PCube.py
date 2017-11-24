from model import Model
from pySAXS.LS.LSsca import *
import numpy

class Cube(Model):
    '''
    Cubes and parallelepiped
    by OS : 03/11/2011
    '''
    
    def PCube(self,q,par):
        """
        q array of q (A-1)
        par[0] side length 1 (in 1/q)
        par[1] SLD particle (cm-2)
        par[2] SLD medium (cm-2)
        par[3] number density (cm-3)
        """        
        a = par[0]
        rho1 = par[1]
        rho2 = par[2]
        n=par[3]

        prefactor = 1e-48*n*(rho1-rho2)**2

        f = a**6*Ppara(q,a,a,a)
        return prefactor*f
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PCube #function
        self.N=0
        self.q=Qlogspace(3e-4,1.,500.)                             #q range(x scale)
        self.Arg=[30.,9.8e11,9.8e10,1e10]                         #list of parameters
        self.Format=["%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,False,False,False]           #list of boolean for fitting
        self.name="Cube"                      #name of the model
        self.Doc=["side length 1 ",\
             "scattering length density of particle (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "Number density (cm-3)"]           #list of description for parameters
        self.Description="Cubes "  # description of model
        self.Author="Olivier Spalla"                 #name of Author
        self.WarningForCalculationTime=True
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=Cube()
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
    
