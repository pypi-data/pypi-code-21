from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class PorodC(Model):
    '''
    Porod Curved
    
    for Spheres poly-Gauss Model
    by OT 10/06/2009
    '''
    def PorodCFunction(self,q,par):
        """
        Porod model to fit q-4 part at high q
        par[0] : Scattering lenght density contrast in cm-2
        par[1] : S/V cm-1
        par[2] : principal curvature 1 cm-1
        par[3] : Principal curvature 2 cm-1
        """
        return 2.0*numpy.pi*1.0e-32*par[0]*par[0]*par[1]*q**-4.0*(1.0+1e-16*q**-2.0*(((par[2]+par[3])**2.)/4.+((par[2]-par[3])**2.)/8.))

            
    '''
    parameters definition
    class Model(7,Porod,/
    Qlogspace(1e-4,1.,500.),(
    [1.0e10,1e6]),
    ("Scattering contrast (cm-2)",
    "S/V (cm-1)"),("%1.3e","%1.3e"),
    (True,True)),
     
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PorodCFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1.0e10,1e6,1e-2,1e-2]           #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,True]    #list of boolean for fitting
        self.name="Porod with curvature correction"          #name of the model
        self.Doc=["Scattering contrast (cm-2)","S/V (cm-1)","C1","C2"] #list of description for parameters
        
if __name__=="__main__":
    '''
    test code
    '''
    modl=PorodC()
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
