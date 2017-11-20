#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore, QtGui, QtWidgets
import qtsnbl.widgets
from . import widgets
from .ui.ui_wmedeval import Ui_MEDeval


class QWMEDeval(QtWidgets.QMainWindow, Ui_MEDeval):
    FourierComponents = 'Real', 'Imaginary', 'Amplitude', 'Phase'
    sigClose = QtCore.pyqtSignal()
    sigDir = QtCore.pyqtSignal(str)
    sigCancelLoading = QtCore.pyqtSignal()
    sigUpdateFourierPlot = QtCore.pyqtSignal()
    sigUpdateDataPlot = QtCore.pyqtSignal()
    sigOpenFiles = QtCore.pyqtSignal(list)
    sigClean = QtCore.pyqtSignal()
    sigWavelength = QtCore.pyqtSignal(str)
    sigData2Th = QtCore.pyqtSignal(int)
    sigDataTime = QtCore.pyqtSignal(int)
    sigFourier2Th = QtCore.pyqtSignal(int)
    sigFourierTime = QtCore.pyqtSignal(int)
    sigUnits = QtCore.pyqtSignal(str)
    sigFourierDomain = QtCore.pyqtSignal(str)
    sigDataY = QtCore.pyqtSignal(int)
    sigDataX = QtCore.pyqtSignal(int)
    sigFourierY = QtCore.pyqtSignal(int)
    sigFourierX = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.page = 0
        self.setUI()
        self.connectSignals()

    def start(self):
        self.tabSwitched(0)
        self.uncheckAllXActionsBut(self.action2Theta)
        self.uncheckAllYActionsBut(self.actionReal)
        self.show()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.dataImage.sigY.connect(self.showCurrentDataTreeItem)
        self.fourierImage.sigY.connect(self.showCurrentFourierTreeItem)
        self.tabWidget.currentChanged[int].connect(self.tabSwitched)
        self.wlEdit.textChanged[str].connect(self.sigWavelength.emit)
        self.dataImage.sigY.connect(self.sigDataTime.emit)
        self.fourierImage.sigY.connect(self.sigFourierTime.emit)
        self.sigDataY.connect(self.sigDataTime.emit)
        self.sigDataY.connect(self.dataImage.setHLine)
        self.dataImage.sigX.connect(self.sigData2Th.emit)
        self.fourierImage.sigX.connect(self.sigFourier2Th.emit)
        self.dataTree.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(self.dataTreeItemClicked)
        self.fourierTree.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(self.fourierTreeItemClicked)
        self.dataTree.sigItemMoved.connect(self.dataItemMoved)
        self.widgetData.sigXMouseMoved.connect(self.showStatusBarMessage)
        self.widgetData.sigYMouseMoved.connect(self.showStatusBarMessage)

    def showStatusBarMessage(self, x, y):
        self.statusbar.showMessage(f'x = {x:.3g}; y = {y:.3g}')

    def dataItemMoved(self, old, new):
        # self.items.insert(new, self.items.pop(old))
        pass

    def dts(self):
        if self.action2Theta.isChecked():
            return 't'
        elif self.actionD.isChecked():
            return 'd'
        elif self.actionD2.isChecked():
            return 'dd'
        else:
            self.uncheckAllXActionsBut(self.action2Theta)
            return 't'

    def cfd(self):
        if self.actionAmplitude.isChecked():
            return 'a'
        elif self.actionImaginary.isChecked():
            return 'i'
        elif self.actionReal.isChecked():
            return 'r'
        elif self.actionPhase.isChecked():
            return 'p'
        else:
            self.uncheckAllYActionsBut(self.actionReal)
            return 'r'

    def tabSwitched(self, page):
        if page == 0:
            self.widgetFourier.setVisible(False)
            self.widgetData.setVisible(True)
        elif page == 1:
            self.widgetData.setVisible(False)
            self.widgetFourier.setVisible(True)
        self.page = page

    def setUI(self):
        self.setupUi(self)
        self.tabWidget = QtWidgets.QTabWidget()
        self.dock.setWidget(self.tabWidget)
        self.setData()
        self.setFourier()
        self.widgetMain = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.widgetData)
        layout.addWidget(self.widgetFourier)
        self.widgetMain.setLayout(layout)
        self.setCentralWidget(self.widgetMain)
        self.toolBar.addSeparator()
        self.wlEdit = QtWidgets.QLineEdit()
        self.wlEdit.setValidator(QtGui.QDoubleValidator())
        self.wlEdit.setMaximumWidth(200)
        self.toolBar.insertWidget(self.actionD, self.wlEdit)
        style = QtWidgets.QApplication.style()
        self.actionClean.setIcon(style.standardIcon(style.SP_DialogResetButton))
        self.actionOpenFiles.setIcon(style.standardIcon(style.SP_FileIcon))
        self.actionOpenDir.setIcon(style.standardIcon(style.SP_DirIcon))

    def updateStatusBar(self, x, y):
        self.statusbar.showMessage(f'x = {x:.6f}, y = {y:.6f}')

    def setData(self):
        self.dataImage = widgets.CustomImageView()
        self.widgetData = qtsnbl.widgets.CutSliceWidget(imageview=self.dataImage)
        self.widgetData.ploty.getPlotItem().invertY()
        self.dataTree = widgets.TreeWidget()
        self.dataTree.setHeaderLabel('Patterns')
        self.tabWidget.addTab(self.dataTree, 'Data')

    def setFourier(self):
        self.fourierImage = widgets.CustomImageView()
        self.widgetFourier = qtsnbl.widgets.CutSliceWidget(imageview=self.fourierImage)
        self.widgetFourier.ploty.getPlotItem().invertY()
        self.fourierTree = QtWidgets.QTreeWidget()
        self.fourierTree.setHeaderLabel('Harmonics')
        self.tabWidget.addTab(self.fourierTree, 'Fourier')

    def saveSettings(self, s):
        s.setValue('WMedved/Geometry', self.saveGeometry())
        s.setValue('WMedved/State', self.saveState())
        s.setValue('WMedved/lastdir', self.lastdir)
        s.setValue('WMedved/wavelength', self.wlEdit.text())
        self.widgetFourier.saveSettings()
        self.widgetData.saveSettings()

    def loadSettings(self, s):
        self.restoreGeometry(s.value('WMedved/Geometry', b''))
        self.restoreState(s.value('WMedved/State', b''))
        self.lastdir = s.value('WMedved/lastdir', '', str)
        self.wlEdit.setText(s.value('WMedved/wavelength', '0.7', str))
        self.widgetFourier.loadSettings()
        self.widgetData.loadSettings()

    def closeEvent(self, event):
        self.sigClose.emit()
        super().closeEvent(event)

    def finishedLoad(self, t, ft, d, fd, files):
        self.dataImage.setMaxX(d)
        self.dataImage.setMaxY(t)
        self.fourierImage.setMaxX(fd)
        self.fourierImage.setMaxY(ft)
        self.dataTree.takeTopLevelItem(0)
        mainItem = QtWidgets.QTreeWidgetItem()
        # mainItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled)
        mainItem.setText(0, 'Data files')
        self.dataTree.addTopLevelItem(mainItem)
        self.items = []
        for i, f in enumerate(files):
            item = QtWidgets.QTreeWidgetItem()
            # item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
            item.setText(0, f'{i}: {f}')
            mainItem.addChild(item)
            self.items.append(item)
        for _ in self.FourierComponents:
            self.fourierTree.takeTopLevelItem(0)
        self.fitems = {}
        for name in self.FourierComponents:
            mainItem = QtWidgets.QTreeWidgetItem(self.fourierTree)
            mainItem.setText(0, name)
            self.fitems[name] = []
            for i in range(ft):
                item = QtWidgets.QTreeWidgetItem(mainItem)
                item.setText(0, f'Harmonic {i:d}')
                self.fitems[name].append(item)
            self.fourierTree.addTopLevelItem(mainItem)

    @QtCore.pyqtSlot()
    def on_actionOpenDir_triggered(self):
        dire = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', directory=self.lastdir)
        if dire:
            self.lastdir = dire
            self.sigDir.emit(dire)

    def showCurrentDataTreeItem(self, value):
        if value < len(self.items):
            self.dataTree.setCurrentItem(self.items[value])

    def showCurrentFourierTreeItem(self, value):
        if self.fitems:
            for component in self.FourierComponents:
                if self.__dict__[f'action{component}'].isChecked() and value < len(self.fitems[component]):
                    self.fourierTree.setCurrentItem(self.fitems[component][value])
                    return

    def dataTreeItemClicked(self, item):
        try:
            self.sigDataY.emit(self.items.index(item))
        except ValueError:
            pass

    def fourierTreeItemClicked(self, item):
        text = item.text(0)
        if text not in self.FourierComponents:
            text = item.parent().text(0)
            self.fourierSliders.timeSlider.setSliderPosition(self.fitems[text].index(item))
        self.uncheckAllYActionsBut(self.__dict__[f'action{text}'])

    @QtCore.pyqtSlot()
    def on_actionReal_triggered(self):
        self.uncheckAllYActionsBut(self.actionReal)

    @QtCore.pyqtSlot()
    def on_actionImaginary_triggered(self):
        self.uncheckAllYActionsBut(self.actionImaginary)

    @QtCore.pyqtSlot()
    def on_actionPhase_triggered(self):
        self.uncheckAllYActionsBut(self.actionPhase)

    @QtCore.pyqtSlot()
    def on_actionAmplitude_triggered(self):
        self.uncheckAllYActionsBut(self.actionAmplitude)

    @QtCore.pyqtSlot()
    def on_action2Theta_triggered(self):
        self.uncheckAllXActionsBut(self.action2Theta)

    @QtCore.pyqtSlot()
    def on_actionD_triggered(self):
        self.uncheckAllXActionsBut(self.actionD)

    @QtCore.pyqtSlot()
    def on_actionD2_triggered(self):
        self.uncheckAllXActionsBut(self.actionD2)

    def uncheckAllYActionsBut(self, action):
        actions = self.actionReal, self.actionPhase, self.actionAmplitude, self.actionImaginary
        self.uncheckAllActionsBut(action, actions)

    def uncheckAllXActionsBut(self, action):
        actions = self.action2Theta, self.actionD, self.actionD2
        self.uncheckAllActionsBut(action, actions)

    def uncheckAllActionsBut(self, action, actions):
        for act in actions:
            if action != act:
                act.setChecked(False)
        action.setChecked(True)
        self.sigUnits.emit(self.dts())
        self.sigFourierDomain.emit(self.cfd())
        self.sigUpdateFourierPlot.emit()
        self.sigUpdateDataPlot.emit()

    def showModelError(self, msg):
        QtWidgets.QMessageBox.critical(self, 'Error', msg)

    @QtCore.pyqtSlot()
    def on_actionQuit_triggered(self):
        self.close()

    @QtCore.pyqtSlot(bool)
    def on_dock_visibilityChanged(self, visible):
        self.actionListDock.setChecked(visible)

    @QtCore.pyqtSlot(bool)
    def on_actionListDock_toggled(self, checked):
        self.dock.setVisible(checked)

    @QtCore.pyqtSlot()
    def on_actionOpenFiles_triggered(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open data files', self.lastdir)[0]
        if files:
            self.sigOpenFiles.emit(files)
            self.lastdir = os.path.dirname(files[0])

    @QtCore.pyqtSlot()
    def on_actionClean_triggered(self):
        self.sigClean.emit()
        self.fourierTree.clear()
        self.dataTree.clear()
        self.widgetData.clear()
        self.widgetFourier.clear()
        self.items.clear()
        self.fitems.clear()
