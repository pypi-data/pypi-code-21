#!/usr/bin/python
"""
project : pySAXS
description : wxPython Class to plot some data files to gnuplot
authors : Antoine Thill, Olivier Spalla, Olivier Tache, Debasis Sen
Last changes :
    10-11-2009 OT : Replaced LsScattering by GuiSAXS.py
    15-06-2009 OT : little changes for new models, replace with by with_ for gnuplot commands
                change gnuplot plotting commands
    05-06-2007 OT : big changes everywhere !
                    add data management, no more reference to usaxs data directly
    16-03-2007 OT : send loglog commands directly to gnuplot
    13-03-2007 OT : add a SAXS and USAXS menu
                    add a HELP (about and licence dialog box) menu

"""
import unicodedata
import wx
import numpy
#import Gnuplot
import os
from os import path
import sys
import pySAXS.LS.LSusaxs as LSusaxs
import pySAXS.LS.LSsca as LSsca
from pySAXS.guisaxs import LSAbsorptionDlg
try:
        import pySAXS.xraylib
        from pySAXS.guisaxs import LSAbsorptionXRL
        #print "xraylib found"
        WITH_XRAYLIB=True
except :
        print "xraylib could not be found"
        WITH_XRAYLIB=False

import pySAXS.guisaxs.LSneutronDlg as LSneutronDlg
from  pySAXS.guisaxs.LSModelDlg import LSModelDlg
import pySAXS.guisaxs.LSBackgroundDlg as LSBackgroundDlg
from  pySAXS.guisaxs.LSInvariantDlg import LSInvariantDlg
import pySAXS.guisaxs.LSFitGaussianDlg as LSFitGaussianDlg
from pySAXS.guisaxs.LSGenericParameterDlg import *
#import pySAXS.guisaxs.LSZeroAdjustDlg as LSZeroAdjustDlg
from pySAXS.guisaxs.LSTransmissionDlg import LSTransmissionDlg
from pySAXS.guisaxs.LSUSAXSsimuDlg import LSUSAXSsimuDlg
import pySAXS.guisaxs.LSDeconvolutionDlg as LSDeconvolutionDlg
import pySAXS.guisaxs.LSResolutionDlg as LSResolutionDlg
from pySAXS.guisaxs.LSSelectxyRangeDlg import LSSelectqRangeDlg
from pySAXS.guisaxs.LSClipqRangeDlg import LSClipqRangeDlg
#from pySAXS.guisaxs.pySaxsPlotwx import pySaxsPlot
from pySAXS.guisaxs.SAXSAbsoluteDlg import SAXSAbsoluteDlg
from pySAXS.guisaxs.LSConcatenateDlg import LSConcatenateDlg
from pySAXS.guisaxs.LSInterpolateDlg import LSInterpolateDlg
from pySAXS.guisaxs.LSEvalDlg import LSEvalDlg
from pySAXS.guisaxs.dataset import *
from pySAXS.tools import filetools
from pySAXS.tools import DetectPeaks
import pySAXS.tools.fileimage as fileimage
from pySAXS.guisaxs.textView import *
import pySAXS.LS.SAXSparametersXML as SAXSparameters
import string as string
from scipy import interpolate
from scipy import misc
from scipy import stats
from scipy import integrate
from copy import copy
from pySAXS.models import listOfModels
import pySAXS.models
import pySAXS
from pySAXS.guisaxs import pySaxsColors
from matplotlib import colors

try :
        from pySAXS.guisaxs import wxmpl
        from pySAXS.guisaxs import matplotlibwx
except:
        print "Matplotlib is not installed"

try:
    import pyFAI
    from pySAXS.guisaxs import FAIdlg
    WITH_PYFAI=True
except:
    print "pyFAI is not installed"
    WITH_PYFAI=False
    
    
# ---------------This program uses the above modules-----
#type of datas [description, file extension, color]
typefile={'usaxs':['USAXS Raw Data file','txt','BLUE'],\
                  'usaxsrck':['USAXS Rocking Curve','txt','MAROON' ],\
                  'usaxsdsm':['USAXS Desmeared File','dsm','MAROON'],\
                  'saxs':['SAXS raw datas','rgr','FIREBRICK'],\
                  'fit2d':['datas from fit2D','chi','RED'],\
                  'txttab':['datas in 2 columns (or 3 with error) with tab separator','*','MAROON'],\
                  'txtcomma':['datas in 2 columns (or 3 with error) with comma separator','*','PURPLE'],\
                  'scaled':['datas scaled','*','TEAL'],\
                  'calculated':['datas calculated','*','PURPLE'],\
                  'reference':['reference','*','VIOLET RED'],\
                  'model':['model','*','GREEN'],\
                  'supermodel':['super model','*','INDIAN RED'],\
                  'resfunc':['USAXS resolution function','dat','MAROON']}
        
#list of data type to propose in open file dialog        
typefile_list=['saxs','usaxs','usaxsrck','usaxsdsm','fit2d','txttab','txtcomma','resfunc'] 


