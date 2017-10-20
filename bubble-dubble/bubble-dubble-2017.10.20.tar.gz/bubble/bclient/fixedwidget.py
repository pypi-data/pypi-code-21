#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui


class FixedWidget(QtWidgets.QWidget):
    def _fixWindow(self):
        self.resize(0, 0)
        geometry = self.geometry()
        self.setFixedSize(geometry.width(), geometry.height())

    def fixWindow(self):
        QtCore.QTimer.singleShot(0, self._fixWindow)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


def clearButtonSlot(widget: QtCore.QObject):
    button = QtCore.QObject.sender(widget)
    bname = button.objectName()
    end = bname.find('ClearButton')
    widget.__dict__[f'{bname[:end]}LineEdit'].setText('')
