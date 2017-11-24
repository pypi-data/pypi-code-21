'''
execute this file for opening guiSAXS qt (the graphic user interface for pySAXS)
'''
#import guidata
from PyQt5 import QtGui,QtCore,QtWidgets
import os
import sys
import pySAXS
app = QtWidgets.QApplication(sys.argv)
from pySAXS.guisaxs.qt.mainGuisaxs import showSplash
splash=showSplash()
app.processEvents()

from pySAXS.guisaxs.qt import mainGuisaxs
myapp = mainGuisaxs.mainGuisaxs(splashScreen=splash)
myapp.show()

splash.destroy()
sys.exit(app.exec_())