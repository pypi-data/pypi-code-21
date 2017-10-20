from __future__ import division
import sys
import os
from . import tplot_common
from .timestamp import TimeStamp
from .TVarFigure1D import TVarFigure1D
from .TVarFigure2D import TVarFigure2D
from .TVarFigureSpec import TVarFigureSpec
from .TVarFigureAlt import TVarFigureAlt

import time
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QFileDialog, QAction, QMainWindow
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

def tplot2(name, 
           var_label = None, 
           auto_color=True, 
           interactive=False, 
           combine_axes=True):


    pg.setConfigOptions(imageAxisOrder='row-major')

    pg.mkQApp()
    win = pg.GraphicsLayoutWidget()
    win.setWindowTitle('pyqtgraph example: Image Analysis')

    win.resize(800, 800)
    win.show()

    # Name for .html file containing plots
    out_name = ""
    
    #Check a bunch of things
    if(not isinstance(name, list)):
        name=[name]
        num_plots = 1
    else:
        num_plots = len(name)
    
    for i in range(num_plots):
        if isinstance(name[i], int):
            name[i] = list(tplot_common.data_quants.keys())[name[i]]
        if name[i] not in tplot_common.data_quants.keys():
            print(str(i) + " is currently not in pytplot")
            return
    
    if isinstance(var_label, int):
        var_label = list(tplot_common.data_quants.keys())[var_label]
    
    # Vertical Box layout to store plots
    all_plots = []
    axis_types=[]
    i = 0
    
    # Configure plot sizes
    total_psize = 0
    j = 0
    while(j < num_plots):
        total_psize += tplot_common.data_quants[name[j]].extras['panel_size']
        j += 1
    p_to_use = tplot_common.tplot_opt_glob['window_size'][1]/total_psize
    
    axis = DateAxis(orientation='bottom')
    #vb = CustomViewBox()
    # Create all plots  
    while(i < num_plots):
        last_plot = (i == num_plots-1)
        temp_data_quant = tplot_common.data_quants[name[i]]
        
        p_height = int(temp_data_quant.extras['panel_size'] * p_to_use)
        p_width = tplot_common.tplot_opt_glob['window_size'][0]
        p = win.addPlot(title='Orbit', axisItems={'bottom':axis})#, viewBox = vb)
        p.plot(temp_data_quant.data.index.tolist(), temp_data_quant.data[0].tolist(), pen=(255,0,0))
        
        i+=1
    # Add date of data to the bottom left corner and timestamp to lower right
    # if py_timestamp('on') was previously called
    total_string = ""
    if 'time_stamp' in tplot_common.extra_layouts:
        total_string = tplot_common.extra_layouts['time_stamp']
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print(sys.flags.interactive)
        QtGui.QApplication.instance().exec_()

     
    return

def _generate_gui(total_html):  
    
    class PlotWindow(QMainWindow):
        
        def __init__(self):
            super().__init__()
            self.initUI()
            self.setcleanup()
            
        def initUI(self):
            self.setWindowTitle('PyTplot')
            self.plot_window = QWebEngineView()
            self.setCentralWidget(self.plot_window)
            
            self.resize(tplot_common.tplot_opt_glob['window_size'][0]+100,tplot_common.tplot_opt_glob['window_size'][1]+100)
            self.plot_window.resize(tplot_common.tplot_opt_glob['window_size'][0],tplot_common.tplot_opt_glob['window_size'][1])
            
            #self.plot_window.setHtml(total_html)
            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.plot_window.setUrl(QtCore.QUrl.fromLocalFile(os.path.join(dir_path, "temp.html")))
            menubar = self.menuBar()
            exportMenu = menubar.addMenu('Export')
            exportDatahtmlAction = QAction("HTML", self)
            exportDatahtmlAction.triggered.connect(self.exporthtml)
            exportMenu.addAction(exportDatahtmlAction)        
            exportDatapngAction = QAction("PNG", self)
            exportDatapngAction.triggered.connect(self.exportpng)
            exportMenu.addAction(exportDatapngAction)
            
            self.show()
        
        def setcleanup(self):
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.plot_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            for child in self.findChildren(QWebEngineView):
                if child is not self.plot_window:
                    child.deleteLater()
        
        def exporthtml(self):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            fname = QFileDialog.getSaveFileName(self, 'Open file', 'pytplot.html', filter ="html (*.html *.)")
            with open(fname[0], 'w+') as html_file:
                with open(os.path.join(dir_path, "temp.html")) as read_file:
                    html_file.write(read_file.read())
            
        def exportpng(self):
            fname = QFileDialog.getSaveFileName(self, 'Open file', 'pytplot.png', filter ="png (*.png *.)")
            sshot = self.plot_window.grab()
            sshot.save(fname[0])            
    
    app = QApplication(sys.argv)
    web = PlotWindow()    
    web.show()
    web.activateWindow()
    app.exec_()
    return

class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
            print(string)
            print(label1)
            print(label2)
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >=3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.gmtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.gmtime(min(values)))+time.strftime(label2, time.gmtime(max(values)))
        except ValueError:
            label = ''
        #self.setLabel(text=label)
        return strns
    
# class CustomViewBox(pg.ViewBox):
#     def __init__(self, *args, **kwds):
#         pg.ViewBox.__init__(self, *args, **kwds)
#         self.setMouseMode(self.RectMode)
#         
#     ## reimplement right-click to zoom out
#     def mouseClickEvent(self, ev):
#         if ev.button() == QtCore.Qt.RightButton:
#             self.autoRange()
#             
#     def mouseDragEvent(self, ev):
#         if ev.button() == QtCore.Qt.RightButton:
#             ev.ignore()
#         else:
#             pg.ViewBox.mouseDragEvent(self, ev)