class GuiSAXS(wx.Frame):
    
    def __init__(self, parent, title):
        '''
        Initialisations and menus
        '''
        MainWidthSize=500
        wx.Frame.__init__(self, parent, title="pySAXS",\
                           style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |\
                             wx.CLOSE_BOX|wx.CLIP_CHILDREN\
                             ,pos=(50,50))
        self.favicon=wx.Icon(pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'pySaxs32.gif',wx.BITMAP_TYPE_GIF)
        wx.Frame.SetIcon(self,self.favicon)
        
       
              
        #------------ main object  for datas 
        self.data_dict={}
        '''--------------------------'''
        self.ISMODEL=False
        self.DataBackground=0.0
        self.RockBackground=0.0
        self.backgr=0.
        self.wavelength=1.54
        self.workingdirectory=""
        self.M=pySAXS.models.Model()
        self.plotexp=0.0
        self.loglog=10023
        self.loglin=10024
        self.linlog=10025
        self.linlin=10026
        self.axetype=self.loglog
        self.i_plot=10027
        self.iq_plot=10028
        self.iq2_plot=10029
        self.iq3_plot=10030
        self.iq4_plot=10031
        self.xselect='set xrange[:]'
        self.yselect='set yrange[:]'
        self.np=50
        self.qmini=None
        self.qmaxi=None
        self.Imini=None
        self.Imaxi=None

        self.colors=pySaxsColors.listOfColors()
        self.colorsD=pySaxsColors.listOfColorsNames()

        #self.saxsparameters=SAXSparameters.SAXSparameters()

        # -------------- Set up menu bar for the program.
        self.mainmenu = wx.MenuBar()                  # Create menu bar.

        # Make the 'Project' menu.

        # Make the 'File' menu.
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, 'Open\tCtrl-O', 'Open data file')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnDataLoad, item)  # Create and assign a menu event.
        item = menu.Append(wx.ID_ANY, 'Open a dataset\tCtrl-D', 'Open a dataset')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnDataOpenDataset, item)  # Create and assign a menu event.
        item = menu.Append(wx.ID_ANY, 'Append a dataset', 'Append a dataset')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnDataAppend, item)  # Create and assign a menu event.

        item = menu.Append(wx.ID_ANY, 'Save as txt', 'save data file')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnDataSave, item)  # Create and assign a menu event.
        item = menu.Append(wx.ID_ANY, 'Save as dataset\tCtrl-S', 'save all dataset')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnDataSaveDataset, item)  # Create and assign a menu event.
        
        item = menu.Append(wx.ID_ANY, '&Reset Data', 'Reset Data')
        self.Bind(wx.EVT_MENU, self.OnDataReset, item)
        item = menu.Append(wx.ID_EXIT, 'Exit\tCtrl-W', 'Exit program')
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, item)
        self.mainmenu.Append(menu, '&File')  # Add the project menu to the menu bar.

        #----------- Menu Edit
        
        
        #-- pop up menu for listbox
        self.popupmenu=wx.Menu()
        item=self.popupmenu.Append(wx.ID_ANY, 'Select all\tCtrl-A', 'Check all datasets')
        self.Bind(wx.EVT_MENU, self.OnSelectAll, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'UnSelect all', 'Check all datasets')
        self.Bind(wx.EVT_MENU, self.OnUnSelectAll, item)
        self.popupmenu.AppendSeparator()
        #---
        item=self.popupmenu.Append(wx.ID_ANY, 'Refresh', 'Refresh data from file (if exist)')
        self.Bind(wx.EVT_MENU, self.OnPopUpRefresh, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Rename', 'Rename Data set')
        self.Bind(wx.EVT_MENU, self.OnPopUpRename, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Remove\tDelete', 'Remove Data set')
        self.Bind(wx.EVT_MENU, self.OnPopUpRemove, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Duplicate\tCtrl-C', 'Duplicate Data set')
        self.Bind(wx.EVT_MENU, self.OnPopUpDuplicate, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Duplicate without link', 'Duplicate Data set')
        self.Bind(wx.EVT_MENU, self.OnPopUpDuplicateWithoutLink, item)
        self.popupmenu.AppendSeparator()
        #---
        
        #---
        item=self.popupmenu.Append(wx.ID_ANY, 'Clip Q range', 'Clip Q range')
        self.Bind(wx.EVT_MENU, self.OnClipqRangeShow, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Scale Q range', 'Scale Q range')
        self.Bind(wx.EVT_MENU, self.OnScaleQ, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Concatenate', 'Concatenate datas')
        self.Bind(wx.EVT_MENU, self.OnConcatenateShow, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Derivate', 'Derivate Data set')
        self.Bind(wx.EVT_MENU, self.OnDerivate, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Smooth', 'Smooth Data set')
        self.Bind(wx.EVT_MENU, self.OnSmooth, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Find peaks', 'Find peaks')
        self.Bind(wx.EVT_MENU, self.findPeaks, item)
        item=self.popupmenu.Append(wx.ID_ANY, 'Interpolate', 'Interpolate q range')
        self.Bind(wx.EVT_MENU, self.OnInterpolateShow,item)
        item = self.popupmenu.Append(wx.ID_ANY, 'Calculator', 'Calculator')
        self.Bind(wx.EVT_MENU, self.OnEvalShow, item)
        item = self.popupmenu.Append(wx.ID_ANY, 'Statistics', 'Statistics')
        self.Bind(wx.EVT_MENU, self.OnStatInformations, item)
        item = self.popupmenu.Append(wx.ID_ANY, 'Generate Noise', 'Noise generator')
        self.Bind(wx.EVT_MENU, self.OnGenerateNoise, item)
        self.popupmenu.AppendSeparator()
        item = self.popupmenu.Append(wx.ID_ANY, 'Add a reference value', 'Add a reference value')
        self.Bind(wx.EVT_MENU, self.OnAddReferenceValue, item)
        
        #--pop up menu for colours
        self.popupmenuC=wx.Menu()
        ic=30000
        for name in self.colorsD:
            item=self.popupmenuC.Append(ic, str(name))
            self.Bind(wx.EVT_MENU, self.OnChangeColors, item)
            ic+=1
        item=self.popupmenu.Append(wx.ID_ANY,'Change Colors', 'Change Colors')
        self.Bind(wx.EVT_MENU, self.OnChangeColors, item)
        #self.popupmenu.AppendMenu(wx.ID_ANY, 'Change Colors', self.popupmenuC)
        self.popupmenu.AppendSeparator()

        self.mainmenu.Append(self.popupmenu, '&Edit') # Add the edit menu to the menu bar.
        #------- make the 'Data treatement' menu
        #U------ SAXS MENU
        menuUsaxs = wx.Menu()
        item = menuUsaxs.Append(wx.ID_ANY, 'Transmission and background correction', 'Transmission and background correction')
        self.Bind(wx.EVT_MENU, self.OnUSAXSTransmissionDlgShow, item)
        item = menuUsaxs.Append(wx.ID_ANY, '&Calculate Resolution Function', 'Resolution Function')
        self.Bind(wx.EVT_MENU, self.OnResolution, item)
        item = menuUsaxs.Append(wx.ID_ANY, '&Deconvolution', 'Deconvolution')
        self.Bind(wx.EVT_MENU, self.OnUSAXSDeconvolution, item)


        #------- SAXS MENU
        menuSaxs=wx.Menu()
        item = menuSaxs.Append(wx.ID_ANY, 'Scaling Data', 'Scaling Data')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnScalingSAXSDlgShow,item)
        item = menuSaxs.Append(wx.ID_ANY, 'Load Parameters', 'Load Parameters')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnScalingSAXSDlgLoad,item)
        item = menuSaxs.Append(wx.ID_ANY, 'Data substraction', 'Substraction')  # Append a new menu
        self.Bind(wx.EVT_MENU, self.OnSAXSSubstraction,item)
        if WITH_PYFAI:
            item = menuSaxs.Append(wx.ID_ANY, 'Radial Averaging', 'Radial Averaging')  # Append a new menu
            self.Bind(wx.EVT_MENU, self.OnSAXSRAD,item)
        
        #item = menuSaxs.Append(wx.ID_ANY, 'Quick Plot', 'Quick plot')  # Append a new menu
        #self.Bind(wx.EVT_MENU, self.OnQuickPlot, item)
        
        #------- DATA TREATMENT MENU
        dataTr = wx.Menu()
        dataTr.AppendMenu(wx.ID_ANY, 'USAXS', menuUsaxs)
        dataTr.AppendMenu(wx.ID_ANY, 'SAXS', menuSaxs)
        self.mainmenu.Append(dataTr, '&Data treatment')  # Add the project menu to the menu bar.

        # ------- Model menu
        menuModels=wx.Menu()

        item = menuModels.Append(wx.ID_ANY, 'Invariant', 'Compute the invariant')
        self.Bind(wx.EVT_MENU, self.OnInvariant, item)
        
        submenu = wx.Menu()
        modelsDict=listOfModels.listOfModels() #get {'Spheres Monodisperse': 'MonoSphere', 'Gaussian': 'Gaussian'}
        dd=modelsDict.items()#[('Spheres Monodisperse', 'MonoSphere'), ('Gaussian', 'Gaussian')]
        dd=self.sortDictByKey(modelsDict)
        self.modelsDictId={}
        for id in range(len(dd)):
            #construct a dictionary of models with id item
            #{0,('Spheres Monodisperse', 'MonoSphere') : 1,('Gaussian', 'Gaussian')}
            self.modelsDictId[id]=dd[id]
            item = submenu.Append(id, dd[id][0])
            self.Bind(wx.EVT_MENU, self.OnModelSelect, item)
        self.numberOfModels=id
        supermodelsDict=listOfModels.listOfSuperModels() #get {'Spheres Monodisperse': 'MonoSphere', 'Gaussian': 'Gaussian'}
        dd=supermodelsDict.items()#[('Spheres Monodisperse', 'MonoSphere'), ('Gaussian', 'Gaussian')]
        dd=self.sortDictByKey(supermodelsDict)
        self.supermodelsDictId={}
        for ids in range(len(dd)):
            #construct a dictionary of models with id item
            #{0,('Spheres Monodisperse', 'MonoSphere') : 1,('Gaussian', 'Gaussian')}
            self.supermodelsDictId[ids]=dd[ids]
            item = submenu.Append(self.numberOfModels+ids, "SUPER : "+dd[ids][0])
            self.Bind(wx.EVT_MENU, self.OnSuperModelSelect, item)

        item = menuModels.AppendMenu(wx.ID_ANY, 'Models',submenu)
        self.mainmenu.Append(menuModels, 'Compute') # Add the file menu to the menu bar.

        #---------- Menu GnuPlot
        '''menu=wx.Menu()
        submenu=wx.Menu()
        item = submenu.Append(self.loglog, '&xLog-yLog', 'Log-Log Plot type')
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(self.loglin, '&xLog-yLin', 'Log-Lin Plot type')
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(self.linlog, '&xLin-yLog', 'Lin-Log Plot type')
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(self.linlin, '&xLin-xLin', 'Lin-Lin Plot type')
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Axes',submenu)

        submenu=wx.Menu()
        item = submenu.Append(wx.ID_ANY, 'Grid ON', 'Grid On')
        self.Bind(wx.EVT_MENU, self.OnGridOn, item)
        item = submenu.Append(wx.ID_ANY, 'Grid OFF', 'Grid Off')
        self.Bind(wx.EVT_MENU, self.OnGridOff, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Grid',submenu)


        item = menu.Append(10003, '&Select XY Plot Range', 'Select XY Range')
        self.Bind(wx.EVT_MENU, self.OnSelectqRangeShow, item)
        item = menu.Append(10004, '&Reset XY Plot Range', 'Reset XY Range')
        self.Bind(wx.EVT_MENU, self.OnResetSelectqRange, item)

        submenu=wx.Menu()
        item = submenu.Append(self.i_plot, 'I', 'I Plot type')
        self.Bind(wx.EVT_MENU, self.OnPorodPlotType, item)
        item = submenu.Append(self.iq_plot, 'Iq', 'Iq Plot type')
        self.Bind(wx.EVT_MENU, self.OnPorodPlotType, item)
        item = submenu.Append(self.iq2_plot, 'Iq2', 'Iq2 Plot type')
        self.Bind(wx.EVT_MENU, self.OnPorodPlotType, item)
        item = submenu.Append(self.iq3_plot, 'Iq3', 'Iq3 Plot type')
        self.Bind(wx.EVT_MENU, self.OnPorodPlotType, item)
        item = submenu.Append(self.iq4_plot, 'Iq4', 'Iq4 Plot type')
        self.Bind(wx.EVT_MENU, self.OnPorodPlotType, item)
        item = menu.AppendMenu(wx.ID_ANY, 'Plot &Type', submenu)

        item = menu.Append(wx.ID_ANY, 'Send command to plot', 'Send command to plot')
        self.Bind(wx.EVT_MENU, self.OnSendCommandToPlot, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, 'Reinit Gnuplot', 'Reinit Gnuplot')
        self.Bind(wx.EVT_MENU, self.OnReinitGnulot, item)
        
        self.mainmenu.Append(menu, '&Gnuplot') # Add the file menu to the menu bar
        '''
        #----------- Menu Tools
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, 'X-Ray absorption tool\tCtrl-X', 'X-Ray absorption tool')
        self.Bind(wx.EVT_MENU, self.OnToolsContraste, item)
        if WITH_XRAYLIB:
                item = menu.Append(wx.ID_ANY, 'X-Ray absorption tool XRAYLIB', 'X-Ray absorption tool')
                self.Bind(wx.EVT_MENU, self.OnToolsContrasteXRL, item)
        item=menu.Append(wx.ID_ANY, 'Find peaks', 'Find peaks')
        self.Bind(wx.EVT_MENU, self.findPeaks, item)
        self.mainmenu.Append(menu, '&Tools') # Add the tools menu to the menu bar.

        #----------- Menu Help
        helpmenu=wx.Menu()
        item=helpmenu.Append(wx.ID_ANY, '&About pySAXS', '')
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        #helpmenu.AppendSeparator()
        item=helpmenu.Append(wx.ID_ANY, 'Changes', '')
        self.Bind(wx.EVT_MENU, self.OnChange, item)
        item=helpmenu.Append(wx.ID_ANY, 'License', '')
        self.Bind(wx.EVT_MENU, self.OnLicence, item)
        
        #------- DOC MENU
        menuDoc=wx.Menu()
        self.docs=self.getListOfDocs()
        i=0
        for name in self.docs:
           item = menuDoc.Append(20000+i, path.basename(name), name)  # Append a new menu
           self.Bind(wx.EVT_MENU, self.OnDocClick,item)
           i+=1
        menuDocMain=wx.Menu()
        helpmenu.AppendMenu(wx.ID_ANY, 'Documents', menuDoc)
        self.mainmenu.Append(helpmenu, '&Help') # Add the help menu to the menu bar.

        # Attach the menu bar to the window.
        self.SetMenuBar(self.mainmenu)
        
             
        
        #------------------------------- Main Controls
        panel=wx.Panel(self,-1,style=wx.SUNKEN_BORDER)
        #MainSizer=wx.BoxSizer(wx.VERTICAL) #MainSizer filled with sizerA and sizerB
        MainSizer=wx.BoxSizer(wx.VERTICAL) #MainSizer filled with sizerA and sizerB
        sizerA=wx.BoxSizer(wx.HORIZONTAL)#top with list box at left and infos at right
        sizerB=wx.BoxSizer(wx.VERTICAL)#bottom with text
        
       
        
        #-- Listbox for data set
        samplelist=[]
        box1=wx.StaticBox(panel,-1,"Data set :")
        sizer1=wx.StaticBoxSizer(box1,wx.VERTICAL)
        #sizer1=wx.BoxSizer(wx.VERTICAL)
        self.listBox=wx.CheckListBox(panel,-1,size=(MainWidthSize,300),choices=samplelist,style=wx.LB_SINGLE)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckData, self.listBox)
        self.Bind(wx.EVT_LISTBOX, self.OnClickData, self.listBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.OnDClickData,self.listBox)
        self.listBox.Bind(wx.EVT_CONTEXT_MENU,self.OnShowPopup) #create event for popup menu
        sizer1.Add(self.listBox,flag=wx.EXPAND)

        #-- Static Box for informations
        box2 = wx.StaticBox(panel, -1, "Data set Informations :")
        sizer2=wx.StaticBoxSizer(box2,wx.HORIZONTAL)
        #sizer2=wx.BoxSizer(wx.VERTICAL)
        self.infotxt=wx.StaticText(panel,-1,"infos...\n on \n dataset",size=(MainWidthSize,100))
        sizer2.Add(self.infotxt,flag=wx.EXPAND)
        #sizer2.Add(sb)
        
        #-- Static box for text
        box3=wx.StaticBox(panel, -1, "Informations :")
        sizer3=wx.StaticBoxSizer(box3,wx.HORIZONTAL)
        #sizer3=wx.BoxSizer(wx.VERTICAL)
        self.multitxt=wx.TextCtrl(panel,-1,"-- Welcome to GuiSAXS--\n",size=(MainWidthSize,150),style=wx.TE_MULTILINE)
        sizer3.Add(self.multitxt,flag=wx.EXPAND)
        
        sizerA.Add(sizer1,0,flag=wx.ALL|wx.EXPAND,border=1)
        sizerB.Add(sizer2,0,flag=wx.ALL|wx.EXPAND,border=1)
        sizerB.Add(sizer3,0,flag=wx.ALL|wx.EXPAND,border=1)
        MainSizer.Add(sizerA,0,flag=wx.ALL|wx.EXPAND,border=1)
        MainSizer.Add(sizerB,0,flag=wx.ALL|wx.EXPAND,border=1)
        
        panel.SetSizer(MainSizer)
        MainSizer.Fit(self)
        #self.SetAutoLayout(True)
        #self.SetSizer(Big)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
               
        
        #self.Bind(wx.EVT_SIZE, self.OnSize)
        try :
                self.createWxPlot()
                
        except:
            print "Problem when using matplotlib"
            self._matplotlib=False
        
        ## ---------- Initialize default values
        self.qmod=LSsca.Qlogspace(1e-4,1.,500.)
        '''self.gp=Gnuplot.Gnuplot()
        self.gp.reset()'''
        
        self.Show(True)
    
    def sortDictByKey(self,d):
        '''
        return list of couple sorted by key
        '''
        l=[]
        for key in sorted(d.iterkeys()):
            l.append((key, d[key]))
        return l
        
    def OnSize(self, evt):
        print "resize"
        #self.MainSizer.Fit(self)
        if self.GetAutoLayout():
            self.Layout()
        
    def printTXT(self,txt="",par=""):
        '''
        print on comment ctrl
        '''
        self.multitxt.AppendText(str(txt)+str(par)+"\n")
    
    def OnCloseWindow(self,event):
        self.gp=None
        try:
            if self._matplotlib:
                self.plotframe.Close()
        except:
            pass
        finally:
            self.Destroy()  # frame
            

    def OnShowPopup(self,event):
        '''
        show popup menu
        '''
        index=self.listBox.GetSelection()
        if index<>-1:
            pos=event.GetPosition()
            pos=self.listBox.ScreenToClient(pos)
            self.listBox.PopupMenu(self.popupmenu,pos)
    
    def OnChangeColors(self,event):
        index=self.listBox.GetSelection()
        if index==-1:
            return
        name = self.listBox.GetString(index)
        '''#get the color
        id=event.GetId()-30000'''
        dialog = wx.ColourDialog(None)
        dialog.GetColourData().SetChooseFull(True)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData()
            #print 'You selected: %s\n' % str(data.GetColour().GetAsString(flags=wx.C2S_HTML_SYNTAX))
            self.data_dict[name].color=data.GetColour().GetAsString(flags=wx.C2S_HTML_SYNTAX)
            dialog.Destroy()
        #self.data_dict[name].color=self.colors[id]
        #print id,self.data_dict[name].color
        self.redrawTheList()
        self.replotWxPlot()
            
    def OnPopUpRefresh(self,event):
        '''
        refresh data from file (is exist)
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        label = self.listBox.GetString(index)
        filename=self.data_dict[label].filename
        type=self.data_dict[label].type
        if type!=None:
            self.printTXT("refresh "+ filename)
            self.ReadFile(filename,type)
            self.RePlot()
        else:
            self.printTXT('type of data unknown -> not possible to refresh datas ')
        

    def OnPopUpRename(self,event):
        '''
        rename a data set
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        label = self.listBox.GetString(index)
        dlg=wx.TextEntryDialog(self,"Enter the data set new name :","pySAXS - Please enter text",defaultValue=label,style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            newlabel=dlg.GetValue()
            newlabel=self.cleanString(newlabel)
            if self.data_dict.has_key(newlabel):
                dlg2=wx.MessageDialog(self, 'There is already a data set with this name !',  wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
            #print newlabel
            self.printTXT("Rename  "+label+" into : ",newlabel)
            self.data_dict[newlabel]=self.data_dict[label]
            self.data_dict[newlabel].name=newlabel
            self.data_dict.pop(label)
            self.redrawTheList()
            self.RePlot(event)

    def OnPopUpDuplicate(self,event):
        '''
        duplicate a data set
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        label = self.listBox.GetString(index)
        dlg=wx.TextEntryDialog(self,"Enter the data set new name :","pySAXS - Please enter text",defaultValue=label,style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            newlabel=dlg.GetValue()
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                dlg2=wx.MessageDialog(self,
                                      message='There is already a data set with this name !',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
            self.data_dict[newlabel]=copy(self.data_dict[label])
            self.data_dict[newlabel].name=newlabel
            #self.data_dict.pop(label)
            self.redrawTheList()
            self.RePlot(event)
    
    def OnPopUpDuplicateWithoutLink(self,event):
        '''
        '''
        '''
        duplicate a data set
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        label = self.listBox.GetString(index)
        dlg=wx.TextEntryDialog(self,"Enter the data set new name :","pySAXS - Please enter text",defaultValue=label,style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            newlabel=dlg.GetValue()
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                dlg2=wx.MessageDialog(self,
                                      message='There is already a data set with this name !',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
            self.data_dict[newlabel]=copy(self.data_dict[label])
            self.data_dict[newlabel].parent=None
            self.data_dict[newlabel].name=newlabel
            self.redrawTheList()
            self.RePlot(event)

    def OnPopUpRemove(self,event):
        '''
        remove a data set
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        index=self.listBox.GetSelection()
        label = self.listBox.GetString(index)
        dlg=wx.MessageDialog(self, 'Are you sure you want to remove this data set : '+label+' ?',  style=wx.YES_NO | wx.ICON_INFORMATION)
        if dlg.ShowModal()==wx.ID_YES:
            #remove
            self.printTXT("removing ",label)
            self.data_dict.pop(label)
            self.redrawTheList()
            self.RePlot(event)

    def OnPopUpModifyModel(self,event):
        index=self.listBox.GetSelection()
        if index==-1:
            return
        label = self.listBox.GetString(index)
        if self.data_dict[label].model<>None:
            childmodel=LSModelDlg(self,label)
            childmodel.Show()

    
    def OnDataLoad(self, event):
        '''
        Load datas
        '''
        if self.data_dict.has_key('exp'):
            dlg=wx.MessageDialog(self,'Do you want to reset active sample datas before loading new ?','pySAXS alert',wx.YES_NO| wx.ICON_QUESTION)
            retCode=dlg.ShowModal()
            dlg.Destroy()
            if (retCode<>wx.ID_YES):
                #reset active datas
                #self.OnDataReset(event)
                #continue
                #exiting
                return
        
        
        wc=''
        for k in typefile_list:
            wc+=typefile[k][0]+' (*.'+typefile[k][1]+')|*.'+typefile[k][1]+'|'
        wc=wc[:-1] #remove last |
        
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            for datafilename in dlg.GetPaths():
                self.printTXT("opening " + datafilename) 
                self.workingdirectory=os.path.dirname(dlg.GetPath())
                extension=filetools.getExtension(datafilename)
                filter_index= dlg.GetFilterIndex()
                filter_key=typefile_list[filter_index]
                self.ReadFile(datafilename,filter_key)
                
        dlg.Destroy()
        self.redrawTheList()
        #-- replot
        self.RePlot()

    def ReadFile(self,datafilename,file_type=None):
        '''
        read file depending of type of file
        '''
        name = filetools.getFilename(datafilename)
        if file_type=='usaxs':
            #if extension=="txt": #it is a txt file
            #data = LSusaxs.ReadUSAXSData(datafilename)
            self.ImportData(datafilename,usecols = (0,2),name=name,type=file_type)
            #self.data_dict[name]=dataset(datafilename,data[:,0],data[:,1],datafilename+ ' raw data',type=file_type)#[data[:,0],data[:,1],datafilename,True]
            #self.data_dict[name].q=LSusaxs.QtoTheta(self.data_dict[name].q,self.wavelength)# Should be masked if the data is already in theta
        elif file_type=='usaxsrck':
            #a USAXS rocking curve
            self.ImportData(datafilename,usecols = (0,2),name='rock',type=file_type)
            #datarock = LSusaxs.ReadUSAXSData(datafilename)
            #self.data_dict['rock']=dataset('rock',datarock[:,0],datarock[:,1],datafilename,type=file_type)#[datarock[:,0],datarock[:,1],datafilename,True]
            #self.data_dict['rock'].q=LSusaxs.QtoTheta(self.data_dict['rock'].q,self.wavelength)# Should be masked if the data is already in theta
        elif file_type=='usaxsdsm':
            #elif extension=="dsm": #it is a dsm file
            #data = LSusaxs.ReadUSAXSData(datafilename)
            self.ImportData(datafilename,usecols = (0,2),name='dec',type=file_type)
            #self.data_dict['dec']=dataset('dec',data[:,0],data[:,1],datafilename,type=file_type)#[data[:,0],data[:,1],datafilename,True]
            self.data_dict['InterpolForFit']=dataset('InterpolForFit',data[:,0],data[:,1],datafilename)#[data[:,0],data[:,1],datafilename]
        elif file_type=='fit2d':
            #elif extension=="chi": #it is a chi file from fit2D
            self.ImportData(datafilename,'  ',name=name,type=file_type )
        elif file_type=='saxs':
            #it is a rgr file
            self.ImportData(datafilename,'\t',name=name,type=file_type )
        elif file_type=='txttab':
            #it is a txt file
            self.ImportData(datafilename,name=name,type=file_type)
        elif file_type=='txtcomma':
            #it is a txt file
            self.ImportData(datafilename,name=name,delimiter=',',type=file_type)
        elif file_type=='resfunc':
            #it is a dat file
            self.ImportData(datafilename,name='resfunc',delimiter=',',type=file_type)

    
    def ImportData(self, datafilename,lineskip=0,delimiter='\t',usecols=None,type=None,name=None):
        '''
        extract data from file
        '''
        if name==None:
            name = filetools.getFilename(datafilename)
        
        #----- file -> data
        #data = importArray(datafilename, lineskip, dataSeparator,cols)
        data=numpy.loadtxt(datafilename, comments='#', skiprows=0, usecols=usecols)# Load data from a text file.
        data=numpy.transpose(numpy.array(data))
        #print data
        #----- data -> dataset
        name=self.cleanString(name)
        self.data_dict[name] = dataset(name,data[0], data[1], datafilename,type=type)#[data[0], data[1], datafilename, True]
        if len(data)>3:
            self.data_dict[name].error=data[3]#/data[1]#1/numpy.sqrt(abs(data[1]*data[2]))
        ''' elif len(data)>2:
            self.data_dict[name].error=1/numpy.sqrt(abs(data[1]*data[2]))'''
 
    def redrawTheList(self):
        '''
        redraw the listbox
        '''
        l=[]
        for name in self.data_dict:
            l.append(name)
            l.sort()
        self.listBox.Set(l)
        #set the check box
        for name in self.data_dict:
            pos=self.listBox.FindString(name)
            if pos<>-1 :
                self.listBox.Check(pos,int(self.data_dict[name].checked))
                #check colors of data
                if self.data_dict[name].color!=None:
                    #self.listBox.SetItemForegroundColour(pos, pySaxsColors.getColorRGB(self.data_dict[name].color))
                    self.listBox.SetItemForegroundColour(pos, self.data_dict[name].color)
                else:
                    self.listBox.SetItemForegroundColour(pos, self.get_color(pos))
                #tp=self.data_dict[name].type #typefile[self.data_dict[name].type]
                #if typefile.has_key(tp):
                        #self.listBox.SetItemForegroundColour(pos, typefile[tp][2]) 
                         


    def checkPlotData(self,name):
        '''
        check if we plot data
        '''
        pos=self.listBox.FindString(name)
        if pos<>-1 :
            if self.listBox.IsChecked(pos):
                return True
        return False

    def ListOfDatasChecked(self):
        '''
        check if there are data checked
        return list of dataset checked
        '''
        l=[]
        for name in self.data_dict:
            if self.data_dict[name].checked:
                #data are checked
                l.append(name)
        return l


    '''def OnDataBackground(self,event):
        
        #load background
        
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)<=0:
            return
        dlg=LSBackgroundDlg.LSBackgroundDlg(self,listofdata)
        dlg.Show()'''

    def OnResolution(self,event):
        dlg2 = wx.FileDialog(self, 'Open the beam divergence file (Counts vs Radian)', self.workingdirectory, '', '*.div', wx.OPEN)
        dlg2.ShowModal()
        dlg=LSResolutionDlg.LSResolutionDlg(self)
        dlg.CenterOnScreen()
        val=dlg.ShowModal()
        fname=str(dlg2.GetPath())#'OSbeam.div'
        c=dlg.c#=0.01
        step=dlg.step#0.01
        boundary=dlg.boundary#0.05
        dlg1=wx.MessageDialog(self, "Please wait, it will take some time................\nFor using new resolution function, \nstart pySAXS again after this calculation.", "Wait", wx.OK| wx.ICON_INFORMATION)
        val1=dlg1.ShowModal()
        LSusaxs.calculate_res_func_USAXS(fname,c,step,boun=boundary)
        dlg1.Destroy()
        
    def OnSAXSSubstraction(self,event):
        ''' 
        User click on SAXS substraction
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            dlg = wx.MessageDialog(self, 'No data were selected','pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        selectedData = self.ListOfDatasChecked()#self.listBox.GetString(index)
        dlgparameter={}
        # text, valeur par defaut, valeur min, valeur max, final value
        for i in range(len(selectedData)):
            dlgparameter[i]=[selectedData[i],i,0,10,0]
        dlgparameter['Sample thickness']=['Sample thickness (cm)',1.0,0,100,0]
        dlg=LSGenericParameterDlg(self,"Substraction ","truc",\
                                  parameters=dlgparameter,\
                                  callbackFunction=self.OnSAXSSubstractionApply,\
                                  comment="     Specify the order in the substraction. \nie 0,1,2 for i0-i1-i2")#self.OnUSAXSTransmission)
        dlg.Show()
    
    def OnSAXSSubstractionApply(self,event,selectedData,parameters):
         pass
        
    '''def testDlgShow(self,event):
        dlgparameter={}
        # text, valeur par defaut, valeur min, valeur max, final value
        dlgparameter['thickness']=['Thickness of sample (cm)',1e-1,0,1,0]
        dlgparameter['backgroundData']=['Background data(cps/s) ',0,0,100,0]
        dlgparameter['backgroundRC']=['Background RC (cps/s) ',0,0,100,0]
        dlgparameter['shiftdata']=['Shift Data (steps)',0,0,100,0]
        dlgparameter['shiftrock']=['Shift Rocking curve (steps)',0,0,100,0]
        #call the parameter dialog box with feedback to OnUSAXSTransmission()
        dlg=LSGenericParameterDlg(self,"Transmission and Data correction","truc",parameters=dlgparameter,callbackFunction=None)#self.OnUSAXSTransmission)
        dlg.Show()
        '''

    def OnUSAXSTransmissionDlgShow(self,event):
        '''
        The user click on "USAXS - Data correction"
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            dlg = wx.MessageDialog(self, 'No data were selected','pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        selectedData = self.listBox.GetString(index)
        
        if not(self.data_dict.has_key(selectedData)) or not(self.data_dict.has_key('rock')):
            dlg = wx.MessageDialog(self, "Load data and rocking curve before correcting by transmission \n(Try to rename the rocking curve datas into 'rock')",'pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        parameter={}
        # text, valeur par defaut, valeur min, valeur max, final value
        parameter['thickness']=['Thickness of sample (cm)',0.1,0,1,0.1]
        parameter['backgroundData']=['Background data(cps/s) ',0,0,100,0]
        parameter['backgroundRC']=['Background RC (cps/s) ',0,0,100,0]
        parameter['shiftdata']=['Shift Data (steps)',0,0,100,0]
        parameter['shiftrock']=['Shift Rocking curve (steps)',0,0,100,0]
        #call the parameter dialog box with feedback to OnUSAXSTransmission()
        dlg=LSGenericParameterDlg(self,"Transmission and Data correction",selectedData,parameters=parameter,callbackFunction=self.OnUSAXSTransmission)#self.OnUSAXSTransmission)
        dlg.Show()
        #self.child=LSTransmissionDlg(self,label)#,parameter,callbackFunction=self.OnUSAXSTransmission)
        

    def OnUSAXSTransmission(self,event,selectedData,parameters):
        '''
        do the tramsission correction after dialog box LSTransmissionDlg
        '''
        #--- do the correction
        self.printTXT("-----USAXS Data correction --------")
        self.wavelength=1.54
        #self.printTXT(parameters)
        self.thick=parameters['thickness'][4]
        self.steprock=parameters['shiftrock'][4]
        self.stepexp=parameters['shiftdata'][4]
        self.backgrdData=parameters['backgroundData'][4]
        self.backgrdRC=parameters['backgroundRC'][4]
        n=15
        a1=10000.
        a2=1e-10
        it=2000
        tol=1e-15
        qminimum=1e-4
        #--- setting the datas
        Iexp=self.data_dict[selectedData].i-self.backgrdData
        qexp=self.data_dict[selectedData].q
        Irock=self.data_dict['rock'].i-self.backgrdRC
        qrock=self.data_dict['rock'].q

        a0exp=Iexp[numpy.argmax(Iexp)]
        a0rock=Irock[numpy.argmax(Irock)]
        Thetaexp=qexp
        Thetarock=qrock

        #--- "Fitting to the Gaussian"
        Fitexp , Thetaexp_sel  ,Iexp_sel , FitParamexp  =LSusaxs.FitGauss(Thetaexp,Iexp,n,a0exp,a1,a2,tol,it)
        Fitrock, Thetarock_sel ,Irock_sel, FitParamrock = LSusaxs.FitGauss(Thetarock,Irock,n,a0rock,a1,a2,tol,it)
        self.printTXT("Data center found at ",FitParamexp[2])
        self.printTXT("RC center found at ",FitParamrock[2])
       
        DeltaThetaexp =-FitParamexp[2] #center
        DeltaThetarock =-FitParamrock[2]
        #---"-----Fitting procedure end-----"
        #---"--Steps in Theta-----------------------------------------------"
        shiftexp=abs(Thetaexp_sel[0]- Thetaexp_sel[1])
        shiftrock=abs(Thetarock_sel[0]- Thetarock_sel[1])
        #---------------------------------------------------------------"

        NewThetaexp_sel=LSusaxs.Qscalemod(DeltaThetaexp,Thetaexp_sel,self.stepexp*shiftexp)
        NewThetarock_sel=LSusaxs.Qscalemod(DeltaThetarock,Thetarock_sel,self.steprock*shiftrock)
        
        CorrThetaexp_positive=numpy.repeat(NewThetaexp_sel,NewThetaexp_sel>0.0)
        Iexp_sel_positive=numpy.repeat(Iexp_sel,NewThetaexp_sel>0.0)
        ####self.somme=LSusaxs.somme(self.CorrThetaexp_positive,self.Iexp_sel_positive)

        #---"New Theta scales after zero shifting and manual shifting (if any)------"
        qnewexp=LSusaxs.Qscalemod(DeltaThetaexp,Thetaexp,self.stepexp*shiftexp)
        qnewrock=LSusaxs.Qscalemod(DeltaThetarock,Thetarock,self.steprock*shiftexp)
        self.data_dict[selectedData+' centered']=dataset(selectedData+' centered',qnewexp,Iexp,'centered datas',type='calculated')
        self.data_dict['rock'+ ' centered']=dataset('rock'+' centered',qnewrock,Irock,'rock datas',type='calculated')
        "------------------------------------------------"
        self.TransmissionValue=FitParamexp[0]/FitParamrock[0]
        self.printTXT('Transmission of the sample (%)= ',self.TransmissionValue)
        self.printTXT('Sample thickness (cm.)=', self.thick)
        qnewpos=numpy.repeat(qnewrock,qnewrock>=0.0)
        Inewpos=numpy.repeat(Irock,qnewrock>=0.0)
        self.printTXT( 'minimum Theta taken for central beam calculation= ', qnewpos[0])
        #print 'Intensity at minimum Theta value taken for central beam calculation= ', Inewpos[0]
        #--- 'Area in the central beam'
        somme=2.*LSusaxs.somme(qnewpos,Inewpos)
        self.printTXT( 'Central beam area(counts.s^-1.rad^-2)= ', somme)
        qnew,ITcorr=LSusaxs.TrCorrectedProf(qnewexp,Iexp,qnewrock,Irock,self.thick,somme,self.TransmissionValue)
        #qnew,ITcorr=LSusaxs.TrCorrectedProf(qexp,Iexp,qrock,Irock,self.thick,somme,self.TransmissionValue)

        #ITcorr=LSusaxs.TrCorrectedProf(qnewexp,Iexp,qnewrock,Irock,self.thick,somme,self.TransmissionValue)[1]
        self.data_dict[selectedData+' substracted']=dataset(selectedData+' substracted',numpy.repeat(qnew,qnew>qminimum),numpy.repeat(ITcorr,qnew>qminimum),'substracted datas',type='scaled')
               
        self.redrawTheList()
        self.RePlot(event)

    def OnUSAXSDeconvolution(self,event):
        '''
        The user click on "USAXS - Deconvolution"
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            dlg = wx.MessageDialog(self, 'No data were selected','pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        label = self.listBox.GetString(index)
        if not(self.data_dict.has_key('resfunc')):
            dlg = wx.MessageDialog(self, "Load resolution function before deconvolution",'pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        #read the resolution function
        resx=self.data_dict['resfunc'].q
        resy=self.data_dict['resfunc'].i
        #call the transmission dialog box with feedback to OnUSAXSTransmission()
        dlg=LSDeconvolutionDlg.LSDeconvolutionDlg(self)
        dlg.CenterOnScreen()
        val=dlg.ShowModal()
        it=3
        ns=1
        
        type=dlg.type
        if val==wx.ID_OK:
                Isous=self.data_dict[label].i
                qsous=self.data_dict[label].q
                #print len(Isous)
                #print len(qsous)
                Idec=LSusaxs.lake(qsous,Isous,it,type,ns,self.plotexp,resx,resy)
                qdec=LSusaxs.ThetatoQ(qsous,self.wavelength)
                #qdec=qsous   
                self.data_dict[label+' deconvoluted']=dataset(label+' deconvoluted',qdec,Idec,label+'deconvoluted',True,type='calculated')
                self.redrawTheList()
                self.RePlot(event)

    def OnModelPlot(self, event):
        '''if self.ISMODEL==True:
            self.gp('set title \' '+str(self.M.IntensityFunc).split(' ')[1]+' \' ')
            GD=Gnuplot.Data(self.M.q,self.M.GetIntensity()*(self.M.q**self.plotexp),with='l lt 2')
            self.gp.replot(GD)'''
        pass

    def OnUSAXSsimuPlot(self, event):
        if self.ISUSAXSsimu==True:
            self.gp('set title \' '+'USAXS data simulation for'+str(self.M.IntensityFunc).split(' ')[1]+' \' ')
            qsimu1=LSusaxs.ThetatoQ(self.qsimu,self.wavelength)
            GD=Gnuplot.Data(qsimu1,self.IUSAXSsimu*(qsimu1**self.plotexp),with_='p 250')
            qrocking21=LSusaxs.ThetatoQ(self.qrocking2,self.wavelength)
            GD1=Gnuplot.Data(qrocking21,(self.Irocking2+self.backgr)*(self.qrocking2**self.plotexp),with_='l lt 3')
            self.gp.replot(GD,GD1)

#
    def OnDataReset(self, event):
        #if self.ISDATA==True:
        self.SetTitle("pySAXS")
        self.DataBackground=0.0

        self.data_dict.clear()
        self.redrawTheList()
        self.RePlot()


    def OnFileSaveModel(self, event):# This saves the model
        save_modelfit_file=string.replace(self.DATAFILE,'dsm' ,'fit')
        dlg1=wx.MessageDialog(self, "Save fitted model and data?", "Save", wx.YES_NO| wx.ICON_INFORMATION)
        val1=dlg1.ShowModal()

        if val1==wx.ID_YES:
           dlg2 = wx.FileDialog(self, message="Save file as ...", defaultDir=self.workingdirectory, defaultFile=save_modelfit_file, style=wx.SAVE)
           dlg2.ShowModal()
           data=numpy.zeros((len(self.qInterpolForFit),2))

           data[:,0]=self.qInterpolForFit
           data[:,1]=self.IInterpolForFit

           LSusaxs.WriteUSAXSdata(str(dlg2.GetPath()),data)

    def OnInvariant(self, event):
        '''
        user click on invariant
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            dlg2=wx.MessageDialog(self,
                                      message='No data selected.',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
            dlg2.ShowModal()
            dlg2.Destroy()
            return

        datasetname = self.listBox.GetString(index)
        newdataset_PQ=datasetname+" invariant low q"
        self.data_dict[newdataset_PQ]=dataset(newdataset_PQ,\
                                              self.data_dict[datasetname].q,\
                                              self.data_dict[datasetname].i,\
                                              comment="invariant low q",\
                                              type='calculated')
        
        newdataset_GQ=datasetname+" invariant high q"
        self.data_dict[newdataset_GQ]=dataset(newdataset_GQ,\
                                              self.data_dict[datasetname].q,\
                                              self.data_dict[datasetname].i,\
                                              comment="invariant high q",\
                                              type='calculated')
        
        self.redrawTheList()
        self.childInvariant=LSInvariantDlg(self,datasetname,newdataset_PQ,newdataset_GQ)
        self.childInvariant.Show()


    def OpenModel(self,M,index=-1,name="",pos=wx.Point(50,50)):
        '''
        open the model dialog box
        '''
        
        if index==-1:
            '''
            no data checked
            add a new dataset with an empty model
            '''
            
            if name=="":
                data_selected_for_model=M.name
            else:
                data_selected_for_model=name               
            self.data_dict[data_selected_for_model]=dataset(data_selected_for_model,
                                                                 M.q,
                                                                 M.getIntensity(),
                                                                 "",
                                                                 True,
                                                                 M,
                                                                 type="model")#new data set checked
            self.childmodel=LSModelDlg(self,data_selected_for_model,type="model",pos=pos)
        else:
            ''' data is checked '''
            
            data_selected_for_model=self.listBox.GetString(index)
            if name=="":
                new_dataname=data_selected_for_model+"-"+M.name+" model"
            else:
                new_dataname=name        
            #self.data_dict[data_selected_for_model].model=M
            #self.printTXT( "for ",data_selected_for_model)
            q=self.data_dict[data_selected_for_model].q
            M.q=q
            i=M.getIntensity() #intensity by default
            filename=self.data_dict[data_selected_for_model].filename
            #new_dataname=data_selected_for_model+" model"
            self.data_dict[new_dataname]=dataset(new_dataname,copy(q),
                                                    copy(i),
                                                    filename,
                                                    True,
                                                    M,#reference to model
                                                    rawdata_ref=data_selected_for_model,
                                                    type="calculated")#reference to original datas
            self.childmodel=LSModelDlg(self,new_dataname,type="data",pos=pos)
        self.childmodel.Show()
        self.redrawTheList()
        self.RePlot()
        return self.childmodel
        

    def OnModelSelect(self, event):
        '''
        user click on model
        '''
        id=event.GetId()
        #self.printTXT('model ' +str(id) +' was selected' +'corresponding to  ' +str(self.modelsDictId[id][1]) +' model')
        modelname=self.modelsDictId[id][1]
        M=getattr(pySAXS.models,modelname)()#create a new model
        if M.WarningForCalculationTime:
            dlg=wx.MessageDialog(self, "Computation time can be high for this model. Continue ?", "WARNING", wx.YES_NO| wx.ICON_INFORMATION)
            val=dlg.ShowModal()
            if val!=wx.ID_YES:
                return
        index=self.listBox.GetSelection()
        self.OpenModel(M, index)

    def OnModelUpdate(self,child):
        '''
        when the user update from the Model
        '''
        dataset_name=child.dataset_name
        if self.data_dict.has_key(dataset_name):
            #update intensities
            if self.data_dict[dataset_name].model<>None:
                #ok model exist
                self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                self.data_dict[dataset_name].model=child.Model
                self.data_dict[dataset_name].i=child.Model.getIntensity()
                self.data_dict[dataset_name].q=copy(child.Model.q)
                self.RePlot()
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))


    def OnModelReset(self, event):

        pass


    def OnModelQRange(self, event):
        return 1

    def OnModelFit(self, child):
        '''
        when user click on fit on the model child dialog box
        '''
        dataset_name=child.dataset_name
        if self.data_dict.has_key(dataset_name):
            rawdata_name=self.data_dict[dataset_name].rawdata_ref
            self.printTXT( "fit with raw data from ",rawdata_name)
            if self.data_dict.has_key(rawdata_name) and self.data_dict[dataset_name].model<>None:
                if (child.qminIndex!=0) or (child.qmaxIndex!=len(self.data_dict[rawdata_name].q)-1):
                    #qmin and qmax have changed
                    q=self.data_dict[rawdata_name].q[child.qminIndex:child.qmaxIndex]
                    i=self.data_dict[rawdata_name].i[child.qminIndex:child.qmaxIndex]
                else :
                    #update intensities
                    q=self.data_dict[rawdata_name].q
                    i=self.data_dict[rawdata_name].i
                    child.Model.q=q
                #FIT
                res=child.Model.fit(i,child.fitexp)
                #fitted parameters -> new parameters
                self.printTXT('fitted parameters : ',res)
                #child.Model.Arg=res
                child.UpdateAfterFit(res)
                self.data_dict[dataset_name].model=child.Model
                self.data_dict[dataset_name].i=child.Model.getIntensity()
                self.RePlot()
                
    def OnModelFitBounds(self, child):
        '''
        when user click on fit on the model child dialog box
        '''
        dataset_name=child.dataset_name
        bounds=child.bounds #get bounds
        #print bounds
        if self.data_dict.has_key(dataset_name):
            rawdata_name=self.data_dict[dataset_name].rawdata_ref
            self.printTXT("fit with raw data from ",rawdata_name)
            if self.data_dict.has_key(rawdata_name) and self.data_dict[dataset_name].model<>None:
                if (child.qminIndex!=0) or (child.qmaxIndex!=len(self.data_dict[rawdata_name].q)-1):
                    #qmin and qmax have changed
                    q=self.data_dict[rawdata_name].q[child.qminIndex:child.qmaxIndex]
                    i=self.data_dict[rawdata_name].i[child.qminIndex:child.qmaxIndex]
                else :
                    #update intensities
                    q=self.data_dict[rawdata_name].q
                    i=self.data_dict[rawdata_name].i
                res=child.Model.fitBounds(i,bounds,child.fitexp)#fit with bounds
                #fitted parameters -> new parameters
                self.printTXT('fitted parameters with bounds : ',res)
                #child.Model.Arg=res
                child.UpdateAfterFit(res)
                self.data_dict[dataset_name].model=child.Model
                self.data_dict[dataset_name].i=child.Model.getIntensity()
                self.RePlot()


    def OnModelInfo(self, event):
        return 1
    
    def OnSuperModelSelect(self,event):
        '''
        user call SUPER Model
        '''
        id=event.GetId()-self.numberOfModels
        #self.printTXT('model ' +str(id) +' was selected' +'corresponding to  ' +str(self.modelsDictId[id][1]) +' model')
        supermodelname=self.supermodelsDictId[id][1]
        SM=getattr(pySAXS.models.super,supermodelname)()#create a new model
        basename=SM.name
        index=self.listBox.GetSelection()
        lm=SM.modelList#getModels()
        space=5
        plotf=self.plotframe 
        mdlpositionx = plotf.GetSize()[0] + plotf.GetScreenPosition()[0] + space
        mdlpositiony= self.GetScreenPosition()[1] - 5
        parentlist=[]
        parentdict={} #Guinier Model : beaucage-0-guinier,...
        for i in range(len(lm)):
            M=lm[i]
            child=self.OpenModel(M, index,basename+"-"+str(i)+"-"+M.name,pos=(mdlpositionx,mdlpositiony))
            mdlpositiony+=child.GetSize()[1]+space
            parentlist.append(basename+"-"+str(i)+"-"+M.name)
            parentdict[M.name]=basename+"-"+str(i)+"-"+M.name
        #add a result...
        iref=SM.q
        #for i1: beaucage-0-guinier 
        newvariabledict={}
        for key in SM.variableDict:
            name=SM.variableDict[key]
            newvariabledict[key]=parentdict[name]
            
        newdata=dataset(SM.name,SM.q,iref,comment=SM.name,type='calculated',\
                        parent=parentlist,parentformula=SM.formula,variableDict=newvariabledict)
        
        
        r=newdata._evaluateFromParent(self.data_dict)
        self.printTXT(r)
        self.data_dict[basename]=newdata
        self.redrawTheList()
        self.RePlot()
        
        
            
    def OnUSAXSsimuDlgShow(self,event):
        if self.ISMODEL==True:
           self.childUSAXSsimuDlg = LSUSAXSsimuDlg(self)
           self.childUSAXSsimuDlg.Show()
           "Dialogbox to open rocking curve"
           dlg = wx.FileDialog(self, 'Choose a RC data to open', self.workingdirectory, '', '*.txt', wx.OPEN)
           if dlg.ShowModal() == wx.ID_OK:
               sys.stderr.write("\n"+dlg.GetPath()+"\n")
               self.workingdirectory=os.path.dirname(dlg.GetPath())
               datarocking = LSusaxs.ReadUSAXSData(str(dlg.GetPath()))
               self.Irocking=datarocking[:,1]
               self.qrocking=datarocking[:,0]
               ROCKFILE=str(dlg.GetFilename())
               dlg.Destroy()
               self.ISUSAXSsimu=True
               
    def OnUSAXSsimu(self,event):
##        if self.ISMODEL==True:
##           self.ISUSAXSsimu=True
        if self.ISUSAXSsimu==True:
            self.mu_p=self.childUSAXSsimuDlg.mu_p
            self.rho_p=self.childUSAXSsimuDlg.rho_p
            self.mu_S=self.childUSAXSsimuDlg.mu_S
            self.rho_S=self.childUSAXSsimuDlg.rho_S
            self.phim_p=self.childUSAXSsimuDlg.phim_p
            self.rho_soln=self.childUSAXSsimuDlg.rho_soln
            self.thicks=self.childUSAXSsimuDlg.thicks
            self.backgr=self.childUSAXSsimuDlg.backgr
            self.cb_val=self.childUSAXSsimuDlg.cb_val
            T=LSusaxs.CalTransmission(self.mu_p,self.rho_p,self.mu_S,self.rho_S,self.phim_p,self.rho_soln,self.thicks)
            max_poition=numpy.argmax(self.Irocking)# q value at Peak position of rocking curve
            qrocking1=self.qrocking-self.qrocking[max_poition]
            qrocking1=LSusaxs.QtoTheta(qrocking1,self.wavelength)#Converting rocking curve q to theta
            "qneg is the array of negative part of the rocking curve"
            qneg=numpy.repeat(qrocking1,qrocking1<0.0)
            I_qneg=numpy.repeat(self.Irocking,qrocking1<0.0)
            "Converting an array to a list because later we will append this"
            qneg_list=qneg.tolist()
            I_qneg_list=I_qneg.tolist()
            "Choosing the positive q part"
            self.qrocking2=numpy.repeat(qrocking1,qrocking1>=0.0)
            self.Irocking2=numpy.repeat(self.Irocking,qrocking1>=0.0)
            sel_q=self.qrocking2#numpy.take(self.qrocking2,range(14))
            sel_I=self.Irocking2#numpy.take(self.Irocking2,range(14))
            N0dX=2.*LSusaxs.somme(sel_q,sel_I)
            #print 'Minimum Theta taken for central beam cal= ', sel_q[0]
            #print 'Intensity at minimum Theta value taken for central beam cal= ', sel_I[0]

            self.printTXT('Central beam area (counts.s^-1.Radian)= ',N0dX)

            self.Irocking2=self.Irocking2-self.backgr
            "Interpolating the model curve for the rocking curve q range"
            modeltheta=LSusaxs.QtoTheta(self.M.q,self.wavelength)
            self.qsimu=numpy.repeat(self.qrocking2,self.qrocking2>=min(modeltheta))
            self.Irocking2=numpy.repeat(self.Irocking2,self.qrocking2>=min(modeltheta))
            self.qrocking2=self.qsimu
            #print max(modeltheta),min(modeltheta),max(self.qsimu),min(self.qsimu)
            #Isimu=interpolate.splrep(self.M.q,self.M.GetIntensity(), k=3)
            #Isimu=interpolate.splrep(modeltheta,self.M.GetIntensity(), k=3)
            Isimu=interpolate.interp1d(modeltheta,self.M.GetIntensity(), kind='linear')
            IInterpolsimu=Isimu(self.qsimu)
            #IInterpolsimu=interpolate.splev(self.qsimu,Isimu)
            self.IUSAXSsimu = T*(self.Irocking2+LSusaxs.USAXS_count_convolute(self.qsimu,IInterpolsimu,N0dX,self.thicks,self.wavelength))+self.backgr
            #self.IUSAXSsimu=LSusaxs.USAXS_count_convolute(self.M.q,self.M.GetIntensity(),N0dX,dY,p,thick,T)
            self.RePlot(event)
            self.printTXT( 'Transmission (%)= ',T)
            "Converting array to a list"

            qrocking2_list=self.qsimu.tolist()
            IUSAXSsimu_list=self.IUSAXSsimu.tolist()
            "Appending to the already existing negative  q part list"
            qneg_list.extend(qrocking2_list)
            I_qneg_list.extend(IUSAXSsimu_list)

            qsimu1a=numpy.array(qneg_list)
            qsimu1=LSusaxs.ThetatoQ(qsimu1a,self.wavelength)
            IUSAXSsimu1=numpy.array(I_qneg_list)
            save_simu_file='test.txt'
            if self.cb_val==True:
                dlg1=wx.MessageDialog(self, "Save simulated SAXS data?", "Save", wx.YES_NO| wx.ICON_INFORMATION)
                val1=dlg1.ShowModal()
                if val1==wx.ID_YES:
                   dlg2 = wx.FileDialog(self, message="Save file as ...", defaultDir=self.workingdirectory, defaultFile=save_simu_file, style=wx.SAVE)
                   dlg2.ShowModal()
                   data=numpy.zeros((len(qsimu1),3))
                   data[:,0]=qsimu1
                   data[:,1]=numpy.zeros(len(qsimu1))
                   data[:,2]=IUSAXSsimu1
                   LSusaxs.WriteUSAXSdata(str(dlg2.GetPath()),data)

    def OnUSAXSsimuReset(self, event):
        if self.ISUSAXSsimu==True:
            self.ISUSAXSsimu=False
            self.RePlot(event)

    def OnToolsContraste(self, event):
        dlg=LSAbsorptionDlg.AbsorptionForm(self)
        dlg.CenterOnScreen()
        val=dlg.Show()#dlg.ShowModal()
        
        
    def OnToolsContrasteXRL(self, event):
        dlg=LSAbsorptionXRL.AbsorptionForm(self,printout=self.printTXT)
        dlg.CenterOnScreen()
        val=dlg.Show()#dlg.ShowModal()
        

    def OnToolsContrasteNeutron(self, event):
        dlg=LSneutronDlg.LSNeutronCon(self)
        dlg.Show()

    def OnLogPlotType(self, event):
        self.axetype=event.GetId()
        #self.RePlot(event)
        if self.axetype==self.loglog:
            self.gp('set logscale xy')
        if self.axetype==self.loglin:
            self.gp('set logscale x')
        if self.axetype==self.linlog:
            self.gp('set logscale y')
        if self.axetype==self.linlin:
            self.gp('set nologscale')
        self.RePlot(event)

    def OnPorodPlotType(self, event):
        if event.GetId()==self.i_plot:
            self.plotexp=0.0
        if event.GetId()==self.iq_plot:
            self.plotexp=1.0
        if event.GetId()==self.iq2_plot:
            self.plotexp=2.0
        if event.GetId()==self.iq3_plot:
            self.plotexp=3.0
        if event.GetId()==self.iq4_plot:
            self.plotexp=4.0
        self.RePlot(event)

    def OnSendCommandToPlot(self,event):
        dlg=wx.TextEntryDialog(None,"Enter the command to send to Gnuplot :","Command entry",
                               defaultValue="set nokey",
                               style=wx.OK|wx.CANCEL|wx.CENTRE)

        if dlg.ShowModal()==wx.ID_OK:
            self.gp(dlg.GetValue())
        self.RePlot()
        dlg.Destroy()

    def OnSelectqRangeShow(self,event):
        '''
        change scale
        '''
        if self.qmini==None or self.qmaxi==None or self.Imini==None or self.Imaxi==None:
            #-- recherche qmin,qmax,imin, imax
            self.OnResetSelectqRange(event)
        self.childSelectqRange=LSSelectqRangeDlg(self,self.qmini,self.qmaxi,self.Imini,self.Imaxi)
        self.childSelectqRange.Show()

    def OnSelectqRange(self,qmin,qmax,imin,imax):
        # qmin,qmax,imin,imax
        self.qmini=qmin
        self.qmaxi=qmax
        self.Imini=imin
        self.Imaxi=imax
        setx=str(self.qmini)+':'+str(self.qmaxi)
        self.xselect='set xrange'+'['+setx+']'
        self.gp(self.xselect)
        sety=str(self.Imini)+':'+str(self.Imaxi)
        self.yselect='set yrange'+'['+sety+']'
        self.gp(self.yselect)
        self.gp('replot')



    def OnClipqRangeShow(self,event):
        index=self.listBox.GetSelection()
        if index==-1:
            return
        dataset = self.listBox.GetString(index)
        self.childClipqRange=LSClipqRangeDlg(self,dataset)
        self.childClipqRange.Show()

    def OnClipqRange(self,child):
        dataset_name=child.dataset_name
        if self.data_dict.has_key(dataset_name):
            q=numpy.array(self.data_dict[dataset_name].q)
            i=numpy.array(self.data_dict[dataset_name].i)
            if self.data_dict[dataset_name].error<>None:
                error=numpy.array(self.data_dict[dataset_name].error)
                error=numpy.repeat(error,q>=child.qmini)
            i=numpy.repeat(i,q>=child.qmini)
            q=numpy.repeat(q,q>=child.qmini)
            if self.data_dict[dataset_name].error<>None:
                error=numpy.repeat(error,q<=child.qmaxi)
            i=numpy.repeat(i,q<=child.qmaxi)
            q=numpy.repeat(q,q<=child.qmaxi)
            #I put k=1 for interpollation below because for k=3 (cubic spline)the interpollation is not proper for sharp oscillations.

            #-------------------------------------------------------------------
            #self.qInterpolForFit=LSsca.Qlogspace(numpy.min(self.qdec2),numpy.max(self.qdec2),self.np)
            #Isampl= interpolate.splrep(self.qdec2,self.Idec2, k=1)
            #Isampl=interpolate.interp1d(self.qdec2,self.Idec2,kind='linear')
            #print numpy.min(self.qdec2),numpy.min(self.qInterpolForFit),numpy.max(self.qdec2),numpy.max(self.qInterpolForFit)
            #self.IInterpolForFit=Isampl(self.qInterpolForFit)
            #self.IInterpolForFit=interpolate.splev(self.qInterpolForFit,Isampl)
            #self.ISCLIP=True
            self.data_dict[dataset_name].q=q
            self.data_dict[dataset_name].i=i
            if self.data_dict[dataset_name].error<>None:
                self.data_dict[dataset_name].error=error
            self.RePlot()

    def OnConcatenateShow(self,event):
        '''
        user want to concatenate different dataset
        '''
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)<=0:
            return
        #create a new data set
        newdatasetname=listofdata[0]+' new'
        self.data_dict[newdatasetname]=copy(self.data_dict[listofdata[0]])
        self.data_dict[newdatasetname].name=newdatasetname
        dlg=LSConcatenateDlg(self,listofdata,newdatasetname)
        dlg.Show()

    def OnConcatenate(self):
        '''
        user click on apply
        '''
        self.redrawTheList()
        self.RePlot()

    def OnConcatenateCancel(self,datasetname):
        if self.data_dict.has_key(datasetname):
            self.data_dict.pop(datasetname)
        self.redrawTheList()
        self.RePlot()
        
    
    def OnSmooth(self,event):
        '''
        user want to smooth dataset
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        index=self.listBox.GetSelection()
        label = self.listBox.GetString(index)
        #create a new data set
        dlg=wx.TextEntryDialog(None,"Smooth window parameter :","Smooth parameter","1.0",style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            pp=float(dlg.GetValue())
            newdatasetname=label+' smooth'
            self.data_dict[newdatasetname]=copy(self.data_dict[label])
            self.data_dict[newdatasetname].name=newdatasetname
            q=self.data_dict[newdatasetname].q
            i=self.data_dict[newdatasetname].i
            tck = interpolate.splrep(q,i,s=pp)
            ysmooth = interpolate.splev(q,tck,der=0)
            '''
            coeff = sg_filter.calc_coeff(pp, 4)
            ysmooth = sg_filter.smooth(i, coeff) 
            
            ysmooth=i.copy()
            start=int(pp/2)
            for j in range(start,len(i)-start):
                ysmooth[j]=i[j-start:j+start].mean()'''
            self.data_dict[newdatasetname].i=ysmooth
            self.redrawTheList()
            self.RePlot()
    
    def OnDerivate(self,event):
        '''
        user want to derivate dataset
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        index=self.listBox.GetSelection()
        label = self.listBox.GetString(index)
        #create a new data set
        newdatasetname=label+' derivate'
        self.data_dict[newdatasetname]=copy(self.data_dict[label])
        self.data_dict[newdatasetname].name=newdatasetname
        q=self.data_dict[newdatasetname].q
        i=self.data_dict[newdatasetname].i
        tck = interpolate.splrep(q,i,s=0)
        yder = interpolate.splev(q,tck,der=1)
        self.data_dict[newdatasetname].i=yder
        #test for peak detection
        
        self.redrawTheList()
        self.RePlot()
        
        
    def findPeaks(self,events):
        '''
        find peaks
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        index=self.listBox.GetSelection()
        label = self.listBox.GetString(index)
        i=self.data_dict[label].i
        q=self.data_dict[label].q
        newq=None
        newi=None
        pp=20
        dlg=wx.TextEntryDialog(None,\
                               "PySAXS will scan the datas and detect in a window\n if somes values are higher than the background.\n Please indicate the window (no of point taken in acount in the scan) :",\
                               "Peaks parameter","20",style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            pp=int(dlg.GetValue())
            
        dlg2=wx.TextEntryDialog(None,"Peaks height from the background (in percent) :","Peaks parameter","100.0",style=wx.OK|wx.CANCEL)
        if dlg2.ShowModal()==wx.ID_OK:
            percent=float(dlg2.GetValue())/100.0
        '''tck = interpolate.splrep(q,i,s=0)
        yder = interpolate.splev(q,tck,der=1) #derivate
        self.printTXT( "---------      peak detection ---------")
        lastpeak=0
        n=0 #number of detected peaks
        imin=i.min()
        imax=i.max()
        window=int(pp/2)
        for ii in range(window,len(q)-pp):
                #calculate mean on the derivate for the two part of the window
                try:
                    mean1=yder[ii-window:ii].mean()
                    mean2=yder[ii:ii+window].mean()
                except:
                    self.printTXT("Error on input data, cannot calulate derivative")
                    return
                
                if mean1>0 and mean2<0:
                    #first part of the derivate >0 and the second one is <0 there is a peak.
                    mn=i[ii-window:ii+window].min()-imin
                    mx=i[ii-window:ii+window].max()-imin
                    h=mx-mn
                    if mx>mn*(1+percent):
                        #print "I have a peak between ",q[ii]," and ",q[ii+pp]
                        if ii<lastpeak+pp:
                            #print "same peak"
                            pass
                        else:
                            #print "new peak between ",q[ii]," and ",q[ii+pp]," last peak",lastpeak
                            lastpeak=ii
                            #self.printTXT( "mean : "+str(yder[ii-window:ii].mean())+" - "+str(yder[ii:ii+window].mean()))
                            #try to fit with gaussian
                            res,result_q,result_i=self.fitPeakWithGaussian(q[ii-window:ii+window*2-1],i[ii-window:ii+window*2-1])
                            self.printTXT(  "found peak at q="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1]))
                            n+=1
                            if newq==None:
                                newq=result_q
                                newi=result_i
                            else:
                                #print result_q
                                newq=numpy.concatenate((newq,numpy.array(result_q)))
                                newi=numpy.concatenate((newi,result_i))
                                                        
                            #print newq#
                            #--- plot in gnuplot
                            #self.gp('set label "peak at '+str(res[2])+'"   at '+str(res[2])+','+str(res[0])+'  rotate left')
                            #self.gp('set arrow from  '+str(res[2])+', '+str(imin)+' to '+str(res[2])+', '+str(imax)+ ' nohead')
                            #self.gp.replot()
                            #--- plot in matplotlib
                            if self._matplotlib:
                                ax=self.plotframe.axes
                                ax.annotate('q='+str(res[2])+'\nFWHM='+str(res[1]),\
                                             xy=(res[2], res[0]),  xycoords='data',\
                                            xytext=(20, 20), textcoords='offset points', \
                                            arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90,rad=10"),\
                                            fontsize=10,)
                                            #horizontalalignment='center', verticalalignment='center'
                                            #'angle', xy=(2., 1),  xycoords='data',
                                self.plotframe.draw()
        #end of peak search
        '''
        founds, newq,newi=DetectPeaks.findPeaks(q,i,pp,percent,self)
        n=len(founds)
        if n>0:
            for res in founds:
                #[height,fwhm,center]
                self.printTXT(  "found peak at q="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1]))
                #--- plot in matplotlib
                if self._matplotlib:
                                ax=self.plotframe.axes
                                ax.annotate('q='+str(res[2])+'\nFWHM='+str(res[1]),\
                                             xy=(res[2], res[0]),  xycoords='data',\
                                            xytext=(20, 20), textcoords='offset points', \
                                            arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90,rad=10"),\
                                            fontsize=10,)
                                            #horizontalalignment='center', verticalalignment='center'
                                            #'angle', xy=(2., 1),  xycoords='data',
                                self.plotframe.draw()
                
            self.data_dict[label+" peaks"]=dataset(label+" peaks",numpy.array(newq),numpy.array(newi),comment=label+" peaks",type='calculated')#[data[0], data[1], datafilename, True]
        self.printTXT(str(n)+" peaks found ---------")    
        self.redrawTheList()

        
    '''def fitPeakWithGaussian(self,q,i):
        #
        #fit peak with a gaussian
        #
        gauss=pySAXS.models.Gaussian()
        istofit=[False,True,True,False]
        gauss.q=q
        #print q
        #print i
        maxi=i.max()#height of gaussian
        mini=i.min()
        center=q[i.argmax()]
        fwhm=(q.max()-q.min())/4.0
        gauss.Arg=[maxi,fwhm,center,mini]
        #print "initial parameters : ",gauss.Arg
        bounds=[(maxi*0.9,maxi*1.1),(fwhm*0.2,fwhm*1.5),(q.min(),q.max()),(mini*0.9,mini*1.1)]
        #print "bounds : ",bounds
        #print gauss.Arg
        #print bounds
        res=gauss.fitBounds(i,bounds)
        gauss.setArg(res)
        #print "res : ",res
        newi=gauss.getIntensity()
        return res,q,newi'''
        
    def OnResetSelectqRange(self,event):
        l=self.ListOfDatasChecked()
        if len(l)==0:
            return
        lqmin=[]
        lqmax=[]
        limin=[]
        limax=[]
        for label in l:
            lqmin.append(numpy.min(self.data_dict[label].q))
            lqmax.append(numpy.max(self.data_dict[label].q))
            limin.append(numpy.min(self.data_dict[label].i))
            limax.append(numpy.max(self.data_dict[label].i))
        self.qmini=min(lqmin)
        self.qmaxi=max(lqmax)
        self.Imini=min(limin)
        self.Imaxi=max(limax)
        self.gp('set autoscale xy')
        self.gp('replot')


    def RePlot(self,event=None):
        l=self.ListOfDatasChecked()
        if len(l)==0:
            return
        #check if data have parents
        for name in l:
            if hasattr(self.data_dict[name], 'parent'):
                if self.data_dict[name].parent!=None:
                    #print "#parent, need to be recalculated"
                    r=self.data_dict[name]._evaluateFromParent(self.data_dict)
                    if r!="":
                        self.printTXT(r)
                
        #print "replot"
        '''self.gp.reset()
        if self.axetype==self.loglog:
            self.gp('set logscale xy')
        if self.axetype==self.loglin:
            self.gp('set logscale x')
        if self.axetype==self.linlog:
            self.gp('set logscale y')
        if self.axetype==self.linlin:
            self.gp('set nologscale')
        self.gp('set xlabel \'q\'')
        if self.plotexp==0.0:
            self.gp('set ylabel \'I\'')
        if self.plotexp==1.0:
            self.gp('set ylabel \'Iq\'')
        if self.plotexp==2.0:
            self.gp('set ylabel \'Iq2\'')
        if self.plotexp==3.0:
            self.gp('set ylabel \'Iq3\'')
        if self.plotexp==4.0:
            self.gp('set ylabel \'Iq4\'')
        #gplt('set yrange[8e22:9e24]')
        self.gp(self.xselect)
        self.gp(self.yselect)
        #plot the data selected by the check box
        i=0 #nb de fichier selectionne pour le plot
        lc=0
        listOfdata=[]
        
        for name in self.data_dict:
            lc=lc+1
            #print 'plotting ',name
            if self.data_dict[name].checked:
                i=i+1
                #print self.data_dict[name][2],string.replace(self.data_dict[name][2],'/' ,' ')
                qexp=self.data_dict[name].q
                iexp=self.data_dict[name].i
                if self.data_dict[name].model<>None:
                    with_option=' l lt ' +str(lc)
                else:
                    with_option=' lp lt ' + str(lc)
                try:
                    GD=Gnuplot.Data(qexp,iexp*(qexp**self.plotexp),title=str(name),with_=with_option)#p ps 2 pt 254')
                    listOfdata.append(GD)
                except:
                    self.printTXT("error gnuplot when trying to plot "+str(name))
                
                if self.data_dict[name].error<>None:
                    try:
                        GDerror=Gnuplot.Data(qexp,iexp*(qexp**self.plotexp),self.data_dict[name].error*(qexp**self.plotexp),with_=' errorbar ')#p ps 2 pt 254')
                        listOfdata.append(GDerror)
                    except:
                        pass
                #else:
                    
        self.gp('set pointsize 0.5')
        #print len(listOfdata)
        self.gp.plot(*listOfdata)
        if i==0:
            self.gp('set nologscale')
            self.gp('set title \' nothing to plot\' ')
            self.gp('set nokey')
            self.gp.plot('x')
        '''
        if self._matplotlib:
            self.replotWxPlot()
        
    def replotWxPlot(self):
        """
        plot the wx frame
        """
        l=self.ListOfDatasChecked()
        if len(l)==0:
            return
        i=0
        try:
            self.plotframe.clearData()
        except :
            #PyDeadObjectError
            self.createWxPlot()
        l=[]
        for name in self.data_dict:
            l.append(name)
            l.sort()
        for name in l:
            qexp=self.data_dict[name].q
            iexp=self.data_dict[name].i
            
            if self.data_dict[name].checked:
                #print dir(self.data_dict[name])
                if self.data_dict[name].color!=None:
                    col=self.data_dict[name].color#pySaxsColors.getColorRGB(self.data_dict[name].color)
                    
                else:
                    col=None
                '''print name
                print self.data_dict[name].i
                print self.data_dict[name].q
                print iexp[0]    '''
                if self.data_dict[name].error<>None:
                    #print self.data_dict[name].error
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,error=self.data_dict[name].error,color=col)
                else:
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,color=col)
            i=i+1
        self.plotframe.replot()

    def OnLicence(self,event):
        file=pySAXS.__path__[0]+ os.sep+"LICENSE.txt"
        ViewMessage(file,"LICENCE")

    def OnAbout(self,event):
        file=pySAXS.__path__[0]+ os.sep+"ABOUT.txt"
        ViewMessage(file,"ABOUT "+pySAXS.__version__+pySAXS.__subversion__)
            
    def OnChange(self,evant):
        file=pySAXS.__path__[0]+ os.sep+"CHANGELOG.txt"
        ViewMessage(file,"What's new ? "+pySAXS.__version__+pySAXS.__subversion__)
    
    def OnCheckData(self,event):
        #what's happen when the user chek a box
        index = event.GetSelection()
        label = self.listBox.GetString(index)
        self.data_dict[label].checked= self.listBox.IsChecked(index)
        #print('Box %s is %s' % (label, self.data_dict[label][3]))
        self.RePlot(event)
        
    def OnSelectAll(self,event):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=True
        self.redrawTheList()
        self.RePlot(event)
    
    def OnUnSelectAll(self,event):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=False
        self.redrawTheList()
        self.RePlot(event)
        

    def OnClickData(self,event):
        '''
        what's happen when the user select a dataset
        '''
        index = event.GetSelection()
        label = self.listBox.GetString(index)
        st="name :\t"+self.data_dict[label].name+"\n"
        st+="nb datas : \t"+str(len(self.data_dict[label].q))+"\n"
        st+="filename : \t"+str(self.data_dict[label].filename)+"\n"
        if  self.data_dict[label].type<>None:
            tp=self.data_dict[label].type
            if typefile.has_key(tp):
                st+="type : \t"+str(typefile[tp][0])+"\n"
        if  self.data_dict[label].model<>None:
            st+="model : \tYes\n"
        if self.data_dict[label].parameters<>None:
            st+="parameters : \t"+self.data_dict[label].parameters.xmlString()+"\n"
        if self.data_dict[label].comment<>None:
            st+=self.data_dict[label].comment+"\n"
        self.infotxt.SetLabel(st)
        
    def OnDClickData(self,event):
        '''
        user doucle click on data : open what ?
        '''
        index = event.GetSelection()
        label = self.listBox.GetString(index)
        if self.data_dict[label].parameters<>None:
            self.OnScalingSAXSDlgShow(event)
        elif self.data_dict[label].model<>None:
            #check if reference datas exist
            m=self.data_dict[label].model
            if self.data_dict[label].type=="model":
                self.childmodel=LSModelDlg(self,label,type="model")
                self.childmodel.Show()
                return
            if not(self.data_dict.has_key(self.data_dict[label].rawdata_ref)):
                self.printTXT("references datas are missing")
                return
            if len(self.data_dict[label].i)<>len(self.data_dict[self.data_dict[label].rawdata_ref].i):
                self.printTXT("size for references datas and current datas are different")
                return
            #print len(self.data_dict[label].q),len(self.data_dict[label].i),len(self.data_dict[self.data_dict[label].rawdata_ref].i)
            self.data_dict[label].model.q=self.data_dict[label].q
            self.childmodel=LSModelDlg(self,label,type="data")
            self.childmodel.Show()
            
        

    def OnScalingSAXSDlgShow(self,event):
        '''
        The user click on "Scale Saxs Datas"
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            dlg = wx.MessageDialog(self, 'No data were selected','pySAXS alert',  wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        label = self.listBox.GetString(index)
        if self.data_dict[label].parameters==None:
            #--load datas
            #-- open dialog for parameters
            wc = "SAXS parameters xml file (*.xml)|*.xml|SAXS parameters file (*.par)|*.par"
            dlg=wx.FileDialog(self, message="Choose a parameter file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
            returnValue=dlg.ShowModal()
            if  returnValue== wx.ID_OK:
                self.printTXT("loading parameters file ",str(dlg.GetPath()))
                filename=str(dlg.GetPath())
                ext=filetools.getExtension(filename)
                saxsparameters=SAXSparameters.SAXSparameters(printout=self.printTXT)
                if ext=='par':
                    saxsparameters.importOLD(filename)#load(str(dlg.GetPath()))
                else:
                    #xml file
                    saxsparameters.openXML(filename)
                saxsparameters.parameters['filename'].value=filename
                saxsparameters.printout=self.printTXT
            else:
                saxsparameters=SAXSparameters.SAXSparameters(printout=self.printTXT)
        else:
            saxsparameters=self.data_dict[label].parameters
            saxsparameters.printout=self.printTXT
        self.childSaxs=SAXSAbsoluteDlg(self,saxsparameters,datasetname=label)
        self.childSaxs.Show()

    def OnScalingSAXSDlgLoad(self,event):
        '''
        The user click on "load parameters"
        '''
        #-- open dialog for parameters
        wc = "SAXS parameters xml file (*.xml)|*.xml|SAXS parameters file (*.par)|*.par"
        dlg=wx.FileDialog(self, message="Choose a parameter file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            self.printTXT( "loading parameters file ",str(dlg.GetPath()))
            filename=str(dlg.GetPath())
            ext=filetools.getExtension(filename)
            if ext=='par':
                saxsparameters=SAXSparameters.SAXSparameters(printout=self.printTXT)
                saxsparameters.importOLD(filename)#load(str(dlg.GetPath()))
                saxsparameters.parameters['filename'].value=filename
                saxsparameters.printout=self.printTXT
            else:
                #xml file
                saxsparameters=SAXSparameters.SAXSparameters(printout=self.printTXT)
                saxsparameters.openXML(filename)
                saxsparameters.parameters['filename'].value=filename
                saxsparameters.printout=self.printTXT
                
        else:
            saxsparameters=SAXSparameters.SAXSparameters(printout=self.printTXT)
        self.childSaxs=SAXSAbsoluteDlg(self,saxsparameters)
        self.childSaxs.Show()

    def OnScalingSAXSApply(self,applyQ,applyI,dataname,backgdname):
        '''
        child dialog box ask to apply parameters
        '''
        #-- 1 create new datas
        #q=self.saxsparameters.calculate_q
        q=self.data_dict[dataname].q
        i=self.data_dict[dataname].i
        saxsparameters=self.data_dict[dataname].parameters
        error=self.data_dict[dataname].error
        #print type(i)
        #print error
        #-- 2 apply parameters
        self.printTXT("------ absolute intensities ------")
        if applyQ:
            self.printTXT("--set q range --")
            q=saxsparameters.calculate_q(q)
        if applyI:
            if backgdname=='':
                i,error=saxsparameters.calculate_i(i,deviation=error)
                
            else:
                b=self.data_dict[backgdname].i
                berror=self.data_dict[backgdname].error
                if (len(b)<>len(i))and(numpy.mean(q)<>numpy.mean(self.data_dict[backgdname].q)):
                    self.printTXT("WARNING "+dataname+" and "+backgdname+" don't have  the same q !")
                    self.printTXT("trying interpolation for ",backgdname)
                    newf=interpolate.interp1d(self.data_dict[backgdname].q,
                                          self.data_dict[backgdname].i,
                                          kind='linear',bounds_error=0)
                    b=newf(q)
                    if self.data_dict[backgdname].error!=None:
                        newb=interpolate.interp1d(self.data_dict[backgdname].q,
                                              self.data_dict[backgdname].error,
                                              kind='linear',bounds_error=0)
                        berror=newb(q)
                    else:
                        berror=None
                i,error=saxsparameters.calculate_i(i,b,deviation=error,bdeviation=berror)
                #error=None
        self.printTXT("------ absolute intensities END ------")
        #-- 3 replot
        self.data_dict[dataname+' scaled']=dataset(dataname+' scaled',q,i,dataname+' scaled',\
                                                   parameters=saxsparameters,error=error,\
                                                   type='scaled')
        self.redrawTheList()
        self.RePlot()

    def OnDataSave(self,event):
        '''
        save the checked datas
        '''
        #-- open dialog for parameters
        wc = "Save data file(*.txt)|*.txt"
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.SAVE |  wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            #check if file exist already
            filename=dlg.GetPath()
            if filetools.fileExist(filename):
                  dlg2=wx.MessageDialog(self, "File exist, replace datas", caption="Question", style=wx.OK | wx.CANCEL)
                  returnValue=dlg2.ShowModal()
                  if returnValue!=wx.ID_OK:
                      self.printTXT("file "+str(filename)+" exist. Datas was NOT replaced")
                      return
            self.DataSaveAsTXT(filename)
            

    def DataSaveAsTXT(self,filename):
        '''
        save the checked datas
        '''
        self.printTXT("-------------------")
        self.printTXT("Saving data as txt in " + filename) 
        l=self.ListOfDatasChecked()
        f=open(filename,mode='w')
        #--- header
        header1='#'
        header2='#'
        nrows=0
        for name in l:
            self.printTXT( name)
            header1+=name+'\t\t'
            header2+='q\t i\t'
            if self.data_dict[name].error<>None:
                header1+='\t'
                header2+='error\t'
            if len(self.data_dict[name].q)>nrows:
                nrows=len(self.data_dict[name].q)
        header1+='\n'
        header2+='\n'
        f.write(header1)
        f.write(header2)
        self.printTXT(str( nrows)+" rows will be saved")
        #-- datas
        for n in range(nrows):
            dat=''
            for name in l:
                if n<len(self.data_dict[name].q):
                    dat+=str(self.data_dict[name].q[n])+'\t'
                    dat+=str(self.data_dict[name].i[n])+'\t'
                    if self.data_dict[name].error<>None:
                         dat+=str(self.data_dict[name].error[n])+'\t'
                else:
                    dat+='\t\t'
                    if self.data_dict[name].error<>None:
                        dat+='\t'
            dat+='\n'
            f.write(dat)
        self.printTXT("data are saved")
        self.printTXT("-------------------")
        f.close()

    def OnDataSaveDataset(self,event):
        '''
        save all the data set
        '''
        #-- open dialog for parameters
        wc = "dataset  xml file (*.xml)|*.xml|dataset file(*.dst)|*.dst"
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.SAVE |  wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            #check if file exist already
            filename=dlg.GetPath()
            if filetools.fileExist(filename):
                  dlg2=wx.MessageDialog(self, "File exist, replace datas", caption="Question", style=wx.OK | wx.CANCEL)
                  returnValue=dlg2.ShowModal()
                  if returnValue!=wx.ID_OK:
                      self.printTXT("file "+str(dlg.GetPath())+" exist. Datas was NOT replaced")
                      return
            if filetools.getExtension(filename)=='dst':
                saveDataDictRaw(filename,self.data_dict)
            else:
                saveDataDictOnXMLFile(filename,self.data_dict)
            self.SetTitle(filename)
            self.printTXT("datas saved in file "+filename)
            
        
    
    def OnDataOpenDataset(self,event):
        '''
        open the data set
        '''
        if len(self.data_dict)>0:
            #print "hello"
            dlg2=wx.MessageDialog(self,
                                      message='There is already an open data set. Do you want to overwrite ?',
                                      caption='pySAXS error',
                                      style=wx.YES_NO | wx.ICON_INFORMATION)
            returnValue=dlg2.ShowModal()
            if returnValue<>wx.ID_YES:
                return
        #-- open dialog for parameters
        wc = "dataset  xml file (*.xml)|*.xml|dataset file(*.dst)|*.dst"
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN |  wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            filename=str(dlg.GetPath())
            ext=filetools.getExtension(filename)             
            if ext=='dst':
                self.data_dict=getDataDictRaw(filename)
                #for compatibility with new dataset
                for name in self.data_dict:
                    self.data_dict[name].parent=None
                
            else:
                self.data_dict=getDataDictFromXMLFile(filename)
            self.redrawTheList()
            self.RePlot()
            self.SetTitle(dlg.GetPath())
            self.printTXT("open dataset : ",filename)

  
    def OnDataAppend(self,event):
        #-- open dialog
        wc = "dataset  xml file (*.xml)|*.xml|dataset file(*.dst)|*.dst"
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN |  wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            new_dict={}
            filename=str(dlg.GetPath())
            ext=filetools.getExtension(filename)             
            if ext=='dst':
                new_dict=getDataDictRaw(filename)
                #for compatibility with new dataset
                for name in self.data_dict:
                    self.data_dict[name].parent=None
            else:
                new_dict=getDataDictFromXMLFile(filename)
            for name in new_dict:
                if self.data_dict.has_key(name):
                    newname=self.giveMeANewName()
                    self.printTXT(name+" dataset already exist, renamed as "+newname)
                    new_dict[name].name=newname
                    self.data_dict[newname]=new_dict[name]
                    
                else:
                    self.data_dict[name]=new_dict[name]
            self.redrawTheList()
            self.RePlot()


    '''def DataAppend(self,filename):
        import pickle
        f=open(filename,mode='r')
        newdata_dict=pickle.load(f)
        for name in newdata_dict:
            if self.data_dict.has_key(name):
                newname=self.giveMeANewName()
                self.data_dict[newname]=newdata_dict[name]
            else:
                self.data_dict[name]=newdata_dict[name]
        f.close()
    '''
    def OnGridOn(self, event):
        self.gp('set grid')
        self.gp('replot')

    def OnGridOff(self, event):
        self.gp('unset grid')
        self.gp('replot')

    def OnEvalShow(self,event):
        l=self.ListOfDatasChecked()
        newdataset=self.giveMeANewName()
        dlg=LSEvalDlg(self,l,newdataset)
        dlg.Show()
        
    def OnEvalCalcul(self,formula,variableDict,newdatasetname,listofdata):
        '''
        feedback from evaluator dialog box
        #formula="i1+i0+i2"
        #variableDict={'i0':'data1','i1':'data2',...}
        #listofdata=['data1',data2'...]
        '''
        newdatasetname=self.cleanString(newdatasetname)
        qref=copy(self.data_dict[listofdata[0]].q)
        iref=zeros(shape(qref))
         #--
        formulaForComment=formula
        for var in variableDict:
            formulaForComment=formulaForComment.replace(var,variableDict[var])
        self.printTXT( formulaForComment)
        #new dataset
        newdata=dataset(newdatasetname,qref,iref,comment=formulaForComment,type='calculated',\
                        parent=listofdata,parentformula=formula,variableDict=variableDict)
        r=newdata._evaluateFromParent(self.data_dict)
        self.printTXT(r)
        self.data_dict[newdatasetname]=newdata
        self.redrawTheList()
        self.RePlot()
        
        

    def OnEvalCalculate(self,formula,variableDict,newdatasetname,listofdata):
        #from numpy import *
        '''
        feedback from evaluator dialog box
        #formula="i1+i0+i2"
        #variableDict={'i0':'data1','i1':'data2',...}
        #listofdata=['data1',data2'...]
        '''
        newdatasetname=self.cleanString(newdatasetname)
        qref=copy(self.data_dict[listofdata[0]].q)
        #print variableDict
        #--
        formulaForComment=formula
        for var in variableDict:
            formulaForComment=formulaForComment.replace(var,variableDict[var])
            self.printTXT( formulaForComment)
        newdict={}
        newerror=numpy.zeros(numpy.shape(qref))
        
        #--convert variableDict
        for var in variableDict:
            name=variableDict[var]
            #print name
            if not(self.data_dict.has_key(name)):
                print "error"
                return
            #variableDict contain variable name and dataset name
            i=self.data_dict[name].i
            q=self.data_dict[name].q
            if str(q)<>str(qref):
                self.printTXT("trying interpolation for ",name)
                newf=interpolate.interp1d(q,i,kind='linear',bounds_error=0)
                newi=newf(qref)
            else:
                newi=i
                #addition for errors
                error=self.data_dict[name].error
                if error!=None and newerror!=None:
                    newerror+=error
                else:
                    newerror=None
            newdict[var]=newi
        #--evaluate
        self.printTXT("trying evaluation of ",formula)
        
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', \
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',\
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'] #use the list to filter the local namespace safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        for k in safe_list:
            newdict[k]=locals().get(k)
        
        iout=numpy.array(eval(formula,newdict))
        self.data_dict[newdatasetname]=dataset(newdatasetname,qref,iout,comment=formulaForComment,type='calculated',error=newerror)#[data[0], data[1], datafilename, True]
        self.redrawTheList()
        self.RePlot()

    def giveMeANewName(self):
        '''
        return a new name for a data set
        '''
        newname='newdata'
        i=0
        while self.data_dict.has_key(newname):
            newname='newdata'+str(i)
            i+=1
        return newname

    def OnInterpolateShow(self,event):
        '''
        user click on Interpolate
        '''
        index=self.listBox.GetSelection()
        if index==-1:
            return
        olddataset = self.listBox.GetString(index)
        newdataset=self.giveMeANewName()
        self.data_dict[newdataset]=copy(self.data_dict[olddataset])
        dlg=LSInterpolateDlg(self,newdataset,olddataset)
        dlg.Show()
        self.redrawTheList()
        self.RePlot(event)

    def OnInterpolate(self,newdataset,olddataset,new_qrange):
        '''
        do the interpolation with the new qrange
        '''
        self.printTXT("trying interpolation for ",newdataset)
        i=self.data_dict[olddataset].i
        q=self.data_dict[olddataset].q
        newf=interpolate.interp1d(q,i,kind='linear',bounds_error=0)
        newi=newf(new_qrange)
        self.data_dict[newdataset].q=new_qrange
        self.data_dict[newdataset].i=newi
        self.data_dict[newdataset].error=None
        self.RePlot()

    def OnAddReferenceValue(self,event):
        '''
        user want to add a reference value
        '''
        #check if a data set is selected
        index=self.listBox.GetSelection()
        if index==-1:
            return

        datasetq = self.listBox.GetString(index)
        #message box for entry
        dlg=wx.TextEntryDialog(None,
                               "Value for reference :",
                               "Insert a value for reference",
                               "0",
                               style=wx.OK|wx.CANCEL)
        if dlg.ShowModal()==wx.ID_OK:
            value=float(dlg.GetValue())
            #add a data set
            newdataset="reference "+str(value)
            q=self.data_dict[datasetq].q
            ilist=[value]*len(q)
            i=numpy.array(ilist)
            self.data_dict[newdataset]=dataset(newdataset,q,i,datasetq,type='reference')
        self.redrawTheList()
        self.RePlot(event)

    def OnScaleQ(self,event):
        '''
        user want to scale q with a formula
        '''
        #check if a data set is selected
        index=self.listBox.GetSelection()
        if index==-1:
            return

        datasetname = self.listBox.GetString(index)
        #message box for entry
        dlg=wx.TextEntryDialog(None,
                               "Formula for q scaling :",
                               "specify a formula for q scaling",
                               "1*q",
                               style=wx.OK|wx.CANCEL)
        
        if dlg.ShowModal()==wx.ID_OK:
            formula=dlg.GetValue()
            #add a data set
            newdataset=datasetname+ " scaled with "+str(formula)
            q=self.data_dict[datasetname].q
            i=self.data_dict[datasetname].i
            try :
                qout=eval(formula,{"q":q})
            except :
                self.printTXT("error on evaluation of "+formula)
            qout=numpy.array(qout)
            self.data_dict[newdataset]=dataset(newdataset,qout,i,datasetname)
        self.redrawTheList()
        self.RePlot(event)
        
    def OnStatInformations(self,event):
        '''
        user want statistical information
        '''
        #check if a data set is selected
        index=self.listBox.GetSelection()
        if index==-1:
            return

        datasetq = self.listBox.GetString(index)
        q=self.data_dict[datasetq].q
        i=self.data_dict[datasetq].i
        #message box 
        info=""
        info+="Statistical information for "+datasetq+" : \n"
        info+="Number of points : "+str(len(q))+"\n"
        info+="x min : "+str(q[0])+", x max : "+str(q[len(q)-1])+"\n"
        info+="y min : "+str(min(i))+" at "+str(q[numpy.argmin(i)])+", y max : "+str(max(i))+" at "+str(q[numpy.argmax(i)])+"\n"
        info+="Mean of y : "+str(numpy.mean(i))+" with standard deviation : "+str(numpy.std(i))+"\n"
        info+="The signal-to-noise ratio( defined as the ratio between the mean and the standard deviation): "+str(stats.signaltonoise(i))+"\n"
        #info+="Integrate using the composite trapezoidal rule :"+str(integrate.trapz(i,q))+"\n"
        dlg=wx.MessageBox(message=info,caption="Statistical information",style=wx.OK)
        try:
            dlg.ShowModal()
        except:
            pass
        #if dlg.ShowModal()==wx.ID_OK:
        
        
    def OnGenerateNoise(self,event):
        '''
        user want generate a noise from the data
        '''
        #check if a data set is selected
        index=self.listBox.GetSelection()
        if index==-1:
            return
        datasetname = self.listBox.GetString(index)
        
        #message box for entry
        dlg=wx.TextEntryDialog(None,
                               "Percent of value :",
                               "specify a percent of random noise around the data value",
                               "10",
                               style=wx.OK|wx.CANCEL)
        
        if dlg.ShowModal()==wx.ID_OK:
            percent=int(dlg.GetValue())/100.0
            #add a data set
            newdataset=datasetname+ " noised with "+str(percent*100)+"%"
            q=self.data_dict[datasetname].q
            i=self.data_dict[datasetname].i
            randomarray=(numpy.random.rand(len(i))*2)-1 #randoms numbers between -1 and +1
            i=i+i*percent*randomarray
            self.data_dict[newdataset]=dataset(newdataset,q,i,datasetname,type="calculated")
        self.redrawTheList()
        self.RePlot(event)
            
            
            
    
    def removeNonOrdinalChar(self,s):
        result=''
        for c in s:
            if ord(c)<=128:
                result+=c
    def OnReinitGnulot(self,event):
        '''
        reinit gnuplot instance
        '''
        self.gp=None
        self.gp=Gnuplot.Gnuplot()
        self.gp.reset()
        self.RePlot(event)
        
    def getListOfDocs(self):
        p=path.dirname(pySAXS.__file__)
        l=filetools.listFiles(p+os.sep+"doc",'*.*')
        return l
    
    def OnDocClick(self,event):
        '''
        start the default application for the doc file
        '''
        no=event.GetId()
        name_file= self.docs[no-20000]
        if os.name == "nt":
            os.startfile("%s" % name_file)
        elif os.name == "posix":
            os.system("/usr/bin/xdg-open %s" % name_file)

    def createWxPlot(self):
        space = 5
        plotposition = self.GetSize()[0] + self.GetScreenPosition()[0] + space, self.GetScreenPosition()[1] - 5
    #print plotposition
        self.plotframe = matplotlibwx.PlotFrame(None, 1, "pySAXS datas", size=(700, self.GetSize()[1]),\
                                                 pos=plotposition,axetype=1)
        wx.Frame.SetIcon(self.plotframe, self.favicon)
        self.plotframe.Show(True)
        self.plotframe.xlabel = '$q(\AA^{-1})$'
        self.plotframe.ylabel = '$I$'
        self._matplotlib = True


    def cleanString(self,s):
        """Removes all accents from the string"""
        if isinstance(s,str):
            s = unicode(s,"utf8","replace")
            s=unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')
        
    def get_color(self,n):
        ''' return a color name from the list of colors
        if n> length of list of colors, return at the beginning
        '''
        t=divmod(n,len(self.colors)) #return the no of color in the list
        return self.colors[t[1]]
             
    def OnSAXSRAD(self,event):
        '''
        user click on radial averaging
        '''
        myFAIdlg=FAIdlg.FAIsaxsDlg(self,withGuisaxs=True)
        myFAIdlg.Show()
    
                            
if __name__== '__main__':
    app = wx.App(redirect=True)
    frame = GuiSAXS(None, 1)
    app.MainLoop()
