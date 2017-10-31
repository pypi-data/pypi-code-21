

"""
Scan Alignment + Normalization Project - PyQtGraph version
stxmProc - 30/10/2017
"""

import os
os.environ['PYQTGRAPH_QT_LIB']='PyQt5' #Garantee pyqtgraph uses PyQt5

import matplotlib.image as mpimg

import h5py as h5

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
from pyqtgraph.dockarea import *
import pyqtgraph.exporters

import tifffile as tf

import numpy as np

from myRoll import myRoll

class MyApp(object):

    def __init__(self):

        self.roll = myRoll()

        self.linesel = 0 # The line the selection is placed
        self.winPlot = None # Window that display the image
        self.plt = None
        self.img = None # The Image Item that contains the Image opened
        self.data = None
        self.data_orig = None
        self.roi = None
        self.list_roi = []
        self.ssvfpath = '' # The path of the original ssv file
        self.fpath = '' # The path of file opened
        self.fname = '' # The name of file opened
        self.fformat = '' # The format of file opened
        self.transformation = None
        self.next_transformation = [] # List to store the transformation history for DO command
        self.preview_transformation = [] # List to store the transformations history for UNDO command

        
        self.app = QtGui.QApplication([])
        
        ## Configuring Main Window and Dock Area
        self.winMain = QtGui.QMainWindow()
        area = DockArea()
        self.winMain.setCentralWidget(area)
        self.winMain.resize(1000,600)
        self.winMain.setWindowTitle('STXM Processing')
        

        d1 = Dock("Image", size=(350,))
        d2 = Dock("Tools")

        area.addDock(d1, 'right')
        area.addDock(d2, 'left')
        

        ## Configuring the Plot Area
        self.winPlot = pg.GraphicsWindow(title="STXM Processing")
        self.plt = self.winPlot.addPlot()
##        print help(self.plt)
        print self.plt.geometry()
        print self.plt.contentsRect()
        print self.plt.rect()
        print self.plt.viewRect()
##        self.plt.autoRange()
##        self.plt.enableAutoRange()
##        self.plt.disableAutoRange()
##        self.plt.setAspectLocked(True)
##        self.plt.setAutoPan(False)
##        self.plt.setAutoVisible(True)
##        self.plt.setDownsampling(mode='mean')
##        self.plt.enableAutoScale()
        self.img = pg.ImageItem()
        self.plt.addItem(self.img)
##        self.winPlot.show()

        """All Buttons """
        winButton = QtGui.QWidget()

        """File"""        
        fileGroup = QtGui.QGroupBox("File")
        ##        fileGroup.setCheckable(True)        

        button_load = QtGui.QPushButton("Load")
        button_load.clicked.connect(self.openFile)
        
        button_save = QtGui.QPushButton("Save")
        button_save.clicked.connect(self.saveProject)
        
        button_export = QtGui.QPushButton("Export")
        button_export.clicked.connect(self.exportImage)

        """Scan Alignment"""        
        alignGroup = QtGui.QGroupBox("Scan Alignment")

        button_selection_line = QtGui.QPushButton("Set Selection Line")
        button_selection_line.clicked.connect(self.setSelectionLine)
        self.spin_selection_line = QtGui.QSpinBox()
