from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import *
import numpy

class MonoEllipse(Model):
    '''
    Mono Ellipse
    by OT 10/06/2009
    '''
    def MonoEllipseFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Semi major axis(A)
        par[1] Eccentricity
        par[2] concentration of sphere (cm-3)
        par[3] scattering length density of sphere (cm-2)
        par[4] scattering length density of outside (cm-2)
        """
        R=par[0]
        ec=par[1]
        return par[2]*(1.e-48)*(( numpy.pi*(4./3.)*(ec*par[0]**3.) )**2.)*((par[3]-par[4])**2.)*P5(q,R,e)
            
    '''
    parameters definition
    Model(3,MonoEllipse,
    Qlogspace(1e-4,1.,500.)
    ,([100.,0.5,1.5e14,2e11,1e10])
    ,("Semi major axis (A)"
    ," Eccentricity","Number density",
    "Scattering length density of ellipse (cm-2)"
    ,"scattering length density of medium (cm-2)")
    ,("%f","%f","%1.3e","%1.3e","%1.3e"),(True,True,True,False,False)),
    
     
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.MonoEllipseFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[100.,0.5,9.8e11,9.8e10,1e10]          #list of defaults parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,False,False]    #list of boolean for fitting
        self.name="Mono Ellipse"          #name of the model
        self.Doc=["Semi major axis (A)",\
             " Eccentricity","Number density",\
             "Scattering length density of ellipse (cm-2)"\
             ,"scattering length density of medium (cm-2)"] #list of description for parameters
    
