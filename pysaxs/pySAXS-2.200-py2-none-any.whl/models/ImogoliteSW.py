from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import Pcylmulti
import numpy
import os


class ImogoliteSW(Model):
     '''

     class Imogolite SW 
     by AT 09/02/2011
     '''
     def ImogoliteSWFunction(self,q,par):
          """
          q array of q (A-1)
          par[0] Concentration en Ge
          par[1] Nombre d'Atome de Ge dans la circonference du tube
          par[2] ratio de Si dans la paroi
          par[2] Epaisseur de la paroi du tube
          par[3] Longueur du tube
          """

          r=numpy.zeros(2)
#conc en Ge en mol/cm-3
#par[0]=8e-5*0.5
          
          hmaille=8.5
          
          r[0]=hmaille/(2.0*numpy.sqrt(3.0)*numpy.sin(numpy.pi/par[1]))-1.7
          r[1]=r[0]+par[3]
          
          rho=numpy.zeros(3)
          rhow=0.334
          rho[0]=rhow
          rho[2]=rhow
          
          rho[1]=(par[1]*(86+par[2]*14+(1.0-par[2])*32)*2)/(numpy.pi*hmaille*(r[1]*r[1]-r[0]*r[0]))

          #print 'rayon interne =', r[0]
          #print 'rho paroi =',rho[1]

          rho=rho*1e24*0.282e-12

          C=6.023e23*par[0]/((2.0*par[4]/hmaille)*par[1]*1000)
          
          return Pcylmulti(self.q,r,rho,par[4],C)
     def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.ImogoliteSWFunction
        self.q=Qlogspace(0.005,1.0,500)    #q range(x scale)
        self.Arg=[.042,19,0.0,6.0,100.0]         #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False,True]    #list of boolean for fitting
        self.name="Specific: Imogolite Single Wall Si/Ge"          #name of the model
        self.Author="Antoine Thill"
        self.Description = "Imodolite single wall variable thickness"
        self.Doc=["Si or Ge concentration (mol/l)",\
             "Si or Ge in tube circumference ",\
             "ratio of Si in the wall ",\
             "Wall thickness (A)",\
             "imogolite tube length (A)"] #list of description for parameters