##        self.spin_selection_line.setFocusProxy(self.winPlot)
        self.spin_selection_line.setValue(1)
        self.spin_selection_line.setAlignment(QtCore.Qt.AlignHCenter)        
        
        button_selection_height = QtGui.QPushButton("Set Selection Height")
        button_selection_height.clicked.connect(self.setSelectionHeight)        
        self.spin_selection_height = QtGui.QSpinBox()
        self.spin_selection_height.setSingleStep(1)
        self.spin_selection_height.setValue(1)
        self.spin_selection_height.setAlignment(QtCore.Qt.AlignHCenter)      
        
        label_shift_step =  QtGui.QPushButton("Set Shift Step")
        self.spin_shift_step = QtGui.QSpinBox()
        self.spin_shift_step.setSingleStep(1)
        self.spin_shift_step.setValue(1)
        self.spin_shift_step.setAlignment(QtCore.Qt.AlignHCenter)

        """Normalization"""
        self.normGroup = QtGui.QGroupBox("Normalization")
        self.normGroup.setCheckable(True)
        self.normGroup.setChecked(False)
        print self.normGroup.isChecked()
        
        button_add_roi = QtGui.QPushButton("Add ROI")
        button_add_roi.clicked.connect(self.addRoi)
        button_normalize_image = QtGui.QPushButton("Normalize Image")
        button_normalize_image.clicked.connect(self.normImage)
        button_clear_roi = QtGui.QPushButton("Clear ROI")
        button_clear_roi.clicked.connect(self.clearRoi)
        

        """Edit"""
        editGroup = QtGui.QGroupBox("Edit")

        button_reset = QtGui.QPushButton("Reset Image")
        button_reset.clicked.connect(self.resetImage)
        button_do = QtGui.QPushButton("Redo")
        button_do.clicked.connect(self.redo)
        button_undo = QtGui.QPushButton("Undo")
        button_undo.clicked.connect(self.undo)


        """Layouts"""

        fileLayout = QtGui.QVBoxLayout()
        fileLayout.addWidget(button_load)
        fileLayout.addWidget(button_save)
        fileLayout.addWidget(button_export)
        fileGroup.setLayout(fileLayout)
        
        alignLayout = QtGui.QVBoxLayout()
        alignLayout.addWidget(button_selection_line)
        alignLayout.addWidget(self.spin_selection_line)
        alignLayout.addWidget(button_selection_height)
        alignLayout.addWidget(self.spin_selection_height)
        alignLayout.addWidget(label_shift_step)
        alignLayout.addWidget(self.spin_shift_step)        
        alignGroup.setLayout(alignLayout)

        normLayout = QtGui.QVBoxLayout()
        normLayout.addWidget(button_add_roi)
        normLayout.addWidget(button_normalize_image)
        normLayout.addWidget(button_clear_roi)
        self.normGroup.setLayout(normLayout)        

        editLayout = QtGui.QVBoxLayout()
        editLayout.addWidget(button_reset)
        editLayout.addWidget(button_do)
        editLayout.addWidget(button_undo)
        editGroup.setLayout(editLayout)

        buttonsLayout = QtGui.QVBoxLayout()
        buttonsLayout.addWidget(fileGroup)
        buttonsLayout.addWidget(alignGroup)
        buttonsLayout.addWidget(self.normGroup)
        buttonsLayout.addWidget(editGroup)        
        winButton.setLayout(buttonsLayout)     

        ## Adding widgets into the Dock Area
        d1.addWidget(self.winPlot)
        d2.addWidget(winButton)        

        self.winPlot.keyPressEvent = self.plotKeyPressEvent
        alignGroup.keyPressEvent = self.alignGroupKeyPressEvent
##        self.spin_selection_line.keyPressEvent = self.alignGroupKeyPressEvent

        self.spin_selection_line.valueChanged['int'].connect(self.setSelectionLine)
        self.spin_selection_height.valueChanged['int'].connect(self.setSelectionHeight)

        self.normGroup.clicked.connect(self.canNormalize)       

    def plotKeyPressEvent(self, event):       
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Space:                
                print "key space"
            elif event.key() == QtCore.Qt.Key_Control:
                print "key control"
            elif event.key() == QtCore.Qt.Key_Left:
                print "key left"
                self.shiftLineLeft(self.linesel, int(self.roi.size().y()), self.spin_shift_step.value())
            elif event.key() == QtCore.Qt.Key_Right:
                print "key right"
                self.shiftLineRight(self.linesel, int(self.roi.size().y()), self.spin_shift_step.value())
            
            elif event.key() == QtCore.Qt.Key_Up:
##                print "key up"
                self.linesel += 1                
                self.selectLine()
##                self.roi.setPos([0, self.linesel])
            elif event.key() == QtCore.Qt.Key_Down:
##                print "key down"
                self.linesel -= 1
                self.selectLine()
