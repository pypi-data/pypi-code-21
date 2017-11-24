from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

#from lmfit import  Model

from scipy import optimize

import numpy


import os


from numpy import *

import scipy


import time

import os

import pySAXS

from pySAXS.guisaxs.qt import QtMatplotlib

from pySAXS.tools import specLogReader

from pySAXS.guisaxs.dataset import *

from pySAXS.models import Gaussian

from pySAXS.models import Trapez as MTRAPEZ

from pySAXS.models import Gaussian as MGAUSSIAN

from pySAXS.models import Capillary

from pySAXS.guisaxs.qt import dlgModel

from pySAXS.guisaxs.qt import preferences

ICON_PATH=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'images'+os.sep  
import threading

import time


class Intervallometre(threading.Thread):
 
    def __init__(self, duree, fonction, parent=None):
        threading.Thread.__init__(self)
        self.duree = duree
        self.fonction = fonction
        self.parent = parent
        self.encore = True
        
    def run(self):
        self.encore = True
        self.parent.ui.tableWidget.setEnabled(False)
        while self.encore:
            self.fonction()
            time.sleep(self.duree)
            '''val=self.parent.ui.progressBar.value()
            if val+10>self.parent.ui.progressBar.maximum():
                self.parent.ui.progressBar.setValue(0)
            else:
                self.parent.ui.progressBar.setValue(val+10)'''
        
        self.parent.ui.tableWidget.setEnabled(True)
        print "thread stopped"
    def stop(self):
        self.encore = False
        self.parent.ui.tableWidget.setEnabled(True)
        print "thread stopped"


