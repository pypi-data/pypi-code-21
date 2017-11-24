'''
calculation of invariant
'''
import numpy
from scipy import integrate
from scipy import interpolate
from scipy import special
from math import  *
import pySAXS.LS.LSsca as LSsca

class invariant:
    '''
    class for calculation of  invariant
    from data in i(q)
    '''
    def __init__(self,q,i,printout=None,radius=300.0,verbose=True):
        self.q=q
        self.i=i
        self.printout=printout
        self.verbose=verbose
        self.radius=radius
        self.I0=0.0
        self.Istar=0.0
        self.qmini=numpy.min(self.q)
        self.qmaxi=numpy.max(self.q)
       
        self.radius=300.0
        self.P1=0.0
        self.P2=0.0
        self.P3= 0.0
        #results----
        self.invariant=0.0 #final result : invariant=P1+P2+P3
        self.volume=0.0 # particle volume
        
        if verbose:
            self.printTXT('--- Initializing invariant calculation ---')
        #---- for low q range (guinier)
        self.LowQq=LSsca.Qlogspace(self.qmini/10,self.qmini,100)
        self.calculateI0()
        self.LowQi=numpy.array(LSsca.Guinier(self.LowQq, self.I0, self.radius))
        self.A=self.i[0]
        
        #---- for high q range (Porod)
        #the last nbp points where i>0
        ipositive=self.i[numpy.where(self.i>0)]
        nbp=int(len(ipositive)/3)
        av=numpy.average(ipositive[-nbp:])
        self.B=av*self.qmaxi**4.0*1e32
        if self.verbose:
            self.printTXT('I at qmin : '+str(self.A))
            self.printTXT('Intensity average for last '+str(nbp)+' positive points = '+str(av))
        
        self.HighQq=LSsca.Qlogspace(self.qmaxi,self.qmaxi*10.0,100)
        self.HighQi=LSsca.Porod(self.HighQq,self.B)

    def calculateI0(self):
        '''
        calculate I0
        I0 = Istar * exp(qmini ** 2 * radius ** 2 / 3.0)
        Istar is interpolation at qmin
        '''
        f = interpolate.interp1d(self.q, self.i)
        if numpy.min(self.q) < self.qmini:
            self.Istar = f(self.qmini)
        else:
            self.Istar = self.i[0]
        self.I0 = self.Istar * exp(self.qmini ** 2 * self.radius ** 2 / 3.0)
        if self.verbose:
            self.printTXT("I*=" + str(self.Istar) + "   I0=" + str(self.I0))
        return self.I0
        
        
    def calculate(self,radius=None,qmin=None,qmax=None,extrapolation=None):
        '''
        calculate invariant and particle volume
        '''
        if self.verbose:
            self.printTXT("--- Calculating Invariant ---")
        if qmin!=None:
            self.qmini = qmin
        if qmax!=None:
            self.qmaxi = qmax
        if radius!=None:
            self.radius=radius
        if extrapolation!=None:
            self.B = float(extrapolation)
        if self.verbose:
            self.printTXT("qmin="+str(self.qmini)+"  qmax="+str(self.qmaxi)+" radius="+str(self.radius)+" extrapolation="+str(self.B))    
        
        #update q et i inside the qmini, qmaxi range
        imax=int(max(numpy.argwhere(self.q<self.qmaxi)))
        imin=int(min(numpy.argwhere(self.q>self.qmini)))
        qc=self.q[imin:imax]
        ic=self.i[imin:imax]

        self.LowQq=LSsca.Qlogspace(self.qmini/10,self.qmini,100)
        #calculate I0
        self.calculateI0()
        self.LowQi=numpy.array(LSsca.Guinier(self.LowQq, self.I0, self.radius))
        
        self.A=self.i[0]
        #porod on high q
        
        self.HighQq=LSsca.Qlogspace(self.qmaxi,self.qmaxi*20.0,100)
        self.HighQi=LSsca.Porod(self.HighQq,self.B)
        
        #calculation
        pp1=(3.0*self.Istar)/(2*self.radius**2)
        pp2=exp(self.qmini**2*self.radius**2/3.0)
        pp3=((3.*pi)**0.5)/(2*self.radius)
        pp4=special.erf(self.qmini*self.radius/(3.0**0.5))
        self.P1=pp1*(-self.qmini+pp2*pp3*pp4)*1e24
        self.P2=integrate.trapz(ic*qc*qc*1e16,qc*1e8)
        self.P3= self.B/(self.qmaxi*1e8)
        self.invariant=self.P1+self.P2+self.P3
        '''
        calculate the particle volume
        Vpart=2 * PI**2 * I(0) / invariant
        '''
        self.volume=2*pi**2*self.I0/self.invariant
        
        if self.verbose:
            '''self.printTXT("P1 (cm-4)=",self.P1)    
            self.printTXT("P2 (cm-4)=",self.P2)
            self.printTXT("P3 (cm-4)=",self.P3)'''
            self.printTXT("Invariant (cm-4) = P1+P2+P3 =",self.invariant)
            self.printTXT("Particle Volume = 2 * PI**2 * I0 / invariant ="+str(self.volume)+" cm3")
            
        return self.invariant
    
    def getInvariant(self):
        '''
        return the calculate value
        use calculate() function before
        '''
        return self.invariant
    
    def getVolume(self):
        '''
        return the calculate volume for a particule
        use calculate() function before
        '''
        return self.volume
       
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
            
   