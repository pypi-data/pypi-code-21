from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import *
import numpy

class Pcylmultimin(Model):
    '''
    Multilayer Cylinder
    by OT 10/06/2009
    '''
    def PcylmultiminFunction(self,q,par):
        R=[par[0],par[1],par[2],par[3],par[4],par[5]]
        rho=[par[6],par[7],par[8],par[9],par[10],par[11],par[12]]
        L=par[13]
        rhos=par[14]
        return self.Pcylmulti(q,R,rho,L,rhos)
    
    def Pcylmulti(self,q,R,rho,L,rhos):
        """
        This function calculates the P(q) of a cylinder of length L and and multilayers R of density Rho the last one being solvent
        """
        Pcylnew=1.*q
        Pcylold=1.*q
        for i in range(len(q)):
            N=1.
            alpha0=1e-12
            alphaN=pi/2
            
    #----------------------------------------------------------------------------------------------------       
            """Somme sur les ecorces"""
            dPeco=0.
            for j in range(len(R)):
                dPeco=dPeco+(rho[j]-rho[j+1])*(2.*R[j]*SPspecial.j1(q[i]*R[j]*numpy.sin(alpha0))/(q[i]*numpy.sin(alpha0)))     
            dPcyl0=numpy.sin(alpha0)*(numpy.sin(q[i]*L*numpy.cos(alpha0)/2.)/(q[i]*L*numpy.cos(alpha0)/2.)*dPeco)**2
    
    #----------------------------------------------------------------------------------------------------        
            dPeco=0.
            for k in range(len(R)):
                dPeco=dPeco+(rho[k]-rho[k+1])*(2.*R[k]*SPspecial.j1(q[i]*R[k]*numpy.sin(alphaN))/(q[i]*numpy.sin(alphaN)))            
            dPcylN=numpy.sin(alphaN)*(numpy.sin(q[i]*L*numpy.cos(alphaN)/2.)/(q[i]*L*numpy.cos(alphaN)/2.)*dPeco)**2
    #----------------------------------------------------------------------------------------------------
            
            dPcylold=(dPcyl0+dPcylN)/2.
            Pcylold[i]=pi/2*dPcylold
            test=1.
            while(abs(test)>1e-4):
                N=2.*N
                dalpha=(pi/2.-alpha0)/N
                alpha=numpy.arange(dalpha,pi/2.,2.*dalpha)
    #----------------------------------------------------------------------------------------------------
                dPeco=0.*alpha
                for l in range(len(R)):
                    dPeco=dPeco+(rho[l]-rho[l+1])*(2.*R[l]*SPspecial.j1(q[i]*R[l]*numpy.sin(alpha))/(q[i]*numpy.sin(alpha)))      
                dPcyl=numpy.sin(alpha)*(numpy.sin(q[i]*L*numpy.cos(alpha)/2.)/(q[i]*L*numpy.cos(alpha)/2.)*dPeco)**2            
    #----------------------------------------------------------------------------------------------------         
                dPcylnew=sum(dPcyl)+dPcylold
                dPcylold=dPcylnew
                Pcylnew[i]=dalpha*dPcylnew
                test=(Pcylnew[i]-Pcylold[i])/Pcylold[i]
                Pcylold[i]=Pcylnew[i] 
        return Pcylold*numpy.pi**2*L**2*1e-48*rhos
            
    '''
    parameters definition
    Model(10,Pcylmultimin,Qlogspace(1e-4,1.,500.),
          ([13.,14.,15.,16.,17.,18.,9.418e+010,8.798e+010,4.041e+011,3.925e+011,4.224e+011,3.902e+011,9.418e+010,400.,1e17]),
          ("R1 (A)","R2 (A)","R3 (A)","R4 (A)","R5 (A)","R6 (A)","rho1 (cm-2)","rho2 (cm-2)","rho3 (cm-2)","rho4 (cm-2)","rho5 (cm-2)","rho6 (cm-2)","rho7 (cm-2)","L (A)","Rhos (cm-3)"),
          ("%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e"),
          (True,True,True,True,True,True,True,True,True,True,True,True,True,True,True))]

    from LSsca
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=PcylmultiminFunction #function
        self.N=0
        self.q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
        self.Arg=[13.,14.,15.,16.,17.,18.,9.418e+010,8.798e+010,4.041e+011,3.925e+011,4.224e+011,3.902e+011,9.418e+010,400.,1e17]         #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,True,True,True,True,True,True,True,True,True,True,True,True,True]    #list of boolean for fitting
        self.name="Multilayer Cylinder"          #name of the model
        self.Doc=["R1 (A)","R2 (A)","R3 (A)","R4 (A)","R5 (A)","R6 (A)","rho1 (cm-2)","rho2 (cm-2)","rho3 (cm-2)","rho4 (cm-2)","rho5 (cm-2)","rho6 (cm-2)","rho7 (cm-2)","L (A)","Rhos (cm-3)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=Pcylmultimin()
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