class scanPlot(QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.data_dict={}
        self.SelectedKey=None
        QtWidgets.QWidget.__init__(self, parent)
        #self.ui = QtMatplotlibui.Ui_MainWindow()
        self.ui = uic.loadUi(pySAXS.UI_PATH+"scanPlot.ui", self)#
        if parent is not None:
            #print "icon"
            self.setWindowIcon(parent.windowIcon())
            
         #-- get preferences
        filename=pySAXS.__path__[0]+os.sep+'saxsdata'+os.sep+'saxs_20170202.log'
        self.parent=parent
        if parent is not None:
            #self.printout = parent.printTXT
            self.workingdirectory = parent.workingdirectory
            filename=self.parent.get('scanfile',section="spec")
            
        
        '''QtCore.QObject.connect(self.ui.changeFileButton, QtCore.SIGNAL("clicked()"), self.OnClickFileButton)
        QtCore.QObject.connect(self.ui.tableWidget,QtCore.SIGNAL('cellClicked(int, int)'), self.cellClicked)
        QtCore.QObject.connect(self.ui.BtnGaussian, QtCore.SIGNAL("clicked()"), self.OnClickFitGaussian)
        QtCore.QObject.connect(self.ui.BtnTrapez, QtCore.SIGNAL("clicked()"), self.OnClickFitTrapez)
        QtCore.QObject.connect(self.ui.BtnCapillary, QtCore.SIGNAL("clicked()"), self.OnClickFitCapillary)
        QtCore.QObject.connect(self.ui.BtnRefresh, QtCore.SIGNAL("clicked()"), self.OnClickRefresh)
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        QtCore.QObject.connect(self.ui.BtnStartAuto, QtCore.SIGNAL("clicked()"), self.StartAuto)
        QtCore.QObject.connect(self.ui.BtnStopAuto, QtCore.SIGNAL("clicked()"), self.StopAuto)
        QtCore.QObject.connect(self.ui.BtnExport, QtCore.SIGNAL("clicked()"), self.ExportData)'''
        self.ui.changeFileButton.clicked.connect(self.OnClickFileButton)
        self.ui.tableWidget.cellClicked[int, int].connect(self.cellClicked)
        self.ui.BtnGaussian.clicked.connect(self.OnClickFitGaussian)
        self.ui.BtnTrapez.clicked.connect(self.OnClickFitTrapez)
        self.ui.BtnCapillary.clicked.connect(self.OnClickFitCapillary)
        self.ui.BtnRefresh.clicked.connect(self.OnClickRefresh)
        self.ui.buttonBox.clicked.connect(self.click)
        self.ui.BtnStartAuto.clicked.connect(self.StartAuto)
        self.ui.BtnStopAuto.clicked.connect(self.StopAuto)
        self.ui.BtnExport.clicked.connect(self.ExportData)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0,1)
        
    
        #self.xdata=arange(-10,10,0.1)
        #self.ydata=sin(self.xdata)
        self.move(QtCore.QPoint(100,100))
        self.plotframe=QtMatplotlib.QtMatplotlib()
        
        self.plotframe.move(self.width()+self.x() + 15, self.y())
        self.plotframe.resize(self.plotframe.width(),self.height())
        self.plotframe.show()
        self.plotframe.set_marker('.')
        self.plotframe.setWindowTitle("SPEC Plot")
        #self.a=self.plotframe.addData(self.xdata,self.ydata,color='b')
        #self.plotframe.replot()
        
        self.ui.logfileEdit.setText(filename)
        self.FillList()
        self.th=None
        
        
        self.ui.show()
    
    def click(self,obj=None):
        name=obj.text()
        #print name
        if name=='Close':
            self.close()
            self.plotframe.close()
        else:
            self.close()
            self.plotframe.close()
            
    def closeEvent(self, event):
        '''
        when window is closed
        '''
        if self.parent is not None:
                self.parent.pref.set("scanfile",section="spec",value=str(self.ui.logfileEdit.text()))
                self.parent.pref.save()
        try:
            self.th.encore=False
            self.plotframe.close()
        except:
            pass

    def OnClickFileButton(self):
        '''
        select a log file
        '''
        filters = "log Files (*.log);;All Files (*)"
        selected_filter = "log (*.log)"
        fd = QtWidgets.QFileDialog(self)#," File dialog ", filter="log Files (*.log)")#, selected_filter)
        filename,truc = fd.getOpenFileName(filter="log Files (*.log)")#directory=self.workingdirectory)[0]
        self.workingdirectory = filename
        # print filename
        self.ui.logfileEdit.setText(filename)
        self.FillList()
        
    def FillList(self):
        filename=self.ui.logfileEdit.text()
        #try to decode
        self.scanList=specLogReader.readScanLog(filename)
        #print obj
        
        #update list
        
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setRowCount(len(self.scanList))
        headerNames = ["No", "Scan"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0,50)
        self.ui.tableWidget.setColumnWidth(1, 300)
          
        i = 0
        for item in sorted(self.scanList,reverse=True):
            scan=self.scanList[item]
            self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(scan.No)))
            self.ui.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(scan.description))
            self.ui.tableWidget.setRowHeight(i, 20)          
            i += 1
        self.cellClicked(0,0)
        
    def cellClicked(self,row,col):
        
        self.SelectedKey=int(self.ui.tableWidget.item(row,0).text())
        #print "scan : ",self.scanList[key].description
        #try to plot
        self.data_dict={}
        self.data_dict[self.SelectedKey]=dataset(str(self.SelectedKey))
        self.data_dict[self.SelectedKey].q=array(self.scanList[self.SelectedKey].x)
        self.data_dict[self.SelectedKey].i=array(self.scanList[self.SelectedKey].y)
        datax=self.data_dict[self.SelectedKey].q
        datay=self.data_dict[self.SelectedKey].i
        '''p0=[(datax[-1]+datax[0])/2-1,(datax[-1]-datax[0])/3,(datax[-1]-datax[0])/20,-(datay.max()-datay.min()),datay.max()]
        print p0
        self.data_dict['leastsq']=dataset('leastsq',datax,Trapez(datax,p0),color='b')'''
        self.Replot()
    
    def OnClickRefresh(self):
        self.FillList()
        self.OnClickFitTrapez()
        
    def OnClickFitGaussian(self):
        if self.SelectedKey is not None:
            self.M=MGAUSSIAN()
            datax=self.data_dict[self.SelectedKey].q
            datay=self.data_dict[self.SelectedKey].i
            '''
            #p0=array([(datax[-1]+datax[0])/2,(datax[-1]-datax[0])/5,(datax[-1]-datax[0])/10,-(datay.max()-datay.min()),datay.min()])
            #a,c=fit_function(p0 , datax, datay, Trapez, curve_fit_function=Trapezf) 
            plot(datax,Gauss(datax,a),label='leastsq')
            plot(datax,Gauss(datax,b),label='pfit_curvefit')
            plot(datax,Gauss(datax,c),label='bootstrap')'''
            
            self.M.Arg=self.M.prefit(datax,datay)
            self.M.q=datax
            b=self.M.fit(datay)
            self.data_dict['pysaxs']=dataset('pysaxs',datax,self.M.getIntensity(datax,b))
            
            self.Replot()
            reporttext="TRAPEZ Fit\n"
            for i in range(len(b)):
                reporttext+=self.M.Doc[i]+' : ' +str(b[i])+'\n'
            
            self.plotframe.text(0.05,0.05,reporttext)#display text
        
    def OnClickFitTrapez(self):
        if self.SelectedKey is not None:
            self.M=MTRAPEZ()
            datax=self.data_dict[self.SelectedKey].q
            datay=self.data_dict[self.SelectedKey].i
            '''
            #p0=array([(datax[-1]+datax[0])/2,(datax[-1]-datax[0])/5,(datax[-1]-datax[0])/10,-(datay.max()-datay.min()),datay.min()])
            #a,c=fit_function(p0 , datax, datay, Trapez, curve_fit_function=Trapezf) 
            plot(datax,Gauss(datax,a),label='leastsq')
            plot(datax,Gauss(datax,b),label='pfit_curvefit')
            plot(datax,Gauss(datax,c),label='bootstrap')'''
            if len(datax)>10:
                self.M.Arg=self.M.prefit(datax,datay)
                self.M.q=datax
                b=self.M.fit(datay)
                self.data_dict['pysaxs']=dataset('pysaxs',datax,self.M.getIntensity(datax,b))
                
                self.Replot()
                reporttext=""
                for i in range(len(b)):
                    reporttext+=self.M.Doc[i]+' : ' +str(b[i])+'\n'
                
                self.plotframe.text(0.05,0.05,reporttext)#display textMGAUSSIAN
            
    def OnClickFitCapillary(self):
        if self.SelectedKey is not None:
            self.M=Capillary()
            self.DisplayModelBox()
    
    def DisplayModelBox(self):
            data_selected_for_model=self.SelectedKey
            new_dataname=str(data_selected_for_model)+"-"+self.M.name+" model"
            q=self.data_dict[data_selected_for_model].q
            
            self.M.q=q
            i=self.M.getIntensity() #intensity by default
            filename=self.data_dict[data_selected_for_model].filename
            self.data_dict[new_dataname]=dataset(new_dataname,copy(q),
                                                        copy(i),
                                                        filename,
                                                        True,
                                                        self.M,#reference to model
                                                        parent=[data_selected_for_model],
                                                        rawdata_ref=data_selected_for_model,
                                                        type="model")#reference to original datas
            self.childmodel=dlgModel.dlgModel(self,new_dataname,type="data")
            self.childmodel.show()
    
    def Replot(self):
        if self.SelectedKey is not None:
            self.plotframe.clearData()
            for key in self.data_dict:
                self.plotframe.addData(self.data_dict[key].q,self.data_dict[key].i)#,color='b')
            self.plotframe.replot()
    
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        print(str(txt)+str(par))
        
    
    def StartAuto(self):
        self.th=Intervallometre(5.0,self.OnClickRefresh,self)
        self.th.start()
        self.ui.progressBar.setRange(0,0)

    def StopAuto(self):
        self.ui.tableWidget.setEnabled(True)
        self.th.encore=False
        self.ui.progressBar.setRange(0,1)
        
    def ExportData(self):
        if self.SelectedKey is not None:
             datax=self.data_dict[self.SelectedKey].q
             datay=self.data_dict[self.SelectedKey].i
             filters = "txt (*.txt);;log Files (*.log);;All Files (*)"
             fd = QtWidgets.QFileDialog(self)#," File dialog ", filter="log Files (*.log)")#, selected_filter)
             filename = fd.getSaveFileName(filter=filters)#")#directory=self.workingdirectory)[0]
             if filename<>"":
                 D=array([datax,datay])
                 D=D.transpose()
                 numpy.savetxt(str(filename),D,header="X\tY")
            
             

