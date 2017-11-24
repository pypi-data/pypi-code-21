from PyQt5 import QtCore, QtGui, uic,QtWidgets
import sys
 
#from pySAXS.guisaxs.qt import dlgQtFAITestui
from pyFAI import azimuthalIntegrator
from numpy import *

import os.path, dircache
from pySAXS.tools import FAIsaxs
#import pyFAI
import pySAXS
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset
import time
import fabio
#from pySAXS.guisaxs.qt import QtImageTool
from pySAXS.tools import FAIsaxs
from pySAXS.guisaxs.qt import QtMatplotlib
from  pySAXS.LS import SAXSparametersXML
from pySAXS import ICON_PATH
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import  QCursor
from PyQt5.QtCore import Qt

def waiting_effects(function):
    def new_function(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        function(self)
        QApplication.restoreOverrideCursor()
    return new_function

class FAIDialogTest(QtWidgets.QDialog):
    def __init__(self, parent=None,parameterfile=None,outputdir=None):
        
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgQtFAITest.ui", self)
        self.pixmapExcl = QtGui.QPixmap(ICON_PATH+'exclamation.png')
        self.pixmapValid = QtGui.QPixmap(ICON_PATH+'tick.png')
        self.parent=parent
        self.workingdirectory=""
        self.printout=None
        self.fai=FAIsaxs.FAIsaxs()
        if parent is None:
            self.myapp = QtMatplotlib.QtMatplotlib()
        if parent is not None:
            #print "icon"
            self.setWindowIcon(parent.windowIcon())
            self.printout=parent.printTXT
            self.workingdirectory=parent.workingdirectory
            
        self.im=None#image
        self.imName=None
        self.mad=None#mask
        self.madName=None
        
        self.ui.show()
        #self.ui.setupUi(self)
        self.setWindowTitle('Radial averaging test tool for SAXS')
        #QtCore.QObject.connect(self.ui.Button_paramFile, QtCore.SIGNAL("clicked()"),self.OnClickButton_paramFile)
        self.ui.Button_paramFile.clicked.connect(self.OnClickButton_paramFile)
        #QtCore.QObject.connect(self.ui.Button_maskFilename, QtCore.SIGNAL("clicked()"),self.OnClickButton_maskFilename)
        self.ui.Button_maskFilename.clicked.connect(self.OnClickButton_maskFilename)
        #QtCore.QObject.connect(self.ui.Button_SampleName, QtCore.SIGNAL("clicked()"),self.OnClickButton_SampleName)
        self.ui.Button_SampleName.clicked.connect(self.OnClickButton_SampleName)
        #QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        self.ui.buttonBox.clicked.connect(self.click)
        
        self.ui.progressBar.setValue(0)
        
        self.ui.labelMask.setPixmap(self.pixmapExcl)
        self.ui.labelSample.setPixmap(self.pixmapExcl)
        
        self.parameterfile=parameterfile
        if parameterfile is not None:
            self.ui.txt_paramfile.setText(parameterfile)
            self.importXML(parameterfile)
            
        
    def OnClickButton_paramFile(self):
        fd = QtWidgets.QFileDialog(self)
        filename,truc=fd.getOpenFileName(directory=self.workingdirectory,filter="XML files (*.xml);;Poni files(*.poni)")
        if str(filename)=="":
            return
        try:
            self.workingdirectory=os.path.dirname(str(filename))
            self.ui.txt_paramfile.setText(str(filename))
            ext=filetools.getExtension(filename)
            if ext=='xml':
                    self.importXML(filename)
            elif ext=='poni':
                    self.importPONI(filename)
        except:
            print "error"
        
            
        
    def importXML(self,filename=None):
        if filename is not None:
                #print self.paramFile
                self.fai.importIJxml(filename)
                self.ui.edit_centery.setText(str(self.fai._xmldirectory['user.centery']))
                self.ui.edit_centerx.setText(str(self.fai._xmldirectory['user.centerx']))
                self.ui.edit_dd.setText(str(self.fai._xmldirectory['user.DetectorDistance']))#6*10 #m->mm
                self.ui.edit_tilt.setText(str(90-self.fai._xmldirectory['user.alpha_deg']))
                self.ui.edit_pixelsize.setText(str(self.fai._xmldirectory['user.PixelSize']))#*1e4 #m->micron
                self.ui.edit_wavelength.setText(str(self.fai._xmldirectory['user.wavelength']))
                self.ui.txt_MaskFilename.setText(str(self.fai._xmldirectory['user.MaskImageName']))
                self.ui.edit_qdiv.setText(str(self.fai._xmldirectory['user.QDiv']))
                self.loadMask()
    
    def importPONI(self,filename=None):
        if filename is not None:
            from pyFAI import geometry
            g=geometry.Geometry()
            g.load(filename)
            out=g.getFit2D()
            self.ui.edit_centery.setText(str(out['centerY']))
            self.ui.edit_centerx.setText(str(out['centerX']))
            self.ui.edit_dd.setText(str(out['directDist']/10))
            self.ui.edit_tilt.setText(str(out['tilt']))
            self.ui.edit_pixelsize.setText(str(out['pixelX']))
            self.ui.edit_wavelength.setText(str(g.get_wavelength()*1e9))
            #self.prepare()
    
    def prepare(self):
        #print 'prepare'
        #self.ui.progressBar.setValue(10)
        self.dd=float(self.ui.edit_dd.text())
        self.centerx=float(self.ui.edit_centerx.text())
        self.centery=float(self.ui.edit_centery.text())
        self.tilt=float(self.ui.edit_tilt.text())
        self.qdiv=float(self.ui.edit_qdiv.text())
        self.pixelsize=float(self.ui.edit_pixelsize.text()) #m->micron
        self.wavelength=float(self.ui.edit_wavelength.text())
        self.fai.set_wavelength(self.wavelength*1e-9)
        self.fai.setFit2D(self.dd*10,centerX=self.centerx,centerY=self.centery,tilt=self.tilt,\
                          pixelX=self.pixelsize*1e4,pixelY=self.pixelsize*1e4)
        #maskname=str(self.ui.txt_MaskFilename.text())
        #self.ui.progressBar.setValue(20)
        #self.loadMask()
        #print self.fai.getMaskFilename()
        #print self.mad    
        
            
    @ waiting_effects
    def loadMask(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        # do lengthy process
        QApplication.restoreOverrideCursor()
        maskname=str(self.ui.txt_MaskFilename.text())
        if not filetools.fileExist(maskname):
            self.ui.labelMask.setPixmap(self.pixmapExcl)
            return 
        ma=fabio.open(maskname)
        mad=ma.data
        self.mad=mad.astype(bool)
        self.ui.labelMask.setPixmap(self.pixmapValid)
        self.madName=maskname
        self.printTXT(maskname+' opened')
        
    
    def OnClickButton_maskFilename(self):
        fd = QtWidgets.QFileDialog(self)
        filename,truc=fd.getOpenFileName(directory=self.workingdirectory)
        self.workingdirectory=os.path.dirname(str(filename))
        self.ui.txt_MaskFilename.setText(str(filename))
        self.loadMask()
    
    def OnClickButton_SampleName(self):
        fd = QtWidgets.QFileDialog(self)
        filename,truc=fd.getOpenFileName(directory=self.workingdirectory)
        #print list(filename)
        self.workingdirectory=os.path.dirname(str(filename))
        '''
        ll=[]
        for i in filename:
            ll.append(str(i))
        filename=str(ll)
        '''
        self.ui.txt_SampleName.setText(str(filename))
        self.loadSample()
    
    @ waiting_effects
    def loadSample(self):
        #QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        imageFilename=str(self.ui.txt_SampleName.text())
        try:
            self.im=fabio.open(imageFilename)
            self.ui.labelSample.setPixmap(self.pixmapValid)
            self.imName=imageFilename
            self.printTXT(imageFilename+' opened')
        except:
            print 'error in opening ',imageFilename 
            self.im=None
            self.ui.labelSample.setPixmap(self.pixmapExcl)
        # do lengthy process
        #QApplication.restoreOverrideCursor()
        
            
    def OnClickRADButton(self):
        self.ui.progressBar.setValue(00)
        if self.imName<>str(self.ui.txt_SampleName.text()):
            self.loadSample()
        self.ui.progressBar.setValue(20)
        if self.madName<>str(self.ui.txt_MaskFilename.text()):
            self.loadMask()
        self.ui.progressBar.setValue(40)
        self.prepare()
        imageFilename=str(self.ui.txt_SampleName.text())
        name=filetools.getFilename(filetools.getFilenameOnly(imageFilename))
        newname=filetools.getFilenameOnly(imageFilename)+".rgr"
        #print newname
        if self.im is not None:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.ui.progressBar.setValue(50)
            im,q,i,s,newname=self.fai.integratePySaxs(imageFilename, self.mad, self.printTXT)#, outputdir)
            '''try:
                SAXSparametersXML.saveImageHeader(self.im.header,imageFilename)
                self.printTXT("Header file saved")
            except :
                self.printTXT("Error on Header file saving")
            qtemp,itemp,stemp=self.fai.integrate1d(self.im.data,self.qdiv,filename=newname,mask=self.mad,error_model="poisson")
            
            '''
            self.ui.progressBar.setValue(100)
            if im is None:
                return
            if self.parent is None:
                self.myapp.show()
                self.myapp.addData(qtemp, itemp, label=imageFilename,error=stemp)
                self.myapp.replot()
            else:
                myname=filetools.getFilename(imageFilename)
                if im.header.has_key('Comment'):
                        comment=im.header['Comment']
                        if comment !='' :
                            myname+="-"+comment
                self.parent.data_dict[myname]=dataset.dataset(myname,q,i, imageFilename,error=s,type='saxs',image="Image")
                self.parent.redrawTheList()
                self.parent.Replot()        
            
            self.fai.saveGeometryRPT(imageFilename, self.madName, self.qdiv)
            QApplication.restoreOverrideCursor()
        self.ui.progressBar.setValue(0)
    
    
        
    
    def click(self,obj=None):
        #save the preferences
        if self.parent is not None:
                #self.parent.pref.set("outputdir",section="pyFAI",value=str(self.ui.outputDirTxt.text()))
                self.parent.pref.set("parameterfile",section="pyFAI",value=str(self.ui.txt_paramfile.text()))
                self.parent.pref.save()
        name=obj.text()
        #print name
        if name=='Close':
            self.close()
        elif name=='Apply':
            self.OnClickRADButton()
        elif name=='Save':
            self.prepare()
            fd = QtWidgets.QFileDialog(self)
            #get the filenames, and the filter
            wc = "dataset  xml file (*.xml)"
            filename,truc=fd.getSaveFileName (filter=wc,directory=os.path.dirname(str(self.ui.txt_paramfile.text())))
            if filename:
                filename=str(filename)
                self.fai.saveGeometryXML(filename,self.centerx,self.centery,self.dd,90+self.tilt,\
                                         self.pixelsize,self.wavelength,str(self.ui.txt_MaskFilename.text()),self.qdiv)
    
    '''def reject(self):
        self.destroy()
    '''
    
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
 
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = FAIDialogTest()
    myapp.show()
    sys.exit(app.exec_())
