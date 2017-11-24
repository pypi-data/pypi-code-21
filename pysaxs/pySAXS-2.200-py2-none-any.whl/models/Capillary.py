from pySAXS.models.model import Model
import numpy as np
import matplotlib.pyplot as plt

def gaussian(x, A,x0,sigma):
    return A*np.exp(-(x - x0)**2 / (2*sigma**2))


class Capillary(Model):
    '''
    Model to fit capilary scan read from SPEC log file
    by AT and OT : 02/02/2017
    '''
    
    def CapillaryFunction(self,q,par):
        """
        q is the x position of the capilary scan around the center 
        
	    par[0] : incident flux (cps)
	    par[1] : position of the capilary
        par[2] : internal diameter of the capilary
        par[3] : Thikness of capilary wall
        par[4] : FWHM of the beam at the sample position
        par[5] : linear exctinction coefficient of the sample
        par[6] : linear exctinction coefficient of the glass

        """
        ri=par[2]/2.0
        e=par[3]
        center=par[1]/10.0
        
        #x=np.linspace(q[0],xexp[len(q)-1],10000)
    	E=np.zeros(len(q))
    	Ew=np.zeros(len(q))
    	T=np.zeros(len(q))
    	for i in range(len(q)):
    	  if((((q[i]/10.0)-center)<-(ri+e)) | (((q[i]/10.0)-center)>(ri+e))):
    	    E[i]=0
    	    Ew[i]=0
    	  else:
    	    if((((q[i]/10.0)-center)<-ri) | (((q[i]/10.0)-center)>ri)):
    	      E[i]=2.0*((ri+e)*np.cos(np.arcsin(((q[i]/10.0)-center)/(ri+e))))
    	      Ew[i]=0
    	    else:
    	      E[i]=2.0*((ri+e)*np.cos(np.arcsin(((q[i]/10.0)-center)/(ri+e)))-ri*np.cos(np.arcsin(((q[i]/10.0)-center)/ri)))
    	      Ew[i]=2.0*ri*np.cos(np.arcsin(((q[i]/10.0)-center)/ri))
    	  T[i]=par[0]*np.exp(-par[6]*E[i])*np.exp(-par[5]*Ew[i])
    
    	#Beam shape convolution
    
    	sigma=par[4]/2.3548
    
    	Tc=np.zeros(len(q))
    	for i in range(len(q)):
    	  B=gaussian((q/10.0)-center,1,(q[i]/10.0)-center,sigma)
    	  Tc[i]=Tc[i]+np.sum(B*T)/np.sum(B)
    
        return (Tc)
    
    def prefit(self,q,y):
        '''
        try to determine some parameters from the datas
        '''
        self.Arg=[y.max(),(q[-1]-q[0])/2,0.13,0.0022,0.054,0,77.12]            #list of parameters
        return self.Arg
      
    '''
    parameters definition
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.CapillaryFunction #function
        self.N=0
        self.q=np.arange(-2,2,0.1)      #q range(x scale)
        self.Arg=[3.4e6,7.2,0.13,0.0022,0.054,0,77.12]            #list of parameters
        self.Format=["%f","%f","%f","%f","%f","%f","%f"]      #list of c format
        self.istofit=[True,True,True,True,False,False,False]    #list of boolean for fitting
        self.name="Capillary"          #name of the model
        self.Doc=["Incident Flux (cps)"\
		 , "capillary center (mm) (unit spec)"\
                 ,"internal diameter of the capillary (cm)"\
                 ,"Thikness of the capilary wall (cm)"\
		 ,"FWHM of the beam at the sample position (cm)"\
		 ,"linear exctinction coefficient of the sample (1/cm)"\
		 ,"linear exctinction coefficient of the glass (1/cm)"] #list of description for parameters
        self.Description="Fit of transmission scan of capillary"  # description of model
        self.Author="Antoine Thill'"       #name of Author
    
if __name__=="__main__":
    '''
    test code
    '''
    
    scannumber=raw_input('numero de scan ? :')
    lookstr='#S ' + scannumber 
    file=open('/home/saxs/data/saxs_20170202.log','r')
    l=file.readlines()
    li=0
    for tl in l:
      if (tl.find(lookstr) == -1):
	li=li+1
      else:
	startline=li
    #on est arrive a la bonne ligne
    #il faut lire le nombre de point
    NBP=int(l[startline].split()[6])

    xexp=[]
    Texp=[]
    for tl in l[startline+13:startline+13+NBP]:
      xexp.append(float(tl.split()[0]))
      Texp.append(float(tl.split()[9]))
    xexp=np.asarray(xexp)
    Texp=np.asarray(Texp)

    
    xexp=(xexp)
    dataexport=np.array([xexp,Texp])
    np.savetxt('saxs_20170202scan26b.txt',dataexport.transpose())
    g=Capillary()
    g.Arg=[3.4e6,7.2,0.13,0.0022,0.054,0,70.12]
    g.q=xexp
    plt.ion()
    
    #plt.plot(g.q,g.getIntensity(),with_='points')
    
    plt.plot(xexp,Texp,'.')
 
    #g.Arg=g.fit(Texp) 
    
    plt.plot(g.q,g.IntensityFunc(g.q,g.Arg))
    print g.Arg
    print 'external diameter of the capillary :' + str(g.Arg[2]+2.0*g.Arg[3])
    raw_input("enter")    
    
   # bounds=[(0.02,0.1),(0.0015,0.004),(0.02,0.06),(9.3,9.4),(77.9,78.0)]
    #res2=g.fitBounds(yn,bounds)
    #print res2
    #raw_input("enter")  
    
