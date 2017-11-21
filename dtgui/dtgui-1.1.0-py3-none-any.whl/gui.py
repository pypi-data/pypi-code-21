# -*- coding: utf-8 -*-

import sys

import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from qdarkstyle import load_stylesheet_pyqt5

from .control_bar import ControlBar
from .controller import Controller
from .dataviewer import DataViewer
from .error_aware import ErrorAware

class DtGui(QtGui.QMainWindow, metaclass = ErrorAware):

    error_message_signal = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.controller = Controller(parent = self) # TODO: different thread?

        self.controls = ControlBar(parent = self)
        self.controller.raw_data_loaded_signal.connect(self.controls.data_available_signal)
        self.controls.raw_data_path.connect(self.controller.load_raw_data)
        self.controls.export_data_path.connect(self.controller.export_data)
        self.controls.baseline_parameters_signal.connect(self.controller.compute_baseline)

        self.data_viewer = DataViewer(parent = self)
        self.controller.raw_plot_signal.connect(self.data_viewer.plot_raw_data)
        self.controller.baseline_plot_signal.connect(self.data_viewer.plot_baseline)
        self.controller.clear_raw_signal.connect(self.data_viewer.clear_raw_data)
        self.controller.clear_baseline_signal.connect(self.data_viewer.clear_baseline_data)
        self.data_viewer.trim_bounds_signal.connect(self.controller.trim_data_bounds)
        
        self.controls.show_trim_widget.connect(self.data_viewer.toggle_trim_widget)
        self.controls.trim_bounds_signal.connect(self.data_viewer.trim_bounds)

        self.error_message_signal.connect(self.show_error_message)
        self.controller.error_message_signal.connect(self.show_error_message)
        self.data_viewer.error_message_signal.connect(self.show_error_message)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.data_viewer)
        layout.addWidget(self.controls)

        self.central_widget = QtGui.QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle('DTGUI - Baseline-removal via DTCWT')
        self.center_window()
        self.show()

    @QtCore.pyqtSlot()
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @QtCore.pyqtSlot(str)
    def show_error_message(self, msg):
        self.error_dialog = QtGui.QErrorMessage(parent = self)
        self.error_dialog.showMessage(msg)


def run():
    
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet_pyqt5())
    gui = DtGui()
    sys.exit(app.exec_())