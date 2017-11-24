from PyQt5 import QtCore, QtGui, QtWidgets, uic

#from PyQt4.Qt import QString
from fileinput import filename
from pyFAI import azimuthalIntegrator
from pySAXS.guisaxs import dataset
from pySAXS.guisaxs.qt import preferences
from pySAXS.guisaxs.qt import QtMatplotlib
from matplotlib import pyplot       # Load matplotlib
import matplotlib.colors as colors
from pySAXS.tools import FAIsaxs
from pySAXS.tools import filetools
import os
import sys


def my_excepthook(type, value, tback):
    # log the exception here
    #print value
    #print tback
    # then call the default handler
    sys.__excepthook__(type, value, tback)

sys.excepthook = my_excepthook

#from reportlab.graphics.widgets.table import TableWidget
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
#from spyderlib.widgets.externalshell import namespacebrowser
from time import *
import fabio
import numpy
import os.path, dircache
import pyFAI
import sys
import threading
import glob
import fnmatch

import pySAXS
from  pySAXS.LS import SAXSparametersXML
from pySAXS.guisaxs.qt import dlgQtFAITest



ICON_PATH=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'images'+os.sep 
OPTION_XEUSS=True
FROM_EDF_HEADER=['Comment','x','count_time','pilroi0','pilai1']
 

class SurveyorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, parameterfile=None, outputdir=None):
        QtWidgets.QWidget.__init__(self, parent)
        #self.ui = dlgSurveyorui.Ui_surveyorDialog()
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgSurveyor.ui", self)#
        self.setWindowTitle('Continuous Radial averaging tool for pySAXS')
        if parent is not None:
            # print "icon"
            self.setWindowIcon(parent.windowIcon())
        
        plt=self.ui.matplotlibwidget
        
        self.plt=self.ui.matplotlibwidget.figure
        self.plt.patch.set_facecolor('White')
        self.canvas = FigureCanvas(self.plt)
        #self.axes = self.plt.gca()
        self.axes = self.plt.add_subplot(111)#subplots()
        self.clbar=None#(imgplot)
        self.plt.tight_layout()
        
        #self.ui.setupUi(self)
        self.ui.paramFileButton.clicked.connect(self.OnClickparamFileButton)
        self.ui.changeDirButton.clicked.connect(self.OnClickchangeDirButton)
        #QtCore.QObject.connect(self.ui.STARTButton, QtCore.SIGNAL("clicked()"), self.OnClickSTARTButton)
        #QtCore.QObject.connect(self.ui.STOPButton, QtCore.SIGNAL("clicked()"), self.OnClickSTOPButton)
        self.ui.plotChkBox.clicked.connect(self.OnClickPlotCheckBox)
        self.ui.btnExtUpdate.clicked.connect(self.updateListInit)
        self.ui.tableWidget.cellClicked[int, int].connect(self.cellClicked)
        self.ui.tableWidget.cellDoubleClicked[int, int].connect(self.cellDoubleClicked)
        self.ui.btnDisplaySelected.clicked.connect(self.btnDisplayClicked)
        self.ui.btnZApply.clicked.connect(self.btnZApplyClicked)
        self.ui.btnReset.clicked.connect(self.btnZResetClicked)
        self.ui.btnDisplayAV.clicked.connect(self.btnDisplayAVClicked)
        self.ui.paramViewButton.clicked.connect(self.OnClickparamViewButton)
        self.ui.navi_toolbar = NavigationToolbar(self.ui.matplotlibwidget, self)
        self.ui.verticalLayout_2.insertWidget(0,self.ui.navi_toolbar)#verticalLayout_2
        l=self.ui.navi_toolbar.actions()
        #remove the Pan tool
        l=self.ui.navi_toolbar.actions()
        for i in l:
            #print i.text()
            if i.text()=='Pan':
                panAction=i
            if i.text()=='Customize':
                customizeAction=i
            if i.text()=='Subplots':
                subplotAction=i
            
        #self.ui.navi_toolbar.removeAction(panAction)
        self.ui.navi_toolbar.removeAction(customizeAction)
        self.ui.navi_toolbar.removeAction(subplotAction)
        #--Autoscale
        self.AutoscaleAction= QtWidgets.QAction('Autoscale', self)
        self.AutoscaleAction.triggered.connect(self.OnAutoscale)
        self.ui.navi_toolbar.addAction(self.AutoscaleAction)
        #-- fix scale
        self.FixScaleAction= QtWidgets.QAction(QtGui.QIcon(ICON_PATH+'magnet.png'),'Fix Scale', self)
        self.FixScaleAction.setCheckable(True)
        self.FixScaleAction.setChecked(False)
        self.FixScaleAction.triggered.connect(self.OnButtonFixScale)
        self.ui.navi_toolbar.addAction(self.FixScaleAction)
        
        self.SelectedFile=None
        self.ui.labelSelectedFIle.setText("")
        self.ui.btnDisplaySelected.setEnabled(False)
        self.ui.btnDisplayAV.setEnabled(False)
        self.ui.radioButton_lin.setChecked(True)
        self.ui.radioButton_lin.toggled.connect(lambda:self.btnStateLinLog(self.radioButton_lin))
        #self.ui.radioButton_log.toggled.connect(lambda:self.btnStateLinLog(self.radioButton_log))
        self.DISPLAY_LOG=False
        
        self.ui.chkDisplayBeam.clicked.connect(self.OnClickDisplayBeam)
        self.ui.btnGetBeamXY.clicked.connect(self.OnClickGetBeamXY)
        self.ui.btnBeamApply.clicked.connect(self.OnClickButtonBeam)
        '''self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0,1)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        '''
        self.parent = parent
        self.plotapp= None
        self.printout = None
        self.whereZ=False
        self.workingdirectory = None
        self.parameterfile=parameterfile
        try:
            if self.parameterfile is not None and self.parameterfile!="":
                self.ui.paramTxt.setText(str(parameterfile))
        except:
            pass
            
        self.fai=None
            
         #-- get preferences
        self.pref=preferences.prefs()
        
        if parent is not None:
            self.printout = parent.printTXT
            self.workingdirectory = parent.workingdirectory
            self.pref=self.parent.pref
            '''print "import pref"
            print self.pref
            print self.pref.getName()'''
            try:
                if self.pref.fileExist():
                    self.pref.read()
                    #print "file exist"
                    dr=self.pref.get('defaultdirectory',section="guisaxs qt")
                    #print "dr :",dr
                    if dr is not None:
                        self.workingdirectory=dr
                        #print 'set wd',dr
                        self.ui.DirTxt.setText(str(self.workingdirectory))
                    pf=self.pref.get('parameterfile',section="pyFAI")
                    
                    if pf is not None:
                        self.parameterfile=pf
                        self.ui.paramTxt.setText(str(self.parameterfile))
                    
                    ext=self.pref.get('fileextension',section="pyFAI")
                    if ext is not None:
                        self.ui.extensionTxt.setText(ext)
                    
                
                else:
                    self.pref.save()
            except:
                print "couldnt reach working directory "
                return
            
            
        else :
            self.workingdirectory = "Y:/2017/2017-08-24-OT" #for debugging
            self.ui.DirTxt.setText(self.workingdirectory)   #for debugging
            
        print self.workingdirectory
        self.imageToolWindow = None
        self.updateListInit()
        self.fp = str(self.ui.DirTxt.text())
        '''self.qfsw = QtCore.QFileSystemWatcher()
        self.fp = str(self.ui.DirTxt.text())
        if self.fp!='':
            self.qfsw.addPath(self.fp)
            QtCore.QObject.connect(self.qfsw,QtCore.SIGNAL("directoryChanged(QString)"),self.onFileSystemChanged)
            #self.qfsw.directoryChanged.connect(self.updateListInit)
        '''
        self._fileSysWatcher    = QtCore.QFileSystemWatcher()
        if self.fp!='':
            if os.path.isdir(self.fp):
                self._fileSysWatcher.addPath(self.fp)
                self._fileSysWatcher.directoryChanged.connect(self.slotDirChanged)
                
        
        
        
    @QtCore.pyqtSlot("QString")   
    def slotDirChanged(self, path):
        print path, " changed !"
        self.updateListInit()      
        
    
    def OnClickparamFileButton(self):
        '''
        Allow to select a parameter file
        '''
        fd = QtWidgets.QFileDialog(self)
        filename = fd.getOpenFileName(directory=self.workingdirectory)[0]
        #self.workingdirectory = filename
        # print filename
        self.ui.paramTxt.setText(filename)
        # self.ui.editor_window.setText(plik)
        self.radialPrepare()

    def OnClickSTARTButton(self):
        '''
        Used when start button is clicked
        '''
        print "start"
        self.ui.progressBar.setRange(0,0)
        #print "start2"
        self.radialPrepare()
        #self.ui.progressBar.setValue(100)
        
        self.ui.STOPButton.setEnabled(True)
        self.ui.STARTButton.setDisabled(True)
        if self.ui.refreshTimeTxt.text() == '':
            t = 30
        else :
            t = float(self.ui.refreshTimeTxt.text())    
        #print(time)
        self.t = Intervallometre(t, self.updateList, self)
        self.t.start()
        
    def OnClickSTOPButton(self):
        '''
        Used when stop button is clicked
        '''
        print "stop"
        #self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0,1)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        self.t.stop()
        
    def OnClickchangeDirButton(self):
        '''
        Allow to select a directory
        '''
        #QFileDialog
        #fd = QtWidgets.QFileDialog(self, directory=self.workingdirectory)
        #fd.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dir=QtWidgets.QFileDialog.getExistingDirectory(directory=self.workingdirectory)
        #if fd.exec_() == 1:
        #print fd.selectedFiles()
        #dir = str(fd.selectedFiles().first())
        #dir = str(fd.selectedFiles()[0])
        print dir
        if dir=='':
            return
        if not(os.path.isdir(dir)):
            return
        # dir=fd.getOpenFileName()
        self.ui.DirTxt.setText(dir)
        self.workingdirectory = dir
        self.updateListInit()
        
        try:
            self.pref.set('defaultdirectory', self.workingdirectory,section="guisaxs qt")
            self.pref.save()
        except:
            pass
        '''    
        l=self.qfsw.directories()
        print "previous watched directories :",list(l)
        self.qfsw.removePaths(l)
        self.qfsw.addPath(dir)
        l=self.qfsw.directories()
        print "Now watched directories :",list(l)
        '''
        print "la"
        l=self._fileSysWatcher.directories()
        print "previous watched directories :",list(l)
        if len(l)>0:
            self._fileSysWatcher.removePaths(l)
        self._fileSysWatcher.addPath(dir)
        l=self._fileSysWatcher.directories()
        print "now watched directories :",list(l)
            
    def cellClicked(self,row,col):
        self.SelectedFile=str(self.ui.tableWidget.item(row,0).text())
        self.ui.labelSelectedFIle.setText(self.workingdirectory+os.sep+self.SelectedFile)
        #print self.workingdirectory+os.sep+self.SelectedFile
        self.ui.btnDisplaySelected.setEnabled(True)
        self.ui.btnDisplayAV.setEnabled(True)
        
    def cellDoubleClicked(self,row,col):
        self.SelectedFile=str(self.ui.tableWidget.item(row,0).text())
        self.ui.labelSelectedFIle.setText(self.workingdirectory+os.sep+self.SelectedFile)
        #print self.workingdirectory+os.sep+self.SelectedFile
        self.ui.btnDisplaySelected.setEnabled(True)
        self.ui.btnDisplayAV.setEnabled(True)
        self.btnDisplayClicked()
        
    def btnDisplayClicked(self):
        '''
        display the image
        '''
        self.axes.cla() 
        if self.SelectedFile is None:
            return
        try:
            self.img = fabio.open(self.workingdirectory+os.sep+self.SelectedFile) # Open image file
        except:
            print "pySAXS : unable to open imagefile : "+self.workingdirectory+os.sep+self.SelectedFile
            #QtWidgets.QMessageBox.information(self,"pySAXS", "unable to open imagefile : "+self.workingdirectory+os.sep+self.SelectedFile, buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return
        
        
        #pyplot.ion()
        
        
        #ax.imshow(img)
        #try:
        #    D=numpy.log(self.img.data)
        #except:
        #    D=self.img.data
        D=self.img.data
        if self.whereZ:
            zmin=float(self.ui.edtZmin.text())
            zmax=float(self.ui.edtZmax.text())
            D=numpy.where(D<=zmin,zmin,D)
            D=numpy.where(D>zmax,zmax,D)
        else:
            self.ui.edtZmin.setText(str(D.min()))
            self.ui.edtZmax.setText(str(D.max()))
        norm=colors.LogNorm(vmin=D.min(), vmax=D.max())
        if self.DISPLAY_LOG:
            zmin=float(self.ui.edtZmin.text())
            if zmin<=0:
                zmin=1
                self.ui.edtZmin.setText("1")
            zmax=float(self.ui.edtZmax.text())
            D=numpy.where(D<=zmin,zmin,D)
            D=numpy.where(D>zmax,zmax,D)
            norm=colors.LogNorm(vmin=D.min(), vmax=D.max())
            imgplot=self.axes.imshow(D,cmap="jet",norm=norm)
            #print "mode log"#,norm=colors.LogNorm(vmin=D.min(), vmax=D.max()))            # Display as an image  norm=colors.LogNorm(vmin=Z1.min(), vmax=Z1.max()),
        else:
            #imgplot=plt.axes.imshow(D,cmap="jet")#,norm=norm)
            imgplot=self.axes.imshow(D,cmap="jet")#,norm=norm)
        #imgplot.set_cmap('nipy_spectral')
        #--- fix scale
        if self.FixScaleAction.isChecked():
            #axes limits should have been memorized
            self.axes.set_xlim((self.xlim_min,self.xlim_max))
            self.axes.set_ylim((self.ylim_min,self.ylim_max))
        if self.clbar is None :
            self.clbar=self.plt.colorbar(imgplot,shrink=0.5)
        else:
            try:
                self.clbar.remove()
            except:
                pass
            self.clbar=self.plt.colorbar(imgplot,shrink=0.5)
        #display the beam (or not)
        if self.ui.chkDisplayBeam.isChecked():
            #draw a cross
            #try:#if text is not float
            BeamX=float(self.ui.edtBeamX.text())
            BeamY=float(self.ui.edtBeamY.text())
            xmax,ymax=numpy.shape(D)
            #print xmax, ymax
            #print plt.axes
            #except:
            #print "text is not float"
            #BeamX=0.0
            #BeamY=0.0
        
            x1, y1 = [BeamX, 0], [BeamX, ymax] #vertical
            x2, y2 = [0,BeamY], [xmax, BeamY]
            #self.axes.plot(x1, y1, x2, y2, marker = 'o')
            
            # Create a Rectangle patch
            rect = patches.Rectangle((0, 0),BeamX, BeamY,linewidth=1,edgecolor='r',facecolor='none')
            rect2 = patches.Rectangle((BeamX, BeamY),xmax, ymax,linewidth=1,edgecolor='r',facecolor='none')

            # Add the patch to the Axes
            self.axes.add_patch(rect)
            self.axes.add_patch(rect2)
            
        # Display the image
                    
        self.ui.matplotlibwidget.draw()
        '''except:
            pass'''
        #pyplot.show()                       # Show GUI window
    
    def btnDisplayAVClicked(self):
        if self.SelectedFile is None:
            return
        self.radialAverage(self.workingdirectory+os.sep+self.SelectedFile)
        
    def OnAutoscale(self):
        print 'autoscale'
        sh=self.img.data.shape
        plt=self.ui.matplotlibwidget
        plt.axes.set_ylim((sh[0],0))
        plt.axes.set_xlim((0,sh[1]))
        self.xlim_min,self.xlim_max=plt.axes.get_xlim()
        self.ylim_min,self.ylim_max=plt.axes.get_ylim()
        plt.draw()
    
    def OnButtonFixScale(self):
        print "OnButtonFixScale"
        #memorize the current scale"
        plt=self.ui.matplotlibwidget
        self.xlim_min,self.xlim_max=plt.axes.get_xlim()
        self.ylim_min,self.ylim_max=plt.axes.get_ylim()
        #print self.xlim_min,self.xlim_max," - ",self.ylim_min,self.ylim_max
            
    def btnZApplyClicked(self):
        try:
            self.zmin=float(self.ui.edtZmin.text())
            zmax=float(self.ui.edtZmax.text())
            self.whereZ=True
            self.btnDisplayClicked()
            #print zmin, zmax
        except:
            pass
    def btnZResetClicked(self):
        self.whereZ=False
        self.btnDisplayClicked()
    
    def btnStateLinLog(self,b):
        print "toggled"
        if b.text() == "lin":
            if b.isChecked() == True:
                self.DISPLAY_LOG=False
            else:
                self.DISPLAY_LOG=True
                #print "zmin text :",self.ui.edtZmin.text()
                if float(self.ui.edtZmin.text())<=0:
                    self.ui.edtZmin.setText("1")
                    
        self.whereZ=True
        self.btnDisplayClicked()
                
        '''if b.text() == "log":
            if b.isChecked() == True:
                self.DISPLAY_LOG=True
                if float(self.ui.edtZmin.text())<=0:
                    self.ui.edtZmin.setText("1")
            else:
                self.DISPLAY_LOG=False'''
            #self.btnDisplayClicked()
        
    def OnClickGetBeamXY(self):
        '''
        try to get Beam X Y from parameter file
        '''
        if self.ui.paramTxt.text()=="":
            QtWidgets.QMessageBox.information(self,"pySAXS", "Parameter file is not specified", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return
        
        filename = self.ui.paramTxt.text()
        if not os.path.exists(filename):
            self.printTXT(filename + ' does not exist')
            QtWidgets.QMessageBox.information(self,"pySAXS", str(filename) + " does not exist", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return
        if self.fai is None:
            self.radialPrepare()
        self.fai.setGeometry(filename)
        self.ui.edtBeamY.setText(str(self.fai._xmldirectory['user.centery']))
        self.ui.edtBeamX.setText(str(self.fai._xmldirectory['user.centerx']))
        #display beam
        self.OnClickButtonBeam()
    
    def OnClickButtonBeam(self):
        self.ui.chkDisplayBeam.setChecked(True)
        #--simply redraw the image
        self.btnDisplayClicked()
        
    def updateList(self):
        '''
        Update the list
        '''
        print "refresh"
        #print '-UPDATE LIST'
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        #print self.fp
        listoffile = self.getList(self.fp, self.ext)
        #print listoffile
        files=sorted(listoffile,reverse=True)
        #print files
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)
        i = 0
        for name in files:
            self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)
            if not listoffile[name][1] :
                try :
                    self.radialAverage(self.fp + os.sep+ name)
                except:
                    print "unable to average on file :",name
                
            i += 1
        #self.timer()
        self.listoffileVerif = glob.glob(os.path.join(self.fp, self.ext))#filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile
        if len(listoffile)>0:
            self.cellClicked(0,0)
            self.btnDisplayClicked()
        else:
            self.SelectedFile=None
            self.ui.labelSelectedFIle.setText("")
            self.ui.btnDisplaySelected.setEnabled(False)
            self.ui.btnDisplayAV.setEnabled(False)
        #print "list updated"

    def updateListInit(self):
        '''
        Update the initial List WITHOUT treatment 
        '''
        print 'generate list'
        
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        listoffile = self.getList(self.fp, self.ext)
        files=sorted(listoffile,reverse=True)
        #print listoffile
        
        
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        if OPTION_XEUSS:
            headerNames+=FROM_EDF_HEADER
        self.ui.tableWidget.setColumnCount(len(headerNames))
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)
        '''for n in range(len(FROM_EDF_HEADER)):
             self.ui.tableWidget.setColumnWidth(4+n,50)'''
        i = 0
        for name in files:
            self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)          
            if OPTION_XEUSS:
                #display information from edf
                infos=self.getInformationFromEDFXeuss(name)
                for j in range(len(infos)):
                    self.ui.tableWidget.setItem(i, 4+j, QtWidgets.QTableWidgetItem(infos[j]))
            i += 1
        self.listoffileVerif = glob.glob(os.path.join(self.fp, self.ext))#filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile
        #display first
        if len(listoffile)>0:
            if self.ui.chkAutomaticDisplayFirst.isChecked():
                #print 'display first'
                self.cellClicked(0,0)
                self.btnDisplayClicked()
            
            if self.ui.chkAutomaticAV.isChecked():
                self.cellClicked(0,0)
                self.btnDisplayClicked()
                self.btnDisplayAVClicked()
        else:
            self.SelectedFile=None
            self.ui.labelSelectedFIle.setText("")
            self.ui.btnDisplaySelected.setEnabled(False)
            self.ui.btnDisplayAV.setEnabled(False)
    
    def getList(self, fp, ext):
        #print "getlist, ",fp,ext
        #print os.path.join(self.fp, self.ext)
        #listoffile = glob.glob(os.path.abspath(self.fp)+os.sep+self.ext)#filetools.listFiles(fp, ext)
        listoffile=[]
        if self.fp=='':
            return []
        for file in os.listdir(self.fp):
            if fnmatch.fnmatch(file, self.ext):
                #print(file)
                listoffile.append(os.path.abspath(self.fp)+os.sep+file)
        
        #print "end glob : ",listoffile
        files = {}
        for name in listoffile:
            fich = filetools.getFilename(name)
            dt = filetools.getModifiedDate(name)
            newfn = filetools.getFilenameOnly(name)
            ficTiff = newfn
            newfn += '.rgr'
            # print newfn
            if filetools.fileExist(newfn) :
                proc = True
                new = False
            else:              
                proc = False
                new = True
            files[fich] = [dt, proc, new]    
        #print "end of getlist: ",files
        return files
    
    
    def printTXT(self, txt="", par=""):
        '''
        for printing messages
        '''
        if self.printout == None:
            print(str(txt) + str(par))
        else:
            self.printout(txt, par)

    def radialPrepare(self):
        self.fai = FAIsaxs.FAIsaxs()
        filename = self.ui.paramTxt.text()
        if not os.path.exists(filename):
            self.printTXT(filename + ' does not exist')
            return
        outputdir = self.ui.DirTxt.text()
        self.fai.setGeometry(filename)
        '''self.qDiv = self.fai.getProperty('user.qDiv')
        if self.qDiv is None:
            self.qDiv = 1000'''
        self.mad = self.fai.getIJMask()
        maskfilename = self.fai.getMaskFilename()
  
    def radialAverage(self, imageFilename):
        if self.fai is None :
            self.radialPrepare()
        t0=time()
        '''im = fabio.open(imageFilename)
        #try:
        SAXSparametersXML.saveImageHeader(im.header,imageFilename)
        self.printTXT("Header file saved")
        #except :
        #        self.printTXT("Error on Header file saving")
        newname = filetools.getFilenameOnly(imageFilename) + ".rgr"
        qtemp, itemp, stemp = self.fai.integrate1d(im.data, self.qDiv, filename=newname, mask=self.mad, error_model="poisson")
        print time()-t0, " s"
        '''
        im,q,i,s,newname=self.fai.integratePySaxs(imageFilename, self.mad, self.printTXT)#, self.qDiv)
        if im is None:
            return
        try:
            
            self.OnClickPlotCheckBox()
            if self.parent is None:
                self.plotapp.addData(q, i, label=imageFilename)#,error=s)
                self.plotapp.replot()
            else:
                myname=filetools.getFilename(imageFilename)
                if im.header.has_key('Comment'):
                        comment=im.header['Comment']
                        if comment !='' :
                            myname+="-"+comment
                self.parent.data_dict[myname]=dataset.dataset(myname,q,i, imageFilename,error=s,type='saxs',image="Image")
                self.parent.redrawTheList()
                if self.ui.plotChkBox.isChecked():
                    self.parent.Replot()        
            
        except:
            print "Error plot"
        self.fai.saveGeometry(imageFilename)#save rpt
        
    def OnClickPlotCheckBox(self):
        if self.parent is None:
            if self.ui.plotChkBox.isChecked():
                self.plotapp=QtMatplotlib.QtMatplotlib()
                self.plotapp.show()
            else:
                self.plotapp.close()
    
    def OnClickDisplayBeam(self):
        '''
        user clicked on display beam
        '''
        #print "chk"
        #--simply redraw the image
        self.btnDisplayClicked()

    def OnClickparamViewButton(self):
        filename=str(self.ui.paramTxt.text())
        if filename is not None and filename <>'':
            self.dlgFAI=dlgQtFAITest.FAIDialogTest(self.parent,filename,None)
            self.dlgFAI.show()
            
    def getInformationFromEDFXeuss(self,filename):
        d=self.ui.DirTxt.text()
        filename=self.workingdirectory+os.sep+filename
        try:
            im=fabio.open(filename)
        except:
            #file not exist
            return []
        l=[]
        for n in FROM_EDF_HEADER:
            try:
               l.append(str(im.header[n])) 
            except:
                l.append("?")
        return l
    
    def closeEvent(self, event):
        '''
        when window is closed
        '''
        l=self._fileSysWatcher.directories()
        #print "previous watched directories :",list(l)
        self._fileSysWatcher.removePaths(l)
        
        #print "close"
        #save the preferences
        if self.parent is not None:
                #self.parent.pref.set("outputdir",section="pyFAI",value=str(self.ui.outputDirTxt.text()))
                self.pref.set("parameterfile",section="pyFAI",value=str(self.ui.paramTxt.text()))
                self.pref.set('defaultdirectory',section="guisaxs qt",value=str(self.ui.DirTxt.text()))
                self.pref.set('fileextension',section="pyFAI",value=str(self.ui.extensionTxt.text()))
                self.pref.save()
        try:
            self.t.stop()
            
        except:
            pass

