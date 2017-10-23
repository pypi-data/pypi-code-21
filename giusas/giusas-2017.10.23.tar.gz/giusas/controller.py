#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore
from .gui.ptree import Params
from .gui.wgiusas import WGiuSAS
from .gui.ftree import FilesTree
from .model import GiSASModel


class Controller(QtCore.QObject):
    sendParameters = QtCore.pyqtSignal(dict, dict)
    calculateSignal = QtCore.pyqtSignal()
    emitDataSignal = QtCore.pyqtSignal()
    loadModelParametersSignal = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.createModel()
        self.createWindows()
        self.connectSignals()

    def createModel(self):
        self.gmodelThread = QtCore.QThread()
        self.gmodel = GiSASModel()
        self.gmodel.moveToThread(self.gmodelThread)

    def loadSettings(self):
        self.settings = QtCore.QSettings()
        self.loadModelParameters()
        self.wgiusas.loadSettings()
        self.wparams.loadSettings()
        self.wftree.loadSetting()
        self.wftree.workDir = self.workDir = self.settings.value('WGiuSAS/workDir', '', str)
        # self.sendParameters.emit(self.wgiusas.tabs.imageParameters(), self.wgiusas.tabs.checkBoxesState())
        self.calculateSignal.emit()
        self.emitDataSignal.emit()

    def saveSettings(self):
        self.wgiusas.saveSettings()
        self.wparams.saveSettings()
        self.wftree.saveSettings()
        self.settings.setValue('WGiuSAS/workDir', self.workDir)

    def start(self):
        self.loadSettings()
        self.connectParamsSignals()
        self.gmodelThread.start()
        self.wgiusas.show()

    def createWindows(self):
        self.wparams = Params()
        self.wftree = FilesTree()
        self.wgiusas = WGiuSAS(self.wparams, self.wftree)

    def connectSignals(self):
        self.sendParameters.connect(self.gmodel.setStartingParameters)
        self.calculateSignal.connect(self.gmodel.calculate)
        self.emitDataSignal.connect(self.gmodel.emitData)
        self.wgiusas.closeEventSignal.connect(self.closeAll)
        self.wgiusas.actionRotateImage.triggered.connect(self.gmodel.rotateImage)
        self.wgiusas.actionFlipImageH.triggered.connect(self.gmodel.flipImageH)
        self.wgiusas.actionFlipImageV.triggered.connect(self.gmodel.flipImageV)
        self.wgiusas.actionLogarithmicScale.triggered[bool].connect(self.gmodel.switchLog)
        self.wgiusas.plot2DView.setBeamCenterSignal.connect(self.gmodel.setBeamCenter)
        self.wgiusas.plot2DView.setBeamCenterSignal.connect(self.wparams.setBeamCenter)
        self.gmodel.data2dSignal.connect(self.wgiusas.show2d)
        self.gmodel.errorSignal.connect(self.wgiusas.showError)
        self.wgiusas.plot2DView.setHROIDataSignal.connect(self.gmodel.calcHCut)
        self.wgiusas.plot2DView.setVROIDataSignal.connect(self.gmodel.calcVCut)
        self.gmodel.cutHValuesSignal.connect(self.wgiusas.plotHROIData)
        self.gmodel.cutVValuesSignal.connect(self.wgiusas.plotVROIData)
        # noinspection PyUnresolvedReferences
        self.gmodelThread.finished.connect(self.gmodel.saveSettings)
        self.gmodel.saveModelParametersSignal.connect(self.saveModelParameters)
        self.gmodel.changeCutUnitsSignal.connect(self.wgiusas.changeCutUnits)
        self.gmodel.changeCutUnitsSignal.connect(self.wgiusas.plot2DView.leftAxis.changeUnits)
        self.gmodel.changeCutUnitsSignal.connect(self.wgiusas.plot2DView.bottomAxis.changeUnits)
        self.gmodel.changeHCutSizeSignal.connect(self.wgiusas.plot2DView.changeHCutSize)
        self.gmodel.changeVCutSizeSignal.connect(self.wgiusas.plot2DView.changeVCutSize)
        self.loadModelParametersSignal.connect(self.gmodel.loadSettings)
        self.wgiusas.plot2DView.leftAxis.changeRangeSignal.connect(self.gmodel.calcVRange)
        self.wgiusas.plot2DView.bottomAxis.changeRangeSignal.connect(self.gmodel.calcHRange)
        self.gmodel.verticalRangeSignal.connect(self.wgiusas.plot2DView.leftAxis.setRealRange)
        self.gmodel.horizontalRangeSignal.connect(self.wgiusas.plot2DView.bottomAxis.setRealRange)
        self.wftree.openDataSignal.connect(self.setWorkDir)
        self.wftree.openDataSignal.connect(self.gmodel.openFrames)
        self.wftree.openDarkSignal.connect(self.setWorkDir)
        self.wftree.openDarkSignal.connect(self.gmodel.openDark)
        self.wftree.applyDarkSignal.connect(self.gmodel.setDarkState)
        self.wftree.openBkgSignal.connect(self.setWorkDir)
        self.wftree.openBkgSignal.connect(self.gmodel.openBkg)
        self.wftree.applyBkgSignal.connect(self.gmodel.setBkgState)
        self.wftree.openFloodSignal.connect(self.setWorkDir)
        self.wftree.openFloodSignal.connect(self.gmodel.openFlood)
        self.wftree.applyFloodSignal.connect(self.gmodel.setFloodState)
        self.wftree.openSplineSignal.connect(self.setWorkDir)
        self.wftree.openSplineSignal.connect(self.gmodel.openSpline)
        self.wftree.applySplineSignal.connect(self.gmodel.setSplineState)

    def connectParamsSignals(self):
        for group in self.wparams.params.children():
            for child in group.children():
                child.sigValueChanging.connect(lambda p, v: self.gmodel.setParameters({p.name(): v}))
                child.sigValueChanged.connect(lambda p, v: self.gmodel.setParameters({p.name(): v}))
                child.sigValueChanged.emit(child, child.value())

    def setWorkDir(self, flist):
        if flist:
            self.workDir = self.wftree.workDir = os.path.dirname(flist[0])

    def closeAll(self):
        self.saveSettings()
        self.gmodelThread.quit()
        self.gmodelThread.wait()

    def saveModelParameters(self, params):
        for param in params:
            self.settings.setValue(f'Model/{param}', params[param])

    def loadModelParameters(self):
        self.loadModelParametersSignal.emit(
            {k.split('/')[-1]: self.settings.value(k) for k in self.settings.allKeys() if k.startswith('Model/')}
        )
