'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import logging
logger = logging.getLogger(__name__)

FILE_MENU_TEXT = 'File'
OPEN_ACTION_TEXT = 'Open'

class BaseExample(qtWidgets.QMainWindow):
    
    def __init__(self, parent=None):
        super(BaseExample, self).__init__(parent)
        logger.debug("BaseExample.__init__")
        menuBar = self.menuBar()
        #menuBar.setNativeMenuBar(False)
    
        fileMenu = menuBar.addMenu(FILE_MENU_TEXT)
        self.openAction = qtWidgets.QAction(OPEN_ACTION_TEXT, self)
        fileMenu.addAction(self.openAction)
        self.show()
        logger.debug("BaseExample.__init__")
        
    def connectOpenFileAction(self, openFileAction):
        logger.debug("connectOpenFileAction")
        self.openAction.triggered.connect(openFileAction)
