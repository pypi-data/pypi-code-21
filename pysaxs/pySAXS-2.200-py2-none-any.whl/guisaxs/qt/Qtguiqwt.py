from PyQt4 import QtGui, QtCore
import sys
from pySAXS.guisaxs.qt import Qtguiqwtui
from guiqwt.builder import make
from guiqwt import styles
'''from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import colors
import matplotlib.font_manager as font_manager
'''
from pySAXS.guisaxs import pySaxsColors
import os
import itertools
from numpy import *


from guidata.qt.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QMainWindow)
from guidata.qt.QtCore import SIGNAL

#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.plot import PlotManager
from guiqwt.builder import make
from guidata.configtools import get_icon
from numpy import * 

APP_NAME = "Qt pySAXS"
APP_DESC = "Signal and Image Filtering Tool<br> Simple signal and image processing application based on guiqwt and guidata"
VERSION = '0.2.6'

class myfont():
    def __init__(self,family,size,bold,italic):
        self._family=family
        self._size=size
        self._bold=bold
        self._italic=italic
    def family(self):
        return self._family
    def pointSize(self):
        return self._size
    def bold(self):
        return self._bold
    def italic(self):
        return self._italic
    
    
class data:
    def __init__(self,x,y,label=None,id=None,error=None,color=None,curve=None):
        self.x=x
        self.y=y
        self.label=label
        self.id=id #id in the list of datas
        self.error=error
        self.color=color
        self.curve=curve
        