##                self.roi.setPos([0, self.linesel])

    def alignGroupKeyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                print "key return"
                self.winPlot.setFocus()
                

    def openFile(self):
        if self.fpath != '':
            self.fpath = ''
            self.fname = ''
            self.fformat = ''
        print "openFile"
        self.fpath = QtGui.QFileDialog.getOpenFileName(self.winMain, 'Open File', '',\
                                                       "Images (*.png *.jpg *.tiff *.tif *.ssv);;HDF files (*.h5 *.hdf5);;All Files (*.*)")
        self.fpath = self.fpath[0]        
        self.fname = self.fpath[self.fpath.rindex('/')+1::]
        self.fformat = self.fpath[self.fpath.rindex('.')+1::]
        
        self.loadFile()


    def saveProject(self):
        if self.fformat == "ssv":
            savename = QtGui.QFileDialog.getSaveFileName(self.winMain, 'Save File', '',\
                                                             "(*.h5);; (*.hdf5)")

            fpath = str(savename[0])
            name = fpath[fpath.rindex("/")+1::]
            fpath = fpath[0:fpath.rindex("/")+1]
            saveformat = str(savename[1])
            saveformat = saveformat[saveformat.rindex('.'):-1]
            prefix = "scanProc_"

            with h5.File(fpath + prefix + name + saveformat, "w") as hf:
                hf.create_dataset("stxm", data=self.data_orig, dtype=np.int32)                            
                hf["stxm"].attrs["filepath"] = self.fpath
                hf.create_dataset("transformation", data=self.transformation, dtype=np.int16)
                hf.close()
                            
        elif self.fformat == "h5" or self.fformat == "hdf5":
            savename = QtGui.QFileDialog.getSaveFileName(self.winMain, 'Save File', '',\
                                                             "(*.h5);; (*.hdf5)")

            fpath = str(savename[0])
            name = fpath[fpath.rindex("/")+1::]
            fpath = fpath[0:fpath.rindex("/")+1]
            saveformat = str(savename[1])
            saveformat = saveformat[saveformat.rindex('.'):-1]
            prefix = "scanProc_"
            
            with h5.File(fpath + prefix + name + saveformat, "w") as hf:
                hf.create_dataset("stxm", data=self.data_orig, dtype=np.int32)                            
                hf["stxm"].attrs["filepath"] = self.ssvfpath
                hf.create_dataset("transformation", data=self.transformation, dtype=np.int16)
                hf.close()
        else:
            reply = QtGui.QMessageBox.information(self.winMain, "Warning",
"""The file loaded must be of ssv or hdf5 type in order to Save a Project.
If you want ot export the image as tif, jpg, png, etc use the Export button.
""")


    def exportImage(self):
        print "Export image as"
        self.roi.setVisible(False)
        exportname = QtGui.QFileDialog.getSaveFileName(self.winMain, 'Export File', '',\
                                                       "(*.png);;(*.tif);;(*.jpg);;(*.bmp);;(*.ico);;(*.jpeg);;(*.ppm);;(*.tiff);;(*.xbm);;(*.xpm);;(*.ssv)")
        fpath = str(exportname[0])
        fformat = str(exportname[1])        
        fformat = fformat[fformat.rindex('.'):-1]        
        exportname = fpath + fformat        

        if fformat == ".tif" or fformat == ".tiff":
            tf.imsave(exportname, self.img.image)
        elif fformat == ".ssv":
            np.savetxt(exportname, self.img.image, fmt='%.7d', delimiter='  ')
        else:
            exporter = pg.exporters.ImageExporter(self.img)       
            exporter.export(exportname)

        self.roi.setVisible(True)
        

    def loadFile(self):
        if self.fformat == 'ssv':
            print "open ssv"
            self.data = np.genfromtxt(self.fpath, dtype=np.int32)
            self.data_orig = np.genfromtxt(self.fpath, dtype=np.int32)
            self.transformation = np.zeros(self.data.shape[1], dtype=np.int16) # Setting the transformation array to keep track of the shifts done on the image
        elif self.fformat == 'jpg' or self.fformat == 'png':
            print "open jpg, png"
            self.data = mpimg.imread(self.fpath)
            self.data_orig = mpimg.imread(self.fpath)
            self.transformation = np.zeros(self.data.shape[1], dtype=np.int16)
        elif self.fformat == 'tiff' or self.fformat == 'tif':
            print "open tiff, tif"
            self.data = tf.imread(self.fpath)
            self.data_orig = tf.imread(self.fpath)
            self.transformation = np.zeros(self.data.shape[1], dtype=np.int16)
        elif self.fformat == 'h5' or self.fformat == 'hdf5':
            print "open h5, hdf5"
            with h5.File(self.fpath, "r") as hf:
                self.data = hf["stxm"].value
                self.data_orig = hf["stxm"].value
                self.ssvfpath = hf["stxm"].attrs["filepath"]
                self.transformation = np.zeros(self.data.shape[1], dtype=np.int16)
                self.transformation = hf["transformation"].value                
                hf.close()
            self.data = self.roll.transfRoll(self.data, self.transformation, 0)
        else:
            print "Unsupported file format!"
            reply = QtGui.QMessageBox.information(self.winMain, "Warning",
"""Unsupported file format!
""")
            self.openFile()

        # Setting the image data in the Image Item
        self.img.setImage(self.data)
        print self.data.shape
        self.plt.setTitle(self.fname)
        # Adding a rectangle ROI as selection area
        if self.roi != None:
            self.plt.removeItem(self.roi)
            self.roi = None
        self.pen = pg.mkPen(color='r', width=0.5)
        self.roi = pg.ROI([0, self.linesel],[self.data.shape[0],1], pen=self.pen, movable=False) # pg.ROI([x0, y0],[x1,y1])
        self.plt.addItem(self.roi)
        if self.normGroup.isChecked():
            self.roi.setVisible(False)
        # Setting the spin boxes ranges
        self.spin_selection_line.setRange(0, self.data.shape[1])
        self.spin_selection_height.setRange(1, self.data.shape[1])
        self.spin_shift_step.setRange(1, self.data.shape[0])

        self.next_transformation = []
        self.preview_transformation = []

        if len(self.list_roi) > 0:
            self.clearRoi()
        

    def setSelectionLine(self):
        self.linesel = self.spin_selection_line.value()
        self.selectLine()        

    
    def selectLine(self):
        if (self.linesel + self.roi.size().y()) > self.data.shape[1]:
            self.linesel = 0
            self.roi.setPos([0,self.linesel])
        elif self.linesel < 0:
            self.linesel = (self.data.shape[1]) - self.roi.size().y()
            self.roi.setPos([0,self.linesel])
        else:
            self.roi.setPos([0, self.linesel])
        self.spin_selection_line.setValue(self.linesel)
        

    def setSelectionHeight(self):
        size = self.roi.size()
        size.setY(self.spin_selection_height.value())
        self.roi.setSize(size)
