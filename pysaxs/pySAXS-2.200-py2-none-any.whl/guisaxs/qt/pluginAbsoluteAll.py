# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt5 import QtGui, QtCore,QtWidgets

from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI

classlist=['AbsoluteAll'] #need to be specified

class AbsoluteAll(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Absolute all"
    icon="expand_selection.png"
    def execute(self):
        datalist=self.ListOfDatasChecked()
        
        #display the dialog box
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
        #print 'reference data ',reference
        self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=params,\
                                                datasetname=label,printout=self.printTXT,referencedata=reference,\
                                                backgrounddata=self.parent.backgrounddata,datasetlist=datalist)
        #self.dlgFAI=dlgQtFAI.FAIDialog(self.parent)
        self.childSaxs.show()
    
    