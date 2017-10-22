'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.9 date 2017-10-22

This file is part of Struthon.
Struthon is a range of free open source structural engineering design 
Python applications.
https://bitbucket.org/lukaszlaba/py4structure/wiki/Home

Struthon is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Struthon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import sys
import subprocess
import os
import time

from PyQt4 import QtCore, QtGui
    
from mainwindow_ui import Ui_MainWindow
import checkupdate

_appname = 'Struthon'
_version = '0.5.4'
_struthon_project_mainpackages = ['struthon','strupy', 'seepy', 'py4structure', 'dxfstructure']
_about = '''
-------------Licence-------------
Struthon is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
            
Struthon is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
            
You should have received a copy of the GNU General Public License along with Foobar; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
            
Copyright (C) 2015-2017 Lukasz Laba (e-mail : lukaszlab@o2.pl)
-------------Project info-------------
http://struthon.org/
https://pypi.python.org/pypi/struthon
https://pypi.python.org/pypi/strupy
-------------Contact-------------
struthon@gmail.com
lukaszlab@o2.pl
'''

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #---Button clicked events
        self.ui.pushButton_SCMS.clicked.connect(self.run_SCMS)
        self.ui.pushButton_SCP.clicked.connect(self.run_SCP)
        self.ui.pushButton_SSSB.clicked.connect(self.run_SSSB)
        self.ui.pushButton_SSMS.clicked.connect(self.run_SSMS)
        self.ui.pushButton_SSBC.clicked.connect(self.run_SSBC)
        self.ui.pushButton_SeePy.clicked.connect(self.run_RunSeePy)
        self.ui.pushButton_Py4Structure.clicked.connect(self.run_Py4Structure)
        self.ui.pushButton_DxfStructure.clicked.connect(self.run_DxfStructure)
        #---MenuBar events
        self.ui.actionAbout.triggered.connect(self.actionAbout)
        self.ui.actionCheck_for_updates.triggered.connect(self.actionCheckForUpdates)
    #----
    def run_SCMS(self):
        subprocess.Popen(['python', '-m', 'struthon.ConcreteMonoSection.ConcreteMonoSection'])
        
    def run_SCP(self): 
        subprocess.Popen(['python', '-m', 'struthon.ConcretePanel.ConcretePanel'])   
           
    def run_SSSB(self):
        subprocess.Popen(['python', '-m', 'struthon.SteelSectionBrowser.SteelSectionBrowser']) 
        
    def run_SSMS(self):
        subprocess.Popen(['python', '-m', 'struthon.SteelMonoSection.SteelMonoSection']) 

    def run_SSBC(self):
        subprocess.Popen(['python', '-m', 'struthon.SteelBoltedConnection.SteelBoltedConnection']) 
        
    def run_RunSeePy(self):
        subprocess.Popen(['python', '-m', 'seepy.SeePy']) 
        
    def run_Py4Structure(self):
        subprocess.Popen(['python', '-m', 'py4structure.Py4Structure']) 

    def run_DxfStructure(self):
        subprocess.Popen(['python', '-m', 'dxfstructure.DxfStructure']) 
    #---
    def actionAbout(self):
        QtGui.QMessageBox.information(None, 'Info', _about)

    def actionCheckForUpdates(self):
        try:
            status = checkupdate.check_few(_struthon_project_mainpackages)
            if status[0]:
                msg_info = 'Check for packages update - OK'
                msg_text = status[1]
            else:
                msg_info = 'Check for packages update - !!! out to date !!!'
                msg_text = status[1]
            QtGui.QMessageBox.information(None, msg_info, status[1])
        except:
            QtGui.QMessageBox.information(None, 'Check for packages update', 'Checking failed !! ')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    myapp.setWindowTitle(_appname + ' ' + _version)
    myapp.show()
    sys.exit(app.exec_())
    