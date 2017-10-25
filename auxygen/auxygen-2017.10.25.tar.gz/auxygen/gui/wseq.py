#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import sip
from PyQt5 import QtCore, QtGui, QtWidgets
from .. import utils
from .ui.ui_wseq import Ui_WSeq
from .fixedwidget import FixedWidget


class WSeq(QtWidgets.QDialog, Ui_WSeq, FixedWidget):
    sigClosed = QtCore.pyqtSignal()
    sigNextAction = QtCore.pyqtSignal()
    sigStop = QtCore.pyqtSignal()
    sigSleep = QtCore.pyqtSignal(int)
    sigCryostreamWait = QtCore.pyqtSignal()
    sigBlowerWait = QtCore.pyqtSignal()
    sigLakeshoreWait = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.experimentActions = {}
        self.runningItem = None
        self.dontStart = False
        self.blinkTimer = QtCore.QTimer()
        self.setUI()
        self.sigNextAction.connect(self.startNextAction)
        # noinspection PyUnresolvedReferences
        self.blinkTimer.timeout.connect(self.blinkIcon)
        self.runButton.setEnabled(False)
        self.stopButton.setEnabled(False)

    def setUI(self):
        self.setupUi(self)
        style = QtWidgets.QApplication.style()
        self.upButton.setIcon(style.standardIcon(style.SP_ArrowUp))
        self.downButton.setIcon(style.standardIcon(style.SP_ArrowDown))
        self.clearButton.setIcon(style.standardIcon(style.SP_DialogResetButton))
        self.removeButton.setIcon(style.standardIcon(style.SP_DialogCancelButton))

    def blinkIcon(self):
        if self.runningItem is None:
            return
        if self.runningItem.icon(0).isNull():
            icon = QtGui.QIcon(':/macro')
        else:
            icon = QtGui.QIcon()
        self.runningItem.setIcon(0, icon)

    def isRunningItemLast(self):
        if self.runningItem is None:
            return False
        nextItemIndex = self.seqTreeWidget.indexOfTopLevelItem(self.runningItem) + 1
        return nextItemIndex >= self.seqTreeWidget.topLevelItemCount()

    def startNextAction(self):
        if self.isRunningItemLast() or self.dontStart:
            return self.stopAllActions()

        self.dontStart = False
        if self.runningItem is None:
            nextItemIndex = 0
            self.runningItem = self.seqTreeWidget.topLevelItem(0)
            if self.runningItem is None:
                return self.stopAllActions()
        else:
            self.runningItem.setIcon(0, QtGui.QIcon(':/macro'))
            nextItemIndex = self.seqTreeWidget.indexOfTopLevelItem(self.runningItem) + 1
            if nextItemIndex >= self.seqTreeWidget.topLevelItemCount():
                return self.stopAllActions()
            self.runningItem = self.seqTreeWidget.topLevelItem(nextItemIndex)

        self.experimentProgressBar.setValue(100.0 * nextItemIndex / len(self.experimentActions))
        currentAction = self.experimentActions[self.runningItem]
        currentAction['signal'].emit(currentAction['action'], self.sigNextAction)

    def closeEvent(self, event):
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSeq/Geometry', self.saveGeometry())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WSeq/Geometry', b''))

    @QtCore.pyqtSlot()
    def on_addActionButton_clicked(self):
        {
            0: lambda: self.sigSleep.emit(self.actionSpinBox.value()),
            1: self.sigCryostreamWait.emit,
            2: self.sigBlowerWait.emit,
            3: self.sigLakeshoreWait.emit,
        }[self.actionsComboBox.currentIndex()]()

    @QtCore.pyqtSlot()
    def on_removeButton_clicked(self):
        for item in self.seqTreeWidget.selectedItems():
            if item != self.runningItem:
                del self.experimentActions[item]
                sip.delete(item)
        if not self.experimentActions:
            self.runButton.setDisabled(True)
            self.stopButton.setDisabled(True)

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        self.dontStart = False
        self.runButton.setDisabled(True)
        self.stopButton.setEnabled(True)
        self.blinkTimer.start(500)
        self.startNextAction()

    @QtCore.pyqtSlot()
    def on_clearButton_clicked(self):
        self.experimentActions = {}
        self.seqTreeWidget.clear()
        self.runButton.setDisabled(True)
        self.stopButton.setDisabled(True)
        self.runningItem = None
        self.calculateTotalTime()

    @QtCore.pyqtSlot()
    def on_upButton_clicked(self):
        item = self.seqTreeWidget.currentItem()
        row = self.seqTreeWidget.currentIndex().row()
        if row > 0:
            self.seqTreeWidget.takeTopLevelItem(row)
            self.seqTreeWidget.insertTopLevelItem(row - 1, item)
            self.seqTreeWidget.setCurrentItem(item)

    @QtCore.pyqtSlot()
    def on_downButton_clicked(self):
        item = self.seqTreeWidget.currentItem()
        row = self.seqTreeWidget.currentIndex().row()
        if row < self.seqTreeWidget.topLevelItemCount() - 1:
            self.seqTreeWidget.takeTopLevelItem(row)
            self.seqTreeWidget.insertTopLevelItem(row + 1, item)
            self.seqTreeWidget.setCurrentItem(item)

    def stopAllActions(self):
        self.blinkTimer.stop()
        if self.runningItem is not None:
            self.runningItem.setIcon(0, QtGui.QIcon(':/macro'))
            self.runningItem = None
        self.experimentProgressBar.setValue(100)
        self.runButton.setEnabled(True)
        self.stopButton.setDisabled(True)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.dontStart = True
        self.stopAllActions()
        self.sigStop.emit()

    def calculateTotalTime(self):
        totalTime = 0
        for actionItem in self.experimentActions.values():
            for expItem in actionItem['action']:
                for intItem in actionItem['action'][expItem]:
                    if intItem.startswith('Time for action (sec)'):
                        totalTime += float(actionItem['action'][expItem][intItem])
                        break
        days, hours, minutes = utils.calcTime(totalTime)
        if days:
            t = f'Total time:\n{days:d}d {hours:d}h {minutes:d}m'
        elif hours:
            t = f'Total time:\n{hours:d}h {minutes:d}m'
        else:
            t = f'Total time:\n{minutes:d}m'
        self.totalTimeLabel.setText(t)
        return totalTime

    def appendActionToSeqList(self, action, signal=None, afterCurrent=False):
        self.dictToTreeWidgetItem(action, signal)
        if afterCurrent and self.runningItem is not None:
            index = self.seqTreeWidget.indexOfTopLevelItem(self.runningItem) + 1
            lastItemIndex = self.seqTreeWidget.topLevelItemCount() - 1
            lastItem = self.seqTreeWidget.takeTopLevelItem(lastItemIndex)
            self.seqTreeWidget.insertTopLevelItem(index, lastItem)
        self.calculateTotalTime()

    def dictToTreeWidgetItem(self, action, signal=None, parent=None):
        if parent is None:
            parent = self.seqTreeWidget
            disabled = False
            self.runButton.setEnabled(True)
        else:
            disabled = True

        for key in action:
            treeWidgetItem = TreeWidgetItem(parent)
            treeWidgetItem.setDisabled(disabled)
            if not disabled:
                self.experimentActions[treeWidgetItem] = {'action': action, 'signal': signal}
            treeWidgetItem.setText(0, key)
            item = action[key]
            if isinstance(item, dict):
                self.dictToTreeWidgetItem(item, parent=treeWidgetItem)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def on_seqTreeWidget_itemClicked(self, item):
        if item in self.experimentActions:
            currentAction = self.experimentActions[item]
            currentAction['signal'].emit(currentAction['action'], None)


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__uuid = uuid.uuid4()

    def __hash__(self):
        return hash(self.__uuid)
