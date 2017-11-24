from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import Pcylmulti
import numpy
import scipy.special


class ImogoliteSWCH3(Model):
     '''

     class Imogolite SW 
     by AT 09/02/2011
     '''
     def ImogoliteSWCH3Function(self,q,par):
          """
          q array of q (A-1)
          par[0] Concentration en tubes/cm3
          par[1] Rayon interne
          par[2] Epaisseur de la paroi du tube
          par[3] Longueur du tube
          par[4] Nombre d'Atome de Si dans la circonference du tube 
          par[5] Nombre electron par motif
          par[6] Parametre de maille
          par[7] densite electronique interne
          par[8] densite electronique externe
          par[9] Nombre de tubes isoles
          par[10] Nombre de tube par 2
          par[11] Nombre de tube par 3
          par[12] Nombre de tube par 4
          """

          r=numpy.zeros(2)
          
          r[0]=par[1]
          r[1]=r[0]+par[2]
          
          rho=numpy.zeros(3)
          rho[0]=par[7]
          rho[1]=(par[4]*par[5])/(numpy.pi*par[6]*(r[1]*r[1]-r[0]*r[0]))
          rho[2]=par[8]
 
          print 'densite electronique paroi =', rho[1]
       
          rho=rho*1e24*0.282e-12
      
          F2=Pcylmulti(self.q,r,rho,par[3],par[0])

          a=2.0*(r[0]+par[2])
          S2T=2.0*scipy.special.j0(self.q*a)+2.0
          S3T=6.0*scipy.special.j0(self.q*a)+3.0
          S4T=10.0*scipy.special.j0(self.q*a)+2.0*scipy.special.j0(self.q*a*numpy.sqrt(3.0))+4.0
          Sp=par[9]+par[10]+par[11]+par[12]
          p1=par[9]/Sp
          p2=par[10]/Sp
          p3=par[11]/Sp
          p4=par[12]/Sp

          return (p1+p2/2.0*S2T+p3/3*S3T+p4/4*S4T)*F2

     def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.ImogoliteSWCH3Function
        self.q=Qlogspace(0.005,1.0,500)    #q range(x scale)
        self.Arg=[5.0e15,9.0,6.0,600.0,15.0,100.0,4.3,0.11,0.334,2.0,0.0,2.0,1.0]         #list of defaults parameters
        self.Format=["%1.3e","%.3f","%.3f","%.1f","%.2f","%.2f","%.3f","%.3f","%.3f","%.f","%.f","%.f","%.f"]      #list of c format
        self.istofit=[True,True,False,False,True,True,True,False,False,True,True,True,True]    #list of boolean for fitting
        self.name="Specific: Imogolite Single Wall CH3 and hybrid"          #name of the model
        self.Author="Antoine Thill"
        self.Description = "Imogolite single wall CH3"
        self.Doc=["Concentration de tubes (/cm3)",\
             "rayon interne (A) ",\
             "Wall thickness (A)",\
             "imogolite tube length (A)",\
             "Number of Si atom per ring",\
             "Number of electron per structural unit",\
             "Lattice parameter",\
             "internal electronic density (e/A3)",\
             "external electronic density (e/A3)",\
             "number of 1 tube",\
             "number of 2 tubes",\
             "number of 3 tubes",\
             "number of 4 tubes"] #list of description for parameters