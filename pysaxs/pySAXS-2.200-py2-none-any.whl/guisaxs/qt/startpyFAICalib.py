from fileinput import filename
import os
import os
import sys
#from guidata import qt
from PyQt4 import QtGui, QtCore, uic
#from PyQt4.Qt import QString
import fabio
#from guidata.dataset.dataitems import FileOpenItem
import pyFAI, pyFAI.calibrant, pyFAI.detectors
from pyFAI.calibration import calib
import pySAXS
from pySAXS.tools import filetools

#from pySAXS.guisaxs.qt import startpyFAICalibui
class CalibStart(QtGui.QDialog):
    def __init__(self, parent=None):
       
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"startpyFAICalib.ui", self)
        #self.setWindowTitle('CalibStart')
        if parent is not None:
            # print "icon"
            self.setWindowIcon(parent.windowIcon())
        
        #self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.STARTButton, QtCore.SIGNAL("clicked()"), self.OnClickStartButton)
        QtCore.QObject.connect(self.ui.fileButton, QtCore.SIGNAL("clicked()"), self.OnClickFileButton)
        QtCore.QObject.connect(self.ui.cleanButton, QtCore.SIGNAL("clicked()"), self.OnClickCleanButton)
        """ list of calibrants """
        self.calibrants = pyFAI.calibrant.ALL_CALIBRANTS.keys()
        self.list_Calibrants = list(self.calibrants)
        self.list_Calibrants.sort()
        
        """ list of detectors """
        self.detectors = pyFAI.detectors.ALL_DETECTORS.keys()
        self.list_Detectors = list(self.detectors)
        self.list_Detectors.sort()
        
        self.ui.comboBoxCalibrants.addItems(self.list_Calibrants)
        self.ui.comboBoxDetectors.addItems(self.list_Detectors)
        '''
        waveLength = di.FloatItem("Wavelength (A) : ", "0.709")  # Default value 0.709
        detector = type = di.ChoiceItem("Detectors", (list_Detectors))
        calibrant = type = di.ChoiceItem("Calibrants", (list_Calibrants))
        fname = FileOpenItem("File :", ("tiff", "edf", "*"))
        polarization = di.StringItem("Polarization : ", default=None)
        distance = di.StringItem("Distance (mm) : ", default= None)
        fix_distance = BoolItem("fix distance")
        notilt = BoolItem("No Tilt")
        '''
        self.ui.cleanButton.setDisabled(True)
        self.ui.show()
    def OnClickFileButton(self):
        '''
        Allow to select a file
        '''
        fd = QtGui.QFileDialog(self)
        filename = fd.getOpenFileName()
        self.workingdirectory = filename
        # print filename
        self.ui.fileLineEdit.setText(filename)
        # self.ui.editor_window.setText(plik)
        self.fname = filename
        self.ui.cleanButton.setEnabled(True)
    def OnClickStartButton(self):
        self.wavelength = float(self.ui.wavelengthLineEdit.text())
        self.polarization = str(self.ui.PolarizationLineEdit.text())
        self.distance = str(self.ui.DistanceLineEdit.text())
        self.detector = self.ui.comboBoxDetectors.currentIndex()
        self.calibrant = self.ui.comboBoxCalibrants.currentIndex()
        self.execute()
    
    def OnClickCleanButton(self):
        print "Clean Button"
        name = filetools.getFilenameOnly(self.fname)
        print(name)
        ret=QtGui.QMessageBox.question(self,"Clean", "Are you sure you want to delete these items?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if ret!=QtGui.QMessageBox.Yes :
            return
        else :
            removePoni = str(name + ".poni")
            removeNpt = str(name + ".npt")
            try :
                os.remove(removePoni)
                print name + ".poni has been removed"
            except :
                print "Poni file doesn't exist"
            try :
                os.remove(removeNpt)
                print name + ".npt has been removed"
            except :
                print "Npt file doesn't exist"    
        
    def execute(self):
        cmd="pyFAI-calib.py "
        cmd+="-w "+str(self.wavelength)
        cmd+=" -D "+self.list_Detectors[self.detector]
        cmd+=" -c "+self.list_Calibrants[self.calibrant]
        """
        Parameters 
        """
        
        if  self.ui.notiltCheckBox.isChecked() :
            cmd+=" --no-tilt"
        
        if  self.ui.PolarizationLineEdit.text() != "" :
            cmd+=" -P "+self.polarization
            
        if  self.ui.DistanceLineEdit.text() !="" :
            cmd+=" -l "+ self.distance
            
        if self.ui.fixDistanceCheckBox.isChecked() :
            cmd+=" --fix-dist"
         
        
        cmd+=' "'+self.fname+'"'
        print cmd
        cmd = str(cmd)
        cd=os.path.dirname(str(self.fname))
        os.system("cd "+cd)
        os.system(cmd)
        
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = CalibStart()
  myapp.show()
  sys.exit(app.exec_())  
