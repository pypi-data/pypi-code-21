"""
***Source code of Pick Peak Project***
"""


import numpy as np

import myindex

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
from matplotlib.widgets import Button
from matplotlib.widgets import  RectangleSelector
from matplotlib.widgets import Cursor


class PickPeak(object):

    def __init__(self, spec):

        # Figure settings
        self.fig = plt.figure()
        self.fig.canvas.set_window_title("Pick Peak") 
        self.fig.set_figheight(50) # value
        self.fig.set_figwidth(50) # value
        
        # Axes settings
        self.ax = self.fig.add_subplot(121)
        self.tableax = self.fig.add_subplot(122)
        self.tableax.text(0.5, 1.05, "Table of Peaks", horizontalalignment='center', verticalalignment='center',
                                     fontsize=14, color="black", backgroundcolor="1.0", alpha=1)
        self.tableax.patch.set_visible(False)
        self.tableax.set_axis_off()
        self.table = None
        self.cax = None
                
        # Create a spectrum vector and indices to plot it on the main axes 
        self.spec = spec
        self.ind = np.arange(0, np.shape(spec)[0])
        
        # Creates a Line2D artist and add it to the main axes
        self.line, = self.ax.plot(self.ind, self.spec, color='green', lw=3)        
               
        # Creates a patch to use as selection area and add it to the main axes
        self.rect = Rectangle((0,0), 0, 0)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.ax.add_patch(self.rect)

        # Creates the connections between the events and the funtions called by it
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

        # Other global variables
        self.peak = None
        self.peak_index = None
        self.peak_list = []
        self.table = None
        self.ispressed = None

        
    # Functions of buttons
    def new_spec(self, event):
        mult = np.random.randint(1, 11)        
        ydata = self.spec*mult        
        self.line.set_ydata(ydata)
        self.ax.relim() # recompute data limits after changing ydata
        self.ax.autoscale_view(tight=None, scalex=False, scaley=True)       
        plt.draw()
        

    def on_press(self, event):
        self.tableax.figure.canvas.draw()
        if self.ax == self.cax:
            if len(self.ax.patches) == 2:
                pass
            else:
                self.ax.patches[-1].remove()
                

    def onSelect(self, eclick, erelease):               
        self.x0 = eclick.xdata
        self.y0 = eclick.ydata        
        self.x1 = erelease.xdata
        self.y1 = erelease.ydata        

                
    def on_release(self, event):                
        if self.ax == self.cax:
            self.rect = Rectangle((self.x0, self.y0), self.x1 - self.x0, self.y1 - self.y0,
                                   alpha=0.5, facecolor='red', edgecolor='black', linewidth=2)
            self.ax.add_patch(self.rect)
        if self.cax == None:
            MenuItem.check_select(self, event)       
        self.ax.figure.canvas.draw()
        

    def on_motion(self, event):
        self.cax = event.inaxes        
      

    def pick_peak(self, event):
        self.y0 = round(self.y0, 8)
        self.y1 = round(self.y1, 8)
        self.x0 = round(self.x0, 8)
        self.x1 = round(self.x1, 8)
        if self.y0 > self.y1:
                aux = self.y0
                self.y0 = self.y1
                self.y1 = aux
        if self.x0 > self.x1:
                aux = self.x0
                self.x0 = self.x1
                self.x1 = aux
       
        x_lower = self.x0
        x_upper = self.x1
        y_lower = self.y0
        y_upper = self.y1

        yvalues = self.line.get_data()[1]        
        yvalues = np.reshape(yvalues[int(x_lower):int(x_upper+1)], np.shape(yvalues[int(x_lower):int(x_upper+1)]))
        
        yvalues_selected = []                
        for i in yvalues:
            if round(i, 8) >= y_lower and round(i, 8) <= y_upper:
                yvalues_selected = np.append(yvalues_selected, i)              

        if len(yvalues_selected) > 0:
            self.peak = np.amax(yvalues_selected)
            a = myindex.myarray(self.line.get_data()[1])
            self.peak_index = a.index(self.peak)[0][0]            
            self.peak_list.append([self.peak, self.peak_index])           
            self.peak_list.sort()
            self.peak_list.reverse() # ploat the last value on first row
            self.show_table()
        else:
            print "None peak was selected! ... Try again "
            self.show_table()
            
        
    def show_table(self):        
        # Table
        columns = ('Value', 'Index')
        rows = ['peak %d' % x for x in range(len(self.peak_list))]
        colors = plt.cm.BuPu(np.linspace(0, 0.5, len(rows)))
        colors = colors[::-1]
  
        self.tableax.clear() # clear the axes every time it plots the new table (help in minimizing and maximizing the window)

        self.table = self.tableax.table(cellText=self.peak_list, cellColours=None,
                               cellLoc='center', colWidths=None,
                               rowLabels=rows, rowColours=colors, rowLoc='left',
                               colLabels=columns, colColours=None, colLoc='center',
                               loc='center', bbox=None, fontsize=12)
        
        self.tableax.text(0.5, 1.05, "Table of Peaks", horizontalalignment='center',
                                     verticalalignment='center', fontsize=14, color="black",
                                     backgroundcolor="1.0", alpha=1)
        
        self.tableax.set_visible(True)
        self.tableax.set_axis_off()
        self.tableax.relim()
        self.tableax.set_autoscale_on(True)

        self.table.auto_set_column_width(0)
        self.table.auto_set_column_width(1)
        self.table.auto_set_column_width(2)
        self.table.auto_set_font_size(True)
        self.table.scale(1, 1)
        
        self.tableax.figure.canvas.draw()


    def del_peak(self, event):
        del self.peak_list[-1]        
        if len(self.peak_list) <= 0:
            self.tableax.clear()
            self.tableax.text(0.5, 1.05, "Table of Peaks", horizontalalignment='center', verticalalignment='center',
                                     fontsize=14, color="black", backgroundcolor="1.0", alpha=1)
            self.tableax.patch.set_visible(False)
            self.tableax.set_axis_off()
        else:
            self.show_table()


    def clean_peaks(self, event):
        del self.peak_list[:]        
        self.tableax.clear()
        self.tableax.text(0.5, 1.05, "Table of Peaks", horizontalalignment='center', verticalalignment='center',
                                     fontsize=14, color="black", backgroundcolor="1.0", alpha=1)
        self.tableax.patch.set_visible(False)
        self.tableax.set_axis_off()
        

    def gui_design(self):
        """ Buttons design""" 
        # Buttton axes        
        axpickpeak = plt.axes([0.49, 0.015, 0.15, 0.075])
        axdelpeak = plt.axes([0.65, 0.015, 0.15, 0.075])
        axcleanpeaks = plt.axes([0.81, 0.015, 0.155, 0.075])

        # Button names and functions
        bpickpeak = Button(axpickpeak, 'Pick Peak')
        bpickpeak.on_clicked(self.pick_peak)

        bdelpeak = Button(axdelpeak, 'Del Peak')
        bdelpeak.on_clicked(self.del_peak)

        bcleanpeaks = Button(axcleanpeaks, 'Clean Peaks')
        bcleanpeaks.on_clicked(self.clean_peaks)

        #Widgets
        selector = RectangleSelector(self.ax, self.onSelect, drawtype='box',
                     spancoords='data', button=1)
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        plt.show()
        
        


