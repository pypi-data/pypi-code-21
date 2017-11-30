'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import logging
from specguiutils import METHOD_ENTER_STR
logger = logging.getLogger(__name__)

class PositionerSelector(qtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(PositionerSelector, self).__init__(parent)
        layout = qtWidgets.QHBoxLayout()
        self.originalList = qtWidgets.QListWidget()
        self.originalList.setMinimumWidth(300)
        self.originalList.setMinimumHeight(400)
        self.selectedList = qtWidgets.QListWidget()
        self.selectedList.setMinimumWidth(300)
        self.selectedList.setMinimumHeight(400)
        self.addToSelection = qtWidgets.QPushButton("Add to Selection")
        self.removeFromSelection = qtWidgets.QPushButton("RemoveFromSelection")
        layout.addWidget(self.originalList)
        buttonLayout = qtWidgets.QVBoxLayout()
#        buttonLayout.addWidget(qtWidgets.QSpacerItem(100, 30))
        buttonLayout.addWidget(self.addToSelection)
        buttonLayout.addWidget(self.removeFromSelection)
#        buttonLayout.addWidget(qtWidgets.QSpacerItem(100, 30))
        layout.addLayout(buttonLayout)
        layout.addWidget(self.selectedList)
        self.setLayout(layout)
        self.show()
        self.addToSelection.clicked.connect(self._addItemToSelection)
        self.originalList.itemDoubleClicked.connect(self._originalListDoubleClicked)
        self.removeFromSelection.clicked.connect(self._removeItemFromSelection)
        self.selectedList.itemDoubleClicked.connect(self._selectedListDoubleClicked)
        
    @qtCore.pyqtSlot()
    def _addItemToSelection(self):
        logger.debug(METHOD_ENTER_STR % self.originalList.currentItem())
        selectedItem = self.originalList.currentItem()
        if not (selectedItem is None):
            logger.debug("Taking item %s" % selectedItem)
            row = self.originalList.currentRow()
            self.originalList.takeItem(row)
            self.selectedList.addItem(selectedItem)
        
    def loadPositioners(self, positioners):
        logger.debug(METHOD_ENTER_STR % positioners)
        for positioner in positioners.keys():
            item = qtWidgets.QListWidgetItem(positioner)
            self.originalList.addItem(item)
            
    def getSelectedItems(self):
        selectedCount = self.selectedList.count()
        selectedItems = [(self.selectedList.item(x)).text() for x in range(selectedCount)]
        return selectedItems
    
    @staticmethod
    def getPositionSelectorModalDialog(positioners):
        class PositionerSelectDialog(qtWidgets.QDialog):
            def __init__(self, parent, positioners):
                super(PositionerSelectDialog,self).__init__(parent)
                self.selectedPositions = []
                self.setModal(True)
                layout = qtWidgets.QVBoxLayout()
                self.positionSelector = PositionerSelector()
                self.positionSelector.loadPositioners(positioners)
                buttonLayout = qtWidgets.QHBoxLayout()
                self.okButton = qtWidgets.QPushButton("OK")
                self.cancelButton = qtWidgets.QPushButton("Cancel")
                buttonLayout.addWidget(self.okButton)
                buttonLayout.addWidget(self.cancelButton)
                layout.addWidget(self.positionSelector)
                layout.addLayout(buttonLayout)
                self.okButton.clicked.connect(self.okPressed)
                self.cancelButton.clicked.connect(self.cancelPressed)
                self.setLayout(layout)
                self.setGeometry(300, 200, 460, 350)
                self.show()
                
            def cancelPressed(self):
                self.hide()
                self.deleteLater()
                
            def okPressed(self):
                self.selectedPositions = self.positionSelector.getSelectedItems()
                self.hide()
                self.deleteLater()
                
            def getSelectedPositioners(self):
                return self.selectedPositions
            
        positionSelector = PositionerSelectDialog(None, positioners)
        positionSelector.exec()
        return positionSelector.getSelectedPositioners()

    def _originalListDoubleClicked(self, items):
        self._addItemToSelection()
        
        
    @qtCore.pyqtSlot()
    def _removeItemFromSelection(self):
        logger.debug(METHOD_ENTER_STR % self.selectedList.currentItem())
        selectedItem = self.selectedList.currentItem()
        if not (selectedItem is None):
            logger.debug("Taking item %s" % selectedItem)
            row = self.selectedList.currentRow()
            self.selectedList.takeItem(row)
            self.originalList.addItem(selectedItem)
            
    def _selectedListDoubleClicked(self, item):
        self._removeItemFromSelection()