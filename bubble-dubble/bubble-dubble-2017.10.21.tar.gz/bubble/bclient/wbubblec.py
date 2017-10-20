#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui, QtCore, QtWidgets
from ..bcommon import default
from . import connector, wplot, wsaxsparams, wmask, wdark, wabout, wsopts
from .fixedwidget import FixedWidget, clearButtonSlot
from .ui.wbubble import Ui_WBubble


class WBubble(QtWidgets.QDialog, Ui_WBubble, FixedWidget):
    killServerSignal = QtCore.pyqtSignal()
    startServerSignal = QtCore.pyqtSignal(str, int)
    runSignal = QtCore.pyqtSignal(dict, str)
    beamlineToggledSignal = QtCore.pyqtSignal(str)
    applyWaxsDarkSignal = QtCore.pyqtSignal()
    applySaxsDarkSignal = QtCore.pyqtSignal()
    MaxLabelLen = 40

    def __init__(self):
        super().__init__()
        self.saveFolder = ''
        self.threadUpdateChecker = None
        self.setupUi(self)
        self.setValidators()
        self.setVisibleWidgets()
        self.createWindows()
        self.createConnector()
        self.deleteThreadUpdateChecker()
        self.connectSignals()
        self.fixWindow()

    def createConnector(self):
        self.connector = connector.Connector()

    def setValidators(self):
        self.multiplyLineEdit.setValidator(QtGui.QDoubleValidator())

    def createWindows(self):
        self.wabout = wabout.WAboutBubble(self)
        self.wSaxsMask = wmask.WMask('saxs', self)
        self.wWaxsMask = wmask.WMask('waxs', self)
        self.waxsPlot = wplot.WPlot('WAXS', self)
        self.saxsPlot = wplot.WPlot('SAXS', self)
        self.saxsPlot.plot1DView.setLogMode(x=True, y=True)
        self.wSaxsParams = wsaxsparams.WSaxsParams(self)
        self.wSaxsDark = wdark.WDark(self)
        self.wWaxsDark = wdark.WDark(self)
        self.wsopts = wsopts.WSOpts(self)
        self.wupdates = wabout.WUpdates(self)

    def start(self):
        self.loadSettings()
        self.wSaxsMask.loadSettings()
        self.wWaxsMask.loadSettings()
        self.waxsPlot.loadSettings()
        self.saxsPlot.loadSettings()
        self.wSaxsParams.loadSettings()
        self.wSaxsDark.loadSettings()
        self.wWaxsDark.loadSettings()
        self.wsopts.loadSettings()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())
        self.show()
        self.wSaxsParams.showEvent(None)
        self.on_runSaxsButton_clicked(0)
        self.on_runWaxsButton_clicked(0)
        self.checkNewVersion()

    def setVisibleWidgets(self):
        self.stopServerButton.hide()
        self.runServerButton.show()
        self.killServerButton.hide()
        self.stopWaxsButton.hide()
        self.stopSaxsButton.hide()
        self.sspeedCheckBox.setEnabled(False)
        self.multiEdit.setDisabled(True)

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.connector.serverStateSignal.connect(self.showServerState)
        self.connector.errorsSignal.connect(self.showServerErrors)
        self.connector.warningsSignal.connect(self.showServerWarnings)
        self.killServerSignal.connect(self.connector.killServer)
        self.connector.waxsStateSignal.connect(self.showWaxsState)
        self.connector.saxsStateSignal.connect(self.showSaxsState)
        self.connector.waxsPlotSignal.connect(self.waxsPlot.plot)
        self.connector.saxsPlotSignal.connect(self.saxsPlot.plot)
        self.runSignal.connect(self.connector.runSaxsWaxs)
        self.startServerSignal.connect(self.connector.tryServer)
        self.beamlineToggledSignal.connect(self.wWaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.wSaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.connector.setBeamline)
        self.applySaxsDarkSignal.connect(self.wSaxsDark.on_buttonBox_accepted)
        self.applyWaxsDarkSignal.connect(self.wWaxsDark.on_buttonBox_accepted)
        self.saxsPlot.sigClosed.connect(lambda: self.saxsPlotButton.setChecked(False))
        self.waxsPlot.sigClosed.connect(lambda: self.waxsPlotButton.setChecked(False))
        self.wSaxsMask.sigMask.connect(self.saxsMaskLineEdit.setText)
        self.wWaxsMask.sigMask.connect(self.waxsMaskLineEdit.setText)
        self.wabout.buttonUpdate.clicked.connect(self.checkNewVersionByUser)

    def closeEvent(self, event):
        self.connector.disconnectFromServer()
        self.waxsPlot.close()
        self.saxsPlot.close()
        self.wSaxsMask.close()
        self.wWaxsMask.close()
        self.saveSettings()
        self.wsopts.saveSettings()
        self.wSaxsDark.saveSettings()
        self.wWaxsDark.saveSettings()
        self.waxsPlot.saveSettings()
        self.saxsPlot.saveSettings()
        self.wSaxsParams.saveSettings()
        self.deleteThreadUpdateChecker()

    def saveSettings(self, s=None):
        s = s or QtCore.QSettings()
        s.setValue('WBubble/Geometry', self.saveGeometry())
        s.setValue('WBubble/host', self.hostLineEdit.text())
        s.setValue('WBubble/port', self.portSpinBox.value())
        s.setValue('WBubble/speed', self.speedCheckBox.isChecked())
        s.setValue('WBubble/sspeed', self.sspeedCheckBox.isChecked())
        s.setValue('WBubble/waxspath', self.waxsDirLineEdit.text())
        s.setValue('WBubble/waxsPoniPath', self.waxsPoniLineEdit.text())
        s.setValue('WBubble/waxsBkgPath', self.waxsBkgLineEdit.text())
        s.setValue('WBubble/waxsBkgCoef', self.waxsBkgCoefSpinBox.value())
        s.setValue('WBubble/saxspath', self.saxsDirLineEdit.text())
        s.setValue('WBubble/saxsPoniPath', self.saxsPoniLineEdit.text())
        s.setValue('WBubble/saxsMaskPath', self.saxsMaskLineEdit.text())
        s.setValue('WBubble/waxsMaskPath', self.waxsMaskLineEdit.text())
        s.setValue('WBubble/saxsBkgPath', self.saxsBkgLineEdit.text())
        s.setValue('WBubble/saxsBkgCoef', self.saxsBkgCoefSpinBox.value())
        s.setValue('WBubble/saxsAziStart', self.saxsAziStartSpinBox.value())
        s.setValue('WBubble/saxsAziStop', self.saxsAziStopSpinBox.value())
        s.setValue('WBubble/multiply', self.multiplyLineEdit.text())
        s.setValue('WBubble/beamline', self.getBeamlineRadio())
        s.setValue('WBubble/outUnits', self.getUnitsRadio())
        s.setValue('WBubble/waxsNormalization', self.comboNorm.currentText())
        s.setValue('WBubble/extCheckbox', self.extCheckBox.isChecked())
        s.setValue('WBubble/saxsDetector', self.saxsDetectorComboBox.currentText())
        s.setValue('WBubble/waxsDetector', self.waxsDetectorComboBox.currentText())
        s.setValue('WBubble/subdirCheckbox', self.subdirCheckBox.isChecked())
        s.setValue('WBubble/ext', self.extEdit.text())
        s.setValue('WBubble/subdir', self.subdirEdit.text())
        s.setValue('WBubble/saveFolder', self.saveFolder)
        s.setValue('WBubble/multicolumn', self.multiCheckBox.isChecked())
        s.setValue('WBubble/multicolumnName', self.multiEdit.text())
        s.setValue('WBubble/saveEdf', self.edfCheckBox.isChecked())
        s.setValue('WBubble/waxsAzimuth', self.waxsAzimuthCheckBox.isChecked())
        s.setValue('WBubble/waxsAzimuthStart', self.waxsAziStartSpinBox.value())
        s.setValue('WBubble/waxsAzimuthStop', self.waxsAziStopSpinBox.value())
        s.setValue('WBubble/waxsAzimuthSlices', self.waxsSlicesCheckBox.isChecked())
        s.setValue('WBubble/saxsAzimuth', self.saxsAzimuthCheckBox.isChecked())
        s.setValue('WBubble/saxsAzimuthSlices', self.saxsSlicesCheckBox.isChecked())
        s.setValue('WBubble/waxsRadial', self.waxsRadialCheckBox.isChecked())
        s.setValue('WBubble/waxsRadialStart', self.waxsRadStartSpinBox.value())
        s.setValue('WBubble/waxsRadialStop', self.waxsRadStopSpinBox.value())
        s.setValue('WBubble/saxsRadialStart', self.saxsRadStartSpinBox.value())
        s.setValue('WBubble/saxsRadialStop', self.saxsRadStopSpinBox.value())
        s.setValue('WBubble/saxsRadial', self.saxsRadialCheckBox.isChecked())
        s.setValue('WBubble/page', self.tabWidget.currentIndex())
        s.setValue('WBubble/doNotCheckUpdates', self.wupdates.cb.isChecked())

    def loadSettings(self, s=None):
        s = s or QtCore.QSettings()
        self.restoreGeometry(s.value('WBubble/Geometry', b''))
        self.hostLineEdit.setText(s.value('WBubble/host', default.DEFAULT_HOST, str))
        self.portSpinBox.setValue(s.value('WBubble/port', default.DEFAULT_PORT, int))
        self.speedCheckBox.setChecked(s.value('WBubble/speed', False, bool))
        self.sspeedCheckBox.setChecked(s.value('WBubble/sspeed', False, bool))
        self.waxsDirLineEdit.setText(s.value('WBubble/waxspath', '', str))
        self.waxsPoniLineEdit.setText(s.value('WBubble/waxsPoniPath', '', str))
        self.waxsBkgLineEdit.setText(s.value('WBubble/waxsBkgPath', '', str))
        self.waxsBkgCoefSpinBox.setValue(s.value('WBubble/waxsBkgCoef', 0, float))
        self.saxsDirLineEdit.setText(s.value('WBubble/saxspath', '', str))
        self.saxsPoniLineEdit.setText(s.value('WBubble/saxsPoniPath', '', str))
        self.saxsMaskLineEdit.setText(s.value('WBubble/saxsMaskPath', '', str))
        self.waxsMaskLineEdit.setText(s.value('WBubble/waxsMaskPath', '', str))
        self.saxsBkgLineEdit.setText(s.value('WBubble/saxsBkgPath', '', str))
        self.saxsBkgCoefSpinBox.setValue(s.value('WBubble/saxsBkgCoef', 0, float))
        self.saxsAziStartSpinBox.setValue(s.value('WBubble/saxsAziStart', 0, float))
        self.saxsAziStopSpinBox.setValue(s.value('WBubble/saxsAziStop', 0, float))
        self.multiplyLineEdit.setText(s.value('WBubble/multiply', '1', str))
        beamline = s.value('WBubble/beamline', 'Dubble', str).replace('&', '')
        if beamline == 'SNBL':
            self.snblRadio.setChecked(True)
        elif beamline == 'Dubble':
            self.dubbleRadio.setChecked(True)
        norm = s.value('WBubble/waxsNormalization', 'Monitor', str)
        self.comboNorm.setCurrentIndex(self.comboNorm.findText(norm))
        self.saxsDetectorComboBox.setCurrentIndex(self.saxsDetectorComboBox.findText(
            s.value('WBubble/saxsDetector', 'Pilatus', str)))
        self.waxsDetectorComboBox.setCurrentIndex(
            self.waxsDetectorComboBox.findText(s.value('WBubble/waxsDetector', 'Pilatus', str)))
        outUnits = s.value('WBubble/outUnits', 'qRadio', str)
        if outUnits == 'tthRadio':
            self.tthRadio.setChecked(True)
        self.extCheckBox.setChecked(s.value('WBubble/extCheckbox', False, bool))
        self.subdirCheckBox.setChecked(s.value('WBubble/subdirCheckbox', False, bool))
        self.extEdit.setText(s.value('WBubble/ext', '', str))
        self.subdirEdit.setText(s.value('WBubble/subdir', '', str))
        self.saveFolder = s.value('WBubble/saveFolder', '', str)
        self.multiCheckBox.setChecked(s.value('WBubble/multicolumn', False, bool))
        self.multiEdit.setText(s.value('WBubble/multicolumnName', default.MULTICOLUMN_NAME, str))
        self.edfCheckBox.setChecked(s.value('WBubble/saveEdf', False, bool))
        self.waxsAziStartSpinBox.setValue(s.value('WBubble/waxsAzimuthStart', 0, float))
        self.waxsAziStopSpinBox.setValue(s.value('WBubble/waxsAzimuthStop', 0, float))
        self.waxsSlicesCheckBox.setChecked(s.value('WBubble/waxsAzimuthSlices', False, bool))
        self.saxsSlicesCheckBox.setChecked(s.value('WBubble/saxsAzimuthSlices', False, bool))
        self.saxsAzimuthCheckBox.setChecked(s.value('WBubble/saxsAzimuth', False, bool))
        self.saxsRadialCheckBox.setChecked(s.value('WBubble/saxsRadial', False, bool))
        self.waxsRadialCheckBox.setChecked(s.value('WBubble/waxsRadial', False, bool))
        self.waxsRadStartSpinBox.setValue(s.value('WBubble/waxsRadialStart', 0, float))
        self.waxsRadStopSpinBox.setValue(s.value('WBubble/waxsRadialStop', 0, float))
        self.saxsRadStartSpinBox.setValue(s.value('WBubble/saxsRadialStart', 0, float))
        self.saxsRadStopSpinBox.setValue(s.value('WBubble/saxsRadialStop', 0, float))
        self.tabWidget.setCurrentIndex(s.value('WBubble/page', 0, int))
        self.wupdates.cb.setChecked(s.value('WBubble/doNotCheckUpdates', False, bool))

    @QtCore.pyqtSlot()
    def on_exitButton_clicked(self):
        self.close()

    def showServerState(self, status):
        if status['serverRunning']:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.stopServerButton.show()
            self.runServerButton.hide()
            self.killServerButton.show()
        else:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.stopServerButton.hide()
            self.runServerButton.show()
            self.serverStateLabel.setText('Server is stopped')
            self.killServerButton.hide()

    def showWaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.formatLabelText(status.get('path', 'unknown'), self.waxsStateLabel)
            self.runWaxsButton.hide()
            self.stopWaxsButton.show()
        else:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.formatLabelText('stopped', self.waxsStateLabel)
            self.stopWaxsButton.hide()
            self.runWaxsButton.show()
        self.formatLabelText(os.path.basename(status.get('imageFile', '')), self.waxsLastfileLabel)
        self.formatLabelText(f'{status.get("total", 0)} of {status.get("all", 0)}', self.waxsTotalLabel)

    def formatLabelText(self, text: str, label: QtWidgets.QLabel):
        if len(text) >= self.MaxLabelLen:
            label.setText(f'...{text[-self.MaxLabelLen:]}')
        else:
            label.setText(text)
        label.setToolTip(text)

    def showSaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.formatLabelText(status.get('path', 'unknown'), self.saxsStateLabel)
            self.runSaxsButton.hide()
            self.stopSaxsButton.show()
        else:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.formatLabelText('stopped', self.saxsStateLabel)
            self.stopSaxsButton.hide()
            self.runSaxsButton.show()
        self.formatLabelText(os.path.basename(status.get('imageFile', '')), self.saxsLastfileLabel)
        self.formatLabelText(f'{status.get("total", 0)} of {status.get("all", 0)}', self.saxsTotalLabel)

    def showServerErrors(self, errors):
        QtWidgets.QMessageBox.critical(self, 'Server errors', errors)

    def showServerWarnings(self, warnings):
        QtWidgets.QMessageBox.warning(self, 'Server warnings', warnings)

    @QtCore.pyqtSlot(bool)
    def on_localCheckBox_toggled(self, checked):
        if checked:
            self.hostLineEdit.setDisabled(True)
            self.portSpinBox.setDisabled(True)
            self.runServerButton.setText('Start server')
            self.stopServerButton.setText('Stop server')
        else:
            self.hostLineEdit.setEnabled(True)
            self.portSpinBox.setEnabled(True)
            self.runServerButton.setText('Connect')
            self.stopServerButton.setText('Disconnect')

    @QtCore.pyqtSlot()
    def on_stopServerButton_clicked(self):
        self.stopServerButton.hide()
        self.runServerButton.show()
        self.killServerButton.hide()
        self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
        self.serverStateLabel.setText('Disconnected from the server')
        self.connector.disconnectFromServer()

    @QtCore.pyqtSlot()
    def on_runServerButton_clicked(self):
        self.runServerButton.hide()
        self.runServerButton.show()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())

    @QtCore.pyqtSlot()
    def on_killServerButton_clicked(self):
        self.killServerSignal.emit()

    def getBeamlineRadio(self):
        return self.getRadio('Dubble', (self.dubbleRadio, self.snblRadio))

    def getUnitsRadio(self):
        return self.getRadio('q', (self.qRadio, self.tthRadio), False)

    def getRadio(self, start, radios, text=True):
        value = start
        for radio in radios:
            if radio.isChecked():
                if text:
                    value = radio.text().replace('&', '')
                else:
                    value = radio.objectName()
                break
        return value

    def getSpeed(self):
        return {
            'speed': self.speedCheckBox.isChecked(),
            'sspeed': self.sspeedCheckBox.isEnabled() and self.sspeedCheckBox.isChecked(),
        }

    def getCommonParams(self):
        params = {
            'beamline': self.getBeamlineRadio(),
            'units': self.getUnitsRadio()[0],
        }
        params.update(self.getSpeed())
        params.update(self.wsopts.params)
        return params

    @QtCore.pyqtSlot()
    def on_runWaxsButton_clicked(self, run=1):
        path = self.waxsDirLineEdit.text()
        poniPath = self.waxsPoniLineEdit.text()
        ext = self.extEdit.text() if self.extCheckBox.isChecked() else ''
        subdir = self.subdirEdit.text() if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = self.multiEdit.text()
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            QtWidgets.QMessageBox.critical(self, 'WAXS Error', 'You have to set folder and poni file, at least.')
            return
        multiplier = self.multiplyLineEdit.text()
        radial = None
        if self.waxsRadialCheckBox.isChecked():
            radial = self.waxsRadStartSpinBox.value(), self.waxsRadStopSpinBox.value()

        norm = []
        for n in (self.spinWaxsBkgStart.value(), self.spinWaxsBkgStop.value()):
            try:
                norm.append(float(n))
            except ValueError:
                norm.append(0)

        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.waxsBkgCoefSpinBox.value(),
            'backgroundFiles': [s.strip() for s in self.waxsBkgLineEdit.text().split(';') if s],
            'maskFile': self.waxsMaskLineEdit.text(),
            'calibration': float(multiplier) if multiplier else 1,
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.waxsDetectorComboBox.currentText(),
            'azimuth': (self.waxsAziStartSpinBox.value(), self.waxsAziStopSpinBox.value()),
            'azimuthSlices': self.waxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.waxsAzimuthCheckBox.isChecked(),
            'radial': radial,
            'normalization': self.comboNorm.currentText(),
            'normrange': norm,
        }
        params.update(self.getCommonParams())
        params.update(self.wWaxsDark.params)
        self.runSignal.emit(params, 'waxs')

    @QtCore.pyqtSlot()
    def on_runSaxsButton_clicked(self, run=1):
        path = self.saxsDirLineEdit.text()
        poniPath = self.saxsPoniLineEdit.text()
        ext = str(self.extEdit.text()) if self.extCheckBox.isChecked() else ''
        subdir = str(self.subdirEdit.text()) if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = str(self.multiEdit.text())
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            QtWidgets.QMessageBox.critical(self, 'SAXS Error', 'You have to set folder and poni file, at least.')
            return
        radial = None
        if self.saxsRadialCheckBox.isChecked():
            radial = self.saxsRadStartSpinBox.value(), self.saxsRadStopSpinBox.value()
        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.saxsBkgCoefSpinBox.value(),
            'azimuth': (self.saxsAziStartSpinBox.value(), self.saxsAziStopSpinBox.value()),
            'maskFile': str(self.saxsMaskLineEdit.text()),
            'backgroundFiles': [s.strip() for s in str(self.saxsBkgLineEdit.text()).split(';') if s],
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.saxsDetectorComboBox.currentText(),
            'azimuthSlices': self.saxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.saxsAzimuthCheckBox.isChecked(),
            'radial': radial,
            'normalization': 'Monitor',
            'normrange': (None, None),
        }
        params.update(self.getCommonParams())
        params.update(self.wSaxsParams.params)
        params.update(self.wSaxsDark.params)
        self.runSignal.emit(params, 'saxs')

    @QtCore.pyqtSlot()
    def on_stopWaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'waxs')

    @QtCore.pyqtSlot()
    def on_stopSaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'saxs')

    @QtCore.pyqtSlot(bool)
    def on_waxsPlotButton_toggled(self, checked):
        self.waxsPlot.setVisible(checked)

    @QtCore.pyqtSlot(bool)
    def on_saxsPlotButton_toggled(self, checked):
        self.saxsPlot.setVisible(checked)

    @QtCore.pyqtSlot()
    def on_waxsFolderButton_clicked(self):
        self._folderButton_clicked(self.waxsDirLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsFolderButton_clicked(self):
        self._folderButton_clicked(self.saxsDirLineEdit)

    def _folderButton_clicked(self, dirLineEdit):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder', dirLineEdit.text())
        if d:
            dirLineEdit.setText(d)

    @QtCore.pyqtSlot()
    def on_waxsPoniButton_clicked(self):
        self._poniButton_clicked(self.waxsPoniLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsPoniButton_clicked(self):
        self._poniButton_clicked(self.saxsPoniLineEdit)

    def _poniButton_clicked(self, poniLineEdit):
        currentPoni = poniLineEdit.text()
        if currentPoni:
            currentPoni = os.path.dirname(currentPoni)
        poni = QtWidgets.QFileDialog.getOpenFileName(self, 'Select poni file', currentPoni, 'Poni (*.poni)')[0]
        if poni:
            poniLineEdit.setText(poni)

    @QtCore.pyqtSlot()
    def on_waxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.waxsBkgLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.saxsBkgLineEdit)

    def _bkgButton_clicked(self, bkgLineEdit):
        currentBkg = bkgLineEdit.text()
        if currentBkg:
            currentBkg = os.path.dirname(currentBkg.split(';')[0])
        bkg = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select background files', currentBkg,
                                                     'Frames (*.edf *.cbf)')[0]
        if bkg:
            bkgLineEdit.setText(';'.join(bkg))

    @QtCore.pyqtSlot()
    def on_saxsMaskButton_clicked(self):
        self._maskButton_clicked(self.saxsMaskLineEdit)

    @QtCore.pyqtSlot()
    def on_waxsMaskButton_clicked(self):
        self._maskButton_clicked(self.waxsMaskLineEdit)

    def _maskButton_clicked(self, maskLineEdit):
        mask = maskLineEdit.text()
        mask = QtWidgets.QFileDialog.getOpenFileName(self, 'Select mask file', mask,
                                                     'Masks (*.msk *.npz);;Fit2D mask (*.msk);;Bubble mask (*.npz)')[0]
        if mask:
            maskLineEdit.setText(mask)

    @QtCore.pyqtSlot()
    def on_advancedButton_clicked(self):
        self.wSaxsParams.exec()

    @QtCore.pyqtSlot(bool)
    def on_snblRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('SNBL')
            self.tabWidget.setTabEnabled(1, False)

    @QtCore.pyqtSlot(bool)
    def on_dubbleRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('Dubble')
            self.tabWidget.setTabEnabled(1, True)

    @QtCore.pyqtSlot(bool)
    def on_extCheckBox_toggled(self, checked):
        self.extEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_darkFilesButton_clicked(self):
        self.wSaxsDark.exec()

    @QtCore.pyqtSlot()
    def on_waxsDarkFilesButton_clicked(self):
        self.wWaxsDark.exec()

    @QtCore.pyqtSlot(bool)
    def on_subdirCheckBox_toggled(self, checked):
        self.subdirEdit.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_multiCheckBox_toggled(self, checked):
        self.multiEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.saveSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    @QtCore.pyqtSlot(str)
    def on_saxsDetectorComboBox_currentIndexChanged(self, detector):
        self.darkFilesButton.setEnabled(detector == 'Frelon')
        self.applySaxsDarkSignal.emit()

    @QtCore.pyqtSlot(str)
    def on_waxsDetectorComboBox_currentIndexChanged(self, detector):
        self.waxsDarkFilesButton.setEnabled(detector == 'Frelon')
        self.applyWaxsDarkSignal.emit()

    @QtCore.pyqtSlot(name='on_saxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsBkgClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsBkgClearButton_clicked')
    def _clearButton_clicked(self):
        clearButtonSlot(self)

    @QtCore.pyqtSlot()
    def on_loadButton_clicked(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Load window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.loadSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    @QtCore.pyqtSlot()
    def on_waxsMakeMaskButton_clicked(self):
        self.wWaxsMask.show()

    @QtCore.pyqtSlot()
    def on_saxsMakeMaskButton_clicked(self):
        self.wSaxsMask.show()

    @QtCore.pyqtSlot(bool)
    def on_speedCheckBox_toggled(self, checked):
        self.sspeedCheckBox.setEnabled(checked)
        if not checked:
            self.sspeedCheckBox.setChecked(False)
        self.runSignal.emit(self.getSpeed(), 'saxs')
        self.runSignal.emit(self.getSpeed(), 'waxs')

    @QtCore.pyqtSlot(bool)
    def on_sspeedCheckBox_toggled(self, checked):
        self.multiCheckBox.setEnabled(not checked)
        if not self.multiCheckBox.isEnabled():
            self.multiCheckBox.setChecked(False)
        self.runSignal.emit(self.getSpeed(), 'saxs')
        self.runSignal.emit(self.getSpeed(), 'waxs')

    @QtCore.pyqtSlot()
    def on_aboutButton_clicked(self):
        self.wabout.exec()

    @QtCore.pyqtSlot()
    def on_buttonOptions_clicked(self):
        self.wsopts.exec()

    @QtCore.pyqtSlot(bool)
    def on_saxsSlicesCheckBox_toggled(self, checked):
        self.labelSaxsAzimuth.setText('and step' if checked else 'and stop')

    @QtCore.pyqtSlot(bool)
    def on_saxsRadialCheckBox_toggled(self, checked):
        self.saxsRadStartSpinBox.setEnabled(checked)
        self.saxsRadStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_saxsAzimuthCheckBox_toggled(self, checked):
        if not checked:
            self.saxsSlicesCheckBox.setChecked(False)
        self.saxsSlicesCheckBox.setEnabled(checked)
        self.saxsAziStartSpinBox.setEnabled(checked)
        self.saxsAziStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_waxsSlicesCheckBox_toggled(self, checked):
        self.labelWaxsAzimuth.setText('and step' if checked else 'and stop')

    @QtCore.pyqtSlot(bool)
    def on_waxsRadialCheckBox_toggled(self, checked):
        self.waxsRadStartSpinBox.setEnabled(checked)
        self.waxsRadStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_waxsAzimuthCheckBox_toggled(self, checked):
        if not checked:
            self.waxsSlicesCheckBox.setChecked(False)
        self.waxsSlicesCheckBox.setEnabled(checked)
        self.waxsAziStartSpinBox.setEnabled(checked)
        self.waxsAziStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(str)
    def on_comboNorm_currentTextChanged(self, text: str):
        bkg = text == 'Bkg'
        self.spinWaxsBkgStop.setEnabled(bkg)
        self.spinWaxsBkgStart.setEnabled(bkg)

    def checkNewVersion(self):
        if not self.wupdates.cb.isChecked():
            self.createUpdateChecker()
            self.threadUpdateChecker.start()

    def showNewVersion(self, text, error):
        if self.checkUpdatesByUser:
            self.wupdates.error(text) if error else self.wupdates.success(text)
        else:
            if not error and not self.wupdates.cb.isChecked() and text:
                self.wupdates.success(text)

    def checkNewVersionByUser(self):
        self.createUpdateChecker()
        self.checkUpdatesByUser = True
        self.threadUpdateChecker.start()

    def createUpdateChecker(self):
        self.checkUpdatesByUser = False
        self.threadUpdateChecker = QtCore.QThread()
        self.updateChecker = wabout.UpdateChecker()
        self.updateChecker.moveToThread(self.threadUpdateChecker)
        # noinspection PyUnresolvedReferences
        self.threadUpdateChecker.started.connect(self.updateChecker.check)
        self.updateChecker.sigNewVersion.connect(self.showNewVersion)
        self.updateChecker.sigFinished.connect(self.deleteThreadUpdateChecker)

    def deleteThreadUpdateChecker(self):
        self.checkUpdatesByUser = False
        if self.threadUpdateChecker:
            self.threadUpdateChecker.quit()
            self.threadUpdateChecker.wait()
        self.threadUpdateChecker = None
        self.updateChecker = None
