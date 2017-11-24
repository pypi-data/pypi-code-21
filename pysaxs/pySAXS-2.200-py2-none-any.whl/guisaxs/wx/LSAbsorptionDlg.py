#!/usr/bin/python

import wx
import numpy
import sys
from pySAXS.LS import absorption
from pySAXS.tools import isNumeric
'''
29/08/2012 OT : rename file and class LSAbsDlg to LSAbsorptionDlg

15/06/2009 OT : change from Dialog to Frame
    Add Label for NIST
    Change size of Frame

'''

class AbsorptionForm(wx.Frame):
    def __init__(self, parent, set_dir = None):
        wx.Frame.__init__(self, parent, -1, "X-Ray absorption tool", \
                           size=wx.Size(580,600),\
                           pos=wx.DefaultPosition,style = wx.DEFAULT_DIALOG_STYLE)
        if dir(parent).__contains__('favicon'):
            wx.Frame.SetIcon(self,parent.favicon)
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.res=numpy.array([0.,0.,0.])
        self.Z=0
        self.ActiveFormula=""
        self.ActiveAtomes=numpy.zeros(len(absorption.ATOMS))
        
        self.ChampText  =  wx.StaticText(self, 101, "click to select atoms", wx.Point(200, 100))
        #energy slider and buttons
        # the current NRJ is obtained with NRJslider.GetValue() in eV
        
        self.NRJslider=wx.Slider(self,104,8030,1000,50000,\
                                 wx.Point(20,20),\
                                 wx.Size(200,15),\
                                 wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.NRJslider.SetTickFreq(5000,1)
        self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        self.NRJText  =  wx.StaticText(self, 105, "8.03 keV", wx.Point(250, 15))
        self.ResetButton =wx.Button(self, 106, "Reset", wx.Point(320,12),wx.Size(50,30))
        wx.EVT_BUTTON(self, 106, self.OnResetClick)
        #Check box for musrho or musrhoen
        self.MuenBox=wx.CheckBox(self,107,"Mu_en ",(450,15))
        self.Bind(wx.EVT_CHECKBOX, self.CheckBoxUpdate)
        self.MuenBox.SetValue(1)
        self.button=[]
        
        #################
        #Definition des bouttons de chaque atome pris en charge dans le module
        #################
        Bcol=20
        Blig=50
        Bsiz=30
        Znb=1
        # H button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+17*Bsiz
        # He button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=20
        Blig=Blig+Bsiz
        # Li button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Be button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+11*Bsiz
        # B button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # C button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # N button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # O button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # F button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Ne button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=20
        Blig=Blig+Bsiz
        # Na button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Mg button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+11*Bsiz
        # Al button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Si button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # P button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # S button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Cl button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Ar button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1

        Bcol=20
        Blig=Blig+Bsiz
        #ligne 4
        for n in numpy.arange(18):
            # next button
            self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        #ligne 5
        for n in numpy.arange(18):
            # next button
            self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        # Cs button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz        
        # Ba button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz 
        # La button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        #Lanthanides line
        Bcol=20
        Blig=Blig+3*Bsiz
        for n in numpy.arange(14):
            # next button
            self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        #fin de la ligne 6
        Bcol=20+3*Bsiz
        Blig=Blig-3*Bsiz
        for n in numpy.arange(15):
            # next button
            self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        # Fr button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz        
        # Ra button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz 
        # Ac button
        self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        #Acthinides line
        Bcol=20
        Blig=Blig+3*Bsiz
        for n in numpy.arange(3):
            # next button
            self.button =wx.Button(self, Znb, absorption.ATOMS[Znb-1], wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz


        self.SymboleText  =  wx.StaticText(self, 101, "Symbole = ", wx.Point(20, 365))
        self.NameText  =  wx.StaticText(self, 101, "Name = ", wx.Point(20, 380))
        self.ZText  =  wx.StaticText(self, 101, "Atomic number = ", wx.Point(20, 395))
        self.MasseText  =  wx.StaticText(self, 101, "Atomic weight = ", wx.Point(20, 410))
        self.MuText  =  wx.StaticText(self, 101, "Mu_en/rho = ", wx.Point(20, 425))

        # Add button
        self.AtomsNumberLabel=wx.StaticText(self,1092,"Number of atoms  = ",wx.Point(20,455))
        self.AtomsNumber=wx.TextCtrl(self,1091,"",wx.Point(130,453),wx.Size(50,20))
        self.AtomsNumber.SetValue("1.0")
        #self.Bind(wx.EVT_TEXT, self.ThicknessUpdate)
        self.Addbutton=wx.Button(self, 108, "Add", wx.Point(20,475),wx.Size(50,30))
        wx.EVT_BUTTON(self, 108, self.OnAddClick)
        # Remove button
        self.RemoveButton =wx.Button(self, 109, "Remove", wx.Point(70,475),wx.Size(60,30))
        wx.EVT_BUTTON(self, 109, self.OnRemoveClick)
         # Remove all button
        self.RemoveButton =wx.Button(self, 1090, "Remove All", wx.Point(130,475),wx.Size(80,30))
        wx.EVT_BUTTON(self, 1090, self.OnRemoveAllClick)

        self.FormulaLabel=wx.StaticText(self,110,"Active Formula  = ",wx.Point(250,350))
        self.CompoundMuLabel=wx.StaticText(self,112,"Compound Mu_en/rho  = ",wx.Point(250,370))
        self.DensityLabel=wx.StaticText(self,113,"Density  = ",wx.Point(250,390))
        self.DensityText=wx.TextCtrl(self,114,"",wx.Point(375,390),wx.Size(75,20))
        self.DensityText.SetValue("1.00")
        self.Bind(wx.EVT_TEXT, self.DensityUpdate)
        self.DensityUnitLabel=wx.StaticText(self,115,"(g/cm3)",wx.Point(500,390))
        self.CompoundEDLabel=wx.StaticText(self,116,"Electronic density  = ",wx.Point(250,410))
        self.CompoundSLLabel=wx.StaticText(self,117,"Scattering length density  = ",wx.Point(250,430))
        self.ThicknessLabel=wx.StaticText(self,118,"Thickness  = ",wx.Point(250,450))
        self.ThicknessText=wx.TextCtrl(self,119,"",wx.Point(375,450),wx.Size(75,20))
        self.ThicknessText.SetValue("0.1")
        self.Bind(wx.EVT_TEXT, self.ThicknessUpdate)
        self.ThicknessUnitLabel=wx.StaticText(self,120,"(cm)",wx.Point(500,450))
        self.TransLabel=wx.StaticText(self,121,"X-ray trans  = ",wx.Point(250,470))

        self.QuitButton=wx.Button(self,wx.ID_OK,"OK",wx.Point(275,500),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        #NIST Label
        self.NISTLabel=wx.StaticText(self,129,"Datas from NIST X-Ray absorption tables",wx.Point(100,550))
        self.NISTLabel.SetForegroundColour('blue')
        

    def DensityUpdate(self, event):
        self.UpdateFormula()
        
    def ThicknessUpdate(self, event):
        self.UpdateFormula()

    ####   
    #On clique sur les bottons de gestion de l'NRJ
    ####
    def sliderUpdate(self, event):
        self.NRJText.SetLabel(str(self.NRJslider.GetValue()/1000.0) +" keV")
        if(self.MuenBox.GetValue()):
            if self.Z!=0:
                self.MuText.SetLabel("Mu_en/rho = " + str(absorption.getMuZ(self.Z,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
        else:
            if self.Z!=0:
                self.MuText.SetLabel("Mu_en/rho = " + str(absorption.getMuZ(self.Z,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
        self.UpdateFormula()

    def OnResetClick(self,event):
        self.Z=0
        self.NRJslider.SetValue(8028)
        self.NRJText.SetLabel(str(self.NRJslider.GetValue()/1000.0) +" keV")
        self.ChampText.SetLabel("click to select an atom")
        if(self.MuenBox.GetValue()):
            self.MuText.SetLabel("Mu_en/rho = " )
        else:
            self.MuText.SetLabel("Mu/rho = " )
        self.SymboleText.SetLabel("Symbole = ")
        self.NameText.SetLabel("Name = " )
        self.ZText.SetLabel("Atomic number = ")
        self.MasseText.SetLabel("Atomic weight = ")
        self.UpdateFormula()

        
    def CheckBoxUpdate(self, event):
        if(self.MuenBox.GetValue()):
            if self.Z!=0:
                self.MuText.SetLabel("Mu_en/rho = " + str(absorption.getMuZ(self.Z,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
            else:
                self.MuText.SetLabel("Mu_en/rho = ")
        else:
            if self.Z!=0:
                self.MuText.SetLabel("Mu/rho = " + str(absorption.getMuZ(self.Z,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
            else:
                self.MuText.SetLabel("Mu/rho = ")
        self.UpdateFormula()

              
    ####   
    #On clique sur l'un des bouttons du tableau
    ####
    def OnClick(self,event):
        #self.DensityText.SetValue(absorption.ATOMS[event.GetId()-1])
        self.SymboleText.SetLabel("Symbole = " +  str(absorption.ATOMS[event.GetId()-1]))
        self.NameText.SetLabel("Name = " +  absorption.ATOMS_NAME[event.GetId()-1])
        self.ZText.SetLabel("Atomic number : " + str(event.GetId()))
        self.Z=event.GetId()
        self.MasseText.SetLabel("Atomic weight : "+  str(absorption.ATOMS_MASSE[event.GetId()-1]))
        if(self.MuenBox.GetValue()):
            self.MuText.SetLabel("Mu_en/rho = " + str(absorption.getMuZ(event.GetId(),self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
        else:
            self.MuText.SetLabel("Mu/rho = " + str(absorption.getMuZ(event.GetId(),self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())))
      
    def UpdateFormula(self):
        self.ActiveFormula=""
        #If at least one atome exist
        if sum(self.ActiveAtomes)!=0:
            N=self.ActiveAtomes.take(numpy.where(self.ActiveAtomes!=0)[0])
            ind=numpy.where(self.ActiveAtomes!=0)[0]
            j=0
            for i in ind:
                #self.ActiveFormula=self.ActiveFormula + str(absorption.ATOMS[int(i)]) + ' ' + str(int(N[int(j)])) + ' '
                self.ActiveFormula=self.ActiveFormula + str(absorption.ATOMS[int(i)]) + ' ' + str(N[int(j)]) + ' '
                j=j+1
            
            self.FormulaLabel.SetLabel("Active Formula  = "+self.ActiveFormula.strip())
            if(self.MuenBox.GetValue()):
                self.CompoundMuLabel.SetLabel("Compound Mu_en/rho  = %1.5f (cm2/g)" % absorption.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue()))
            else:
                self.CompoundMuLabel.SetLabel("Compound Mu/rho  = %1.5f (cm2/g)" % absorption.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue()))
            self.CompoundEDLabel.SetLabel("Electronic density  = %1.5e (1/cm3)" % absorption.getElectronDensity(self.ActiveFormula,float(self.DensityText.GetValue()))[0])
            self.CompoundSLLabel.SetLabel("Scattering length density  = %1.5e (1/cm2)" % absorption.getElectronDensity(self.ActiveFormula,float(self.DensityText.GetValue()))[1])
            self.TransLabel.SetLabel("X-ray transmission  = %1.5e" % numpy.exp(-float(self.DensityText.GetValue())*absorption.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())*float(self.ThicknessText.GetValue())))
        else:
            try:
                self.FormulaLabel.SetLabel("Active Formula  = ")
                self.CompoundMuLabel.SetLabel("Compound Mu_en/rho  =  (cm2/g)")
                self.CompoundEDLabel.SetLabel("Electronic density  =  (1/cm3)")
                self.CompoundSLLabel.SetLabel("Scattering length density  =  (1/cm2)")
                self.TransLabel.SetLabel("X-ray transmission  = ")
            except:
                pass
        
    def OnAddClick(self,event):
        an=self.AtomsNumber.GetValue()
        if isNumeric.isNumeric(an):
            an=float(an)
            an=abs(an)
        else:
            an=1.0
        if self.Z!= 0:
            if self.ActiveAtomes[self.Z-1] != 0 :
                #The new Atome is already present
                self.ActiveAtomes[self.Z-1]=self.ActiveAtomes[self.Z-1]+an
            else :
                #its a brend new atome
                self.ActiveAtomes[self.Z-1]=an
            self.UpdateFormula()
        
    
            
    def OnRemoveClick(self,event):
        if self.Z != 0:
            if self.ActiveAtomes[self.Z-1] != 0:
                if self.ActiveAtomes[self.Z-1]<=1:
                    #It has to  be removed
                    self.ActiveAtomes[self.Z-1]=0
                else:
                    #One atome has to be removed
                    self.ActiveAtomes[self.Z-1]=self.ActiveAtomes[self.Z-1]-1
                self.UpdateFormula()
    def OnRemoveAllClick(self,event):
        self.ActiveAtomes=numpy.zeros(len(absorption.ATOMS))
        self.UpdateFormula()
    
    def OnExitClick(self,event):
        if self.Parent==None:
            sys.stdout.write("Result of contrast calculation for " + self.ActiveFormula.strip() + " at " + str(self.NRJslider.GetValue()/1000.) +" keV\n")
        else:
            self.Parent.printTXT("Result of contrast calculation for " + self.ActiveFormula.strip() + " at " + str(self.NRJslider.GetValue()/1000.) +" keV")
        
        if(self.MuenBox.GetValue()):
            self.res[0]=absorption.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())
            if self.Parent==None:
                sys.stdout.write("Compound Mu_en/rho  = %1.5f (cm2/g)\n" % self.res[0])
            else:
                self.Parent.printTXT("Compound Mu_en/rho  = %1.5f (cm2/g)" % self.res[0])
            
        else:
            self.res[0]=absorption.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())
            if self.Parent==None:
                sys.stdout.write("Compound Mu_en/rho  = %1.5f (cm2/g)\n" % self.res[0])
            else:
                self.Parent.printTXT("Compound Mu_en/rho  = %1.5f (cm2/g)" % self.res[0])
        self.res[1]=absorption.getElectronDensity(self.ActiveFormula,float(self.DensityText.GetValue()))[0]
        self.res[2]=absorption.getElectronDensity(self.ActiveFormula,float(self.DensityText.GetValue()))[1]
        if self.Parent==None:
            sys.stdout.write("Electronic density  = %1.5e (1/cm3)\n" % self.res[1])
            sys.stdout.write("Scattering length density  = %1.5e (1/cm2)" % self.res[2])
        else:
            self.Parent.printTXT("Electronic density  = %1.5e (1/cm3)" % self.res[1])
            self.Parent.printTXT("Scattering length density  = %1.5e (1/cm2)" % self.res[2])
        '''
        sys.stdout.write("Electronic density  = %1.5e (1/cm3)\n" % self.res[1])
        sys.stdout.write("Scattering length density  = %1.5e (1/cm2)\n" % self.res[2])
        '''
           
        self.Destroy()    

        
    #######


if __name__== '__main__':
    app = wx.PySimpleApp()
    frame=AbsorptionForm(None, -1)
    frame.Show()
    app.MainLoop()