##        print help(size)         
##        print type(size)       


    def shiftLineRight(self, line, numlines, shift):
        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.transformation)
        self.preview_transformation.append(tr)
        
        self.data[:, line:(line+numlines)] = self.roll.npRoll(self.data[:, line:(line+numlines)], shift=shift, axis=0)
        self.transformation[line:(line+numlines)] += shift
        
        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.transformation)
        self.next_transformation.append(tr)
        
        for i in range(line, line+numlines):
            if self.transformation[i] >= self.data.shape[0]:
                self.transformation[i] = self.transformation[i]-self.data.shape[0]

        self.img.setImage(self.data)
        

    def shiftLineLeft(self, line, numlines, shift):
        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.transformation)
        self.preview_transformation.append(tr)

        self.data[:, line:(line+numlines)] = self.roll.npRoll(self.data[:, line:(line+numlines)], shift=-shift, axis=0)
        self.transformation[line:(line+numlines)] -= shift

        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.transformation)
        self.next_transformation.append(tr)

        for i in range(line, line+numlines):
            if self.transformation[i] <= -self.data.shape[0]:
                self.transformation[i] = self.data.shape[0] + self.transformation[i]
                
        self.img.setImage(self.data)

    def canNormalize(self):
        print "can normalize"
        print self.normGroup.isChecked()
        if self.normGroup.isChecked():
            self.roi.setVisible(False)