class Intervallometre(threading.Thread):
 
    def __init__(self, duree, fonction, parent=None):
        threading.Thread.__init__(self)
        self.duree = duree
        self.fonction = fonction
        self.parent = parent
        self.encore = True
        
    def run(self):
        print 'start'
        while self.encore:
            #self.fonction()
            self.parent.updateList()
            self.slip(self.duree)
            '''if self.parent is not None:
                try:
                    val=self.parent.ui.progressBar.value()
                    if val+10>self.parent.ui.progressBar.maximum():
                        self.parent.ui.progressBar.setValue(0)
                    else:
                        self.parent.ui.progressBar.setValue(val+10)
                except:
                    pass'''
    def stop(self):
        self.encore = False
        
    def slip(self,t,intt=1.0):
        if t<intt:
            sleep(t)
            return
        t0=time()
        #print t0,time()-t0
        #self.parent.ui.progressBar.setMaximum(t)
        while t-(time()-t0)>intt:
            print "+",
            #self.parent.ui.progressBar.setValue(t-(time()-t0))
            if self.encore:
                sleep(intt)
                ''''if self.parent is not None:
                    try:
                        val=self.parent.ui.progressBar.value()
                        if val+10>self.parent.ui.progressBar.maximum():
                            self.parent.ui.progressBar.setValue(0)
                        else:
                            self.parent.ui.progressBar.setValue(val+10)
                    except:
                        pass'''
            else:
                return
        sleep(t-(time()-t0))
        
        
        
        
if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  myapp = SurveyorDialog()
  myapp.show()
  sys.exit(app.exec_())
  
