#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
from ..bcommon import default
from .fixedwidget import FixedWidget
from .ui.ui_wsopts import Ui_WSOpts


class WSOpts(QtWidgets.QDialog, Ui_WSOpts, FixedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.values = {}
        self.setUI()
        self.on_buttonBox_accepted()

    def setUI(self):
        self.setupUi(self)
        self.spinThreads.setMaximum(default.MAX_THREADS)
        self.fixWindow()

    def loadSettings(self):
        s = QtCore.QSettings()
        self.checkThreads.setChecked(s.value('WSOpts/checkThreads', False, bool))
        self.checkBins.setChecked(s.value('WSOpts/checkBins', False, bool))
        self.checkPol.setChecked(s.value('WSOpts/checkPol', False, bool))
        self.checkDouble.setChecked(s.value('WSOpts/checkDouble', False, bool))
        self.checkHalina.setChecked(s.value('WSOpts/checkHalina', False, bool))
        self.checkSA.setChecked(s.value('WSOpts/checkSA', True, bool))
        self.spinPol.setValue(s.value('WSOpts/spinPol', 0, float))
        self.spinBins.setValue(s.value('WSOpts/spinBins', 1, int))
        self.spinThreads.setValue(s.value('WSOpts/spinThreads', 1, int))

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSOpts/checkThreads', self.checkThreads.isChecked())
        s.setValue('WSOpts/checkBins', self.checkBins.isChecked())
        s.setValue('WSOpts/checkPol', self.checkPol.isChecked())
        s.setValue('WSOpts/checkDouble', self.checkDouble.isChecked())
        s.setValue('WSOpts/checkHalina', self.checkHalina.isChecked())
        s.setValue('WSOpts/checkSA', self.checkSA.isChecked())
        s.setValue('WSOpts/spinPol', self.spinPol.value())
        s.setValue('WSOpts/spinBins', self.spinBins.value())
        s.setValue('WSOpts/spinThreads', self.spinThreads.value())

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        self.values = {}
        for name in self.__dict__:
            widget = self.__dict__[name]
            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                self.values[name] = widget.value()
            elif isinstance(widget, QtWidgets.QCheckBox):
                self.values[name] = widget.isChecked()

    @QtCore.pyqtSlot(bool)
    def on_checkThreads_toggled(self, checked):
        self.spinThreads.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_checkBins_toggled(self, checked):
        self.spinBins.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_checkPol_toggled(self, checked):
        self.spinPol.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.params = {
            'polarization': self.spinPol.value() if self.checkPol.isChecked() else -2,
            'threads': self.spinThreads.value() if self.checkThreads.isChecked() else 0,
            'bins': self.spinBins.value() if self.checkBins.isChecked() else 0,
            'solidangle': self.checkSA.isChecked(),
            'halina': self.checkHalina.isChecked(),
            'double': self.checkDouble.isChecked(),
        }

    @QtCore.pyqtSlot()
    def on_buttonBox_rejected(self):
        for name in self.values:
            widget = self.__dict__[name]
            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                widget.setValue(self.values[name])
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(self.values[name])
