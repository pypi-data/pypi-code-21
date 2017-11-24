from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import *
import numpy

class SprayGrain(Model):
    '''
    Spray Dried Grain
    by OT 10/06/2009
    '''
    def SprayGrainFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Semi major axis(A)
        par[1] Eccentricity
        par[2] concentration of sphere (cm-3)
        par[3] scattering length density of sphere (cm-2)
        par[4] scattering length density of outside (cm-2)
        """
        reduc='False'
        rho1=par[0]
        rho2=par[1]
        rho3=par[2]
        al1=par[3]
        al2=par[4]
        al3=par[5]
        Phi1=par[6]
        Phi2=par[7]
        RG0=par[8]
        RGsig=par[9]
        R1=par[10]
        sigR1=par[11]
        R3=par[12]
        sigR3=par[13]
        taoS=par[14]
        taoL=par[15]
        scale=par[16]
        return Idqc(q,rho1,rho2,rho3,al1,al2,al3,Phi1,Phi2,RG0,RGsig,R1,sigR1,R3,sigR3,taoL,taoS,scale,reduc)
            
    '''
    parameters definition
    Model(4,SprayGrain,Qlogspace(1e-4,1.,500.)
    ,([1.2e15,9.4e14,2.e15,0.,0.,1.,0.37,0.09,675.,0.55,411.,90.,35.,12.,1.,1.,1.])
    ,("SLD Big Particle"," SLD interstices","SLD small Particle","al1","al2","al3",
    "Vol Frac Meso","Vol Frac micro","Grain radius",
    "Polydispersity","Big partile radius","Polydispersity",
    "Small particle radius","Polydispersity","Stickness meso","
    Stickness micro","Scale factor"),
    ("%1.3e","%1.3e","%1.3e","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f"),
    (False,False,False,True,True,False,False,True,True,True,True,True,True,True,False,False,True)),
    
    
     
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.SprayGrainFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[1.2e15,9.4e14,2.e15,0.,0.,1.,0.37,0.09,675.,0.55,411.,90.,35.,12.,1.,1.,1.]         #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f"]      #list of c format
        self.istofit=[False,False,False,True,True,False,False,True,True,True,True,True,True,True,False,False,True]    #list of boolean for fitting
        self.name="Spray Dried Grain"          #name of the model
        self.Doc=["SLD Big Particle",\
             " SLD interstices",\
             "SLD small Particle","al1","al2","al3",\
             "Vol Frac Meso","Vol Frac micro","Grain radius",\
             "Polydispersity","Big partile radius","Polydispersity",\
             "Small particle radius","Polydispersity","Stickness meso","Stickness micro","Scale factor",\
             "Scattering length density of ellipse (cm-2)"\
             ,"scattering length density of medium (cm-2)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=SprayGrain()
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