# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>, 
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
from PyQt5 import QtWidgets as QW


class WarningMessage(QW.QMessageBox):
    def __init__(self, msg, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Warning message")
        self.setIcon(QW.QMessageBox.Warning)
        self.setText(msg)


class CriticalMessage(QW.QMessageBox):
    def __init__(self, msg, details="", parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Error message")
        self.setIcon(QW.QMessageBox.Critical)

        # Force a minimum width ! Cannot use setFixedWidth. This is a trick
        # found on
        # http://www.qtcentre.org/threads/22298-QMessageBox-Controlling-the-width
        layout = self.layout()
        spacer = QW.QSpacerItem(600,0)
        layout.addItem(spacer, layout.rowCount(), 0,1,layout.columnCount())

        msg = '<b style="color:red">' + msg + "</b><br><br>"
        try: details = str(details).replace("\\n", "<br>")
        except: pass
        self.setText(msg + details)
