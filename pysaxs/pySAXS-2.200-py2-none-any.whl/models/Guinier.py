from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import Guinier
import numpy

class GuinierModel(Model):
    '''
    Guinier
    by OT : 15/11/2011
    '''
    
    def Guinier_function(self,q,par):
        """
        q array of q (A-1)
        par[0] I0
        par[1] Rg
        """
        I0=par[0]
        Rg = par[1]
        
        return Guinier(q,I0,Rg)
    def __init__(self):
        Model.__init__(self)
        #parameters definition
        self.IntensityFunc=self.Guinier_function #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1.0,300]            #list of parameters
        self.Format=["%f","%f"]      #list of c format
        self.istofit=[True,True]    #list of boolean for fitting
        self.name="Guinier"          #name of the model
        self.Doc=["I0",\
             "Radius of giration (A)" ] #list of description for parameters
        self.Description="Guinier model"  # description of model
        self.Author="Olivier Tach'e & Olivier Spalla"       #name of Author
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=PolyGaussAnaDC()
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
    
