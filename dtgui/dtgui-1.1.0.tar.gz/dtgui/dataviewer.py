# -*- coding: utf-8 -*-

import numpy as np
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg

class DataViewer(QtGui.QWidget):
    """ Widget displaying raw and baseline-removed data """

    error_message_signal = QtCore.pyqtSignal(str)
    trim_bounds_signal = QtCore.pyqtSignal(float, float)
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.plot_widget = pg.PlotWidget(title = "<font color = 'green'>Raw data</font>, <font color='red'>Baseline</font>", 
                                         labels = {'left': 'Ordinate', 
                                                   'bottom': 'Abscissa'})


        self.raw_data_item = pg.PlotDataItem(symbol = 'o', symbolBrush = pg.mkBrush('g'), 
                                             symbolPen = None, pen = None, symbolSize = 3, name = 'Raw data')
        self.baseline_data_item = pg.PlotDataItem(symbol = 'o', symbolBrush = pg.mkBrush('r'), 
                                                  symbolPen = None, pen = None, symbolSize = 3, name = 'Baseline')
        self.data_bounds_region = pg.LinearRegionItem()
        self.data_bounds_region.hide()

        
        self.plot_widget.addItem(self.raw_data_item)
        self.plot_widget.addItem(self.baseline_data_item)
        self.plot_widget.addItem(self.data_bounds_region)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)
    
    @QtCore.pyqtSlot(bool)
    def toggle_trim_widget(self, toggle):
        if toggle:
            self.data_bounds_region.setBounds(self.raw_data_item.dataBounds(ax = 0))
            self.data_bounds_region.show()
        else: self.data_bounds_region.hide()
    
    @QtCore.pyqtSlot()
    def trim_bounds(self):
        # getRegion() return a 2-tuple of data bounds, not indices
        self.trim_bounds_signal.emit(*self.data_bounds_region.getRegion())
    
    @QtCore.pyqtSlot(object, object)
    def plot_raw_data(self, x, y):
        """
        Plot a raw data.

        Parameters
        ----------
        x, y : ndarray
        """
        self.raw_data_item.setData(x = np.array(x), y = np.array(y))
    
    @QtCore.pyqtSlot()
    def clear_raw_data(self):
        """ Clear raw data from plot """
        self.raw_data_item.clear()
    
    @QtCore.pyqtSlot(object, object)
    def plot_baseline(self, x, y):
        """
        Plot baseline.

        Parameters
        ----------
        x : ndarray
            x of the measurement
        baseline : ndarray
            Baseline of spectral data
        """
        self.baseline_data_item.setData(x = np.array(x), y = np.array(y))

    @QtCore.pyqtSlot()
    def clear_baseline_data(self):
        """ Clear baseline from plot """
        self.baseline_data_item.clear()