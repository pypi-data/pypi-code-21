#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from .controller import Controller


app = None


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('Dubble')
    app.setOrganizationDomain('esrf.eu')
    app.setApplicationName('GiuSAS')
    ctrl = Controller()
    ctrl.start()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
