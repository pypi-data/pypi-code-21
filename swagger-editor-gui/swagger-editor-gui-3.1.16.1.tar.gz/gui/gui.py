#!/usr/bin/env python
import sys
from PyQt5.QtCore import pyqtSlot, Qt, QUrl, QFileInfo, QCoreApplication, QObject, pyqtSignal,QVariant
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5 import QtWidgets, QtWebEngine, QtWebEngineWidgets, QtWebChannel, QtWebSockets
import signal
from os import path
import os

# exit on ctrl-c
signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication(sys.argv)
    QtWebEngine.QtWebEngine.initialize()

    we = QtWebEngineWidgets.QWebEngineView()

    # set initial size
    dw = QDesktopWidget()
    we.resize(dw.availableGeometry().size()*.7)
    we.setWindowTitle('Swagger Editor')

    pkg_dir = os.path.dirname(os.path.abspath(__file__))

    root_file = path.join(pkg_dir,'index.html')
    lf = QFileInfo(root_file)

    we.load(QUrl.fromLocalFile(lf.absoluteFilePath()))
    we.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
