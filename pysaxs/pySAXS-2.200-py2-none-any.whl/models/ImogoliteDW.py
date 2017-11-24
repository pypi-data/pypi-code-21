from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import Pcylmulti
import numpy
import os


class ImogoliteDW(Model):
     '''

     class Imogolite DW pour melange SiGe 
     by AT 04/03/2011
     '''
     def ImogoliteDWFunction(self,q,par):
          """
          q array of q (A-1)
          par[0] Concentration en Ge
          par[1] Nombre d'Atome de Si ou Ge dans la circonference du tube ext
          par[2] ratio de Si dans la paroi externe
          par[3] Epaisseur de la paroi du tube ext
          par[4] Nombre d'Atome de Ge dans la circonference du tube int
          par[5] ratio de Si dans la paroi interne
          par[6] Epaisseur de la paroi du tube int
          par[7] Longueur du tube
          par[8] densite electronique interne
          par[9] densite electronique interstitielle
          """

          r=numpy.zeros(4)
        #conc en Ge en mol/cm-3
        #par[0]=8e-5*0.5
          
          hmaille=8.5
          r[0]=hmaille/(2.0*numpy.sqrt(3.0)*numpy.sin(numpy.pi/par[4]))-1.7
          r[1]=r[0]+par[6]
          r[2]=hmaille/(2.0*numpy.sqrt(3.0)*numpy.sin(numpy.pi/par[1]))-1.7
          eit=r[2]-r[1]
          r[3]=r[2]+par[3]
          
          rho=numpy.zeros(5)
          rhow=0.334
          rho[0]=par[8]
          rho[2]=par[9]
          rho[4]=rhow
          rho[1]=(par[4]*(86+par[2]*14+(1.0-par[2])*32)*2)/(numpy.pi*hmaille*(r[1]*r[1]-r[0]*r[0]))
          rho[3]=(par[1]*(86+par[5]*14+(1.0-par[5])*32)*2)/(numpy.pi*hmaille*(r[3]*r[3]-r[2]*r[2]))

          #print 'rayon interne =', r[0]
          #print 'rho paroi interne =',rho[1]
          #print 'rayon externe =', r[3]
          #print 'rho paroi =',rho[3]
          rho=rho*1e24*0.282e-12

          C=6.023e23*par[0]/((2.0*par[7]/hmaille)*(par[1]+par[4])*1000)
          
          return Pcylmulti(self.q,r,rho,par[7],C)
      
     def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.ImogoliteDWFunction
        self.q=Qlogspace(0.005,1.0,500)    #q range(x scale)
        self.Arg=[.042,22,0.0,6.0,11,0.0,6.0,200.0,0.334,0.334]         #list of defaults parameters
        self.Format=["%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e","%1.3e"]      #list of c format
        self.istofit=[True,True,False,False,True,False,False,True,False,False]    #list of boolean for fitting
        self.Name="Specific: Imogolite Double Wall Si/Ge"          #name of the model
        self.Author="Antoine Thill"
        self.Description = "Imodolite double wall variable thickness Si/Ge"
        self.Doc=["Ge concentration (mol/l)",\
             "Si or Ge in external tube circumference ",\
             "Si ratio in external tube ",\
             "External Wall thickness (A)",\
             "Si or Ge in internal tube circumference ",\
             "ratio of Si in internal tube ",\
             "Internal Wall thickness (A)",\
             "imogolite tube length (A)",\
             "Internal electronic density (1/A3)",\
             "Interstitial electronic density (1/A3)"] #list of description for parameters

