#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtGui, QtWidgets
from .ui.wsaxsparams import Ui_WSaxsParams
from .fixedwidget import FixedWidget


class WSaxsParams(QtWidgets.QDialog, Ui_WSaxsParams, FixedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.concentrationLineEdit.setValidator(QtGui.QDoubleValidator())
        self.thicknessLineEdit.setValidator(QtGui.QDoubleValidator())
        self.calibrationLineEdit.setValidator(QtGui.QDoubleValidator())
        self.params = {
            'concentration': 0,
            'thickness': 1,
            'calibration': 1e6,
        }
        self.fixWindow()

    def showEvent(self, event):
        self.concentrationLineEdit.setText(str(self.params['concentration']))
        self.thicknessLineEdit.setText(str(self.params['thickness']))
        self.calibrationLineEdit.setText(str(self.params['calibration']))

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.params = {
            'concentration': float(self.concentrationLineEdit.text()),
            'thickness': float(self.thicknessLineEdit.text()),
            'calibration': float(self.calibrationLineEdit.text()),
        }

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSaxsParams/params', json.dumps(self.params))

    def loadSettings(self):
        s = QtCore.QSettings()
        params = s.value('WSaxsParams/params', '', str)
        if params:
            self.params = json.loads(params)
