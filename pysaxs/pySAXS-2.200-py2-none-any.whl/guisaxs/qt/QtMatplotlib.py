from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

#from pySAXS.guisaxs.qt import QtMatplotlibui
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib import colors

import matplotlib.font_manager as font_manager

from pySAXS.guisaxs import pySaxsColors

import os

import itertools

from numpy import *

from matplotlib.widgets import Cursor

import time

import os

import pySAXS
from functools import partial

ICON_PATH=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'images'+os.sep  
class data:
    def __init__(self,x,y,label=None,id=None,error=None,color=None,selected=False):
        self.x=x
        self.y=y
        self.label=label
        self.id=id #id in the list of datas
        self.error=error
        self.color=color
        self.selected=selected
        if len(x)>0:
            self.xmin=x.min()
            self.xmax=x.max()
            self.ymin=y.min()
            self.ymax=y.max()
        else:
            self.xmin=0
            self.xmax=1
            self.ymin=0
            self.ymax=1
        
        
LINLIN='xlin - ylin'
LINLOG='xlin - ylog'
LOGLIN='xlog - ylin'
LOGLOG='xlog - ylog'

class QtMatplotlib(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        #self.ui = QtMatplotlibui.Ui_MainWindow()
        self.ui = uic.loadUi(pySAXS.UI_PATH+"QtMatplotlib.ui", self)#
        if parent is not None:
            #print "icon"
            self.setWindowIcon(parent.windowIcon())
        #self.ui.setupUi(self)
        self.ui.show()
        #-------- toolbar
        self.ui.navi_toolbar = NavigationToolbar(self.ui.mplwidget, self)
        #self.ui.verticalLayout.addWidget(self.ui.navi_toolbar)
        self.ui.verticalLayout.insertWidget(0,self.ui.navi_toolbar)
        #remove the Pan tool
        l=self.ui.navi_toolbar.actions()
        for i in l:
            #print i.text()
            if i.text()=='Pan':
                panAction=i
            if i.text()=='Customize':
                customizeAction=i
            if i.text()=='Subplots':
                subplotAction=i
            
        #self.ui.navi_toolbar.removeAction(panAction)
        self.ui.navi_toolbar.removeAction(customizeAction)
        self.ui.navi_toolbar.removeAction(subplotAction)
        #QObject::connect(myAction, SIGNAL(triggered()),this, SLOT(myActionWasTriggered()))
        
        #--grid button
        self.GridAction = QtWidgets.QAction(QtGui.QIcon(ICON_PATH+'grid.png'), 'Grid On/Off', self)
        self.GridAction.setCheckable(True)
        self.GridAction.setChecked(True)
        self.GridAction.triggered.connect(self.OnButtonGridOnOff)
        self.ui.navi_toolbar.addAction(self.GridAction)
        
        #--Legend
        self.LegendAction = QtWidgets.QAction(QtGui.QIcon(ICON_PATH+'legend.png'), 'Legend On/Off', self)
        self.LegendAction.setCheckable(True)
        self.LegendAction.setChecked(True)
        self.LegendAction.triggered.connect(self.OnButtonLegendOnOff)
        self.ui.navi_toolbar.addAction(self.LegendAction)
        #--Autoscale
        self.AutoscaleAction= QtWidgets.QAction('Autoscale', self)
        self.AutoscaleAction.triggered.connect(self.OnAutoscale)
        self.ui.navi_toolbar.addAction(self.AutoscaleAction)
        #-- fix scale
        self.FixScaleAction= QtWidgets.QAction(QtGui.QIcon(ICON_PATH+'magnet.png'),'Fix Scale', self)
        self.FixScaleAction.setCheckable(True)
        self.FixScaleAction.setChecked(False)
        self.FixScaleAction.triggered.connect(self.OnButtonFixScale)
        self.ui.navi_toolbar.addAction(self.FixScaleAction)
        
        
        self.scaleList=[LINLIN,LINLOG,LOGLIN,LOGLOG]
        self.scaleDictAction={}
        self.axetype=self.scaleList[0]
        first=True
        self.scaleActionGroup = QtWidgets.QActionGroup(self, exclusive=True)
        for item in self.scaleList:
            entry = self.ui.menuAxes.addAction(item) #add in the menu, and remove the first number
            entry.setCheckable(True)
            self.scaleDictAction[item]=entry
            self.scaleActionGroup.addAction(entry)
            if first:
                entry.setChecked(True)
                self.axetype=item
            first=False
            #self.connect(entry,QtCore.SIGNAL('triggered()'), lambda item=item: self.setAxesFormat(item))
            #entry.triggered[()].connect(lambda item=item: self.setAxesFormat(item))
            entry.triggered.connect(partial(self.setAxesFormat,item))
        #---------------    
        
        
        #QtCore.QObject.connect(self.ui.actionGridON,QtCore.SIGNAL("triggered()"),self.OnMenuGridOnOff)
        self.ui.actionGridON.triggered.connect(self.OnMenuGridOnOff)
        #QtCore.QObject.connect(self.ui.actionLegend_ON,QtCore.SIGNAL("triggered()"),self.OnMenuLegendOnOff)
        self.ui.actionLegend_ON.triggered.connect(self.OnMenuLegendOnOff)
        #QtCore.QObject.connect(self.ui.actionError_Bar,QtCore.SIGNAL("triggered()"),self.OnMenuErrorOnOff)
        self.ui.actionError_Bar.triggered.connect(self.OnMenuErrorOnOff)
        self.ui.actionSave_As.triggered.connect(self.OnMenuFileSaveAs)
        self.ui.actionAutoscaling.triggered.connect(self.OnAutoscale)
        self.ui.actionSet_X_range.triggered.connect(self.OnSetXRange)
        self.ui.actionSet_Y_range.triggered.connect(self.OnSetYRange)
        self.ui.actionSetTitle.triggered.connect(self.OnSetTitle)
        self.ui.actionX_label.triggered.connect(self.OnSetXLabel)
        self.ui.actionY_label.triggered.connect(self.OnSetYLabel)
                                                 
        
        self.datalist=[]#list of datas
        self.linelist=[]#list of lines
        self.gridON=True
        self.legendON=True
        self.colors=pySaxsColors.pySaxsColors()
        self.errbar=False
        self.ui.actionError_Bar.setChecked(self.errbar)
        self.plotexp=0 #x vs y
        self.plotlist=['Normal','y/x','y/x^2','y/x^3','y/x^4']
        
        self.ylabel=""
        self.xlabel=""
        self.marker_cycle=itertools.cycle(['.','o','^','v','<','>','s','+','x','D','d','1','2','3','4','h','H','p','|','_'])
        self.marker_fixed=['.','-','.-','o',',','x']
        self.markerSize=5
        self.markerdict={'0No Marker':'','1Point':'.','2Circle':'o','3Diamond':'d','4Cross':'x','5Square':'s'}#need to set the menu priority
        self.linedict={'5No Line':'','1Solid':'-','2Dashed':'--','3Dash-dot':'-.','4Dotted':':'}
        #--------------- LINE FORMAT
        self.ui.actionSet_Line_Width.triggered.connect(self.OnMenuLineWidth) #change line size menu
        self.lineformat='-'
        self.linewidth=1
        first=True
        self.lineActionGroup = QtWidgets.QActionGroup(self, exclusive=True)
        sortedlist=self.linedict.keys()
        sortedlist.sort() #sort the menu
        for item in sortedlist:
            entry = self.ui.menuLines.addAction(item[1:]) #add in the menu, and remove the first number
            entry.setCheckable(True)
            self.lineActionGroup.addAction(entry)
            if first:
                entry.setChecked(True)
                self.lineformat=self.linedict[item]
                self.ui.menuLines.addSeparator()
            first=False
            #self.connect(entry,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnPlotLineFormat(item))
            #entry.triggered.connect(lambda item=item: self.OnPlotLineFormat(item))
            #entry.triggered.connect(lambda truc=item: self.OnPlotLineFormat(truc))
            entry.triggered.connect(partial( self.OnPlotLineFormat, item))
            
        #---------------    MARKERS FORMAT
        self.ui.actionSet_marker_size.triggered.connect(self.OnMenuMarkerSize) #change marker size menu
        self.marker=''
        self.markerActionGroup = QtWidgets.QActionGroup(self, exclusive=True)
        first=True
        sortedlist=self.markerdict.keys()
        sortedlist.sort()
        for item in sortedlist:
            entry = self.ui.menuMarker.addAction(item[1:])#add in the menu, and remove the first number
            entry.setCheckable(True)
            self.markerActionGroup.addAction(entry)
            if first:
                entry.setChecked(True)
                self.marker=self.markerdict[item]
                first=False
                self.ui.menuMarker.addSeparator()
            #self.connect(entry,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnPlotMarkerFormat(item))
            #entry.triggered[()].connect(lambda item=item: self.OnPlotMarkerFormat(item))
            entry.triggered.connect(partial(self.OnPlotMarkerFormat,item))
        
        #---------------   xy type of plot
        self.plotypeActionGroup = QtWidgets.QActionGroup(self, exclusive=True)
        
        for item in range(len(self.plotlist)):
            entry = self.ui.menuY_X_exp.addAction(self.plotlist[item])
            entry.setCheckable(True)
            self.plotypeActionGroup.addAction(entry)
            if item==0:
                entry.setChecked(True)
                self.plotexp=item
            #self.connect(entry,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnPlotType(item))
            #entry.triggered[()].connect(lambda item=item: self.OnPlotType(item))
            entry.triggered.connect(partial(self.OnPlotType,item))
        
        
        self.plt=self.ui.mplwidget.figure
        self.plt.patch.set_facecolor('White')
        self.canvas = FigureCanvas(self.plt)
        
        self.axes = self.plt.gca()
        self.axes.hold(True)
        
        self.replot()
                
    def closeEvent(self, event):
        #self.emit(QtCore.SIGNAL('closing()'))
        #self.closing.emit()
        self.close()
        #print "closing"
           
    def close_event(self):
        print "close event"
    
    
    def OnMenuFileSaveAs(self):
        """
        Handles File->Save menu events.
        """
        #-- open dialog for parameters
        fd = QtWidgets.QFileDialog(self)
        #get the filenames, and the filter
        wc = "Portable Network Graphics (*.png);;Scalable Vector Graphics SVG (*.svg);;Encapsulated Postscript (*.eps);;All files (*.*)"
        filename=fd.getSaveFileName (filter=wc)#,directory=self.workingdirectory)[0]
        filename=str(filename)
        #self.setWorkingDirectory(filename) #set working dir
        if  filename=="":
            return

        path, ext = os.path.splitext(filename)
        ext = ext[1:].lower()

        if ext != 'png' and ext != 'eps' and ext!='svg':
            error_message = 'Only the PNG,SVG and EPS image formats are supported.\n'+ 'A file extension of \'png\', \'svg\' or \'eps\' must be used.'
            QtWidgets.QMessageBox.critical(self,'Error', error_message, buttons=QtWidgets.QMessageBox.Ok)
            return

        try:
            
            self.plt.savefig(filename)
        except IOError, e:
            if e.strerror:
                err = e.strerror
            else:
                err = e

            error_message ='Could not save file: ' +str(err)
            QtWidgets.QMessageBox.critical(self,'Error', error_message, buttons=QtWidgets.QMessageBox.Ok)    
    
    def setAxesFormat(self,axeformat=LINLIN,changeMenu=False):
        '''
        change the Axes format (lin-lin, log-log,...)
        '''
        self.axetype=axeformat
        self.replot()
        if changeMenu:
            if self.scaleDictAction.has_key(axeformat):
                self.scaleDictAction[axeformat].setChecked(True)
        
    
    def OnButtonFixScale(self):
        #memorize the current scale"
        self.xlim_min,self.xlim_max=self.axes.get_xlim()
        self.ylim_min,self.ylim_max=self.axes.get_ylim()
        #print self.xlim_min,self.xlim_max," - ",self.ylim_min,self.ylim_max
        
    
    def OnMenuMarkerSize(self):
        '''
        user want to change the marker size
        '''
       
        size, ok=QtWidgets.QInputDialog.getInt(self, "Marker size", "specify the marker size", value=self.markerSize, min=0, max=20, step=1)
        if ok:
            self.markerSize=size
            self.replot()
    
    def OnMenuLineWidth(self):
        '''
        user want to change the line width
        '''
       
        width, ok=QtWidgets.QInputDialog.getInt(self, "Line Width", "specify the line width", value=self.linewidth, min=0, max=20, step=1)
        if ok:
            self.linewidth=width
            self.replot()
        
    #QtCore.pyqtSlot()
    def OnPlotLineFormat(self,item,val):
        try:
            self.lineformat=self.linedict[item]
            self.replot()
        except:
            pass
    
    def OnPlotMarkerFormat(self, item,val):
        self.marker=self.markerdict[item]
        self.replot()
    
    def OnPlotType(self,item,val):
        '''
        user changed the plotexp
        '''
        #print item
        self.plotexp=item
        self.replot()
        
    def replot(self):
        #print "on replot"
        #t0=time.time()
        
        
        #keep in memory the options
        self.xlim_min,self.xlim_max=self.axes.get_xlim()
        self.ylim_min,self.ylim_max=self.axes.get_ylim()
        
        xlabel=self.axes.get_xlabel()
        ylabel=self.axes.get_ylabel()
        self.title=self.axes.get_title()
        #print self.title
        
        #clear axes --> lose all the axes options
        self.axes.cla() 
        
        #--- fix scale
        if self.FixScaleAction.isChecked():
            #axes limits should have been memorized
            self.axes.set_xlim((self.xlim_min,self.xlim_max))
            self.axes.set_ylim((self.ylim_min,self.ylim_max))
        self.linelist=[]
        for d in self.datalist:
            #which color ?
            col=self.colors.getColor(d.id) #get a new color
            if d.color is not None:
                col=d.color
            #print d.label,d.y,d.color
            linewidth=self.linewidth
            if d.selected:
                linewidth+=1
            l=None    
            if d.error is not None and self.errbar:
                #print "with errorbar"
                if d.id is not None:
                    l=self.axes.errorbar(d.x,d.y*(d.x**self.plotexp),yerr=d.error*(d.y**self.plotexp),\
                                       linestyle=self.get_linestyle(),\
                                       marker=self.get_marker(),\
                                       linewidth=linewidth,\
                                       #ecolor='b',\
                                       label=d.label,markersize=self.markerSize,color=col)#,label=d.label,markersize=5,fmt=None)
                else:
                    l=self.axes.errorbar(d.x,d.y*(d.x**self.plotexp),yerr=d.error,\
                                       linestyle=self.get_linestyle(),\
                                       marker=self.get_marker(),\
                                       linewidth=linewidth,\
                                       label=d.label,\
                                       markersize=self.markerSize,\
                                       color=col)#,label=d.label,markersize=5,fmt=None)
                
            elif col is not None:
                l,=self.axes.plot(d.x,d.y*(d.x**self.plotexp),\
                               self.get_marker()+self.get_linestyle(),\
                               label=d.label,\
                               linewidth=linewidth,\
                               color=col,\
                               markersize=self.markerSize)
            else :
                #print "plot"
                l,=self.axes.plot(d.x,d.y*(d.x**self.plotexp),self.get_marker()+self.get_linestyle(),\
                               label=d.label,markersize=self.markerSize,linewidth=linewidth,)
            self.linelist.append(l)
        #--scale
        if self.axetype==LOGLOG:
            self.axes.set_xscale('log')
            self.axes.set_yscale('log')
        if self.axetype==LOGLIN:
            self.axes.set_xscale('log')
            self.axes.set_yscale('linear')
        if self.axetype==LINLOG:
            self.axes.set_xscale('linear')
            self.axes.set_yscale('log')
        if self.axetype==LINLIN:
            self.axes.set_xscale('linear')
            self.axes.set_yscale('linear')
        
        #--legend    
        if self.legendON:
            font=font_manager.FontProperties(style='italic',size='x-small')
            leg=self.axes.legend(loc='upper right',prop=font)
            #leg.get_frame().set_alpha(0.5)
        else:
            self.axes.legend_ = None
            
         #--grid
        #print self.gridON
        self.axes.get_xaxis().grid(self.gridON)
        self.axes.get_yaxis().grid(self.gridON)
        
        #-- x and y label
        self.setScaleLabels(xlabel, ylabel)
        self.setTitle(self.title)
        self.draw('r')
        
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
            
    
    def OnMenuGridOnOff(self):
        self.gridON=self.ui.actionGridON.isChecked()
        self.GridAction.setChecked(self.gridON)
        self.replot()
    
    def OnButtonGridOnOff(self):
        self.gridON=self.GridAction.isChecked()
        self.ui.actionGridON.setChecked(self.gridON)
        self.replot()
        
    def OnMenuLegendOnOff(self):
        self.legendON=self.ui.actionLegend_ON.isChecked()
        self.LegendAction.setChecked(self.legendON)
        self.replot()
    
    def OnButtonLegendOnOff(self):
        self.legendON=self.LegendAction.isChecked()
        self.ui.actionLegend_ON.setChecked(self.legendON)
        self.replot()
        
    def OnMenuErrorOnOff(self):
        self.errbar=self.ui.actionError_Bar.isChecked()
        self.replot()
        
        
    def OnAutoscale(self):
        '''
        user click on autoscale
        '''
        if len(self.datalist)>0:
            self.xlim_min,self.ylim_min,self.xlim_max,self.ylim_max=self.getXYminMax()
            #print self.xlim_min,self.ylim_min,self.xlim_max,self.ylim_max
            self.axes.set_xlim((self.xlim_min,self.xlim_max))
            self.axes.set_ylim((self.ylim_min,self.ylim_max))
        self.replot()
        

    def addData(self,x,y,label=None,id=None,error=None,color=None):
        ''' datas to the plot
        x and y are datas
        label : the name of datas
        id : no of datas in a list -> give the colors
        '''
        if id is None:
            id=len(self.datalist)
        
        newdata=data(x,y,label,id,error,color=color)
        self.datalist.append(newdata)
        return id
    
    def changeData(self,x,y,id,label=None,error=None,color=None):
        self.datalist[id]=data(x,y,label,id,error,color=color)
        
    def changeDataAndUpdate(self,x,y,id):
        self.changeData(x, y, id)
        self.linelist[id].set_ydata(y)
        self.linelist[id].set_xdata(x)
        self.draw('c')
        
    
    def clearData(self):
        self.datalist=[]
        
    def get_marker(self):
        """ Return an infinite, cycling iterator over the available marker symbols.
        or a fixed marker symbol
        """
        return self.marker#+self.lineformat
        '''#--line style
        if self.linetype<=5:
            #predifined marker
            lstyle=self.marker_fixed[self.linetype]
            #print lstyle
            return lstyle
        else:
            #automatic marker
            return self.marker_cycle.next()+'-'
        '''
    def set_marker(self,marker='.'):
       '''
       change the curve marker
       '''
       self.marker=marker
       
       
    def get_linestyle(self):
        return self.lineformat

    def OnSetXRange(self):
        '''
        user clicked on set x range
        '''
        #self.axes.hold(False)
        self.xlim_min,self.xlim_max=self.axes.get_xlim()
        xlim, ok=QtWidgets.QInputDialog.getDouble(self, "Setting X scale", "x min :", value=self.xlim_min)
        if ok:
            self.xlim_min=xlim
            self.axes.set_xlim((self.xlim_min,self.xlim_max))
            self.FixScaleAction.setChecked(True)
            self.replot()
        xlim, ok=QtWidgets.QInputDialog.getDouble(self, "Setting X scale", "x max :", value=self.xlim_max)
        if ok:
            self.xlim_max=xlim
            self.axes.set_xlim((self.xlim_min,self.xlim_max))
            self.FixScaleAction.setChecked(True)
            self.replot()
            
    def OnSetYRange(self):
        '''
        user clicked on set y range
        '''
        self.ylim_min,self.ylim_max=self.axes.get_ylim()
        ylim, ok=QtWidgets.QInputDialog.getDouble(self, "Setting Y scale", "y min :", value=self.ylim_min)
        if ok:
            self.ylim_min=ylim
            self.axes.set_ylim((self.ylim_min,self.ylim_max))
            self.FixScaleAction.setChecked(True)
            self.replot()
        ylim, ok=QtWidgets.QInputDialog.getDouble(self, "Setting Y scale", "y max :", value=self.ylim_max)
        if ok:
            self.ylim_max=ylim
            self.axes.set_ylim((self.ylim_min,self.ylim_max))
            self.FixScaleAction.setChecked(True)
            self.replot()
    
    def OnSetTitle(self):
        title, ok=QtWidgets.QInputDialog.getText(self, "Setting Graph Title", "title :", text=self.title)
        if ok:
            self.axes.set_title(title)
            self.replot()
    
    def OnSetXLabel(self):
        
        label, ok=QtWidgets.QInputDialog.getText(self, "Setting X label", "label :", text=self.xlabel)
        if ok:
            self.setScaleLabels(label)
            self.replot()
    
    def OnSetYLabel(self):
        label, ok=QtWidgets.QInputDialog.getText(self, "Setting Y label", "label :", text=self.ylabel)
        if ok:
            self.setScaleLabels(xlabel=None,ylabel=label)
            self.replot()
    
    def setTitle(self,title):
        if title!=self.title:
            self.title=title
            self.axes.set_title(title)
            self.draw('t')
        

    def setScaleLabels(self,xlabel=None,ylabel=None,size=None):
        #print "set scale"
        self.axes = self.plt.gca()
        if xlabel is not None :
            if xlabel!=self.axes.get_xlabel():
                self.axes.set_xlabel(xlabel)
                self.xlabel=xlabel
                if size is not None:
                    self.axes.set_xlabel(xlabel,fontsize=size,labelpad=-2)
        if ylabel is not None :
            if ylabel!=self.axes.get_ylabel():
                self.axes.set_ylabel(ylabel)
                self.ylabel=ylabel
                if size is not None:
                    self.axes.set_ylabel(ylabel,fontsize=size)
                    
    def annotate(self,x,y,text):
        #print "annotate ",text, " at ",x,y
        #self.axes = self.plt.gca()
        #self.axes.hold(False)
        self.axes.annotate(text, xy=(x, y),  xycoords='data',\
                                            xytext=(20, 20), textcoords='offset points', \
                                            arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90,rad=10"),\
                                            fontsize=10,)
        self.draw('a')
    
    def text(self,x=0.5,y=0.5,text='test'):
        self.axes.text(x,y,text,transform = self.axes.transAxes,bbox=dict(boxstyle='square',facecolor='gray', alpha=0.5))
        self.draw('tt')
        
    def draw(self,text=''):
        '''
        draw the plot
        text is here for tracking
        '''
        #print 'draw ',text
        #if text is '' : do not draw
        if text!='':
            self.ui.mplwidget.draw()
        
        
    
    def getXYminMax(self):
        '''
        return xmin,ymin,xmax,ymax on all the datas
        '''
        xminlist=[]
        xmaxlist=[]
        yminlist=[]
        ymaxlist=[]
        for d in self.datalist:
            xminlist.append(d.xmin)
            xmaxlist.append(d.xmax)
            yminlist.append(d.ymin)
            ymaxlist.append(d.ymax)
        return min(xminlist),min(yminlist),max(xmaxlist),max(ymaxlist) 
    
    def getAxes(self):
        return self.axes
    
    def getFig(self):
        return self.plt
    
    def changeFaceColor(self,color='None'):
        self.plt.patch.set_facecolor(color)
        

if __name__ == "__main__":
      app = QtWidgets.QApplication(sys.argv)
      myapp = QtMatplotlib()
      myapp.show()
      from pySAXS.models import Gaussian

      modl=Gaussian()
      x=modl.q
      y=modl.getIntensity()
      err=ones(shape(x))#random.rand(len(x))/10
      #err=err*y
      #print err
      myapp.addData(x, y, label='gaussian',error=err)
      myapp.addData(x, -y*1.51, label='gaussian2',error=err)
      i=myapp.addData(x, y*2, label='gaussian3',error=err)
      myapp.replot()
      myapp.setScaleLabels('$q(\AA^{-1})$', "I",15)
      myapp.setAxesFormat(LINLIN)
      myapp.setTitle('DEMO')
      myapp.annotate(1.0, 1.0, "text")
      myapp.annotate(1.0, 20.0, "text")
      myapp.annotate(-2.0, 1.0, "text")
      myapp.text(0.05,0.05,"test of text\nldqksj\ndlqks\nklfqlkjf\nqsdqs qsd\nqsd qsd")
      sys.exit(app.exec_())
