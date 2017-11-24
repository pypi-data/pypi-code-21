# -*- coding: utf-8 -*-
from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy
from numpy import *
from scipy.special import erf
from scipy.special import gamma

class Beaucage3C(Model):
    '''
    by OS
    '''
    ######Definition of the parameters of the cluster with three stages######
    #Model with 9 parameters Df1,Rg1,a1,Df2,Rg2,a2,Df3,Rg3,a3
    '''a1=1.                           #anisotropy of the primary unit (must be above 1)
    Rg1=3.                          #Radius of giration of the primary unit
    Df1=4.                          #Fractal dimension of the primary units
    
    a2=1.                           #anisotropy of the intermediate aggregate (must be above 1)
    Df2=1.1                         #Fractal dimension of the intermediate agregates
    Rg2=150.                        #Radius of giration of the aggregates
    Npart=(Rg2/Rg1)**Df2            #Number of units in the intermediate aggregates
    Phi=Npart*(Rg1/Rg2)**3              #Volume fraction of primary in the intermediate aggregates
    
    a3=1.                           #anisotropy of the larger aggregates (must be above 1)
    Df3=1.                          #Fractal dimension of the larger agregates
    Rg3=5000.                       #Radius of giration of the larger aggregates
    Npart2=(Rg3/Rg2)**Df3           #Number of intermediate aggregates in the larger aggregates
    Phi3=Npart2*Npart*(Rg1/Rg3)**3  #Volume fraction of primary in the larger aggregates'''

    
    def BT2(self,q,Rgi,Df):
        y=((erf(q*1.06*Rgi/sqrt(6.)))**3/q)**Df
        return y

    def BT1(self,q,Rgi):
        y=1./exp((q*Rgi)**2/3)
        return y

    #Calcul a trois niveaux
    def Beaucage3N(self,q,a1=1,a2=1,a3=1,Df1=4,Df2=1.1,Df3=1,Rg1=3,Rg2=150,Rg3=5000):
        ################ Calculation of the parameters required for two levels Beaucage
        #print "HELLOOOOO" 
        R1=sqrt(5./3.*Rg1**2)     #Equivalent sphere radius of the primary unit
        G1=(4./3.*pi*R1**3)**2    #Volume of the primary unit if a sphere
        B1=8.*pi**2*R1**2         #Porod value if the unit is a sphere
    
        R2=sqrt(5./3.*Rg2**2)     #Equivalent sphere radius of the aggregate
        Npart=(Rg2/Rg1)**Df2    
        G2=Npart*G1               #Ratio of intensity at low q of the aggregates    
        B2=G2/Rg2**Df2*gamma(Df2/2.)#Connecting regime term if aggregate spherical
        # Voir page 80 du cahier D13102, je trouve (en refaisant les calculs Beaucage) qu'il faut ajouter un parametre p pour corriger B2
        p=81./50.
        #    p=1.#avant verif on reste  a la valeur publiee
        B2=p*B2
        
        Npart2=(Rg3/Rg2)**Df3
        G3=Npart2*G2
        B3=G3/Rg3**Df3*gamma(Df3/2.)
        B3=p*B3
        
        y1=G1*self.BT1(q,Rg1)+a1**2*B1*self.BT2(q,Rg1,Df1)
        y2=G2*self.BT1(q,Rg2)+a2**2*B2*self.BT1(q,Rg1)*self.BT2(q,Rg2,Df2)
        y3=G3*self.BT1(q,Rg3)+a3**2*B3*self.BT1(q,Rg2)*self.BT2(q,Rg3,Df3)
        
        return y1+y2+y3
    
    def BeaucageF(self,q,par):
        '''
        '''
        a1,Df1,Rg1,Df2,Rg2,Df3,Rg3,BDF=par
        #print par
        b=self.Beaucage3N(q,a1=a1,Df1=Df1,Rg1=Rg1, Df2=Df2, Df3=Df3,  Rg2=Rg2, Rg3=Rg3)
        return b/b[0]+BDF
    
    
    '''
    parameters definition
    
    Model(2,PolyGauss_ana_DC,Qlogspace(1e-4,1.,500.),
    ([250.,10.,1.5e14,2e11,1e10]),
    ("Mean (A)",
    "Polydispersity ","number density","scattering length density of sphere (cm-2)",
    "scattering length density of medium (cm-2)"),
    ("%f","%f","%1.3e","%1.3e","%1.3e"),
    (True,True,False,False,False)),
    
    
    '''
    IntensityFunc=BeaucageF #function
    N=0
    q=Qlogspace(1e-3,1.,500.)      #q range(x scale)
    #Arg=[3,4,1.1,28.,0.8,2500,0]            #list of parameters
    #ArgBound=[(0,4),(1,100),(0.0,4.0),(150,300),(0.0,4.0),(300,5000),(-1,1)]   #list of parameters bounds [(0.0,10.0),(1.1,2.2)]
    #Format=["%f","%f","%f","%f","%f","%f","%f"]      #list of c format
    #istofit=[False,False,True,True,True,True,True]    #list of boolean for fitting
    name="Beaucage 3N"          #name of the model
    '''Doc=["Df1",\
         "Rg1",\
         "Df2",\
         "Rg2 ",\
         "Df3",\
         "Rg3",\
         "BDF"] #list of description for parameters
    '''
    Description="Beaucage 3 complet"  # description of model
    Author="Olivier Spalla"       #name of Author
    WarningForCalculationTime=False
    
    def __init__(self):
        Model.__init__(self)
        #self.Arg=[] #not sure to be necessary
        self.addParameter("A1",1,istofit=False,bound=(1,4))
        self.addParameter("Df1",3,istofit=False,bound=(0,4))
        self.addParameter("Rg1",4,istofit=False,bound=(1,100))
        self.addParameter("Df2",1.1,bound=(0,4))
        self.addParameter("Rg2",28,bound=(100,300))
        self.addParameter("Df3",0.8,bound=(0,4))
        self.addParameter("Rg3",2500,bound=(300,5000))
        self.addParameter("BDF",0,istofit=True,dataformat='%e',bound=(-1,1))
        #print self.Arg

if __name__=="__main__":
    '''
    test code
    '''
    modl=Beaucage3()
    #plot the model
    print modl.q,modl.getIntensity()
    
