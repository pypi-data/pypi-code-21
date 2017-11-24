from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import *
import numpy

class CoreShell(Model):
    '''
    Core Shell Particle
    by OT 10/06/2009
    '''
    def CoreShellFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Outer radius
        par[1] Inner Radius
        par[2] SLD of Shell
        par[3] SLD of Core
        par[4] Number density(cm-3)
        """
        R=[par[0],par[1]]
        rho=[par[2],par[3]]
        return (par[2]**2.)*par[4]*getV(par[0])*getV(par[0])*1e-48*P3(q,R,rho)[0]
            
    '''
    parameters definition
    Model(5,CoreShell,Qlogspace(1e-4,1.,500.),
    ([100.,75.,2e11,1e10,1.e16]),
    ("Outer Radius (A)","Inner radius (A)","SLD shell (cm-2)","SLD Core (cm-2)","Number density (cm-3)"),
    ("%f","%f","%1.3e","%1.3e","%1.3e"),(True,True,True,False,False)),
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.CoreShellFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[100.,75.,2e11,1e10,1.e16]         #list of defaults parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,False,False]    #list of boolean for fitting
        self.name="Core Shell Particle"          #name of the model
        self.Doc=["Outer Radius (A)"\
             ,"Inner radius (A)","SLD shell (cm-2)",\
             "SLD Core (cm-2)","Number density (cm-3)"] #list of description for parameters
    
