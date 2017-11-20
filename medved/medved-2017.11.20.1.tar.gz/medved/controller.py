#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import qtsnbl.version
import qtsnbl.widgets
from .model import MedvedModel
from .wmedeval import QWMEDeval
from . import widgets
try:
    from . import frozen
except ImportError:
    frozen = None


class MedvedController(QtCore.QObject):
    sigCancel = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.move_data_cross = True
        self.move_fourier_cross = True
        self.settings = QtCore.QSettings()
        self.createModel()
        self.createWindows()
        self.connectSignals()

    def createModel(self):
        self.mthread = QtCore.QThread()
        self.model = MedvedModel()
        self.model.moveToThread(self.mthread)

    def loadSettings(self):
        s = self.settings
        self.wmedved.loadSettings(s)
        self.wupdates.loadSettings()

    def saveSettings(self):
        s = self.settings
        self.wmedved.saveSettings(s)
        self.wupdates.saveSettings()

    def createWindows(self):
        self.wmedved = QWMEDeval()
        self.wprogress = widgets.ProgressWindow(self.wmedved)
        version = qtsnbl.version.Version(frozen)
        self.wupdates = qtsnbl.widgets.WUpdates(self.wmedved, version)
        self.wabout = widgets.WAbout(self.wmedved, version.hash, version.string)

    def connectSignals(self):
        self.connectGUISignals()
        self.connectModelSignals()

    def connectGUISignals(self):
        self.wmedved.sigClose.connect(self.closeAll)
        self.wmedved.sigDir.connect(self.wprogress.show)
        self.wmedved.sigDir.connect(self.model.loadData)
        self.wmedved.sigData2Th.connect(self.model.getData2Th)
        self.wmedved.sigDataTime.connect(self.model.getDataTime)
        self.wmedved.sigFourier2Th.connect(self.model.getFourier2Th)
        self.wmedved.sigFourierTime.connect(self.model.getFourierTime)
        self.wmedved.sigUpdateFourierPlot.connect(self.model.getFourierImage)
        self.wmedved.sigUpdateDataPlot.connect(self.model.getDataImage)
        self.wmedved.sigFourierDomain.connect(self.model.setFourierDomain)
        self.wmedved.sigUnits.connect(self.model.setUnits)
        self.wmedved.sigWavelength.connect(self.model.setWavelength)
        self.wmedved.sigOpenFiles.connect(self.model.loadData)
        self.wmedved.sigClean.connect(self.model.cleanData)
        self.wmedved.sigClean.connect(self.clean)
        self.sigCancel.connect(self.model.cancelLoad)
        self.wprogress.sigCancel.connect(self.sigCancel.emit)
        self.wmedved.dataTree.sigItemMoved.connect(self.model.dataOrderChanged)
        self.wmedved.actionAbout.triggered.connect(self.wabout.exec)
        self.wmedved.actionCheckUpdates.triggered.connect(self.wupdates.checkNewVersionByUser)
        self.wabout.buttonUpdate.clicked.connect(self.wupdates.checkNewVersionByUser)
        self.wmedved.widgetData.sig2DMouseLeftClicked.connect(self.refixDataCross)
        self.wmedved.widgetFourier.sig2DMouseLeftClicked.connect(self.refixFourierCross)
        self.wmedved.dataImage.sigBottomAxisRealRangeChanged.connect(self.model.dataChangeRange)
        self.wmedved.fourierImage.sigBottomAxisRealRangeChanged.connect(self.model.fourierChangeRange)

    def connectModelSignals(self):
        self.model.sigLoadingError.connect(self.wmedved.showModelError)
        self.model.sigLoadingError.connect(self.finishedLoad)
        self.model.sigFinishedLoading.connect(self.wmedved.finishedLoad)
        self.model.sigFinishedLoading.connect(self.finishedLoad)
        self.model.sigDataImage.connect(self.plotDataImage)
        self.model.sigFourierImage.connect(self.plotFourierImage)
        self.model.sigVerticalCut.connect(self.wmedved.widgetData.plotVCut)
        self.model.sigPowderPattern.connect(self.wmedved.widgetData.plotHCut)
        self.model.sigFourier2Th.connect(self.showFourier2Th)
        self.model.sigFourierTime.connect(self.showFourierTime)
        self.model.sigLoadProgress.connect(self.wprogress.setValue)
        self.model.sigMaxProgress.connect(self.wprogress.setMaximum)
        self.model.sigProgressName.connect(self.wprogress.setText)
        self.model.sig2ThRange.connect(self.wmedved.dataImage.changeDataBottomRange)
        self.model.sig2ThFRange.connect(self.wmedved.fourierImage.changeDataBottomRange)

    def finishedLoad(self):
        self.wprogress.hide()

    def plotDataImage(self, data, left, bottom):
        page = self.wmedved.page
        self.wmedved.tabSwitched(0)
        self.wmedved.widgetData.plot2DView.setImage(data)
        self.wmedved.widgetData.plot2DView.autoLevels('max')
        self.wmedved.widgetData.plot2DView.rescaleImage()
        self.wmedved.widgetData.plot2DView.leftAxis.setRealRange(left, 0)
        self.wmedved.widgetData.plot2DView.bottomAxis.setRealRange(0, bottom)
        self.wmedved.tabSwitched(page)

    def plotFourierImage(self, data):
        page = self.wmedved.page
        self.wmedved.tabSwitched(1)
        self.wmedved.widgetFourier.plot2DView.setImage(data)
        self.wmedved.widgetFourier.plot2DView.autoLevels('max')
        self.wmedved.widgetFourier.plot2DView.rescaleImage()
        self.wmedved.tabSwitched(page)

    def showFourier2Th(self, units, x, y):
        self.wmedved.widgetFourier.plotVCut(x, y, **self.getPlotParams(units))
        self.wmedved.widgetFourier.ploty.plotItem.axes['bottom']['item'].setTicks(self.getPlotTicks(units))

    def showFourierTime(self, units, x, y):
        self.wmedved.widgetFourier.plotHCut(x, y, **self.getPlotParams(units))
        self.wmedved.widgetFourier.plotx.plotItem.axes['left']['item'].setTicks(self.getPlotTicks(units))

    def getPlotTicks(self, units):
        if units == 'p':
            return [[(-180, '-π'), (-90, '-π/2'), (0, '0'), (90, 'π/2'), (180, 'π')]]

    def getPlotParams(self, units):
        if units == 'p':
            return {'pen': None, 'symbol': 'o'}
        else:
            return {'pen': 'w', 'symbol': None}

    def start(self):
        self.loadSettings()
        self.mthread.start()
        self.wmedved.start()
        self.wupdates.checkNewVersion()

    def closeAll(self):
        self.saveSettings()
        self.sigCancel.emit()
        self.wmedved.hide()
        self.mthread.quit()
        self.mthread.wait()

    def clean(self):
        pass

    def refixDataCross(self):
        self.wmedved.widgetData.fixCross() if self.move_data_cross else self.wmedved.widgetData.moveCross()
        self.move_data_cross = not self.move_data_cross

    def refixFourierCross(self):
        self.wmedved.widgetFourier.fixCross() if self.move_fourier_cross else self.wmedved.widgetFourier.moveCross()
        self.move_fourier_cross = not self.move_fourier_cross
