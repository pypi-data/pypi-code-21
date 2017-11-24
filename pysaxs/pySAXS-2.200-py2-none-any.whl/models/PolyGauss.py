from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import getV
from pySAXS.LS.LSsca import P1
import numpy

class PolyGauss(Model):
    '''
    
    class monoSphere from LSSca
    for Spheres poly-Gauss Model
    by OT 10/06/2009
    '''
    def PolyGauss_anaFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Mean radius(A)
        par[1] FWHM (A)
        par[2] concentration of sphere (cm-3)
        par[3] scattering length density of sphere (cm-2)
        par[4] scattering length density of outside (cm-2)
        """
        a=par[0]
        s=par[1]/(2.*a*numpy.log(2.))**0.5)
        t1=q*a*s
        t2=2.*q*a
        t3=q*a
        f1=1.+ (1.+0.5*s**2.)*((t3)**2.) - (t2)*( 1.+(t1**2.) )*numpy.sin(t2)*numpy.exp(-t1**2.) - ( 1.+(1.5*(s**2.)-1.)*(t3**2.) + (t1**4.) )*numpy.cos(t2)*numpy.exp(-(t1**2.))
        f2=4.5*(t3**(-6.))*(1.+7.5*s**2.+(45./4.)*s**4.+(15./8.)*s**6.)**(-1)
        normfactor=((4.*(a**3.)*numpy.pi/3.)**2.)*(1.+7.5*(s**2.)+(45./4.)*(s**4.)+(15./8.)*(s**6.))
        return normfactor*1e-48*par[2]*((par[3]-par[4])**2.)*f1*f2
            
    '''
    parameters definition
    Model(1,PolyGauss_ana,
    Qlogspace(1e-4,1.,500.)
    ([250.,10.,1.5e14,2e11,1e10]),
    ("Mean (A)",
    "Polydispersity ",
    "number density",
    "scattering length density of sphere (cm-2)",
    "scattering length density of medium (cm-2)"
    ),("%f","%f","%1.3e","%1.3e","%1.3e")
    ,(True,True,False,False,False)),
    
    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PolyGauss_anaFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[250.,10.,1.5e14,2e11,1e10]           #list of defaults parameters
        self.Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,True,True]    #list of boolean for fitting
        self.name="Spheres poly-Gauss"          #name of the model
        self.Doc=["Mean (A)",\
             "Polydispersity ",\
             "number density",\
             "scattering length density of sphere (cm-2)",\
             "scattering length density of medium (cm-2)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=PolyGauss()
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