'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys

import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from specguiutils.scanbrowser import ScanBrowser
from spec2nexus.spec import SpecDataFile
from specguiutils.examples.BaseExample import BaseExample
#from specguiutils.scantypeselector import ScanTypeSelector

APP_NAME = "ScanBrowserExample"

class ScanBrowserExample(BaseExample):
    def __init__(self, parent=None):
        super(ScanBrowserExample, self).__init__(parent)
        self.scanBrowser = ScanBrowser()
        self.scanBrowser.scanSelected[list].connect(self.handleScanChanged)
        self.setCentralWidget(self.scanBrowser)
        self.connectOpenFileAction(self.openFile)
        self.setWindowTitle(APP_NAME)
        self.show()
        
    #@qtCore.pyqtSlot(str)
    def handleScanChanged(self, scanList):
        print("Test Code intecepted scan change %s" % scanList)

    @qtCore.pyqtSlot()
    def openFile(self):
        fileName = qtWidgets.QFileDialog.getOpenFileName(None, "Open Spec File")[0]
        self.specFile = SpecDataFile(fileName)
        self.setWindowTitle(APP_NAME + ' - ' + str(fileName))
        self.scanBrowser.loadScans(self.specFile.scans)
        
if __name__ == '__main__':
    app = qtWidgets.QApplication(sys.argv)
    mainForm = ScanBrowserExample()
    app.exec_()
    
