from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import getV
from pySAXS.LS.LSsca import Multiplet
from pySAXS.LS.LSsca import Doublet_Multiplet
import numpy

class Doublet_Sphere(Model):
    '''
    
    class monoSphere from LSSca
    by OS 19/11/2011
    '''
    def Doublet_Function(self,q,par):
        """
        q array of q (A-1)
        par[0] radius of the sphere (in 1/q)
        par[1] Distance between centers (must be higher than 2R)
        par[2] scattering length density of sphere (cm-2)
        par[3] scattering length density of outside (cm-2)
        par[4] concentration of sphere (cm-3)
        """
        rho=[par[3]-par[2],par[3]-par[2]]
        R=[par[0],par[0]]
        if len(par)!=5:
            sys.stderr.write("This function requires a list of 5 parameters")
            return -1.
        else:
            return par[4]*Multiplet(q,Doublet_Multiplet(par[1]/2.),rho,R)
            #sys.stderr.write(str(par[0]))
            #return P1(q,par[0])
            
    '''
    parameters definition
    Model(0,MonoSphere,Qlogspace(1e-4,1.,500.),([250.0,2e11,1e10,1.5e15]),
    ("radius (A)","scattering length density of sphere (cm-2)","scattering length density of outside (cm-2)","number concentration (cm-3)")
    ,("%f","%1.3e","%1.3e","%1.3e"),(True,True,False,False)),
    from LSsca
    '''
    IntensityFunc=Doublet_Function #function
    def __init__(self):
        Model.__init__(self)
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[30.0,70.0,9.8e11,9.8e10,1.e10]           #list of defaults parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,False,False]    #list of boolean for fitting
        self.name="Multi: Doublet of identical spheres"          #name of the model
        self.Description="Doublet of identical spheres"
        self.Author="O. Spalla"
        self.Doc=["Radius (1/q)",\
             "Distance between centers (1/q): must be larger than diameter",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "number concentration (cm-3)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=Doublet_Sphere()
    #plot the model
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    gp("set logscale xy")
    c=Gnuplot.Data(modl.q,modl.getIntensity(),with_='points')
    gp.plot(c)
    raw_input("enter") 
    #plot and fit the noisy model
    yn=modl.getNoisy(0.4)
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
