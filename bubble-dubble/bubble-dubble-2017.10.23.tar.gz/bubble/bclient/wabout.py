#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from ..bcommon.utils import get_hg_hash, get_version
from .fixedwidget import FixedWidget
from .ui.ui_wabout import Ui_WBubbleAbout


class WAboutBubble(QtWidgets.QDialog, Ui_WBubbleAbout, FixedWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        lt = self.aboutLabel.text()
        lt = lt.replace('@', get_hg_hash()).replace('#', get_version())
        self.aboutLabel.setText(lt)
        self.setWindowIcon(QtGui.QIcon(':/swiss'))
        self.fixWindow()

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_aboutQtButton_clicked(self):
        QtWidgets.QMessageBox.aboutQt(self)


class UpdateChecker(QtCore.QObject):
    Url = 'https://soft.snbl.eu/_sources/bubble.rst.txt'
    VersionToken = '.. Bubble Versions'
    sigNewVersion = QtCore.pyqtSignal(str, bool)
    sigFinished = QtCore.pyqtSignal()

    def check(self):
        try:
            r = requests.get(self.Url)
        except requests.RequestException as err:
            self.sigNewVersion.emit(str(err), True)
        else:
            self.parse(r.text)
        self.sigFinished.emit()

    def parse(self, text):
        version = get_version()
        strings = []
        put = False
        boldline = False
        first = True
        parsing = False
        for line in text.split('\n'):
            if not line:
                continue
            if line == self.VersionToken:
                parsing = True
                continue
            if parsing:
                if line.startswith('..'):
                    continue
                items = line.split()
                try:
                    newv = [int(i) for i in items[1].split('.')]
                except (IndexError, ValueError):
                    pass
                else:
                    try:
                        put = datetime.datetime(*newv) > datetime.datetime(*[int(i) for i in version.split('.')])
                    except ValueError:
                        pass
                    boldline = True
                if put:
                    line = line.strip()
                    line = line[line.index(" ") + 1:]
                    if boldline:
                        boldline = False
                        if not first:
                            strings.append('</ul>')
                        strings.append(f'<span style="font-weight: bold; color: red">{line}</span>'
                                       f'<ul style="list-style-type:disc">')
                    else:
                        strings.append(f'<li>{line}</li>')
                    first = False
        if strings:
            strings.append('</ul>')
        self.sigNewVersion.emit('\n'.join(strings), False)


class WUpdates(QtWidgets.QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('Bubble updates')
        self.setStandardButtons(self.Ok)
        self.cb = QtWidgets.QCheckBox('Do not check updates automatically')
        self.setCheckBox(self.cb)

    def error(self, text):
        self.setIcon(self.Critical)
        self.setText('There has been an error during update checking')
        self.setInformativeText(text)
        self.exec()

    def success(self, text):
        self.setIcon(self.Information)
        if text:
            self.setText('A new Bubble version is available at <a href=https://soft.snbl.eu/bubble.html#download>'
                         'soft.snbl.eu</a>')
            self.setInformativeText(text)
        else:
            self.setText('There are no new updates of Bubble')
        self.exec()
