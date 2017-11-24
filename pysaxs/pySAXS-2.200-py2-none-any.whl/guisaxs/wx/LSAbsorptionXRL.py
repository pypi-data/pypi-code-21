#!/usr/bin/python

import wx
import numpy
import sys
from pySAXS.LS import absorptionXRL
from pySAXS import xraylib
from pySAXS.tools import isNumeric
'''
29/08/2012 OT : rename file and class LSAbsDlg to LSAbsorptionDlg

15/06/2009 OT : change from Dialog to Frame
    Add Label for NIST
    Change size of Frame

initial work by Antoine Thill

'''

class AbsorptionForm(wx.Frame):
    def __init__(self, parent, set_dir = None,printout=None):
        wx.Frame.__init__(self, parent, -1, "X-Ray absorption tool using Xraylib", \
                           size=wx.Size(580,650),\
                           pos=wx.DefaultPosition,style = wx.DEFAULT_DIALOG_STYLE)
        if dir(parent).__contains__('favicon'):
            wx.Frame.SetIcon(self,parent.favicon)
        self.printout=printout
    
        self.energy=8.03
            
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.res=numpy.array([0.,0.,0.])
        self.Z=0
        self.ActiveFormula=""
        self.ActiveAtomes=numpy.zeros(120)
        
        self.ChampText  =  wx.StaticText(self, 101, "click to select atoms", wx.Point(200, 100))
        #energy slider and buttons
        # the current NRJ is obtained with NRJslider.GetValue() in eV
        self.NRJlabel  =  wx.StaticText(self, -1, "Energy (keV)", wx.Point(20, 20))
        self.NRJTextCtrl=wx.TextCtrl(self,104,"",wx.Point(100,20),wx.Size(100,20))
        self.NRJTextCtrl.SetValue(str(self.energy))
        #self.Bind(wx.EVT_TEXT, self.NRJUpdate)
        if self.energy!=0:
            lambdaValue=xraylib.KEV2ANGST/self.energy
        self.LambdaLabel= wx.StaticText(self, -1, "Lambda (Angstrom) = "+str(lambdaValue), wx.Point(250, 20))
        '''
        self.NRJslider=wx.Slider(self,104,8030,1000,50000,\
                                 wx.Point(20,20),\
                                 wx.Size(200,15),\
                                 wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.NRJslider.SetTickFreq(5000,1)
        
        self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        self.NRJText  =  wx.StaticText(self, 105, "8.03 keV", wx.Point(250, 15))'''
        self.CommonsourceText  =  wx.StaticText(self, -1, "Common x-ray source :", wx.Point(50, 52))
        for i in range(len(absorptionXRL.COMMON_XRAY_SOURCE_MATERIALS)):
            Beg=1
            # H button
            self.buttonSource =wx.Button(self, 1000+i, absorptionXRL.COMMON_XRAY_SOURCE_MATERIALS[i], wx.Point(200+i*35,47),wx.Size(30,30))
            self.Bind(wx.EVT_BUTTON, self.OnClickSource, self.buttonSource)
        
        self.ResetButton =wx.Button(self, 106, "Reset", wx.Point(520,12),wx.Size(50,30))
        wx.EVT_BUTTON(self, 106, self.OnResetClick)
        '''
        #Check box for musrho or musrhoen
        self.MuenBox=wx.CheckBox(self,107,"Mu_en ",(450,15))
        self.Bind(wx.EVT_CHECKBOX, self.CheckBoxUpdate)
        self.MuenBox.SetValue(1)
        '''
        self.button=[]
        #################
        #Definition des bouttons de chaque atome pris en charge dans le module
        #################
        Bcol=20
        Blig=100
        Bsiz=30
        Znb=1
        # H button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+17*Bsiz
        # He button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=20
        Blig=Blig+Bsiz
        # Li button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Be button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+11*Bsiz
        # B button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # C button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # N button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # O button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # F button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Ne button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=20
        Blig=Blig+Bsiz
        # Na button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Mg button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+11*Bsiz
        # Al button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Si button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # P button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # S button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Cl button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz
        # Ar button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1

        Bcol=20
        Blig=Blig+Bsiz
        #ligne 4
        for n in numpy.arange(18):
            # next button
            self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        #ligne 5
        for n in numpy.arange(18):
            # next button
            self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        # Cs button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz        
        # Ba button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz 
        # La button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        #Lanthanides line
        Bcol=20
        Blig=Blig+3*Bsiz
        for n in numpy.arange(14):
            # next button
            self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        #fin de la ligne 6
        Bcol=20+3*Bsiz
        Blig=Blig-3*Bsiz
        for n in numpy.arange(15):
            # next button
            self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz
        Bcol=20
        Blig=Blig+Bsiz
        # Fr button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz        
        # Ra button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        Bcol=Bcol+Bsiz 
        # Ac button
        self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        Znb=Znb+1
        #Acthinides line
        Bcol=20
        Blig=Blig+3*Bsiz
        for n in numpy.arange(3):
            # next button
            self.button =wx.Button(self, Znb, xraylib.AtomicNumberToSymbol(Znb), wx.Point(Bcol,Blig),wx.Size(Bsiz,Bsiz))
            self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
            Znb=Znb+1
            Bcol=Bcol+Bsiz

        decal=50
        self.SymboleText  =  wx.StaticText(self, 101, "Symbole = ", wx.Point(20, 365+decal))
        self.NameText  =  wx.StaticText(self, 101, "Name = ", wx.Point(20, 380+decal))
        self.ZText  =  wx.StaticText(self, 101, "Atomic number = ", wx.Point(20, 395+decal))
        self.MasseText  =  wx.StaticText(self, 101, "Atomic weight = ", wx.Point(20, 410+decal))
        self.MuText  =  wx.StaticText(self, 101, "Mu_en/rho = ", wx.Point(20, 425+decal))

        # Add button
        self.AtomsNumberLabel=wx.StaticText(self,1092,"Number of atoms  = ",wx.Point(20,455+decal))
        self.AtomsNumber=wx.TextCtrl(self,1091,"",wx.Point(130,453+decal),wx.Size(50,20))
        self.AtomsNumber.SetValue("1.0")
        #self.Bind(wx.EVT_TEXT, self.ThicknessUpdate)
        self.Addbutton=wx.Button(self, 108, "Add", wx.Point(20,475+decal),wx.Size(50,30))
        wx.EVT_BUTTON(self, 108, self.OnAddClick)
        # Remove button
        self.RemoveButton =wx.Button(self, 109, "Remove", wx.Point(70,475+decal),wx.Size(60,30))
        wx.EVT_BUTTON(self, 109, self.OnRemoveClick)
         # Remove all button
        self.RemoveButton =wx.Button(self, 1090, "Remove All", wx.Point(130,475+decal),wx.Size(80,30))
        wx.EVT_BUTTON(self, 1090, self.OnRemoveAllClick)

        self.FormulaLabel=wx.StaticText(self,110,"Active Formula  = ",wx.Point(250,350+decal))
        self.CompoundMuLabel=wx.StaticText(self,112,"Compound Mu_en/rho  = ",wx.Point(250,370+decal))
        self.DensityLabel=wx.StaticText(self,113,"Density  = ",wx.Point(250,390+decal))
        self.DensityText=wx.TextCtrl(self,114,"",wx.Point(375,390+decal),wx.Size(75,20))
        self.DensityText.SetValue("1.00")
        #self.Bind(wx.EVT_TEXT, self.DensityUpdate)
        self.DensityUnitLabel=wx.StaticText(self,115,"(g/cm3)",wx.Point(500,390+decal))
        self.CompoundEDLabel=wx.StaticText(self,116,"Electronic density  = ",wx.Point(250,410+decal))
        self.CompoundSLLabel=wx.StaticText(self,117,"Scattering length density  = ",wx.Point(250,430+decal))
        self.ThicknessLabel=wx.StaticText(self,118,"Thickness  = ",wx.Point(250,450+decal))
        self.ThicknessText=wx.TextCtrl(self,119,"",wx.Point(375,450+decal),wx.Size(75,20))
        self.ThicknessText.SetValue("0.1")
        self.Bind(wx.EVT_TEXT, self.UpdateFormula)
        self.ThicknessUnitLabel=wx.StaticText(self,120,"(cm)",wx.Point(500,450+decal))
        self.TransLabel=wx.StaticText(self,121,"X-ray trans  = ",wx.Point(250,470+decal))

        self.QuitButton=wx.Button(self,wx.ID_EXIT,"QUIT",wx.Point(275,500+decal),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_EXIT, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        #XRAY LIB 
        self.NISTLabel=wx.StaticText(self,129,"Datas from xraylib libraries",wx.Point(100,550+decal))
        self.NISTLabel.SetForegroundColour('blue')
        


    def OnResetClick(self,event):
        
        self.Z=0
        '''self.NRJslider.SetValue(8028)
        self.NRJText.SetLabel(str(self.NRJslider.GetValue()/1000.0) +" keV")'''
        self.energy=8.03
        self.NRJTextCtrl.SetValue(str(self.energy))
        self.ChampText.SetLabel("click to select an atom")
        self.SymboleText.SetLabel("Symbole = ")
        self.NameText.SetLabel("Name = " )
        self.ZText.SetLabel("Atomic number = ")
        self.MasseText.SetLabel("Atomic weight = ")
        self.UpdateFormula()

 
              
    ####   
    #On clique sur l'un des bouttons du tableau
    ####
    def OnClick(self,event):
        #self.DensityText.SetValue(absorptionXRL.ATOMS[event.GetId()-1])
        Z=event.GetId()
        self.SymboleText.SetLabel("Symbol = " +  xraylib.AtomicNumberToSymbol(Z))
        self.NameText.SetLabel("Name = " +  absorptionXRL.getNameZ(Z))
        self.ZText.SetLabel("Atomic number : " + str(Z))
        self.Z=Z
        self.MasseText.SetLabel("Atomic weight : "+  str(xraylib.AtomicWeight(Z)))
        self.MuText.SetLabel("Mu/rho = " + str(absorptionXRL.getMuZ(Z,self.energy)))
      
    def UpdateFormula(self,verbose=False):
        Tr=-1
        ED=-1
        SLD=-1
        #print "Fupdate"
        energy=self.NRJTextCtrl.GetValue()
        if isNumeric.isNumeric(energy):
            self.energy=float(energy)
            if self.energy!=0:
                lambdaValue=xraylib.KEV2ANGST/self.energy
                self.LambdaLabel.SetLabel("Lambda (Angstrom) = "+str(lambdaValue))
                
        self.ActiveFormula=""
        #If at least one atome exist
        if sum(self.ActiveAtomes)!=0:
            N=self.ActiveAtomes.take(numpy.where(self.ActiveAtomes!=0)[0])
            ind=numpy.where(self.ActiveAtomes!=0)[0]
            j=0
            for i in ind:
                #self.ActiveFormula=self.ActiveFormula + str(absorptionXRL.ATOMS[int(i)]) + ' ' + str(int(N[int(j)])) + ' '
                self.ActiveFormula=self.ActiveFormula + xraylib.AtomicNumberToSymbol(int(i)+1) + ' ' + str(N[int(j)]) + ' '
                j=j+1
            
            self.FormulaLabel.SetLabel("Active Formula  = "+self.ActiveFormula.strip())
            MuRho=absorptionXRL.getMuFormula(self.ActiveFormula,self.energy)
            self.CompoundMuLabel.SetLabel("Compound Mu/rho  = %1.5f (cm2/g)" % MuRho)
            density=self.DensityText.GetValue()
            if isNumeric.isNumeric(density):
                density=float(density)
                ED=absorptionXRL.getElectronDensity(self.ActiveFormula,density)[0]
                self.CompoundEDLabel.SetLabel("Electronic density  = %1.5e (1/cm3)" % ED)
                SLD=absorptionXRL.getElectronDensity(self.ActiveFormula,density)[1]
                self.CompoundSLLabel.SetLabel("Scattering length density  = %1.5e (1/cm2)" % SLD)
                if isNumeric.isNumeric(self.ThicknessText.GetValue()):
                    thickness=float(self.ThicknessText.GetValue())
                    Tr=absorptionXRL.getTransmission(self.ActiveFormula,\
                                               thickness,\
                                               density,\
                                                self.energy)
                    #self.TransLabel.SetLabel("X-ray transmission  = %1.5e" % numpy.exp(-float(self.DensityText.GetValue())*absorptionXRL.getMuFormula(self.ActiveFormula,self.NRJslider.GetValue()/1000.,self.MuenBox.GetValue())*float(self.ThicknessText.GetValue())))
                    self.TransLabel.SetLabel("X-ray transmission  = %1.5e" % Tr)
                    if verbose:
                        self.printTXT("------ Absorption tools using xraylib -----")
                        self.printTXT("Energy : (keV) ", self.energy)
                        self.printTXT("Compound formula: ", self.ActiveFormula)
                        self.printTXT("Compound Mu_en/rho  =  (cm2/g) ",MuRho)
                        self.printTXT("Electronic density  =  (1/cm3) ",ED)
                        self.printTXT("Scattering length density  =  (1/cm2) ",SLD)
                        self.printTXT("X-ray transmission  = ",Tr)
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
        self.ActiveAtomes=numpy.zeros(120)
        self.UpdateFormula()
    
    def OnClickSource(self,event):
        sourceID=1000-event.GetId()
        source=absorptionXRL.COMMON_XRAY_SOURCE_MATERIALS[sourceID]
        energy=absorptionXRL.getEnergyFromSource(source)
        self.NRJTextCtrl.SetValue(str(energy))
           
    def OnExitClick(self,event):
        self.UpdateFormula(verbose=True)
        self.Destroy()    

    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
        
    #######


if __name__== '__main__':
    app = wx.PySimpleApp()
    frame=AbsorptionForm(None, -1)
    frame.Show()
    app.MainLoop()