def line( x, p):
    return p[0]*x + p[1] 

def linef( x, p0, p1):
    return p0*x + p1
    
def Gauss(x,p):
    h,w,f,b=p
    return Gaussf(x,h,w,f,b)
    
def Gaussf(q,h,w,f,b):
    sigm=f*((2*numpy.log(2))**0.5)/2
    return (h-b)*numpy.exp(-((q-w)**2)/sigm**2)+b

def Trapez(x,p):
    c,f,s,h,z=p
    return Trapezf(x,c,f,s,h,z)

def Trapezf(x,center=0,fwmh=1,slope=1,height=1,zero=0):
        y=numpy.zeros(numpy.shape(x))
        #print y
        for i in range(len(x)):
            if x[i]<center:
                y[i]=scipy.special.erf((x[i]-center+fwmh*0.5)/slope)
            else:
                y[i]=-scipy.special.erf((x[i]-center-fwmh*0.5)/slope)
        y= ((y+1)*0.5*height+zero)
        #print y
        return y
        
def fit_function(p0, datax, datay, function, **kwargs):

    errfunc = lambda p, x, y: function(x,p) - y

    ##################################################
    ## 1. COMPUTE THE FIT AND FIT ERRORS USING leastsq
    ##################################################

    # If using optimize.leastsq, the covariance returned is the 
    # reduced covariance or fractional covariance, as explained
    # here :
    # http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es
    # One can multiply it by the reduced chi squared, s_sq, as 
    # it is done in the more recenly implemented scipy.curve_fit
    # The errors in the parameters are then the square root of the 
    # diagonal elements.   
    pfit, pcov, infodict, errmsg, success = \
        optimize.leastsq( errfunc, p0, args=(datax, datay), \
                          full_output=1,diag=1/numpy.array(p0))

    if (len(datay) > len(p0)) and pcov is not None:
        s_sq = (errfunc(pfit, datax, datay)**2).sum()/(len(datay)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    error = [] 
    for i in range(len(pfit)):
        try:
          error.append( numpy.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_leastsq = pfit
    perr_leastsq = numpy.array(error) 

    
    ###################################################
    ## 2. COMPUTE THE FIT AND FIT ERRORS USING curvefit
    ###################################################

    # When you have an error associated with each dataY point you can use 
    # scipy.curve_fit to give relative weights in the least-squares problem. 
    datayerrors = kwargs.get('datayerrors', None)
    curve_fit_function = kwargs.get('curve_fit_function', function)
    if datayerrors is None:
        pfit, pcov = \
            optimize.curve_fit(curve_fit_function,datax,datay,p0=p0)
    else:
        pfit, pcov = \
             optimize.curve_fit(curve_fit_function,datax,datay,p0=p0,\
                                sigma=datayerrors)
    error = [] 
    for i in range(len(pfit)):
        try:
          error.append( numpy.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_curvefit = pfit
    perr_curvefit = numpy.array(error)  

    
    ####################################################
    ## 3. COMPUTE THE FIT AND FIT ERRORS USING bootstrap
    ####################################################        

    # An issue arises with scipy.curve_fit when errors in the y data points
    # are given.  Only the relative errors are used as weights, so the fit
    # parameter errors, determined from the covariance do not depended on the
    # magnitude of the errors in the individual data points.  This is clearly wrong. 
    # 
    # To circumvent this problem I have implemented a simple bootstraping 
    # routine that uses some Monte-Carlo to determine the errors in the fit
    # parameters.  This routines generates random datay points starting from
    # the given datay plus a random variation. 
    #
    # The random variation is determined from average standard deviation of y
    # points in the case where no errors in the y data points are avaiable.
    #
    # If errors in the y data points are available, then the random variation 
    # in each point is determined from its given error. 
    # 
    # A large number of random data sets are produced, each one of the is fitted
    # an in the end the variance of the large number of fit results is used as 
    # the error for the fit parameters. 

    # Estimate the confidence interval of the fitted parameter using
    # the bootstrap Monte-Carlo method
    # http://phe.rockefeller.edu/LogletLab/whitepaper/node17.html
    residuals = errfunc( pfit, datax, datay)
    s_res = numpy.std(residuals)
    ps = []
    # 100 random data sets are generated and fitted
    for i in range(100):
      if datayerrors is None:
          randomDelta = numpy.random.normal(0., s_res, len(datay))
          randomdataY = datay + randomDelta
      else:
          randomDelta =  numpy.array( [ \
                             numpy.random.normal(0., derr,1)[0] \
                             for derr in datayerrors ] ) 
          randomdataY = datay + randomDelta
      randomfit, randomcov = \
          optimize.leastsq( errfunc, p0, args=(datax, randomdataY),\
                            full_output=0)
      ps.append( randomfit ) 

    ps = numpy.array(ps)
    mean_pfit = numpy.mean(ps,0)
    Nsigma = 1. # 1sigma gets approximately the same as methods above
                # 1sigma corresponds to 68.3% confidence interval
                # 2sigma corresponds to 95.44% confidence interval
    err_pfit = Nsigma * numpy.std(ps,0) 

    pfit_bootstrap = mean_pfit
    perr_bootstrap = err_pfit

    '''
    ####################################################
    ## 4. COMPUTE THE FIT AND FIT ERRORS USING lmfit
    ####################################################   
    

    

    # Print results 
    print "\nlestsq method :"
    print "pfit = ", pfit_leastsq
    print "perr = ", perr_leastsq
    print "\ncurvefit method :"
    print "pfit = ", pfit_curvefit
    print "perr = ", perr_curvefit
    print "\nbootstrap method :"
    print "pfit = ", pfit_bootstrap
    print "perr = ", perr_bootstrap
    '''
    #return pfit_leastsq#,pfit_curvefit,pfit_bootstrap
    return pfit_leastsq,pfit_bootstrap
              
    
if __name__ == "__main__":
      app = QtWidgets.QApplication(sys.argv)
      myapp = scanPlot()
      myapp.show()
      sys.exit(app.exec_())
