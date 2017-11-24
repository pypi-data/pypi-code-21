from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import QtImageTool
from PyQt4 import QtGui, QtCore

classlist=['pluginImageTool']

class pluginImageTool(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Image"
    subMenuText="Image Tool"
    icon="image.png"
    
    def execute(self):
        #display the dialog box
        '''label=self.selectedData
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return
        '''
        #print self.data_dict[label].parameters
        #print label
        window = QtImageTool.MainWindow(self.parent)
        #self.dlgFAI=dlgQtFAI.FAIDialog(self.parent)
        #window.exec_()
        window.showNormal()
        