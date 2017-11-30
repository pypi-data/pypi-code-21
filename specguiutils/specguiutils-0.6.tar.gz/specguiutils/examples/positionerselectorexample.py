'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from specguiutils.examples.BaseExample import BaseExample
from specguiutils.positionerselector import PositionerSelector
from spec2nexus.spec import SpecDataFile
import sys

APP_NAME='PositionerSelectorExample'

class PositionerSelectorExample(BaseExample):
    
    def __init__(self, parent=None):
        super(PositionerSelectorExample, self).__init__(parent)
        self.positionerSelector = PositionerSelector()
        menuBar = self.menuBar()
        dataMenu = menuBar.addMenu("Data")
        self.dumpAction = qtWidgets.QAction("DumpSelected", self)
        dataMenu.addAction(self.dumpAction)
        self.dumpAction.triggered.connect(self.dumpSelectedData)
        self.setCentralWidget(self.positionerSelector)
        self.connectOpenFileAction(self.openFile)
        self.setWindowTitle(APP_NAME)
        self.show()
        
    @qtCore.pyqtSlot()
    def openFile(self):
        fileName = qtWidgets.QFileDialog.getOpenFileName(None, "Open Spec File")[0]
        self.specFile = SpecDataFile(fileName)
        self.setWindowTitle(APP_NAME + ' - ' + str(fileName))
        firstScan = self.specFile.getFirstScanNumber()
        self.positionerSelector.loadPositioners(self.specFile.scans[firstScan].positioner)
        
    def dumpSelectedData(self):
        print(self.positionerSelector.getSelectedItems())
        
if __name__ == '__main__':
    app = qtWidgets.QApplication(sys.argv)
    mainForm = PositionerSelectorExample()
    app.exec_()
    
