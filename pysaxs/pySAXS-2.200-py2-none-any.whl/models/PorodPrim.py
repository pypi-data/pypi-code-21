from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy
import scipy

class PorodPrim(Model):
    '''
    Porod
    
    for Porod Model
    by OT & CG 17/01/2012
    '''
    def PorodPrimFunction(self,q,par):
        """
        Porod model to fit q-4 part at high q
        par[0] : B1
        par[1] : rg
        """
        B1=par[0]
        Rg=par[1]
        er=(scipy.special.erf(q*Rg/(6.0**0.5)))**3
        q4=(q/er)**(-4.0)
        return B1*q4
                
    
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PorodPrimFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1e-6,100]           #list of defaults parameters
        self.Format=["%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True]    #list of boolean for fitting
        self.name="PorodPrimaire"          #name of the model
        self.Doc=["B1",\
             "Rg"] #list of description for parameters
        self.specific=True  #for specific model, set to true
        self.Description="Porod model to fit q-4 part at high q"  # description of model
        self.Author="OT & CG 17/01/2012"       #name of Author
        
