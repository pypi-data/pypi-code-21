from PyQt5 import QtGui, QtCore,QtWidgets
'''import guidata
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
'''
import numpy
from pySAXS.LS import LSusaxs
from pySAXS.guisaxs.dataset import *
from pySAXS.guisaxs.qt import plugin
from pySAXS.LS import  invariant
from pySAXS.guisaxs.qt import dlgInvariant

classlist=['pluginInvariant'] #need to be specified

class pluginInvariant(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Calculate Invariant"
    subMenuText="invariant"
    icon="arrow-step-over.png"
    #subMenuText="Background and Data correction"
        
    def execute(self):
        label=self.selectedData
        if self.selectedData is None:
            QtWidgets.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
            return
        
        self.childSaxs=dlgInvariant.dlgInvariant(self.parent,datasetname=label,printout=self.printTXT)
        self.childSaxs.show()

        
        
    