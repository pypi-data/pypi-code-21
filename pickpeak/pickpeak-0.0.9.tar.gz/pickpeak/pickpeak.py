"""
Pick Peak PyQtGraph
09/2017
"""

import os
os.environ['PYQTGRAPH_QT_LIB']='PyQt5' #Garantee pyqtgraph uses PyQt5

import numpy as np

import myindex

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
from pyqtgraph.dockarea import *

class PickPeak(object):

    def __init__(self, data):

##        self.data = np.load("/home/carlos/git-lab-elettra/pickpeak/pickpeak/forPickPeak1.npy")
        self.data = data
        self.peak_list = []
        self.app = QtGui.QApplication([])

        self.winMain = QtGui.QMainWindow()
        area = DockArea()
        self.winMain.setCentralWidget(area)
        self.winMain.resize(1000,600)
        self.winMain.setWindowTitle('Pick Peak')

        d1 = Dock("Pick Peak", size=(350,))
        d2 = Dock("Table of Peaks", size=(300,))

        area.addDock(d1, 'left')
        area.addDock(d2, 'right')

        # Layouts (PLot and Table)
        self.layout_plot = pg.LayoutWidget()
        self.layout_table = pg.LayoutWidget()
        
        """Plot Area"""
        # Plot Widget
        self.plt = pg.PlotWidget()
        self.plt.setAspectLocked(False)
        self.pltItem = self.plt.getPlotItem()
        self.pltItem.setAspectLocked(False)
        self.plt.setAutoVisible(y=True)
        pen = pg.mkPen('g', width=2)
        curve = self.plt.plot(data, pen=pen)
        
##        self.curvePoint = pg.CurvePoint(curve)
        
##        print help(curve)
        """
        sigPlotChanged(self)           Emitted when the data in this item is updated.  
        sigClicked(self)               Emitted when the item is clicked.
        sigPointsClicked(self, points) Emitted when a plot point is clicked
                                       Sends the list of points under the mouse.
        """
        
        
##        self.plt.addItem(self.curvePoint)        
        # View Box
        self.vb = self.pltItem.vb
        # Label (index, values)
        self.label = QtGui.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignVCenter)
        self.label.setText("x=%0.5f, y=%0.5f"\
                            %(0, 0))
        self.label_curve = pg.TextItem("test", anchor=(0.5, -1.0))
##        self.plt.addItem(self.label_curve)
##        self.label_curve.setParentItem(self.curvePoint)   
        # Button Group for Radio Buttons
        button_group = QtGui.QButtonGroup()
        self.radio_max = QtGui.QRadioButton("Max", self.layout_plot)
        self.radio_max.setChecked(True)
        self.radio_min = QtGui.QRadioButton("Min", self.layout_plot)
        button_group.addButton(self.radio_max)
        button_group.addButton(self.radio_min)
        # Group and Layout Settings for Plot
        group = QtGui.QGroupBox(" ")
        group_layout = QtGui.QHBoxLayout()
        group_layout.addWidget(self.label)
        group_layout.addWidget(self.radio_max)
        group_layout.addWidget(self.radio_min)
        group.setLayout(group_layout)
        
        self.layout_plot.addWidget(group, row=1, col=1)
        self.layout_plot.addWidget(self.plt, row=2, col=1)
        
        # Adding Layout Plot to the Dock 1
        d1.addWidget(self.layout_plot)

        """Table Area"""
        self.table = pg.TableWidget()
        self.horizontal_header = ['x', 'y']
##        self.table.setHorizontalHeaderLabels(horizontal_header)
        self.peak_list = [] # List-of-Lists
        self.table.setData(self.peak_list)

        # Buttons for Table Editing
        button_delete_peak = QtGui.QPushButton("Delete Peak")
        button_delete_peak.clicked.connect(self.deletePeak)
        button_clear_table = QtGui.QPushButton("Clear Table")
        button_clear_table.clicked.connect(self.clearTable)

        # Group and Layout Settings for Table
        group_table = QtGui.QGroupBox(" ")
        group_table_layout = QtGui.QHBoxLayout()
        group_table_layout.addWidget(button_delete_peak)
        group_table_layout.addWidget(button_clear_table)
        group_table.setLayout(group_table_layout)
        
        self.layout_table.addWidget(self.table, row=1, col=1)
        self.layout_table.addWidget(group_table, row=2, col=1)
        
        # Adding Layout Table to the Dock 2
        d2.addWidget(self.layout_table)                

        # Proxy
