from __future__ import division
import sys
import os
from . import tplot_common
from .timestamp import TimeStamp
from .TVarFigure1D import TVarFigure1D
from .TVarFigure2D import TVarFigure2D
from .TVarFigureSpec import TVarFigureSpec
from .TVarFigureAlt import TVarFigureAlt

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
    
    # Create all plots  
    while(i < num_plots):
        last_plot = (i == num_plots-1)
        temp_data_quant = tplot_common.data_quants[name[i]]
        
        p_height = int(temp_data_quant.extras['panel_size'] * p_to_use)
        p_width = tplot_common.tplot_opt_glob['window_size'][0]
        
        #Check plot type       
        spec_keyword = temp_data_quant.extras.get('spec', False)
        alt_keyword = temp_data_quant.extras.get('alt', False)
        map_keyword = temp_data_quant.extras.get('map', False)
        
        if spec_keyword:     
            new_fig = TVarFigureSpec(temp_data_quant, interactive=interactive, last_plot=last_plot)
        elif alt_keyword:
            new_fig = TVarFigureAlt(temp_data_quant, auto_color=auto_color, interactive=interactive, last_plot=last_plot)
        elif map_keyword:    
            new_fig = TVarFigure2D(temp_data_quant, interactive=interactive, last_plot=last_plot)
        else:
            new_fig = TVarFigure1D(temp_data_quant, auto_color=auto_color, interactive=interactive, last_plot=last_plot)
            
        axis_types.append(new_fig.getaxistype())
        
        new_fig.setsize(height=p_height, width=p_width) 
        if i == 0:
            new_fig.add_title()
        
        new_fig.buildfigure()
        
            
    # Add date of data to the bottom left corner and timestamp to lower right
    # if py_timestamp('on') was previously called
    total_string = ""
    if 'time_stamp' in tplot_common.extra_layouts:
        total_string = tplot_common.extra_layouts['time_stamp']
    
    ts = TimeStamp(text = total_string)
    tplot_common.extra_layouts['data_time'] = ts
    all_plots.append([tplot_common.extra_layouts['data_time']])
        

    #Add extra x axes if applicable 
    if var_label is not None:
        if not isinstance(var_label, list):
            var_label = [var_label]
        x_axes = []
        x_axes_index = 0
        for new_x_axis in var_label:
            
            axis_data_quant = tplot_common.data_quants[new_x_axis]
            axis_start = min(axis_data_quant.data.min(skipna=True).tolist())
            axis_end = max(axis_data_quant.data.max(skipna=True).tolist())
            x_axes.append(Range1d(start = axis_start, end = axis_end))
            k = 0
            while(k < num_plots ):
                all_plots[k][0].extra_x_ranges['extra_'+str(new_x_axis)] = x_axes[x_axes_index]
                k += 1
            all_plots[k-1][0].add_layout(LinearAxis(x_range_name = 'extra_'+str(new_x_axis)), 'below')
            all_plots[k-1][0].plot_height += 22
            x_axes_index += 1
    
    # Add toolbar and title (if applicable) to top plot.        
    final = gridplot(all_plots)


    #Output types
    if gui:
        script, div = components(final)
        return script, div
    elif nb:
        output_notebook()
        show(final)
        return
    elif save_file != None:
        output_file(save_file, mode='inline')
        save(final)    
        return
    else:        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        output_file(os.path.join(dir_path, "temp.html"), mode='inline')
        save(final)
        js = JSResources(mode='inline')
        css = CSSResources(mode='inline')
        total_html = file_html(final, (js, css))
        _generate_gui(total_html)
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
    