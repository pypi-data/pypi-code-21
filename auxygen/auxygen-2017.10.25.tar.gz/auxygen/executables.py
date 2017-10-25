#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


def cryostream():
    from .gui.wcryo import WCryo
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    wcryo = WCryo(None)
    wcryo.loadSettings()
    wcryo.show()
    sys.exit(app.exec_())


def blower():
    from .gui.wblower import WBlower
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    wblower = WBlower(None)
    wblower.loadSettings()
    wblower.show()
    sys.exit(app.exec_())


def wscripted():
    from .gui.wscripted import WScriptEd
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    ww = WScriptEd(None, {})
    ww.loadSettings()
    ww.show()
    sys.exit(app.exec_())


def wseq():
    from .gui.wseq import WSeq
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    ww = WSeq(None)
    ww.loadSettings()
    ww.show()
    sys.exit(app.exec_())


def lakeshore():
    from .gui.wlakeshore import WLakeshore
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    wwlakeshore = WLakeshore(None)
    wwlakeshore.loadSettings()
    wwlakeshore.show()
    sys.exit(app.exec_())
