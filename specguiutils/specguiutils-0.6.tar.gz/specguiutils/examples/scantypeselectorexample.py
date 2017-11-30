'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from spec2nexus.spec import SpecDataFile
from specguiutils.examples.BaseExample import BaseExample
from specguiutils.scantypeselector import ScanTypeSelector
import logging
import os
logger = logging.getLogger(__name__)

APP_NAME = "ScanTypeSelectorExample"


class ScanTypeSelectorExample(BaseExample):

    def __init__(self, parent=None):
        super(ScanTypeSelectorExample, self).__init__(parent)
        self.typeSelector = ScanTypeSelector()
        self.typeSelector.scanTypeChanged[int].connect(self.handleScanTypeChanged)
        self.setCentralWidget(self.typeSelector)
        self.connectOpenFileAction(self.openFile)
        self.setWindowTitle(APP_NAME)
        self.show()
        
    @qtCore.pyqtSlot()
    def openFile(self):
        fileName = str((qtWidgets.QFileDialog.getOpenFileName(None, "Open Spec File"))[0])
        print(fileName)
        self.specFile = SpecDataFile(fileName)
        self.setWindowTitle(APP_NAME + ' - ' + str(fileName))
        self.typeSelector.loadScans(self.getScanTypes())
         
    def getScanTypes(self):
        scanTypes = set()
        for scan in self.specFile.scans:
            scanTypes.add(self.specFile.scans[scan].scanCmd.split()[0])
        return list(scanTypes)
 
    @qtCore.pyqtSlot(int)
    def handleScanTypeChanged(self, newType):
        logger.info("handleScanTypeChanged newType: %d" % newType)
        logger.info("handleScanTypeChanged newType: %s" % self.typeSelector.getTypeNames()[newType])
          
         
if __name__ == '__main__':
    app = qtWidgets.QApplication(sys.argv)
    print ("mainApp")
    mainForm = ScanTypeSelectorExample()
    mainForm.show()
    app.exec_()
    
