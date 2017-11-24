# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
mainGuisaxs a new GUI made with qt
author : Olivier Tache
(C) CEA 2012
"""
'''import guidata
from guidata import qt
from  guidata.dataset import datatypes
from guidata.dataset import dataitems'''
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import sys

def my_excepthook(type, value, tback):
    '''
    enabled pyqt5 application to catch the exception without 
    crashing
    '''
    # log the exception here
    #print value
    #print tback
    # then call the default handler
    sys.__excepthook__(type, value, tback)

import unicodedata
import genericFormDialog
from functools import partial

from pySAXS.tools import isNumeric
from pySAXS.guisaxs.qt import QtMatplotlib
from pySAXS.guisaxs.qt import dlgClipQRange
from pySAXS.guisaxs.qt import dlgConcatenate
from pySAXS.guisaxs.qt import dlgCalculator
from pySAXS.guisaxs.qt import dlgAbsoluteI
#from pySAXS.guisaxs.qt import pluginUsaxs
#from pySAXS.guisaxs.qt import pluginSubtractBackground
from pySAXS.guisaxs.qt import dlgInfoDataset
try:
    from pySAXS.guisaxs.qt import pluginFAI
except:
    pass
from pySAXS.guisaxs.qt import dlgModel
from pySAXS.guisaxs.qt import dlgTextView
from pySAXS.guisaxs.qt import dlgAbsorption


from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import colors
import matplotlib.font_manager as font_manager


from pySAXS.guisaxs import pySaxsColors

import os
from os import path

import pySAXS

import itertools
import numpy

from scipy import stats
from pySAXS.guisaxs.dataset import *
from pySAXS.tools import filetools
from pySAXS.tools import DetectPeaks
import unicodedata
import pySAXS.LS.SAXSparametersXML as SAXSparameters
from pySAXS.models import listOfModels
import pySAXS.models
from pySAXS.filefilters import fileimport

from pySAXS.guisaxs.qt import preferences

from time import sleep
from pySAXS.guisaxs.qt import pluginMCSAS



  

#type of datas [description, file extension, color]
'''typefile={'usaxs':['USAXS Raw Data file','txt','BLUE'],\
                  'usaxsrck':['USAXS Rocking Curve','txt','MAROON' ],\
                  'usaxsdsm':['USAXS Desmeared File','dsm','MAROON'],\
                  'saxs':['SAXS raw datas','rgr','FIREBRICK'],\
                  'fit2d':['datas from fit2D','chi','RED'],\
                  'txttab':['datas in 2 columns (or 3 with error) with tab separator','*','MAROON'],\
                  'txtcomma':['datas in 2 columns (or 3 with error) with comma separator','*','PURPLE'],\
                  'scaled':['datas scaled','*','TEAL'],\
                  'calculated':['datas calculated','*','PURPLE'],\
                  'referenceVal':['reference','*','VIOLET RED'],\
                  'reference':['reference datas','*','VIOLET RED'],\
                  'model':['model','*','GREEN'],\
                  'supermodel':['super model','*','INDIAN RED'],\
                  'resfunc':['USAXS resolution function','dat','MAROON'],
                  'swing':['Swing dat file','dat','MAROON']}'''
        
#list of data type to propose in open file dialog        
#typefile_list=['saxs','usaxs','usaxsrck','usaxsdsm','fit2d','txttab','txtcomma','swing','resfunc']
typefile_list= fileimport.import_list()
typefile=fileimport.import_dict()

SPLASHSCREEN_TEMPO=0.0

class mainGuisaxs(QtWidgets.QMainWindow):
    def __init__(self, parent=None,splashScreen=None):
        QtWidgets.QWidget.__init__(self, parent)
        #self.ui=mainGuisaxsui.Ui_mainGuisaxsWindows()
        #self.ui.setupUi(self)
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"mainGuisaxs.ui", self)
        
        self.setWindowTitle("pySAXS")
        self.icon=QtGui.QIcon(pySAXS.ICON_PATH+'pySaxs.png')
        self.setWindowIcon(self.icon)
        self.DatasetFilename=""
        self.workingdirectory=""
        self.referencedata=None
        self.backgrounddata=None
        self.referencedataSubtract=True
        self.setAcceptDrops(True)
        self.pastedModel=None
        
        
        #-- colors
        self.colors=pySaxsColors.pySaxsColors()
        if splashScreen is not None:
            splashScreen.showMessage("Loading preferences...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)
        
        #-- get preferences
        self.pref=preferences.prefs()
        if self.pref.fileExist():
            self.pref.read()
            #print "file exist"
            dr=self.pref.get('defaultdirectory')
            if dr is not None:
                self.workingdirectory=dr
                #print 'set wd',dr
        else:
            self.pref.save()
        #print 'last file : ',self.pref.getLastFile()
        #---- add the recent file menu
        rec=self.pref.getRecentFiles()
        for name in rec:
            name=name.strip('\'\"')
            action=self.ui.menuRecents.addAction(name)#add text in the menu
            item=name
            #action.triggered.connect(self.OnRecentFile)
            action.triggered.connect(partial( self.OnRecentFile,item))
            #action.triggered.connect(lambda item=item: self.OnRecentFile(name=item))
        self.ui.menuFile.addAction(self.ui.menuRecents.menuAction())
        if splashScreen is not None:
            splashScreen.showMessage("Loading menus...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)
        #-- connect menus
        #File
        self.ui.actionOpen.triggered.connect(self.OnFileOpen)
        self.ui.actionOpen_Dataset.triggered.connect(self.OnFileOpenDataset)
        self.ui.actionAppend_Dataset.triggered.connect(self.OnFileAppendDataset)
        self.ui.actionSave.triggered.connect(self.OnFileSave)
        self.ui.actionSave.setShortcut('Ctrl+S')
        self.ui.actionSave_As.triggered.connect(self.OnFileSaveAs)
        self.ui.actionExport.triggered.connect(self.OnFileExport)
        self.ui.actionReset_datas.triggered.connect(self.OnFileResetDatas)
        self.ui.actionGenerate_treatment_file.triggered.connect(self.OnFileGenerateABS)
        self.ui.actionExit.triggered.connect(self.close)
        #Edit
        self.ui.actionSelect_All.triggered.connect(self.OnEditSelectAll)
        self.ui.actionUnselect_All.triggered.connect(self.OnEditUnselectAll)
        self.ui.actionSelect_Only_Parents.triggered.connect(self.OnEditSelectParents)
        self.ui.actionSelect_Only_Childs.triggered.connect(self.OnEditSelectChilds)
        
        self.ui.actionRefresh_from_file.triggered.connect(self.OnEditRefresh)
        self.ui.actionRename.triggered.connect(self.OnEditRename)
        self.ui.actionRemove.triggered.connect(self.OnEditRemove)
        self.ui.actionRemove.setShortcut('Delete')
        self.ui.actionRemove_selected.triggered.connect(self.OnEditRemoveSelected)
        self.ui.actionDuplicate.triggered.connect(self.OnEditDuplicate)
        self.ui.actionDuplicate_without_links.triggered.connect(self.OnEditDuplicateWLinks)
        
        self.ui.actionClip_Q_range.triggered.connect(self.OnEditClipQRange)
        self.ui.actionScale_Q_range.triggered.connect(self.OnEditScaleQ)
        self.ui.actionConcatenate.triggered.connect(self.OnEditConcatenate)
        self.ui.actionDerivate.triggered.connect(self.OnEditDerivate)
        self.ui.actionFind_peaks.triggered.connect(self.OnEditFindPeaks)
        self.ui.actionSmooth.triggered.connect(self.OnEditSmooth)
        self.ui.actionCalculator.triggered.connect(self.OnEditCalculator)
        self.ui.actionStatistics.triggered.connect(self.OnEditStat)
        self.ui.actionGenerate_Noise.triggered.connect(self.OnEditGenerateNoise)
        self.ui.actionAddReferenceValue.triggered.connect(self.OnEditAddReference)
        self.ui.actionRemove_dependencies.triggered.connect(self.OnEditRemoveDependencies)
        self.ui.actionChange_color.triggered.connect(self.OnEditChangeColor)
        self.ui.actionSet_as_reference.triggered.connect(self.OnEditSetAsReference)
        self.ui.actionSet_as_Background.triggered.connect(self.OnEditSetAsBackground)
        #
        
        self.ui.actionCalculate_Resolution_function.triggered.connect(self.NotYetImplemented)
        self.ui.actionInvariant.triggered.connect(self.NotYetImplemented)
        self.ui.actionX_ray_absorption.triggered.connect(self.OnToolsAbsorption)
        self.ui.actionChanges.triggered.connect(self.OnHelpChanges)
        self.ui.actionLicence.triggered.connect(self.OnHelpLicense)
        self.ui.actionAbout.triggered.connect(self.OnHelpAbout)
        self.ui.actionInfo.triggered.connect(self.OnInfoDataset)
        
        
        #-- connect other objects
        #QtCore.QObject.connect(self.ui.treeWidget, QtCore.SIGNAL("itemChanged(QTreeWidgetItem*, int)"),self.OnItemChanged) #itemPressed 
        self.ui.treeWidget.itemClicked.connect(self.OnItemChanged)
        self.ui.treeWidget.itemDoubleClicked.connect(self.OnItemDoubleClicked)
                    
        self.ui.treeWidget.setHeaderLabels(["Datas"])
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.popup)
        #------------ main object  for datas 
        self.data_dict={}
        #generate filters names self.filterList
        self.createFilters()
        
        #---- Matplotlib window
        if splashScreen is not None:
            splashScreen.showMessage("Loading plot windows...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)
        self.move(QtCore.QPoint(100,100))
        self.createPlotframe()
        #self.plotframe.close_event().connect(self.OnPlotframeClosed)
        
        self.printTXT("<b>--- Welcome to GuiSAXS in QT ---</b>")
        
        #---- Plugin menu
        if splashScreen is not None:
            splashScreen.showMessage("Loading plugins...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)
        p=path.dirname(pySAXS.__file__)
        p+=os.sep+'guisaxs'+os.sep+'qt'
        pl= self.plugins_list(p)    #get the list of the plugins 
        #print pl
        base="pySAXS.guisaxs.qt."
        #objlist=[]
        submenuDict={}
        toolbarListPluginsActions=[]
        for name in pl:
            try:
                    m=self.my_import(base+name) #import plugins
                    cl= m.classlist             #the the class list from the plugin
                    #print cl
                    for c in cl:
                        try:
                            o=getattr(m,c)          #create an object 
                            #objlist.append(o)
                            #print o.menu,o.subMenu,o.subMenuText #get the menus
                            sub=o.subMenu
                            item=o
                            '''if o.subMenuText=='':
                                #no submenu, just an action
                                action = self.ui.menuData_Treatment.addAction(o.subMenu) #add in the menu
                                self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.callPlugin(item))
                            else:'''
                            if not submenuDict.has_key(sub):
                                    #submenu doesn t exist
                                    itemSub = QtWidgets.QMenu(self.ui.menuData_Treatment)
                                    itemSub.setObjectName(sub)
                                    itemSub.setTitle(sub)
                                    if o.icon is not None:
                                        icon1 = QtGui.QIcon()
                                        icon1.addPixmap(QtGui.QPixmap(pySAXS.ICON_PATH+o.icon), QtGui.QIcon.Normal, QtGui.QIcon.On)
                                        itemSub.setIcon(icon1)
                                    submenuDict[sub]=itemSub
                            #submenu exist
                            itemSub=submenuDict[sub]
                            action = itemSub.addAction(o.subMenuText) #add in the menu
                            if o.icon is not None:
                                #print "add icon ",o.icon, pySAXS.ICON_PATH+o.icon
                                icon1 = QtGui.QIcon()
                                icon1.addPixmap(QtGui.QPixmap(pySAXS.ICON_PATH+o.icon), QtGui.QIcon.Normal, QtGui.QIcon.On)
                                action.setIcon(icon1)
                            self.ui.menuData_Treatment.addAction(itemSub.menuAction())
                            action.triggered.connect(partial(self.callPlugin,o))
                            if o.toolbar:
                                #print "add to toolbar"
                                toolbarListPluginsActions.append(action)
                        except:
                                    print "Unexpected error :", sys.exc_info()[0]
                                    print "module : ",c ," module will not be available"
            except:
                        print "Unexpected error:", sys.exc_info()[0]
                        print "module : ",name ," module will not be available"
        
        #---- Models menu
        if splashScreen is not None:
            splashScreen.showMessage("Loading models...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)

        menuModels = QtWidgets.QMenu(self.ui.menuFit) #add in the menu
        menuModels.setTitle('Models')
        menuModels.setObjectName('Models')
        iconModel = QtGui.QIcon()
        iconModel.addPixmap(QtGui.QPixmap(pySAXS.ICON_PATH+"model.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        menuModels.setIcon(iconModel)
        # self.ui.menuData_Treatment.addAction(itemSub.menuAction())
        modelsDict=listOfModels.listOfModels() #get {'Spheres Monodisperse': 'MonoSphere', 'Gaussian': 'Gaussian'}
        dd=modelsDict.items()               #[('Spheres Monodisperse', 'MonoSphere'), ('Gaussian', 'Gaussian')]
        dd=self.sortDictByKey(modelsDict)
        self.modelsDictId={}
        for id in range(len(dd)):
            #construct a dictionary of models with id item
            #{0,('Spheres Monodisperse', 'MonoSphere') : 1,('Gaussian', 'Gaussian')}
            self.modelsDictId[id]=dd[id]
            #item = submenu.Append(id, dd[id][0])
            #self.Bind(wx.EVT_MENU, self.OnModelSelect, item)
            action=menuModels.addAction(dd[id][0])#add text in the menu
            action.setIcon(iconModel)
            item=dd[id][1]
            action.triggered.connect(partial(self.callModel,item))
        self.ui.menuFit.addAction(menuModels.menuAction())
        
        #menu paste model
        self.ui.menuFit.addSeparator()
        self.actionCopyModel=self.ui.menuFit.addAction("Copy model")#add text in the menu
        self.actionCopyModel.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"clipboard-paste.png"))
        self.actionCopyModel.setEnabled(False)
        self.actionCopyModel.triggered.connect(self.OnFitCopyModel)
        
        self.actionPasteModel=self.ui.menuFit.addAction("Paste model")#add text in the menu
        self.actionPasteModel.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"arrow-curve-270-left.png"))
        self.actionPasteModel.setEnabled(False)
        self.actionPasteModel.triggered.connect(self.OnFitPasteModel)
        
        #---- menu doc
        if splashScreen is not None:
            splashScreen.showMessage("Loading documentation...",color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
            sleep(SPLASHSCREEN_TEMPO)
        self.docs=self.getListOfDocs()
        i=0
        for name in self.docs:
           action = self.ui.menuDocuments.addAction(path.basename(name))
           item=name
           action.triggered.connect(partial(self.OnOpenDocument,item))
        
        self.ui.actionX_ray_absorption.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"table.png"))
        self.ui.actionFind_peaks.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"fit.png"))
        self.ui.actionSelect_All.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"ui-check-box-mix.png"))
        self.ui.actionUnselect_All.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"ui-check-box-uncheck.png"))
        self.ui.actionSelect_Only_Parents.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"node-select.png"))
        self.ui.actionSelect_Only_Childs.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"node-select-child.png"))
        self.ui.actionRename.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"document-rename.png"))
        self.ui.actionRemove.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"editdelete.png"))
        self.ui.actionDuplicate.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"editcopy.png"))
        self.ui.actionDuplicate_without_links.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"blue-document-copy.png"))
        self.ui.actionClip_Q_range.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"scissors"))
        self.ui.actionScale_Q_range.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"slide-resize-actual.png"))#ui-slider-050.png
        self.ui.actionConcatenate.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"plus-button.png"))
        self.ui.actionDerivate.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"hide.png"))
        self.ui.actionSmooth.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"chart-down.png"))
        self.ui.actionFind_Peaks.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"fit.png"))
        self.ui.actionInterpolate.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"chart-down-color.png"))
        self.ui.actionCalculator.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"calculator.png"))
        self.ui.actionStatistics.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"edit-mathematics.png"))
        self.ui.actionGenerate_Noise.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"megaphone.png"))#
        self.ui.actionRefresh_from_file.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"reload.png"))
        self.ui.actionAddReferenceValue.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"arrow.png"))
        self.ui.actionSet_as_reference.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"water.png"))
        self.ui.actionSet_as_Background.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"wall.png"))
        self.ui.actionRemove_dependencies.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"node-delete.png"))
        self.ui.actionChange_color.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"color.png"))
        self.ui.actionReset_datas.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"counter-reset.png"))
        self.ui.actionRemove_selected.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"document--minus.png"))
        self.ui.actionGenerate_treatment_file.setIcon(QtGui.QIcon(pySAXS.ICON_PATH+"blue-documents-stack.png"))
        
        #toolbar
        self.ui.toolBar.addAction(self.ui.actionOpen)
        toolbarListActions=[self.ui.actionOpen,self.ui.actionSave,None,self.ui.actionCalculator,self.ui.actionChange_color,\
                            self.ui.actionSet_as_reference,self.ui.actionSet_as_Background,None]
        toolbarListActions.extend(toolbarListPluginsActions)   
        for act in toolbarListActions:
            if act is not None:
                self.ui.toolBar.addAction(act)
            else:
                self.ui.toolBar.addSeparator()
        self.ui.show()
    
    def keyPressEvent(self, e):
        
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        else :
            print e.key()
        
        
    def callPlugin(self,obj,val):
        print val
        label=self.getCurrentSelectedItem()
        #print label
        child=obj(self,label)
        try:
            child.execute()
        except:
            print "Unexpected error in :"+obj.menu, sys.exc_info()[0]
            
    
    def callModel(self,modelname,val):
        #start model dlg
        label=self.getCurrentSelectedItem()
        M=getattr(pySAXS.models,modelname)()#create a new model
        if M.WarningForCalculationTime:
            ret=QtWidgets.QMessageBox.question(self,"pySAXS", "Computation time can be high for this model. Continue ?", buttons=QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            if ret!=QtWidgets.QMessageBox.Yes:
                return
        self.openModel(M, label)
    
    def openModel(self,M,label,openDialog=True):
            if label is None:
                '''
                no data checked
                add a new dataset with an empty model
                '''
                data_selected_for_model=M.name
                self.data_dict[data_selected_for_model]=dataset(data_selected_for_model,
                                                                     M.q,
                                                                     M.getIntensity(),
                                                                     "",
                                                                     True,
                                                                     M,
                                                                     type="model")#new data set checked
                if openDialog:
                    self.childmodel=dlgModel.dlgModel(self,data_selected_for_model,type="model")
            else:
                ''' data is checked '''
                
                data_selected_for_model=label
                new_dataname=data_selected_for_model+"-"+M.name+" model"
                q=self.data_dict[data_selected_for_model].q
                M.q=q
                i=M.getIntensity() #intensity by default
                filename=self.data_dict[data_selected_for_model].filename
                self.data_dict[new_dataname]=dataset(new_dataname,copy(q),
                                                        copy(i),
                                                        filename,
                                                        True,
                                                        M,#reference to model
                                                        parent=[data_selected_for_model],
                                                        rawdata_ref=data_selected_for_model,
                                                        type="model")#reference to original datas
                if openDialog:
                    self.childmodel=dlgModel.dlgModel(self,new_dataname,type="data")
            
            self.redrawTheList()
            self.Replot()
            
            if openDialog:
                self.childmodel.show()
            
        
    def sortDictByKey(self,d):
        '''
        return list of couple sorted by key
        '''
        l=[]
        for key in sorted(d.iterkeys()):
            l.append((key, d[key]))
        return l
        
    def popup(self, pos):
        '''
        display the Edit menu on popup
        '''
        menu = self.ui.menuEdit
        action = menu.exec_(self.mapToGlobal(pos))
        

    def closeEvent(self, event):
        '''
        when window is closed
        '''
        try:
            self.plotframe.close()
        except:
            pass
    
    def createPlotframe(self):
        '''
        create the plotframe
        '''
        spacex=25
        spacey=+30
        self.plotframe=QtMatplotlib.QtMatplotlib(self)
        
        #self.plotframe=Qtguiqwt.QtGuiqwt()
        x=self.width()+self.x() + spacex
        y=self.y()+spacey
        self.plotframe.move(x, y)
        self.plotframe.resize(self.width()*1.5,self.height())
        self.plotframe.setWindowTitle("Guisaxs Plot")
        self.plotframe.setScaleLabels('$q(\AA^{-1})$', 'I',size=10)
        self.plotframe.setAxesFormat(QtMatplotlib.LOGLOG,changeMenu=True)
        self.plotframe.show()
        '''
        self._matplotlib = True
        '''
    def OnPlotframeClosed(self):
        '''
        when plotframe is closed
        '''
        self.plotframe=None

    def createFilters(self):
        '''
        create file filters
        '''
        self.filterList=''
        #wc = ''
        #self.filterList = QtCore.QStringList()
        self.filterDict = {}
        for k in typefile_list:
            #filterName = typefile[k][0] + ' (*.' + typefile[k][1] + ')'
            filterName = typefile[k][0] + ' (' + typefile[k][1] + ')'
            self.filterList+=filterName+';;'
            #self.filterList.append(QtCore.QString(filterName))
            self.filterDict[filterName] = k
            #wc += typefile[k][0] + ' (*.' + typefile[k][1] + ');;'
        #return wc

    #@QtCore.pyqtSlot(str)
    def OnRecentFile(self,name):
        '''
        user clicked on recent file
        '''
        print "open", name
        if name is None:
            return
        if name is False:
            return
        extension=filetools.getExtension(name) #now we use the extension
        if extension!='xml':
            #data file
            for type in typefile_list:
                if typefile[type][1]==extension:
                    #self.printTXT('type of '+name+ 'is :', type)
                    self.OnFileOpen(false,[name],type)
                    return
            self.printTXT('Don\'t know the type of :', name)
            self.OnFileOpen(False,[name])
        else:
            #dataset
            if len(self.data_dict)>0:
                reply=QtWidgets.QMessageBox.question(self, 'pySAXS error',\
                                             'There is already an open dataset. Do you want to overwrite ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
                if reply == QtWidgets.QMessageBox.No:
                    return
            self.OnFileOpenDataset(filename=name)
            
        

    def OnFileOpen(self,bool=False,filenames=None,file_type=None):
        '''
        Load datas
        '''
        '''if self.data_dict.has_key('exp'):
            msgBox=QtGui.QMessageBox()
            msgBox.setText("Dataset is not empty. ")
            msgBox.setInformativeText("Do you want to reset active sample datas before loading new ?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok |QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
            ret = msgBox.exec_()
            print ret
            if ret!=QtGui.QMessageBox.Ok:
                return
        '''
        if filenames is None:
            #call the dialog box
            print "call the dialog box"
            fd = QtWidgets.QFileDialog(self)
            #get the filenames, and the filter
            filenames,filter=fd.getOpenFileNames(filter=self.filterList,initialFilter=('*.*'),directory=self.workingdirectory)
            #print "filter selected: ",filter
            if len(filenames)<=0:
                return
            #filter_key=typefile_list[filter_index]
            file_type=self.filterDict[str(filter)]
            #print "file_type : ",file_type
        #-- check if filename is dataset
        ext=filetools.getExtension(str(filenames[0]))
        if filetools.getExtension(str(filenames[0]))=='xml':
            self.printTXT("opening Dataset", str(filenames[0]))
            self.OnFileOpenDataset(filename=str(filenames[0]))
            return
        for datafilename in filenames:
                self.printTXT("opening " + datafilename) 
                datafilename=str(datafilename)
                #extension=filetools.getExtension(datafilename) #now we use the extension
                self.ReadFile(datafilename,file_type)
        #save in preferences
        self.setWorkingDirectory(datafilename)
        #redraw
        self.redrawTheList()
        self.Replot()
    
    def OnFileOpenDataset(self,bool=False,filename=None):
        '''
        open the data set
        '''
        if len(self.data_dict)>0:
            #print "hello"
            reply=QtWidgets.QMessageBox.question(self, 'pySAXS error',\
                                                'There is already an open dataset. Do you want to overwrite ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
            if reply == QtWidgets.QMessageBox.No:
                return
        if filename is None:
            #-- open dialog for parameters
            fd = QtWidgets.QFileDialog(self)
            #get the filenames, and the filter
            wc = "dataset  xml file (*.xml);;dataset file(*.dst)"
            filenames,filter=fd.getOpenFileNames(filter=wc,initialFilter=('*.dst'),directory=self.workingdirectory)
            #print "filter selected: ",filter
            #print 'filenames:',filenames
            if len(filenames)<=0:
                return
            filename=str(filenames[0])
        ext=filetools.getExtension(filename)
        #print 'ext:',ext             
        if str(ext).find('dst')>=0:
            self.data_dict=getDataDictRaw(filename)
            #for compatibility with new dataset
            for name in self.data_dict:
                self.data_dict[name].parent=None
                self.data_dict[name].color=None
                self.data_dict[name].image=None
                
        else:
            self.data_dict=getDataDictFromXMLFile(filename)
        
        #check the colors"
        colors=pySaxsColors.pySaxsColors()
        l=[]
        for name in self.data_dict:
            l.append(name)
            if self.data_dict[name].type=='reference':
                self.referencedata=name
                self.printTXT('reference datas are ',name)
            if self.data_dict[name].type=='background':
                self.backgrounddata=name
                self.printTXT('background datas are ',name)
        l.sort()
        i=0
        for name in l:
            if self.data_dict[name].color is None:
                #set a color
                col=colors.getColor(i)
                self.data_dict[name].color=col
                i+=1
        self.setWorkingDirectory(filename)
         
        self.redrawTheList()
               
        self.Replot()
        self.setWindowTitle(filename)
        self.DatasetFilename=filename
        self.printTXT("open dataset : ",filename)
    
    def OnFileAppendDataset(self):
        '''
        append a data set
        '''
        #-- open dialog for parameters
        fd = QtWidgets.QFileDialog(self)
        #get the filenames, and the filter
        wc = "dataset  xml file (*.xml);;dataset file(*.dst)"
        filenames,filter=fd.getOpenFileNames(filter=wc,initialFilter=('*.dst'),directory=self.workingdirectory)
        #print "filter selected: ",filter
        filename=str(filenames[0])
        self.setWorkingDirectory(filename)
        if len(filenames)<=0:
            return
        ext=filetools.getExtension(filename)             
        if str(filter).find('dst')>=0:
            new_data_dict=getDataDictRaw(filename)
            #for compatibility with new dataset
            for name in self.data_dict:
                new_data_dict[name].parent=None
                
        else:
            new_data_dict=getDataDictFromXMLFile(filename)
        #append
        for name in new_data_dict:
            if self.data_dict.has_key(name):
                    newname=name+" "+self.giveMeANewName()
                    self.printTXT(name+" dataset already exist, renamed as "+newname)
                    new_data_dict[name].name=newname
                    self.data_dict[newname]=new_data_dict[name]
            else:
                    self.data_dict[name]=new_data_dict[name]
        self.redrawTheList()
        self.Replot()
        self.printTXT("open dataset : ",filename)
        
        
    def OnFileSave(self):
        '''
        save the dataset in the same file
        '''
        #when dataset filename is empty file save as
        if self.DatasetFilename=="":
            if len(self.data_dict)>0:
                self.OnFileSaveAs()
            return
        
        filename=self.DatasetFilename
        saveDataDictOnXMLFile(filename,self.data_dict)
        self.DatasetFilename=filename
        self.setWindowTitle(filename)
        self.printTXT("datas saved in file "+filename)
    
    def OnFileSaveAs(self):
        '''
        save the checked datas
        '''
        #-- open dialog for parameters
        fd = QtWidgets.QFileDialog(self)
        #get the filenames, and the filter
        wc = "dataset  xml file (*.xml)"
        filename=fd.getSaveFileName (filter=wc,directory=self.workingdirectory)[0]
        filename=str(filename)
        self.setWorkingDirectory(filename) #set working dir
        if  filename!="":
            #check if file exist already
            if filetools.fileExist(filename):
                reply=QtWidgets.QMessageBox.question(self, 'pySAXS Question',\
                                                'File exist. Do you want to replace ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
                if reply == QtWidgets.QMessageBox.No:
                    self.printTXT("file "+str(filename)+" exist. Datas were NOT replaced")
                    return
                
            saveDataDictOnXMLFile(filename,self.data_dict)
            self.setWindowTitle(filename)
            self.DatasetFilename=filename
            self.printTXT("datas saved in file "+filename)
    
    def OnFileExport(self):
        '''
        save the checked datas in txt
        '''
        #-- open dialog for parameters
        fd = QtWidgets.QFileDialog(self)
        #get the filenames, and the filter
        wc = "txt file (*.txt)"
        filename=fd.getSaveFileName(filter=wc,directory=self.workingdirectory)[0]
        filename=str(filename)
        self.setWorkingDirectory(filename) #set working dir
        if  filename!="":
            #check if file exist already
            if filetools.fileExist(filename):
                reply=QtWidgets.QMessageBox.question(self, 'pySAXS Question',\
                                                'File exist. Do you want to replace ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
                if reply == QtWidgets.QMessageBox.No:
                    self.printTXT("file "+str(filename)+" exist. Datas were NOT replaced")
                    return
                
            self.SaveAsTXT(filename)
            self.setWindowTitle(filename)
            self.DatasetFilename=filename
            

    def SaveAsTXT(self,filename):
        '''
        save the checked datas
        '''
        self.printTXT("-------------------")
        self.printTXT("Saving data as txt in " + filename) 
        l=self.ListOfDatasChecked()
        print l
        l.sort()
        print l
        f=open(filename,mode='w')
        #--- header
        header1='#'
        header2='#'
        nrows=0
        for name in l:
            self.printTXT( name)
            header1+=name+'\t\t'
            header2+='q\t i\t'
            if self.data_dict[name].error is not None:
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
                    if self.data_dict[name].error is not None:
                         dat+=str(self.data_dict[name].error[n])+'\t'
                else:
                    dat+='\t\t'
                    if self.data_dict[name].error is not None:
                        dat+='\t'
            dat+='\n'
            f.write(dat)
        self.printTXT("data are saved")
        self.printTXT("-------------------")
        f.close()

    
    def OnFileResetDatas(self):
        '''
        clear the datas
        '''
        self.setWindowTitle("pySAXS")
        self.DatasetFilename=""
        self.data_dict.clear()
        self.redrawTheList()
        self.Replot()
    
    def OnFileGenerateABS(self):
        '''
        generate for each selected datas an ABS file containing all the data treatment
        '''
        self.printTXT("-------------------")
        self.printTXT("Saving ABS data treatment ") 
        l=self.ListOfDatasChecked()
        for name in l:
            if self.data_dict[name].abs is not None:
                print self.data_dict[name].abs
                self.data_dict[name].abs.saveABS(self.data_dict[name].filename)
        
        
    def OnEditSelectAll(self):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=True
        self.redrawTheList()
        self.Replot()
        
    
    def OnEditUnselectAll(self):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=False
        self.redrawTheList()
        self.Replot()
    
    def OnEditSelectParents(self):
        '''
        when the user want to select only parents
        '''
        for label in self.data_dict:
            if self.data_dict[label].parent is None:
                self.data_dict[label].checked=True
            else:
                self.data_dict[label].checked=False
        self.redrawTheList()
        self.Replot()
    
    def OnEditSelectChilds(self):
        '''
        when the user want to select only parents
        '''
        for label in self.data_dict:
            if self.data_dict[label].parent is None:
                self.data_dict[label].checked=False
            else:
                self.data_dict[label].checked=True
        self.redrawTheList()
        self.Replot()
    
    def OnEditRefresh(self):
        '''
        refresh data from file (is exist)
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        filename=self.data_dict[label].filename
        type=self.data_dict[label].type
        if type!=None:
            self.printTXT("refresh "+ filename)
            self.ReadFile(filename,type)
            self.Replot()
        else:
            self.printTXT('type of data unknown -> not possible to refresh datas ')
    
    def OnEditRename(self):
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        newlabel, ok = QtWidgets.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:',text=label)
        newlabel=str(newlabel)
        if ok:
            newlabel=self.cleanString(newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtWidgets.QMessageBox.question(self, 'pySAXS Question', 'There is already a data set with this name ! Replace ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
                if reply == QtWidgets.QMessageBox.No:
                    return
            #print newlabel
            self.printTXT("Rename  "+label+" into : ",newlabel)
            self.data_dict[newlabel]=self.data_dict[label]
            self.data_dict[newlabel].name=newlabel
            self.data_dict.pop(label)
            self.redrawTheList()
            self.Replot()
    
    def OnEditRemove(self):
        '''
        remove a data set
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        reply=QtWidgets.QMessageBox.question(self, 'pySAXS Question', 'Are you sure you want to remove this data set : '+label+' ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
        if reply == QtWidgets.QMessageBox.Yes:
            #remove
            self.printTXT("removing ",label)
            self.data_dict.pop(label)
            self.redrawTheList()
            self.Replot()
    
    def OnEditRemoveSelected(self):
        '''
        remove selected datas
        '''
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)<=0:
            self.noDataErrorMessage()
            return
        reply=QtWidgets.QMessageBox.question(self, 'pySAXS Question', 'Are you sure you want to remove this datas ?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
        if reply == QtWidgets.QMessageBox.Yes:
            #remove
            for label in listofdata:
                self.printTXT("removing ",label)
                self.data_dict.pop(label)
            self.redrawTheList()
            self.Replot()
        
            
    def OnEditDuplicate(self):
        '''
        duplicate a data set
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        newlabel, ok = QtWidgets.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:',text=label)
        newlabel=str(newlabel)
        if ok:
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtWidgets.QMessageBox.warning(self, 'pySAXS Error', 'There is already a data set with this name !')
                return
            self.data_dict[newlabel]=self.data_dict[label]._deepcopy()
            self.data_dict[newlabel].name=newlabel
            self.redrawTheList()
            self.Replot()
    
    def OnEditDuplicateWLinks(self):
        '''
        duplicate a data set without links
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        newlabel, ok = QtWidgets.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:')
        newlabel=str(newlabel)
        if ok:
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtWidgets.QMessageBox.warning(self, 'pySAXS Error', 'There is already a data set with this name !')
                return
            self.data_dict[newlabel]=self.data_dict[label]._deepcopy()
            self.data_dict[newlabel].parent=None
            self.data_dict[newlabel].name=newlabel
            self.redrawTheList()
            self.Replot()
            
    def OnEditClipQRange(self):
        '''
        clip q range
        '''
        dataset_name=self.getCurrentSelectedItem()
        if dataset_name is None:
            self.noDataErrorMessage()
            return
        
                
        datas=self.data_dict[dataset_name]
        qmin=datas.q.min()
        qmax=datas.q.max()
        nbpoints=len(datas.q)
        '''
        dlg=dlgClipQRange.dlgClipQRange(dataset_name,qmin,qmax)
        if dlg.exec_():
            qmin, qmax= dlg.getValues()
        '''
        #here we use guidata to generate a dialog box
        '''items = {
         "dataname": dataitems.StringItem("datas :",dataset_name).set_prop("display", active=False),
         "qmin" : dataitems.FloatItem("qmin :",qmin),
         "qmax" : dataitems.FloatItem("qmax :",qmax)
         }
        clz = type("Clip q range :", (datatypes.DataSet,), items)
        dlg = clz()
        dlg.edit()  
        qmin=dlg.qmin
        qmax=dlg.qmax  '''
        #end of dialog box
        dlg=genericFormDialog.genericFormDialog(title='Clip q range',\
                                                comment="dataset_name",\
                                                names=['qmin','qmax'],
                                                values=[qmin,qmax])
        dlg.exec_()
        if dlg.result is not None:
            qmin,qmax=dlg.getResult()
        else:
            return
        q=numpy.array(self.data_dict[dataset_name].q)
        i=numpy.array(self.data_dict[dataset_name].i)
        error=self.data_dict[dataset_name].error
        #clip q min
        if self.data_dict[dataset_name].error is not None:
            error=numpy.repeat(error,q>=qmin)
        i=numpy.repeat(i,q>=qmin)
        q=numpy.repeat(q,q>=qmin)
        #clip q max
        if self.data_dict[dataset_name].error is not None:
            error=numpy.repeat(error,q<=qmax)
        i=numpy.repeat(i,q<=qmax)
        q=numpy.repeat(q,q<=qmax)
        #clip q min
        self.data_dict[dataset_name].q=q
        self.data_dict[dataset_name].i=i
        self.data_dict[dataset_name].error=error
        #replot
        self.Replot()
        
    def OnEditScaleQ(self):
        '''
        user want to scale q with a formula
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #message box for entry
        formula, ok = QtWidgets.QInputDialog.getText(self, 'Formula for q scaling :', "specify a formula for q scaling",text="1*q")
        formula=str(formula)
        #add a data set
        newdataset=label+ " scaled with "+str(formula)
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        try :
                qout=eval(formula,{"q":q})
        except :
            self.printTXT("error on evaluation of "+formula)
            return
        qout=numpy.array(qout)
        self.data_dict[newdataset]=dataset(newdataset,qout,i,parent=[label])
        self.redrawTheList()
        self.Replot()
    
    def OnEditConcatenate(self):
        '''
        user want to concatenate different dataset
        '''
        #label=self.getCurrentSelectedItem()
        '''if label is None:
            return
            '''
        #create a new data set
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)<=0:
            self.noDataErrorMessage()
        #print listofdata
        newdatasetname=listofdata[0]+' new'
        '''print newdatasetname
        self.data_dict[newdatasetname]=copy(self.data_dict[listofdata[0]])
        self.data_dict[newdatasetname].name=newdatasetname'''
        dlg=dlgConcatenate.dlgConcatenate(self,newdatasetname)
        
        dlg.exec_()
        #dlg.getValues()
        #create a new data set
        #newdatasetname=listofdata[0]+' new'
        #self.data_dict[newdatasetname]=copy(self.data_dict[listofdata[0]])
        #self.data_dict[newdatasetname].name=newdatasetname
            
    def OnEditSmooth(self):
        '''
        user want to smooth dataset
        ref http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        pp, ok = QtWidgets.QInputDialog.getText(self, 'pySAXS Smooth parameter :', 'Smooth parameter:')
        if ok:
            if not(isNumeric.isNumeric(pp)):
                self.printTXT("value : "+str(pp)+" is not a valid numeric")
                return
            pp=float(str(pp))
            newdatasetname=label+' smooth'
            self.data_dict[newdatasetname]=self.data_dict[label]._deepcopy()
            self.data_dict[newdatasetname].parent=[label]
            self.data_dict[newdatasetname].name=newdatasetname
            q=self.data_dict[newdatasetname].q
            i=self.data_dict[newdatasetname].i
            tck = interpolate.splrep(q,i,s=pp)
            ysmooth = interpolate.splev(q,tck,der=0)
            self.data_dict[newdatasetname].i=ysmooth
            self.redrawTheList()
            self.Replot()
            
    def OnEditCalculator(self):
        '''
        show the calculator dialog box
        '''
        '''
        feedback from evaluator dialog box
        #formula="i1+i0+i2"
        #variableDict={'i0':'data1','i1':'data2',...}
        #listofdata=['data1',data2'...]
        '''
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)==0:
            QtWidgets.QMessageBox.information(self,"pySAXS", "No data are selected", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return None
        newdataset=self.giveMeANewName()
        
        dlg=dlgCalculator.dlgCalculator(self,listofdata,newdataset)
        dlg.exec_()
        #dlg.show()
        '''    newdatasetname,formula,variableDict=dlg.getValues()
        else:
            return
        newdatasetname=self.cleanString(newdatasetname)
        qref=copy(self.data_dict[listofdata[0]].q)
        
        #--
        print newdatasetname,formula,variableDict
        formulaForComment=formula
        for var in variableDict.keys():
            formulaForComment=formulaForComment.replace(var,variableDict[var])
            self.printTXT(formulaForComment)
        newdict={}
        newerror=numpy.zeros(numpy.shape(qref))
        
        #--convert variableDict
        for var in variableDict:
            name=variableDict[var]
            #print name
            if not(self.data_dict.has_key(name)):
                print "error on mainGuisaxs.OnEditCalculator"
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
        self.Replot()
        '''
    def OnEditRemoveDependencies(self):
        '''
        remove all dependencies on datasets
        '''
        label=self.getCurrentSelectedItem()
        selectedDatas=self.ListOfDatasChecked()
        for name in selectedDatas:
            self.data_dict[name].parent=None
            self.data_dict[name].child=None
            self.data_dict[name].parentformula=None
            self.data_dict[name].variableDict=None
        self.redrawTheList()
        self.Replot()
    
    
    
    def OnEditChangeColor(self):
        '''
        user want to change the color
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        initial=self.data_dict[label].color
        if initial is None:
            initial="#ffffff"
        col = QtWidgets.QColorDialog.getColor(QtGui.QColor(initial))
        self.data_dict[label].color=str(col.name())
        #print col.name()
        self.Replot()
            
    def OnEditStat(self):
        '''
        user want statistical information
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        
        #message box 
        info=""
        info+="Statistical information for "+label+" : \n"
        info+="Number of points : "+str(len(q))+"\n"
        info+="x min : "+str(q[0])+", x max : "+str(q[len(q)-1])+"\n"
        info+="y min : "+str(min(i))+" at "+str(q[numpy.argmin(i)])+", y max : "+str(max(i))+" at "+str(q[numpy.argmax(i)])+"\n"
        info+="Mean of y : "+str(numpy.mean(i))+" with standard deviation : "+str(numpy.std(i))+"\n"
        info+="The signal-to-noise ratio( defined as the ratio between the mean and the standard deviation): "+str(stats.signaltonoise(i))+"\n"
        dlg=QtWidgets.QMessageBox.information(self,"pySAXS",info, buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
    
    def OnEditGenerateNoise(self):
        '''
        user want generate a noise from the data
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        #message box for entry
        #here we use guidata to generate a dialog box
        '''percent=10.0
        items = {
         "percent": dataitems.FloatItem("Percent of random noise around the data value :",percent),
         }
        clz = type("Noise generator :\nspecify a percent of random noise around the data value", (datatypes.DataSet,), items)
        dlg = clz()
        if not dlg.edit():
            return  
        percent=dlg.percent
        '''
        num,ok = QtWidgets.QInputDialog.getDouble(self,"Noise generator :","specify a percent of random noise around the data value",decimals=10)
        if ok:
            percent=float(num)
        else:
            return
        percent=int(percent)/100.0
        #add a data set
        newdataset=label+ " noised with "+str(percent*100)+"%"
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        randomarray=(numpy.random.rand(len(i))*2)-1 #randoms numbers between -1 and +1
        i=i+i*percent*randomarray
        self.data_dict[newdataset]=dataset(newdataset,q,i,label,type="calculated",parent=[label])
        self.redrawTheList()
        self.Replot()
        

    def OnEditAddReference(self):
        '''
        user want to add a reference value
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #message box for entry
        value=1.0
        '''items = {
         "value": dataitems.FloatItem("Reference value :",value),
         }
        clz = type("Add a reference value", (datatypes.DataSet,), items)
        dlg = clz()
        if not dlg.edit():
            return  
        value=dlg.value'''
        #num,ok = QtGui.QInputDialog.getDouble(self,"Add a reference value :","specify a value",decimals=10)
        num,ok = QtWidgets.QInputDialog.getText(self,"Add a reference value :","specify a value")
        
        if ok:
            value=float(num)
        else:
            return
        #add a data set
        newdataset="reference "+str(value)
        q=self.data_dict[label].q
        ilist=[value]*len(q)
        i=numpy.array(ilist)
        self.data_dict[newdataset]=dataset(newdataset,q,i,label,type='referenceVal')
        self.redrawTheList()
        self.Replot()
        
    def OnEditSetAsReference(self):
        '''
        user want to set a reference 
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #print 'set as reference : ',label
        self.data_dict[label].type='reference'
        self.referencedata=label
        self.printTXT('reference datas are ',label)
        self.redrawTheList()
        
    
    def OnEditSetAsBackground(self):
        '''
        user want to set a background 
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        print 'set as background : ',label
        self.data_dict[label].type='background'
        self.backgrounddata=label
        self.printTXT('background datas are ',label)
        self.redrawTheList()
        
        
        
    def OnFitPasteModel(self):
        '''
        paste model on all checked data set
        '''
        #1- check if model exist in clipboard
        if self.pastedModel is None:
            print "we should'nt have this"
            return
        
        #2- list data checked
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #3- apply
        self.openModel(self.pastedModel._deepcopy(),label,openDialog=False)
        #self.data_dict[label].model=self.pastedModel._deepcopy()
        print self.pastedModel
        self.printTXT("model "+self.pastedModel.Description+ " pasted")
        self.redrawTheList()
        
    def OnFitCopyModel(self):
        item=self.ui.treeWidget.currentItem()
        if item is None:
            return
        if not item.isSelected():
            return
        itemParent=item.parent()
        labelParent=str(itemParent.text(0))
        #self.childmodel=dlgModel.dlgModel(self,labelParent,type="data")
        #self.childmodel.show()
        print labelParent
        if self.data_dict[labelParent].model is not None:
            self.OnCopyModel(self.data_dict[labelParent].model)
    
    def OnCopyModel(self,model):
        '''
        get a copy of a model
        '''
        self.printTXT('Copy of model : ',model.Description )
        self.pastedModel=model
        self.actionPasteModel.setEnabled(True)
        
    def OnInfoDataset(self):
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        data=self.data_dict[label]
        child=dlgInfoDataset.dlgInfoDataset(data)
        
        
        
    #----------------------------------------------------------------------------------------------------------------
        
    def redrawTheList(self):
        '''
        redraw the listbox
        '''
        l=[]
        for name in self.data_dict:
            l.append(name)
            
        l.sort()
        #qt tree widget    
        self.ui.treeWidget.clear()
        self.ui.treeWidget.setHeaderLabels(["Datas"])
        treedict={}
        for name in l:  
            #print name
            item=QtWidgets.QTreeWidgetItem([name])
            item.label=name
            item.internalType='data'
            treedict[name]=item
            #item.setIcon(0, QtGui.QIcon(pySAXS.ICON_PATH+'chart_curve.png'))
            if self.data_dict[name].checked:
                #print "checked:",name,
                item.setCheckState(0,QtCore.Qt.Checked)
                item.setBackground(0,QtGui.QColor('#FFEFD5'))#QtCore.Qt.gray)##C0C0C0
                #print "  ok"
                if self.data_dict[name].color is not None:
                    item.setForeground(0,QtGui.QColor(self.data_dict[name].color))
            else:
                item.setCheckState(0,QtCore.Qt.Unchecked)
                #print "blanc"
                item.setBackground(0,QtCore.Qt.white)
                #print "la"
                #item.setForeground(0,QtCore.Qt.black)
                if self.data_dict[name].color is not None:
                    #print 'color'
                    item.setForeground(0,QtGui.QColor(self.data_dict[name].color))
            #print "ici"
            if name==self.referencedata:
                item.setBackground(0,QtGui.QColor('#FFB6C1'))#FFB6C1    
            if name==self.backgrounddata:
                item.setBackground(0,QtGui.QColor('#C3AEAE'))#FFB6C1    
        #print "test", len(treedict),len(self.data_dict)            
        for name, item in treedict.items():
            #print name
            parent=self.data_dict[name].parent
            #print parent
            if parent is not None:
                #print "parent :",parent
                pere=parent[0]
                if treedict.has_key(pere):
                    #print pere
                    #print "parent found"
                    treedict[pere].addChild(item)
                    treedict[pere].setExpanded(True)
                    item.setExpanded(True)
                    item.setIcon(0, QtGui.QIcon(pySAXS.ICON_PATH+'arrow_join.png'))
                    self.ui.treeWidget.expandItem(item)
                    
                else:
                    self.ui.treeWidget.addTopLevelItem(item)
            else:
                item.setExpanded(True)
                self.ui.treeWidget.addTopLevelItem(item)
            
            #if item has parameters 
            if self.data_dict[name].parameters is not None:
                lbl='Scaling parameters'
                item=QtWidgets.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='parameters'
                item.setIcon(0, QtGui.QIcon(pySAXS.ICON_PATH+'chart_params.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)
            
            if self.data_dict[name].model is not None:
                #print name
                lbl='Model :'+self.data_dict[name].model.name
                item=QtWidgets.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='model'
                item.setIcon(0, QtGui.QIcon(pySAXS.ICON_PATH+'fit.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)
                
            '''if self.data_dict[name].image is not None:
                lbl=self.data_dict[name].image
                item=QtGui.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='image'
                item.setIcon(0, QtGui.QIcon(pySAXS.ICON_PATH+'image.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)'''
                
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.sortByColumn(0,0)
           
       
    def ReadFile(self,datafilename,file_type=None):
        '''
        read file depending of type of file
        '''
        name = filetools.getFilename(datafilename)
        f=fileimport.fileImport(file_type)
        #try:
        q,i,err=f.read(datafilename)
        #except:
        #QtGui.QMessageBox.information(self,"pySAXS", "Error occured when trying to open file, try another filter", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
        #return None
            
        #----- data -> dataset
        name=self.cleanString(name)
        self.data_dict[name] = dataset(name,q, i, datafilename,type=type,error=err)
        self.data_dict[name].color=self.colors.getColor() #set a random color
        
        '''
        if file_type=='usaxs':
            #if extension=="txt": #it is a txt file
            #data = LSusaxs.ReadUSAXSData(datafilename)
            self.ImportData(datafilename,usecols = (0,2),name=name,type=file_type) #here we get (2theta , I)
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
            self.ImportData(datafilename,'  ',name=name,type=file_type,skiprows=4 )
        elif file_type=='saxs':
            #it is a rgr file
            self.ImportData(datafilename,'\t',name=name,type=file_type ,errorcol=2)
        elif file_type=='txttab':
            #it is a txt file
            self.ImportData(datafilename,name=name,type=file_type)
        elif file_type=='txtcomma':
            #it is a txt file
            self.ImportData(datafilename,name=name,delimiter=',',type=file_type)
        elif file_type=='resfunc':
            #it is a dat file
            self.ImportData(datafilename,name='resfunc',delimiter=',',type=file_type)
        elif file_type=='swing':
            self.ImportData(datafilename,name=name,type=file_type,skiprows=32)
        else:
            #don't know
            self.ImportData(datafilename,name=name,type=file_type)
        '''

    def OnItemChanged(self,item,column):
        '''
        what's happen when the user chek a box
        '''
        #print 'on item changed'
        label=str(item.text(0))
        if item.internalType=='model':
            self.actionCopyModel.setEnabled(True)
        else:
            self.actionCopyModel.setEnabled(False)
        if item.internalType!='data':
            return
        '''
        if label=='Scaling parameters' or label=="Image":
            return
        '''
        state=item.checkState(0) #state can be 0 or 2 not boolean
        if self.data_dict[label].checked==state:
            #state didn't changed, don't replot
            return
        self.ui.treeWidget.setCurrentItem(item)
        #print "item changed : ",label,state,self.data_dict[label].checked
        if state:
            self.data_dict[label].checked=True
            #item.setBackgroundColor(0,QtCore.Qt.gray)
            item.setBackground(0,QtGui.QColor('#FFEFD5'))
            if self.data_dict[label].color is not None:
                item.setForeground(0,QtGui.QColor(self.data_dict[label].color))
        else:
            self.data_dict[label].checked=False
            item.setBackground(0,QtCore.Qt.white)
            #item.setForeground(0,QtCore.Qt.black)
        
            
        self.Replot()
        
        if self.DatasetFilename!="":
            self.setWindowTitle("*"+self.DatasetFilename)
        
    def OnItemDoubleClicked(self,item,column):
        '''
        user double clicked on item
        '''
        label=str(item.text(0))
        if item.internalType=='parameters':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=self.data_dict[labelParent].parameters,\
                                                    datasetname=labelParent,printout=self.printTXT\
                                                    ,referencedata=self.referencedata,backgrounddata=self.backgrounddata)
            self.childSaxs.show()
            return
        if item.internalType=='model':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            self.childmodel=dlgModel.dlgModel(self,labelParent,type="data")
            self.childmodel.show()
            return
        
        '''
        if label=='Scaling parameters':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=self.data_dict[labelParent].parameters,datasetname=labelParent,printout=self.printTXT)
            self.childSaxs.show()
            return
        
        if self.data_dict[label].type=="model":
            self.childmodel=dlgModel.dlgModel(self,label,type="data")
            self.childmodel.show()
        '''
            
        
    
    def Replot(self):
        #print "replot on main"
        l=self.ListOfDatasChecked()
        if len(l)==0:
            return
        #check if data have parents
        for name in l:
            if hasattr(self.data_dict[name], 'parent'):
                if self.data_dict[name].parent!=None:
                    #print "#parent, need to be recalculated"
                    r=self.data_dict[name]._evaluateFromParent(self.data_dict)
                    if r!="" and r is not None:
                        self.printTXT(r)
        
        #   plot the qt frame
        i=0
        if self.plotframe is None:
            self.createPlotframe()
        try:
            self.plotframe.clearData()
        except :
            #PyDeadObjectError
            self.createPlotframe()
            print "DeadObjectError"
        l=[]
        for name in self.data_dict:
            l.append(name)
            l.sort()
        for name in l:
            qexp=self.data_dict[name].q
            iexp=self.data_dict[name].i
            
            if self.data_dict[name].checked:
                #print name, ' is checked'
                if self.data_dict[name].color!=None:
                    col=self.data_dict[name].color#pySaxsColors.getColorRGB(self.data_dict[name].color)
                else:
                    col=self.colors.getColor() #get a new color
                    self.data_dict[name].color=col
                    
                '''print name
                print self.data_dict[name].i
                print self.data_dict[name].q
                print iexp[0]    '''
                if self.data_dict[name].error is not None:
                    #print self.data_dict[name].error
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,error=self.data_dict[name].error,color=col)
                else:
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,color=col)
            i=i+1
        self.plotframe.replot()
        #print "end replotFrame on main"
    
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
    
    def ImportData(self, datafilename,lineskip=0,delimiter='\t',usecols=None,type=None,name=None,errorcol=2,skiprows=0):
        '''
        extract data from file
        no more used (8/2015)
        '''
        if name==None:
            name = filetools.getFilename(datafilename)
        
        #----- file -> data
        #data = importArray(datafilename, lineskip, dataSeparator,cols)
        data=numpy.loadtxt(datafilename, comments='#', skiprows=skiprows, usecols=usecols)# Load data from a text file.
        data=numpy.transpose(numpy.array(data))
        q=data[0]
        i=data[1]
        isnotNan=numpy.where(~numpy.isnan(i))

        q=q[isnotNan]
        i=i[isnotNan]
        
        if len(data)>errorcol:
            err=data[errorcol]
            err=err[isnotNan]
            #print err
        else:
            err=None
        #print data
        #----- data -> dataset
        name=self.cleanString(name)
        self.data_dict[name] = dataset(name,q, i, datafilename,type=type)#[data[0], data[1], datafilename, True]
        if errorcol is not None and err is not None:
            self.data_dict[name].error=err#/data[1]#1/numpy.sqrt(abs(data[1]*data[2]))
        self.data_dict[name].color=self.colors.getColor() #set a random color
            
    def cleanString(self,s):
        """Removes all accents from the string"""
        if isinstance(s,str):
            s = unicode(s,"utf8","replace")
            s=unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')
    
    def printTXT(self,txt="",par=""):
        '''
        print on comment ctrl
        '''
        self.ui.multitxt.append(str(txt)+str(par))
    
    def getCurrentSelectedItem(self):
        '''
        return the current item selected
        if no item is selected return None
        '''
        item=self.ui.treeWidget.currentItem()
        if item is None:
            return None
        if not item.isSelected():
            return None
        label=str(item.text(0))
        if not self.data_dict.has_key(label):
            return None
        return label
    
    def noDataErrorMessage(self):
        QtWidgets.QMessageBox.information(self,"pySAXS", "No datas are selected", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
        
    
    def OnEditFindPeaks(self):
        '''
        find peaks
        '''
        #print 'find peaks'
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        i=self.data_dict[label].i
        q=self.data_dict[label].q
        newq=None
        newi=None
        pp=20
        print "fp"
        dlg=genericFormDialog.genericFormDialog(title='Find peaks',comment='parameters'\
                                                ,names=['Window for scan','Peaks height from the background (in percent)']\
                                                ,values=[pp,100.0])
        dlg.exec_()
        print "exit fp"
        if dlg.result is not None:
            pp,percent=dlg.getResult()
        else :
            return
        '''pp=int(r[0])
        percent=float(r[1])'''
        '''
        #here we use guidata to generate a dialog box
        items = {
         "pp": dataitems.IntItem("Window for scan:",pp),
         "percent" : dataitems.IntItem("Peaks height from the background (in percent)",100.0)
         }
        clz = type("Find peaks", (datatypes.DataSet,), items)
        dlg = clz()
        dlg.edit()  
        pp=dlg.pp
        percent=dlg.percent/100.0
        #end of dialog box    
        '''
        #call find peaks
        founds, newq,newi=DetectPeaks.findPeaks(q,i,pp,percent,self)
        n=len(founds)
        if n>0:
            for res in founds:
                #[height,fwhm,center]
                self.printTXT(  "found peak at q="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1]))
                #--- plot in matplotlib
                self.plotframe.annotate(res[2], res[0],"peak at q="+str(res[2])+" i="+str(res[0])+ "  fwhm="+str(res[1])) 
            self.data_dict[label+" peaks"]=dataset(label+" peaks",numpy.array(newq),numpy.array(newi),comment=label+" peaks",type='calculated',parent=[label])#[data[0], data[1], datafilename, True]
        self.printTXT(str(n)+" peaks found ---------")    
        #self.plotframe.draw()
        self.redrawTheList()
        #self.Replot()

    def OnEditDerivate(self):
        '''
        user want to derivate dataset
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #create a new data set
        newdatasetname=label+' derivate'
        self.data_dict[newdatasetname]=self.data_dict[label]._deepcopy()
        self.data_dict[newdatasetname].name=newdatasetname
        q=self.data_dict[newdatasetname].q
        i=self.data_dict[newdatasetname].i
        tck = interpolate.splrep(q,i,s=0)
        yder = interpolate.splev(q,tck,der=1)
        self.data_dict[newdatasetname].i=yder
        self.data_dict[newdatasetname].parent=[label]
               
        self.redrawTheList()
        self.Replot()
        
    def NotYetImplemented(self):
        QtWidgets.QMessageBox.information(self,"PySAXS","Not yet implemented", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
    
    
        
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
    
    def plugins_list(self, plugins_dirs):
        """ List all python modules in specified plugins folders """
        l=[]
        for path in plugins_dirs.split(os.pathsep):
            for filename in os.listdir(path):
                name, ext = os.path.splitext(filename)
                #print name
                if ext.endswith(".py") and name.startswith('plugin'):
                    if name!='plugin':
                        l.append(name)
        return l
    
    def my_import(self,name):
        m = __import__(name)
        for n in name.split(".")[1:]:
            m = getattr(m, n)
        return m

    def setWorkingDirectory(self,filename):
        self.workingdirectory=os.path.dirname(filename)
        self.pref.set('defaultdirectory', self.workingdirectory)
        
        if self.pref.addRecentFile(filename) : 
            self.pref.save()
            action=self.ui.menuRecents.addAction(filename)#add text in the menu
            item=filename
            action.triggered.connect(partial(self.OnRecentFile,item))
            self.ui.menuFile.addAction(self.ui.menuRecents.menuAction())
    
    def getWorkingDirectory(self):
        return self.workingdirectory
    
    def getListOfDocs(self):
        p=path.dirname(pySAXS.__file__)
        l=filetools.listFiles(p+os.sep+"doc",'*.*')
        return l
    
    def OnOpenDocument(self,name,val):
        '''
        start the default application for the doc file
        '''
        if os.name == "nt":
            os.startfile("%s" % name)
        elif os.name == "posix":
            os.system("/usr/bin/xdg-open %s" % name)
    
    def OnHelpChanges(self):
        '''
        start the changes dlg
        '''
        #self.showSplash()
        file=pySAXS.__path__[0]+ os.sep+"CHANGELOG.txt"
        child=dlgTextView.ViewMessage(file,'Changes '+pySAXS.__version__+pySAXS.__subversion__,parent=self)
        child.exec_()
        
    def OnHelpAbout(self):
        '''
        start the about dlg
        '''
        splash=showSplash()
        file=pySAXS.__path__[0]+ os.sep+"ABOUT.txt"
        child=dlgTextView.ViewMessage(file,'About '+pySAXS.__version__+pySAXS.__subversion__,parent=self)
        child.exec_()
    
    def OnHelpLicense(self):
        '''
        start the about dlg
        '''
        #self.showSplash()
        file=pySAXS.__path__[0]+ os.sep+"LICENSE.txt"
        child=dlgTextView.ViewMessage(file,'License',parent=self)
        child.exec_()

    def OnToolsAbsorption(self):
        '''
        start the absorption tool with XRlib
        '''
        dlg=dlgAbsorption.dlgAbsorption(self,printout=self.printTXT)
        dlg.exec_()
              
    def dragEnterEvent(self, event):
        #self.setText("<drop content>")
        #print "drag"
        #self.ui.listWidget.setBackgroundRole(QtGui.QPalette.Highlight)
        event.acceptProposedAction()
        #self.changed.emit(event.mimeData())
    
    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            filenames=[]
            #print mimeData.urls()
            url=QtCore.QUrl()
            
            for url in mimeData.urls():
                #print url.encodedPath()
                f=str(url.path())[1:]
                filenames.append(f)
                #li=QtGui.QListWidgetItem(f)
                #self.ui.listWidget.addItem(li)
            #print str("\n".join([url.path() for url in mimeData.urls()]))
            self.OnFileOpen(filenames=filenames)

def showSplash():
    splash_file=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'images'+os.sep+'splash.png'
    splash_pix = QtGui.QPixmap(splash_file)
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash_font = splash.font()
    splash_font.setPixelSize(20)
    splash.setFont(splash_font)
    splash.setMask(splash_pix.mask())
    splash.showMessage("version : "+pySAXS.__version__+pySAXS.__subversion__,color=QtCore.Qt.white,alignment=QtCore.Qt.AlignBottom)
    splash.show()
    return splash
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    splash=showSplash()
    app.processEvents()
    
    from pySAXS.guisaxs.qt import mainGuisaxs as mainGuisaxs



    myapp = mainGuisaxs.mainGuisaxs(splashScreen=splash)
    myapp.show()
    
    splash.destroy()
    sys.exit(app.exec_())
