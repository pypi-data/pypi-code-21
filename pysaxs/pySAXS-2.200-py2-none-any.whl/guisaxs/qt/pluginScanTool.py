# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt5 import QtGui, QtCore, uic,QtWidgets
from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import scanPlot
from pySAXS.guisaxs import dataset
import pySAXS

from time import sleep
import numpy

from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


classlist=['SCTool'] #need to be specified

class SCTool(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SPEC Tool"
    subMenuText="Scan Plot"
    icon="magnifier.png"
    
    def execute(self):
               
        #display the dialog box
        self.dlg=scanPlot.scanPlot()
        self.dlg.show()