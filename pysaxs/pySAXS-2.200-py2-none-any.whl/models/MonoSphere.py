from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import getV
from pySAXS.LS.LSsca import P1
import numpy

class MonoSphere(Model):
    '''
    
    class monoSphere from LSSca
    by OT 10/06/2009
    '''
    def MonoSphereFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] radius of the sphere (A)
        par[1] scattering length density of sphere (cm-2)
        par[2] scattering length density of outside (cm-2)
        par[3] concentration of sphere (cm-3)
        """
        if len(par)!=4:
            sys.stderr.write("This function requires a list of 4 parameters")
            return -1.
        else:
            return par[3]*(par[1]-par[2])**2.*getV(par[0])*getV(par[0])*1e-48*P1(q,par[0])
            #sys.stderr.write(str(par[0]))
            #return P1(q,par[0])
            
    '''
    parameters definition
    Model(0,MonoSphere,Qlogspace(1e-4,1.,500.),([250.0,2e11,1e10,1.5e15]),
    ("radius (A)","scattering length density of sphere (cm-2)","scattering length density of outside (cm-2)","number concentration (cm-3)")
    ,("%f","%1.3e","%1.3e","%1.3e"),(True,True,False,False)),
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.MonoSphereFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[30.0,9.8e11,9.8e10,1.e10]           #list of defaults parameters
        self.Format=["%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False]    #list of boolean for fitting
        self.name="Spheres Monodisperse"          #name of the model
        self.Doc=["radius (A)",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)",\
             "number concentration (cm-3)"] #list of description for parameters
    