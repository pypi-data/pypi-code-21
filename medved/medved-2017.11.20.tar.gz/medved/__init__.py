#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from .controller import MedvedController


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('medved')
    c = MedvedController()
    c.start()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