class QtGuiqwt(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.setStyleSheet("QFrame { background-color: white }")
        #self.setBackgroundRole()
        self.ui = Qtguiqwtui.Ui_MainWindow()
        #draw the interface from qtdesigner
        self.ui.setupUi(self)
        #connect menus
        self.LegendActionGroup = QtGui.QActionGroup(self, exclusive=True)
        self.LegendActionGroup.addAction(self.ui.actionLegend_ON)
        self.LegendActionGroup.addAction(self.ui.actionLegend_OFF)
        
        QtCore.QObject.connect(self.ui.actionLegend_ON,QtCore.SIGNAL("triggered()"),self.OnLegendOn)
        QtCore.QObject.connect(self.ui.actionLegend_OFF,QtCore.SIGNAL("triggered()"),self.OnLegendOff)
        #---guiqwt plot manager
        self.manager = PlotManager(self)
        self.plot = self.ui.curvewidget.get_active_plot()#CurvePlot(self)
        #self.plot.legend()
        self.legend = make.legend("TR")
        self.plot.add_item(self.legend)
        font=myfont('Times New Roman',10,True,False)
        self.plot.set_axis_font(2, font)
        self.plot.set_axis_font(0, font)
        self.legendON=True
        #self.centralWidget().layout().addWidget(self.plot)
        #---Register plot to manager
        self.manager.add_plot(self.plot)
        #---Add toolbar and register manager tools
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        #-- Add pySAXS toolbar
        self.toolbarPlus = self.addToolBar('pySAXS')
        LegendONAction = QtGui.QAction(QtGui.QIcon('csautoscale.png'), 'Legend ON', self)
        #exitAction.setShortcut('Ctrl+Q')
        LegendONAction.triggered.connect(self.OnLegendOn)
        self.toolbarPlus.addAction(LegendONAction)
        #--
        LegendOFFAction = QtGui.QAction(QtGui.QIcon('csautoscale.png'), 'Legend OFF', self)
        LegendOFFAction.triggered.connect(self.OnLegendOff)
        self.toolbarPlus.addAction(LegendOFFAction)
        #--
        AutoscaleAction= QtGui.QAction(QtGui.QIcon('csautoscale.png'), 'Autoscale', self)
        AutoscaleAction.triggered.connect(self.autoscale)
        self.toolbarPlus.addAction(AutoscaleAction)
        #AutoscaleAction.triggered.connect(self.OnLegendOff)
        #toolbar.addAction( "Legend ON")
        #toolbar.addAction( "Legend OFF")
        
        #self.curve_item = make.curve([], [], color='b')
        #self.plot.add_item(self.curve_item)
        #print self.plot.frameShadow()
        #self.plot.set_scales('lin', 'log')
        self.plot.set_antialiasing(True)
        
        ''''x = np.linspace(-10, 10, 500)
        y = np.random.rand(len(x))+5*np.sin(2*x**2)/x
        self.curve_item.set_data(x, y)
        self.plot.replot()
        '''
                
        self.datalist=[]
        self.gridON=True
        
        self.axetype=4 #lin lin
        #if axetype!=None:
            #self.axetype=axetype
            
        self.plotexp=0 #x vs y
        self.linetype=1
        self.ylabel=""
        self.xlabel=""
        self.marker_cycle=itertools.cycle(['.','o','^','v','<','>','s','+','x','D','d','1','2','3','4','h','H','p','|','_'])
        self.marker_fixed=['.','-','.-','o',',','x']
        self.colors=pySaxsColors.listOfColors()
        self.errbar=False
        self.markerSize=5
        
        '''self.ui.curvewidget.add_toolbar(self.toolbar)
        self.plt=self.ui.curvewidget.get_active_plot()
        '''
        '''self.plt.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.plt)
        self.replot()
        '''
        
                
    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL('closing()'))
        #print "closing"
           
    def close_event(self):
        print "close event"
    
    def replot(self):
        #print "on Qtguiqwt.replot()"
        '''for d in self.datalist:
            #which color ?
            col=self.get_color(d.id)
            if d.color!=None:
                col=d.color
            print col
            c=make.curve(d.x, d.y,color=col)
            self.plot.add_item(c)
        '''
        self.plot.replot()
        self.active_axes=self.plot.get_active_axes()
       
        
        #self.plot.legend()
    
    def annotate(self,posx,posy,label=None):
        '''
        add a marker on the graph
        '''   
        mark=make.marker(position=(posx, posy), label_cb=lambda posx, posy: label+" = %.4f" % posx,
                     markerstyle="|", movable=False,color="black",linestyle="DotLine")
        self.plot.add_item(mark)
        
        
    def OnScale(self):
        #check which scale
        #self.scaleActionGroup.actions()
        wscale=[self.ui.actionXlin_ylin,self.ui.actionXlog_ylin,self.ui.actionXlin_ylog,self.ui.actionXlog_ylog]
        scaletype=[4,2,3,1]
        #print "on scale"
        for i in range(len(wscale)):
            s=wscale[i]
            if s.isChecked():
                self.axetype=scaletype[i]
        self.replot()
            
    
    def OnGridOn(self):
        self.gridON=True
        #self.ui.actionGridOFF.setChecked(False)
        self.replot()
    
    def OnGridOff(self):
        self.gridON=False
        #self.ui.actionGridON.setChecked(False)
        self.replot()
        
    def OnLegendOn(self):
        self.legendON=True
        self.plot.set_item_visible(self.legend,True)
        #self.replot()
    
    def OnLegendOff(self):
        self.legendON=False
        self.plot.set_item_visible(self.legend,False)
        #self.plot.hide_items(items=[self.legend])
        #self.replot()

    def autoscale(self):
        self.plot.do_autoscale(replot=True)
    
    def addData(self,x,y,label=None,id=None,error=None,color=None):
        ''' datas to the plot
        x and y are datas
        label : the name of datas
        id : no of datas in a list -> give the colors
        '''
        if id==None:
            id=len(self.datalist)
        
        #which color ?
        col=self.get_color(id)
        if color!=None:
           col=color
        #print col
        #print label
        c=make.curve(x, y,color=col,title=label)
        self.plot.add_item(c)
        newdata=data(x,y,label,id,error,color=color,curve=c)
        self.datalist.append(newdata)
    
    def clearData(self):
        self.datalist=[]
        self.plot.del_all_items()
        
    def get_marker(self):
        """ Return an infinite, cycling iterator over the available marker symbols.
        or a fixed marker symbol
        """
        
        #--line style
        if self.linetype<=5:
            #predifined marker
            lstyle=self.marker_fixed[self.linetype]
            #print lstyle
            return lstyle
        else:
            #automatic marker
            return self.marker_cycle.next()+'-'

    def get_color(self,n):
        ''' return a color name from the list of colors
        if n> length of list of colors, return at the beginning
        '''
        if n==None:
            return None
        t=divmod(n,len(self.colors)) #return the no of color in the list
        return self.colors[t[1]]

    def setScaleLabels(self,xlabel=None,ylabel=None):
        '''
        define labels for scale
        '''
        #get_active_axes()
        self.plot.set_axis_title(2,xlabel)
        self.plot.set_axis_title(0,ylabel)
        

if __name__ == "__main__":
    """Testing this simple Qt/guiqwt example"""
    from guidata.qt.QtGui import QApplication
    import numpy as np
    import scipy.signal as sps, scipy.ndimage as spi
    
    app = QApplication([])
    myapp = QtGuiqwt()
    
    from pySAXS.models import Gaussian
    modl=Gaussian()
    x=modl.q
    y=modl.getIntensity()
    err=ones(shape(x))#random.rand(len(x))/10
    #err=err*y
    #print err
    myapp.addData(x, y, label='gaussian',error=err)
    myapp.addData(x, -y*1.51, label='gaussian2',error=err)
    myapp.addData(x, y*2, label='gaussian3',error=err)
    myapp.setScaleLabels("q (A)", "I (cm-1)")
    myapp.replot()
    myapp.annotate(1., 100., "label")
    
    myapp.show()
    app.exec_()
    
    