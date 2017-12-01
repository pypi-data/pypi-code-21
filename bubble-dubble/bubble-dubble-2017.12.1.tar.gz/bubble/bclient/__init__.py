#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


app = None


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('Dubble')
    app.setOrganizationDomain('esrf.eu')
    app.setApplicationName('bubble')
    from .wbubblec import WBubble
    wbubble = WBubble()
    wbubble.start()
    sys.exit(app.exec())
