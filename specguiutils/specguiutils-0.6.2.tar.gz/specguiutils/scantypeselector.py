'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import logging
logger = logging.getLogger(__name__)

SCAN_TYPES = ['All',]

class ScanTypeSelector(qtWidgets.QDialog):
    '''
    Provide a ComboBox to allow switching scan between scan types included 
    in the spec file.  An additional item 
    '''
    scanTypeChanged = qtCore.pyqtSignal(int, name='scanTypeChanged')
    
    def __init__(self, parent=None):
        super(ScanTypeSelector, self).__init__(parent)
        logger.debug ("Enter")

        layout = qtWidgets.QHBoxLayout()
        label =qtWidgets.QLabel("Scan Type")
        self.scanTypes = list(SCAN_TYPES)
        self.scanTypeSelection = qtWidgets.QComboBox()
        self.scanTypeSelection.insertItems(0, self.scanTypes)
 
        layout.addWidget(label)
        layout.addWidget(self.scanTypeSelection)
        self.scanTypeSelection.currentIndexChanged[int] \
            .connect(self.typeSelectionChanged)
         
        self.setLayout(layout)
        self.show()

            
    def loadScans(self, scanTypes):
        self.scanTypeSelection.currentIndexChanged[int] \
            .disconnect(self.typeSelectionChanged)
        self.scanTypeSelection.clear()
        logger.debug("SCAN_TYPES %s" % SCAN_TYPES)
        self.scanTypes = list(SCAN_TYPES)
        self.scanTypes.extend(scanTypes)
        logger.debug("scanTypes %s" % scanTypes)
        logger.debug("self.scanTypes %s" % self.scanTypes)
        self.scanTypeSelection.insertItems(0, self.scanTypes)
        #self.scanTypeSelection.insertItems(1, scanTypes)
        #self.setCurrentType(0)
        self.scanTypeSelection.currentIndexChanged[int] \
            .connect(self.typeSelectionChanged)
         
    def getTypeNames(self):
        typeNames = []
        nameCount = self.scanTypeSelection.count()
        for index in range(nameCount):
            typeNames.append(str(self.scanTypeSelection.itemText(index)))
        return typeNames
     
    def getTypeIndexFromName(self, typeName):
        names = self.getTypeNames()
        index = names.index(typeName)
        return index
         
    def getCurrentType(self):
        return str(self.scanTypeSelection.currentText())
    
    def setCurrentType(self, newType):
        self.scanTypeSelection.setCurrentIndex(newType)
         
    @qtCore.pyqtSlot(int)
    def typeSelectionChanged(self, newType):
#        self.scanTypeSelection.setCurrentIndex(newType)
        logger.debug("Enter")
        self.scanTypeChanged[int].emit(newType)
        