##            self.plt.setAutoPan(False)
        else:
            self.roi.setVisible(True)
            self.winPlot.setFocus()
##            self.plt.setAutoPan(True)
        

    def addRoi(self):
##        print "Add ROI"
##        print self.plt.geometry()
##        print self.plt.contentsRect()
##        print self.plt.rect()
##        print self.plt.viewRect()
        rect = QtCore.QRectF(0, 0, self.data.shape[0], self.data.shape[1])
##        print rect
        pen = pg.mkPen(color='g', width=0.5)
        roi = pg.ROI([self.data.shape[0]/2-10, self.data.shape[1]/2-10],
                     [20, 20],
                     pen=pen, removable=True, maxBounds=rect)        
        roi.addScaleHandle([0, 0], [1, 1])
        roi.addScaleHandle([1, 1], [0, 0])
        roi.sigRemoveRequested.connect(self.delRoi)
        
##        roi.forgetViewBox()         
##        print help(roi)
        self.list_roi.append(roi)
        self.plt.addItem(roi)

    def delRoi(self, roi):
        print "del ROI"        
        self.plt.removeItem(roi)        
        self.list_roi.remove(roi)
        
        
    def normImage(self):
        print "Normalize Image"
        nfs = []
        for roi in self.list_roi:
            x0 = roi.pos().x()
            roi_size_x = roi.size().x()
            x1 = x0 + roi_size_x
            x0 = int(round(x0,0))
            x1 = int(round(x1,0))

            y0 = roi.pos().y()
            roi_size_y = roi.size().y()
            y1 = y0 + roi_size_y
            y0 = int(round(y0,0))
            y1 = int(round(y1,0))
            
            print self.data[ x0:x1, y0:y1 ].mean()
            nf = self.data[ x0:x1, y0:y1 ].mean() / self.data[ x0:x1, : ]
            nfs.append(nf.mean(axis=0))
        nfs = np.asarray(nfs)
        print nfs.mean(1).shape, nfs.mean(0).shape
        print self.data[ x0:x1, : ].mean()
        print nf.shape, nf.mean(axis=1).shape, nf.mean(axis=0).shape, nf.mean().shape
        
        print nf.mean(axis=0), nfs.mean(0)
        print 
        self.data = self.data * nfs.mean(axis=0)

        self.img.setImage(self.data)

    def clearRoi(self):
        print "Clear ROI"
        for roi in self.list_roi:
            self.plt.removeItem(roi)
        self.list_roi = []

    def resetImage(self):
        self.loadFile()


    def redo(self):
##        print "redo"
##        print "before", len(self.preview_transformation), len(self.next_transformation)        

        dt = np.zeros(self.data_orig.shape)
        np.copyto(dt, self.data_orig)
##        print self.next_transformation[-1]
        self.data = self.roll.transfRoll(dt, self.next_transformation[-1], 0)
        self.img.setImage(self.data)
        
        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.next_transformation[-1])

        self.preview_transformation.append(tr)        
        self.transformation = tr

        del self.next_transformation[-1]        

##        print "after", len(self.preview_transformation), len(self.next_transformation)
        

    def undo(self):
##        print "undo"
##        print "before", len(self.preview_transformation), len(self.next_transformation)
        
        dt = np.zeros(self.data_orig.shape)
        np.copyto(dt, self.data_orig)
        
        self.data = self.roll.transfRoll(dt, self.preview_transformation[-1], 0)
        self.img.setImage(self.data)

        tr = np.zeros(self.data.shape[1], dtype=np.int16)
        np.copyto(tr, self.preview_transformation[-1])
        
        self.next_transformation.append(tr)
        print self.next_transformation[-1]
        self.transformation = tr
        
        del self.preview_transformation[-1]
        
##        print "after", len(self.preview_transformation), len(self.next_transformation)        
        
##def gui():
##    gui = MyApp()
##    gui.winMain.show()

def gui():
    window = MyApp()
    window.winMain.show()
    QtGui.QApplication.instance().exec_()
    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        window = MyApp()
        window.winMain.show()
        QtGui.QApplication.instance().exec_()



        

