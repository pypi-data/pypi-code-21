from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI

from PyQt5 import QtGui, QtCore,QtWidgets

classlist=['pluginSAXSAbsolute']

class pluginSAXSAbsolute(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Absolute Intensities"
    icon="expand_selection.png"
    toolbar=True
    
    def execute(self):
        
        #display the dialog box
        print "display"
        label=self.selectedData
        if self.selectedData is None:
            QtWidgets.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return
        #print self.data_dict[label].parameters
        #print label
        params=self.data_dict[label].parameters
        if params is not None:
            params.printout=self.printTXT
        reference=self.parent.referencedata
        print 'reference data ',reference
        self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=params,\
                                                datasetname=label,printout=self.printTXT,referencedata=reference,backgrounddata=self.parent.backgrounddata)
        #self.dlgFAI=dlgQtFAI.FAIDialog(self.parent)
        self.childSaxs.show()
        

