#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import partial
from PyQt5 import QtCore, QtWidgets, QtGui
from .fixedwidget import FixedWidget
from .. import utils, devices, scripo
from .ui.ui_wcryo import Ui_WCryo


class WCryo(QtWidgets.QDialog, Ui_WCryo, FixedWidget):
    sigClosed = QtCore.pyqtSignal()
    sigDisconnect = QtCore.pyqtSignal()
    sigConnect = QtCore.pyqtSignal(str)
    sigRestart = QtCore.pyqtSignal()
    sigStop = QtCore.pyqtSignal()
    sigPause = QtCore.pyqtSignal()
    sigResume = QtCore.pyqtSignal()
    sigTurboOn = QtCore.pyqtSignal()
    sigTurboOff = QtCore.pyqtSignal()
    sigCool = QtCore.pyqtSignal(float)
    sigRamp = QtCore.pyqtSignal(int, float)
    sigPlat = QtCore.pyqtSignal(int)
    sigHold = QtCore.pyqtSignal()
    sigEnd = QtCore.pyqtSignal(int)
    sigPurge = QtCore.pyqtSignal()
    sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    sigShowSeqAction = QtCore.pyqtSignal(dict, object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.sigWaitOnHold = None
        self.paused = False
        self.device = devices.cryostream.Cryostream()
        self.script = scripo.cryostream.Cryostream()
        self.setUI()
        self.editTimeout.setValidator(QtGui.QIntValidator())
        self.on_actionComboBox_currentIndexChanged()
        self.disconnectButton.hide()
        self.connectSignals()

    def setUI(self):
        self.setupUi(self)
        self._style = QtWidgets.QApplication.style()
        self.connectButton.setIcon(QtGui.QIcon(':/run'))
        self.disconnectButton.setIcon(QtGui.QIcon(':/stop'))
        self.closeButton.setIcon(self._style.standardIcon(self._style.SP_DockWidgetCloseButton))
        self.turboOnButton.setIcon(self._style.standardIcon(self._style.SP_DialogYesButton))
        self.turboOffButton.setIcon(self._style.standardIcon(self._style.SP_DialogNoButton))
        self.turboLabel.setPixmap(self._style.standardPixmap(self._style.SP_DialogNoButton))
        self.executeButton.setIcon(QtGui.QIcon(':/run'))
        self.toSeqButton.setIcon(QtGui.QIcon(':/macro'))
        self.fixWindow()

    def connectSignals(self):
        self.sigShowSeqAction.connect(self.showSequenceAction)
        self.sigRestart.connect(self.device.restart)
        self.sigStop.connect(self.device.cstop)
        self.sigPause.connect(self.device.pause)
        self.sigResume.connect(self.device.resume)
        self.sigTurboOn.connect(self.device.turboOn)
        self.sigTurboOff.connect(self.device.turboOff)
        self.sigCool.connect(self.device.cool)
        self.sigRamp.connect(self.device.ramp)
        self.sigPlat.connect(self.device.plat)
        self.sigHold.connect(self.device.hold)
        self.sigEnd.connect(self.device.end)
        self.sigPurge.connect(self.device.purge)
        self.sigConnect.connect(self.device.start)
        self.sigDisconnect.connect(self.device.stop)
        self.device.sigError.connect(self.cryoError)
        self.device.sigStatus.connect(self.updateStatus)
        self.device.sigStatus.connect(self.script._setTemp)
        self.script._sigHoldFromSeq.connect(self.setSignalOnHold)
        self.script._sigCreateSeqAction.connect(self.createAction)

    def setSignalOnHold(self, action, signal):
        if signal:
            self.resume()
            self.action = action
            try:
                timeout = int(self.editTimeout.text())
            except ValueError:
                timeout = utils.DEFAULT_TIMEOUT
            QtCore.QTimer.singleShot(int(timeout), lambda: setattr(self, 'sigWaitOnHold', signal))

    def holdPhaseReached(self, temp):
        if not self.paused and self.sigWaitOnHold:
            self.sigWaitOnHold.emit()
            self.sigWaitOnHold = None
        return f'Hold at {temp:.2f} K'

    def pause(self):
        self.paused = True
        self.sigPause.emit()

    def resume(self):
        self.paused = False
        self.sigResume.emit()

    def updateStatus(self, status):
        self.sampleTempLabel.setText(f'{status["SampleTemp"]:.2f} K'.rjust(8, '0'))
        self.setTempLabel.setText(f'{status["TargetTemp"]:.2f} K'.rjust(8, '0'))
        self.tempErrorLabel.setText(f'{status["GasError"]:.2f} K'.rjust(8, ' '))
        self.gasSetTempLabel.setText(f'{status["GasSetPoint"]:.2f} K'.rjust(8, '0'))
        self.gasHeatProgressBar.setValue(status['GasHeat'])
        self.evapHeatProgressBar.setValue(status['EvapHeat'])
        self.suctHeatProgressBar.setValue(status['SuctHeat'])
        self.gasFlowProgressBar.setFormat(f'{status["GasFlow"]:.1f} l/min')
        self.gasFlowProgressBar.setValue(int(status['GasFlow']))
        self.evapTempProgressBar.setFormat(f'{status["EvapTemp"]:.2f} K')
        self.evapTempProgressBar.setValue(int(status['EvapTemp']))
        self.suctTempProgressBar.setFormat(f'{status["SuctTemp"]:.2f} K')
        self.suctTempProgressBar.setValue(int(status['SuctTemp']))
        self.pressureProgressBar.setFormat(f'{status["LinePressure"]:.2f} bar')
        self.pressureProgressBar.setValue(int(status['LinePressure']))
        if status['AlarmCode']:
            self.statusLabel.setText(f'Warning {status["AlarmCode"]:d}: {status["AlarmMessage"]}')
        else:
            s = 'Cryostream running for'
            days, hours, minutes = utils.calcTime(status["RunTime"])
            dp = 's' if days != 1 else ''
            dh = 's' if hours != 1 else ''
            dm = 's' if minutes != 1 else ''
            if days:
                rt = f'{s} {days:d} day{dp}, {hours:d} hour{dh} and {minutes:d} minute{dm}'
            elif hours:
                rt = f'{s} {hours:d} hour{dh} and {minutes:d} minute{dm}'
            else:
                rt = f'{s} {minutes} minute{dm}'
            self.statusLabel.setText(rt)
        if status['Running']:
            phase = {
                'Ramp': f'Ramp to {status["TargetTemp"]:.2f} K with rate {status["RampRate"]:d} K/hour',
                'Cool': f'Cool to {status["TargetTemp"]:.2f} K',
                'Plat': f'Plat at {status["TargetTemp"]:.2f} K for {status["Remaining"]:d} minutes',
                'Hold': self.holdPhaseReached,
                'End': f'End at 300 K with rate {status["RampRate"]:d} K/hour',
                'Purge': 'Purge',
                'Wait': f'Wait for ramp to {status["TargetTemp"]:.2f} K with rate {status["RampRate"]:d} K/hour',
                'Soak': 'Soaking for Purge',
            }[status['Phase']]
        else:
            phase = status['Phase']
        pixmapName = self._style.SP_DialogYesButton if status['TurboMode'] else self._style.SP_DialogNoButton
        self.turboLabel.setPixmap(self._style.standardPixmap(pixmapName))
        self.phaseLabel.setText(phase(status['GasSetPoint']) if callable(phase) else phase)

    def cryoError(self, msg):
        QtWidgets.QMessageBox.critical(self, 'Cryostream error', msg)
        self.disconnectedFromCryo()

    def closeEvent(self, event):
        self.device.stop()
        self.saveSettings()
        self.sigDisconnect.emit()
        self.sigClosed.emit()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WCryo/Geometry', self.saveGeometry())
        s.setValue('WCryo/target', self.targetSpinBox.value())
        s.setValue('WCryo/rate', self.rateSpinBox.value())
        s.setValue('WCryo/duration', self.durationSpinBox.value())
        s.setValue('WCryo/device', self.deviceLineEdit.text())
        s.setValue('WCryo/ip', self.ipLineEdit.text())
        s.setValue('WCryo/timeout', self.editTimeout.text())
        s.setValue('WCryo/devButton', self.deviceGroup.checkedId())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WCryo/Geometry', b''))
        self.targetSpinBox.setValue(s.value('WCryo/target', 300, float))
        self.rateSpinBox.setValue(s.value('WCryo/rate', 360, float))
        self.durationSpinBox.setValue(s.value('WCryo/duration', 1, float))
        self.deviceLineEdit.setText(s.value('WCryo/device', '/dev/ttyS0', str))
        self.ipLineEdit.setText(s.value('WCryo/ip', 'localhost:7900', str))
        self.editTimeout.setText(s.value('WCryo/timeout', '3000', str))
        self.deviceGroup.button(s.value('WCryo/devButton', -2, int)).setChecked(True)

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.resume()
        self.close()

    @QtCore.pyqtSlot()
    def on_connectButton_clicked(self):
        if self.deviceButton.isChecked():
            dev = self.deviceLineEdit.text()
        elif self.ipButton.isChecked():
            dev = self.ipLineEdit.text()
        else:
            return
        self.connectButton.hide()
        self.disconnectButton.show()
        self.sigConnect.emit(dev)

    @QtCore.pyqtSlot()
    def on_disconnectButton_clicked(self):
        self.disconnectButton.hide()
        self.connectButton.show()
        self.sampleTempLabel.setText('000.00 K')
        self.sigDisconnect.emit()

    def disconnectedFromCryo(self):
        self.sampleTempLabel.setText('000.00 K')
        self.disconnectButton.hide()
        self.connectButton.show()

    def connectedToCryo(self):
        self.disconnectButton.show()
        self.connectButton.hide()

    def disableControls(self):
        for widget in ('targetLabel', 'targetSpinBox', 'rateLabel', 'rateSpinBox', 'durationLabel', 'durationSpinBox'):
            self.__dict__[widget].setEnabled(False)

    def actionCool(self):
        self.helpLabel.setText('Cryostream Plus will cool as quickly as possible to the specified temperature')
        self.targetLabel.setEnabled(True)
        self.targetSpinBox.setEnabled(True)
        return partial(self.sigCool.emit, self.targetSpinBox.value())

    def actionRamp(self):
        self.helpLabel.setText('Cryostream Plus will ramp at the given rate to the specified temperature')
        self.targetLabel.setEnabled(True)
        self.targetSpinBox.setEnabled(True)
        self.rateLabel.setEnabled(True)
        self.rateSpinBox.setEnabled(True)
        return partial(self.sigRamp.emit, self.rateSpinBox.value(), self.targetSpinBox.value())

    def actionPlat(self):
        self.helpLabel.setText('Cryostream Plus will hold the current temperature for the time specified')
        self.durationLabel.setEnabled(True)
        self.durationSpinBox.setEnabled(True)
        return partial(self.sigPlat.emit, self.durationSpinBox.value())

    def actionHold(self):
        self.helpLabel.setText('Cryostream Plus will hold the current temperature indefinitely')
        return self.sigHold.emit

    def actionEnd(self):
        self.helpLabel.setText('Cryostream Plus will ramp to 300 K at the specified rate, and then shut down')
        self.rateLabel.setEnabled(True)
        self.rateSpinBox.setEnabled(True)
        return partial(self.sigEnd.emit, self.rateSpinBox.value())

    def actionPurge(self):
        self.helpLabel.setText('Gas flow will cease, and Cryostream Plus will warm up to room temperature in a '
                               'controlled fashion')
        return self.sigPurge.emit

    @QtCore.pyqtSlot(str)
    def on_actionComboBox_currentIndexChanged(self, action=None):
        self.disableControls()
        return getattr(self, f'action{action or self.actionComboBox.currentText()}')()

    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        self.resume()
        self.sigRestart.emit()

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.resume()
        self.sigStop.emit()

    @QtCore.pyqtSlot()
    def on_holdOnButton_clicked(self):
        self.resume()
        self.sigPause.emit()

    @QtCore.pyqtSlot()
    def on_holdOffButton_clicked(self):
        self.resume()
        self.sigResume.emit()

    @QtCore.pyqtSlot()
    def on_turboOnButton_clicked(self):
        self.resume()
        self.sigTurboOn.emit()

    @QtCore.pyqtSlot()
    def on_turboOffButton_clicked(self):
        self.resume()
        self.sigTurboOff.emit()

    @QtCore.pyqtSlot()
    def on_executeButton_clicked(self):
        self.resume()
        self.on_actionComboBox_currentIndexChanged()()

    @QtCore.pyqtSlot()
    def on_toSeqButton_clicked(self):
        phase = self.actionComboBox.currentText()
        target = self.targetSpinBox.value()
        ramp = self.rateSpinBox.value()
        self.createAction(phase, target, ramp, False)

    def showSequenceAction(self, action, signal):
        for elem in list(action.values())[0].values():
            widgetName, value = elem.split('=')
            widget = self.__dict__[widgetName]
            if isinstance(widget, QtWidgets.QSpinBox):
                widget.setValue(int(value))
            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                widget.setValue(float(value))
            elif isinstance(widget, QtWidgets.QComboBox):
                widget.setCurrentIndex(widget.findText(value))
        if signal:
            self.on_executeButton_clicked()
            signal.emit()

    def createAction(self, phase, temp, ramp, now):
        self.actionComboBox.setCurrentIndex(self.actionComboBox.findText(phase))
        if temp:
            self.targetSpinBox.setValue(temp)
        if ramp:
            self.rateSpinBox.setValue(ramp)
        toSeq = {}
        t = f'Cryostream: {phase}'
        toSeq[f'Phase: {phase}'] = f'actionComboBox={phase}'
        if self.targetSpinBox.isEnabled():
            target = self.targetSpinBox.value()
            t += f' to {target} K'
            toSeq[f'Target temperature: {target} K'] = f'targetSpinBox={target}'
        if self.rateSpinBox.isEnabled():
            rate = self.rateSpinBox.value()
            t += f' with rate {rate} K/hour'
            toSeq[f'Temperature rate: {rate} K/hour'] = f'rateSpinBox={rate}'
        if self.durationSpinBox.isEnabled():
            duration = self.durationSpinBox.value()
            t += f' for {duration} minutes'
            toSeq[f'Duration: {duration} mins'] = f'durationSpinBox={duration}'
        self.sigCreateSeqAction.emit({t: toSeq}, self.sigShowSeqAction, now)
