#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_graph_Bitcoin                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program displays a graph of Bitcoin values.                             #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help       display help message
    --version        display version and exit
    --currency=TEXT  currency                  [default: EUR]
    --days=INT       number of days to graph   [default: 60]
    --width=INT      interface width           [default: 900]
    --height=INT     interface height          [default: 900]
"""

name    = "denarius_graph_Bitcoin"
version = "2017-03-08T1411Z"
logo    = None

import docopt
import sys

import denarius
import PyQt5.QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QToolTip,
    QVBoxLayout,
    QWidget
)
from PyQt5 import QtGui
import shijian

def main(options):

    currency  = options["--currency"]
    days      = int(options["--days"])
    width     = int(options["--width"])
    height    = int(options["--height"])
    filename  = shijian.propose_filename() + ".png"
    directory = "/tmp/"

    denarius.save_graph_Bitcoin(
        currency  = currency,
        days      = days,
        filename  = filename,
        directory = directory
    )

    application = QApplication(sys.argv)
    window = Window(
        width     = width,
        height    = height,
        filename  = filename,
        directory = directory
    )
    sys.exit(application.exec_())

class Window(QWidget):

    def __init__(
        self,
        filename  = None,
        directory = ".",
        width     = 500,
        height    = 500
        ):

        super(Window, self).__init__()
        self.resize(height, width)
        self.layout = QVBoxLayout(self)
        self.add_image(
            filename  = filename,
            directory = directory
        )
        self.setFixedSize(self.width(), self.height())
        self.setStyleSheet(
        """
        QWidget{
            background: #ffffff;
        }
        """
        )
        self.show()

    def add_image(
        self,
        filename  = None,
        directory = "."
        ):

        image = QtGui.QPixmap(directory + filename)
        image = image.scaled(
                    self.width(),
                    self.height(),
                    PyQt5.QtCore.Qt.KeepAspectRatio
                )
        image_viewer = QLabel()
        image_viewer.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        image_viewer.setPixmap(image)
        self.layout.addWidget(image_viewer)

    def keyPressEvent(
        self,
        event
        ):

        if event.key() == PyQt5.QtCore.Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