##        proxy = pg.SignalProxy(self.plt.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.plt.scene().sigMouseClicked.connect(self.mouseClicked)
        self.plt.scene().sigMouseMoved.connect(self.mouseMoved)

        self.plt.keyPressEvent = self.keyPressEventPlot

        curve.sigClicked.connect(self.pltClicked)
        curve.mouseDoubleClickEvent = self.pltClicked

        self.crossHair()
        self.roi()

    def crossHair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plt.addItem(self.vLine)
        self.plt.addItem(self.hLine)
        self.vLine.setVisible(False)
        self.hLine.setVisible(False)
        self.crossIsVisible = False
        

    def roi(self):
        self.roi = pg.ROI([0, 0], [10, 10])
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.plt.addItem(self.roi)
        self.roi.setVisible(False)
        self.roiIsVisible = False
        

    def keyPressEventPlot(self, evt):
        if type(evt) == QtGui.QKeyEvent:    
            if evt.key() == QtCore.Qt.Key_C and self.crossIsVisible == False:
                self.vLine.setVisible(True)
                self.hLine.setVisible(True)
                self.crossIsVisible = True
            elif evt.key() == QtCore.Qt.Key_C and self.crossIsVisible == True:
                self.vLine.setVisible(False)
                self.hLine.setVisible(False)
                self.crossIsVisible = False
            elif evt.key() == QtCore.Qt.Key_R and self.roiIsVisible == False:
                self.roi.setVisible(True)
                self.roiIsVisible = True
                self.roi.setPos([self.mouse_x-(self.roi.size().x()/2),
                                 self.mouse_y-(self.roi.size().y()/2)])
            elif evt.key() == QtCore.Qt.Key_R and self.roiIsVisible == True:
                self.roi.setVisible(False)
                self.roiIsVisible = False               
            

    def mouseMoved(self, evt):
##        print help(evt)
         ## using signal proxy turns original arguments into a tuple
        pos = evt.toPoint()
        if self.plt.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
##            print mousePoint.x(), mousePoint.y()
##            print pos.x(), pos.y()
            index = int(mousePoint.x())
            self.mouse_x = mousePoint.x()
            self.mouse_y = mousePoint.y()
            if index > 0 and index < len(self.data):
                self.label.setText("x=%0.5f, y=%0.5f"\
                                   %(self.mouse_x, self.data[index]))
##                self.curvePoint.setPos(self.data[index])
                self.label_curve.setText("x=%0.2f, y=%0.2f"\
                                   %(index, self.data[index]))
                self.label_curve.setPos(index, self.data[index])
##                self.winMain.setWindowTitle("x=%0.5f, y=%0.5f"\
##                                            %(self.mouse_x, self.data[index]))
            self.vLine.setPos(self.mouse_x)
            self.hLine.setPos(self.mouse_y)

    def pltClicked(self, evt):
        print "plt clicked"
        print "evt", evt
        
            

    def mouseClicked(self, evt):
##        print self.roi.size().x(), self.roi.size().y()
        self.roi.setPos([self.mouse_x-(self.roi.size().x()/2),
                         self.mouse_y-(self.roi.size().y()/2)])

        x0 = self.roi.pos().x()
        roi_size_x = self.roi.size().x()
        x1 = x0 + roi_size_x
        x0 = int(round(x0,0))
        x1 = int(round(x1,0))

        y0 = self.roi.pos().y()
        roi_size_y = self.roi.size().y()
        y1 = y0 + roi_size_y        
        
        y_values = self.data[x0:x1]
        y_values_roi = []
        for y in y_values:
            if y >= y0 and y <= y1:
                y_values_roi = np.append(y_values_roi, y)
                
##        print x0,x1
##        print y0, y1
##        print y_values
##        print y_values_roi
        if self.radio_max.isChecked():
            print "max", y_values_roi.max()
            ind = myindex.myarray(self.data)
            index = ind.index(y_values_roi.max())[0][0]
            print "index", index
            if [index, "%0.5f"%y_values_roi.max()] in self.peak_list:
                print "Peak already picked"
            else:
                self.peak_list.append([index, "%0.5f"%y_values_roi.max()])
        elif self.radio_min.isChecked():
            print "min", y_values_roi.min()
            ind = myindex.myarray(self.data)
            index = ind.index(y_values_roi.min())[0][0]
            print "index", index
            if [index, "%0.5f"%y_values_roi.min()] in self.peak_list:
                print "Peak already picked"
            else:
                self.peak_list.append([index, "%0.5f"%y_values_roi.min()])
        print " "
        
        self.table.setData(self.peak_list)
        self.table.setHorizontalHeaderLabels(self.horizontal_header)
        

    def deletePeak(self):
        
        row = self.table.currentRow()
        item = self.table.currentItem()
        if row >= 0:
            x = int(item.text())
            ind = self.peak_list.index([x, "%0.5f"%self.data[x]])
    ##        print ind        
            self.table.removeRow(row)
            del self.peak_list[ind]
        else:
            print "No peak selected in the table to be delete!"

    def clearTable(self):
        self.table.clear()
        self.peak_list = []
        
def pickpeak(data):
    window = PickPeak(data)
    window.winMain.show()
    QtGui.QApplication.instance().exec_()
    return window.peak_list


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        window = PickPeak()
        window.winMain.show()
        QtGui.QApplication.instance().exec_()

print "Done!"
        
    
        


    
        

        
        
