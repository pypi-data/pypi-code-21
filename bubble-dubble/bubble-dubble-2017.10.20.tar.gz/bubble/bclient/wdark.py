#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore, QtWidgets
from .ui.wdark import Ui_WDark
from .fixedwidget import FixedWidget, clearButtonSlot


class WDark(QtWidgets.QDialog, Ui_WDark, FixedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.params = {'darkSample': '', 'darkBackground': '', 'flood': '', 'spline': '', 'incidence': False}
        self.folder = ''
        self.fixWindow()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WDark/folder', self.folder)
        s.setValue('WDark/spline', self.splineLineEdit.text())
        s.setValue('WDark/flood', self.floodLineEdit.text())
        s.setValue('WDark/darkbkg', self.bkgLineEdit.text())
        s.setValue('WDark/darksample', self.sampleLineEdit.text())
        s.setValue('WDark/incidence', self.incidenceCheckBox.isChecked())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.folder = s.value('WDark/folder', '', str)
        self.splineLineEdit.setText(s.value('WDark/spline', '', str))
        self.floodLineEdit.setText(s.value('WDark/flood', '', str))
        self.sampleLineEdit.setText(s.value('WDark/darkbkg', '', str))
        self.bkgLineEdit.setText(s.value('WDark/darksample', '', str))
        self.incidenceCheckBox.setChecked(s.value('WDark/incidence', False, bool))
        self.on_buttonBox_accepted()

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.params = {
            'darkSample': [s.strip() for s in str(self.sampleLineEdit.text()).split(';') if s],
            'darkBackground': [s.strip() for s in str(self.bkgLineEdit.text()).split(';') if s],
            'flood': self.floodLineEdit.text(),
            'spline': self.splineLineEdit.text(),
            'incidence': self.incidenceCheckBox.isChecked(),
        }

    @QtCore.pyqtSlot()
    def on_buttonBox_rejected(self):
        self.bkgLineEdit.setText(';'.join(self.params['darkBackground']))
        self.sampleLineEdit.setText(';'.join(self.params['darkSample']))
        self.floodLineEdit.setText(self.params['flood'])
        self.splineLineEdit.setText(self.params['spline'])
        self.incidenceCheckBox.setChecked(self.params['incidence'])

    @QtCore.pyqtSlot()
    def on_bkgButton_clicked(self):
        self._openButton_clicked(self.bkgLineEdit, self._getFiles)

    @QtCore.pyqtSlot()
    def on_sampleButton_clicked(self):
        self._openButton_clicked(self.sampleLineEdit, self._getFiles)

    @QtCore.pyqtSlot()
    def on_floodButton_clicked(self):
        self._openButton_clicked(self.floodLineEdit, self._getFile)

    @QtCore.pyqtSlot()
    def on_splineButton_clicked(self):
        self._openButton_clicked(self.splineLineEdit, self._getFile, 'Spline file (*.spline)')

    def _getFile(self, lineEdit, current, mask):
        files = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', current, mask)[0]
        if files:
            lineEdit.setText(files)
            self.folder = os.path.dirname(files)

    def _getFiles(self, lineEdit, current, mask):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select files', current, mask)[0]
        if files:
            lineEdit.setText(';'.join(files))
            self.folder = os.path.dirname(files[0].split(';')[0])

    def _openButton_clicked(self, lineEdit, func, mask='EDF Images (*.edf)'):
        current = lineEdit.text()
        if current:
            current = os.path.dirname(current.split(';')[0])
        else:
            current = self.folder
        func(lineEdit, current, mask)

    @QtCore.pyqtSlot(name='on_bkgClearButton_clicked')
    @QtCore.pyqtSlot(name='on_sampleClearButton_clicked')
    @QtCore.pyqtSlot(name='on_floodClearButton_clicked')
    @QtCore.pyqtSlot(name='on_splineClearButton_clicked')
    def _clearButton_clicked(self):
        clearButtonSlot(self)
