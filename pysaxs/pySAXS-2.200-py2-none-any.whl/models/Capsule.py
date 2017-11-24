from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import Pcylh

import numpy

class Capsule(Model):
    '''
    
    class monoSphere from LSSca
    by OT 10/06/2009
    '''
    def CapsuleFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Radius(A)
        par[1] Length (A)
        par[2] concentration of sphere (cm-3)
        par[3] scattering length density of sphere (cm-2)
        par[4] scattering length density of outside (cm-2)
        """
        R=par[0]
        L=par[1]
        return par[2]*(1.e-48)*((par[3]-par[4])**2.)*((numpy.pi*(par[0])**2.*(par[1]))**2.)*Pcylh(q,R,L)
            
    '''
    parameters definition
    Model(2,MonoCylinder,Qlogspace(1e-4,1.,500.)
    ,([25.,100.,1.5e14,2e11,1e10]),
    ("Radius (A)","Length ","Number density",
    "Scattering length density of cyl (cm-2)",
    "scattering length density of medium (cm-2)"),
    ("%f","%f","%1.3e","%1.3e","%1.3e"),
    (True,True,False,False,False)),
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.CapsuleFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,100.)      #q range(x scale)
        self.Arg=[25.,100.,9.8e11,9.8e10,1e10]           #list of defaults parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False,False]    #list of boolean for fitting
        self.name="Capsule"          #name of the model
        self.author="O Spalla"   #name of the authors
        self.WarningForCalculationTime=True
        self.Doc=["Radius (A)",\
             "Length ",\
             "Number density",\
             "Scattering length density of cyl (cm-2)",\
             "scattering length density of medium (cm-2)"] #list of description for parameters
    
