'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from specguiutils.radiobuttondelegate import RadioButtonDelegate
import logging
logger = logging.getLogger(__name__)


class CounterSelectorView(qtWidgets.QTableView):
    
    counterDataChanged = qtCore.pyqtSignal(list, name="signalChanged")
    
    def __init__(self, parent=None, tableModel = None):
        super(CounterSelectorView,self).__init__(parent=parent)
        self.setModel(tableModel)
        self.columnGroups = {}
        
    def headerChanged(self, orientation, first, last):
        logger.debug( "Entering %s, %s, %s", orientation, first, last) 
        delegate = RadioButtonDelegate(self.parent())
        self.columnGroups.clear()
        for col in range(1, last):
            self.columnGroups[col] = qtWidgets.QButtonGroup(self.parent())
        for col in range (1,last):
            
            numRows = self.model().rowCount()
            logger.debug ("setting column delegates for col %d" % col)
            self.setItemDelegateForColumn(col, delegate)
            for row in range(numRows):
                self.openPersistentEditor(self.model().index(row,col))
                editor = self.indexWidget(self.model().index(row,col))
                self.columnGroups[col].addButton(editor)
                editor.clicked.connect(self.aButtonClicked)
#                 if row == 0:
#                     editor.setChecked(True)
                
    @qtCore.pyqtSlot(bool)
    def aButtonClicked(self, state):
        logger.debug("Entering")
        dataOut = []
        dataOut = self.getSelectedCounters()
        self.counterDataChanged[list].emit(dataOut)
            
    def getSelectedCounters(self):
        dataOut = []
        logger.debug (" %s" % dataOut )
        for bGroup in self.columnGroups.keys():
#             position = qtCore.QModelIndex()
#             print " row, col %d, %d" % (position.row(), position.column())
            widgetId = self.columnGroups[bGroup].checkedId()
            if widgetId != -1:
                dataOut.append(-1*widgetId -2)
            else:
                dataOut.append(-1)
        logger.debug ("Leaving %s" % dataOut )
        return dataOut
                
            
        