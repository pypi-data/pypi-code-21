from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pySAXS


#from pySAXS.guisaxs.qt import dlgModelui
from time import *
import sys
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset
from pySAXS.tools.isNumeric import *

from copy import copy
import numpy


class dlgModel(QtWidgets.QDialog):#,dlgModelui.Ui_dlgModel):
    def __init__(self,parent,selectedData,type='model'):
        #QtGui.QDialog.__init__(self)
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgModel.ui", self)
        
        self.parentwindow=parent
        self.selectedData=selectedData
        self.Model=parent.data_dict[selectedData].model
        self.par=self.Model.getArg()
        self.argbounds=self.Model.getArgBounds()
        self.itf=self.Model.getIstofit()
        self.qbase=copy(self.Model.q)
        #self.setupUi(self)
        self.ParDoc=[]
        self.ParText=[]
        self.MinText=[]
        self.MaxText=[]
        self.ParUncert=[]
        self.SlideMax=1000
        self.CheckFit=[]
        self.slider=[]
        self.fitexp=0
        self.qmax=None
        self.backupArg=None
        self.type=type #if type == 'model' desactivate fit buttons
        if self.type!='model':
            self.qbase=self.parentwindow.data_dict[self.selectedData].q
                
        self.setWindowTitle(self.Model.Description)
        if self.type!='model':
            #get q from parent
            #print "q from : ",self.qbase[0]," to ",self.qbase[-1]
            p=self.parentwindow.data_dict[self.selectedData].parent
            if self.parentwindow.data_dict.has_key(p[0]):
                self.qmax=self.qbase[-1]
                qp=self.parentwindow.data_dict[p[0]].q
                #print "q parent from ",qp[0], " to ",qp[-1]
                self.qbase=qp
            
        
        self.constructUI()
        self.labelDatas.setText('')
        #print "q from : ",self.qbase[0]," to ",self.qbase[-1]
        if self.type!='model':
            self.labelDatas.setText(self.selectedData)
            if self.Model.prefit is not None:
                rawdata_name=self.parentwindow.data_dict[self.selectedData].rawdata_ref
                iexp=parent.data_dict[rawdata_name].i
                self.qbase=self.parentwindow.data_dict[self.selectedData].q
                #try to estimate fit parameters
                self.par=self.Model.prefit(self.qbase,iexp)
                #print self.par
                self.UpdateAfterFit(self.par)
        
    def constructUI(self):
        '''
        construct the UI
        '''
        #--- description and author
        self.ui.labelDescription.setText(self.Model.Description)
        self.ui.labelAuthor.setText(self.Model.Author)
        print self.par
        #--- Parameters
        for i in range(len(self.par)):
            #--control par doc
            item=QtWidgets.QLabel(self.ui.gbParameters)
            #print self.par[i]
            item.setText(self.Model.Doc[i]+" : ")
            self.ui.gridParameters.addWidget(item, i+1, 0, 1, 1)
            self.ParDoc.append(item)
            
            #--control par text
            item=QtWidgets.QLineEdit(self.ui.gbParameters)
            item.setText(self.Model.Format[i] % self.par[i])
            self.ui.gridParameters.addWidget(item, i+1, 1, 1, 1)
            item.textChanged.connect(self.onModelUpdate)
            item.setFixedWidth(75)
            #item.setValidator(QtGui.QDoubleValidator())
            self.ParText.append(item)
            
            #--control par Uncertainties
            item=QtWidgets.QLabel(self.ui.gbParameters)
            item.setText('-')#self.Model.Format[i] % -1)
            item.setFixedWidth(150)
            item.setStyleSheet('color: blue')
            self.ui.gridParameters.addWidget(item, i+1, 2, 1, 1)
            self.ParUncert.append(item)
            
            #--control check fit
            item=QtWidgets.QCheckBox(self.ui.gbParameters)
            item.setFixedWidth(20)
            item.setChecked(self.Model.istofit[i])
            self.ui.gridParameters.addWidget(item, i+1, 3, 1, 1)
            self.ui.CheckFit.append(item)
            
            #--control min bounds
            item=QtWidgets.QLineEdit(self.ui.gbParameters)
            if self.argbounds[i] is None :
                min=0.0*self.par[i]
            else :
                min=self.argbounds[i][0]
            item.setText(self.Model.Format[i] % min)
            item.setFixedWidth(75)
            self.ui.MinText.append(item)
            item.editingFinished.connect(self.onModelUpdate)
            #item.setValidator(QtGui.QDoubleValidator())
            self.ui.gridParameters.addWidget(item, i+1, 4, 1, 1)
            
            #--control max bounds
            item=QtWidgets.QLineEdit(self.ui.gbParameters)
            item.setFixedWidth(75)
            if self.argbounds[i] is None :
                max=2.0*self.par[i]
            else :
                max=self.argbounds[i][1]
            
            item.setText(self.Model.Format[i] % max)
            self.ui.MaxText.append(item)
            item.editingFinished.connect(self.onModelUpdate)
            #item.setValidator(QtGui.QDoubleValidator())
            self.ui.gridParameters.addWidget(item, i+1, 5, 1, 1)
            
        #--- qmin qmax
        qmin=self.qbase[0]
        qmax=self.qbase[-1]
        self.qminIndex=0
        self.qmaxIndex=len(self.qbase)-1
        self.ui.editQmin.setText(str(qmin))
        self.ui.editQmax.setText(str(qmax))
        self.ui.editQminVal.setText(str(qmin))
        self.ui.editQmaxVal.setText(str(qmax))
        self.ui.sliderQmin.setMinimum(0)
        self.ui.sliderQmax.setMinimum(0)
        self.ui.sliderQmin.setMaximum(self.qmaxIndex)
        self.ui.sliderQmax.setMaximum(self.qmaxIndex)
        self.ui.sliderQmin.setValue(0)
        '''if self.qmax is not None:
            #find qmax index
            qmi=self.qbase'''
        self.ui.sliderQmax.setValue(self.qmaxIndex)
        #QtCore.QObject.connect(self.ui.sliderQmin, QtCore.SIGNAL('valueChanged(int)'), self.onSliderQminChange)
        self.ui.sliderQmin.valueChanged.connect(self.onSliderQminChange)
        #QtCore.QObject.connect(self.ui.sliderQmax, QtCore.SIGNAL('valueChanged(int)'), self.onSliderQmaxChange)
        self.ui.sliderQmax.valueChanged.connect(self.onSliderQmaxChange)
        self.ui.editQminVal.textChanged.connect(self.onQminEditChange)
        self.ui.editQmaxVal.textChanged.connect(self.onQmaxEditChange)
        #QtCore.QObject.connect(, QtCore.SIGNAL('valueChanged(float)'), self.onQminEditChange)
        
        #--- plotexp
        choicelist=['Normal','I/q','I/q^2','I/q^3','I/q^4','log(I)']
        self.radioList=[]
        i=0
        for choice in choicelist:
            item=QtWidgets.QRadioButton(self.ui.groupPlotExp)
            self.ui.gridLayoutPlotExp.addWidget(item, 0, i, 1, 1)
            item.setText(choice)
            self.ui.radioList.append(item)
            i+=1
        self.ui.radioList[0].setChecked(True)
        if self.type=='model':
            #desactivate fit buttons
            self.ui.btnFit.setEnabled(False)
            self.ui.btnFitBounds.setEnabled(False)
            self.ui.groupPlotExp.setEnabled(False)
        else:
            self.ui.btnFit.setEnabled(True)
            self.ui.btnFitBounds.setEnabled(True)
            self.ui.groupPlotExp.setEnabled(True)
            self.ui.btnFit.clicked.connect(self.onFit)
            self.ui.btnFitBounds.clicked.connect(self.onFitBounds)
            self.ui.btnFitLMFIT.clicked.connect(self.onFitLMFIT)
            self.ui.btnBack.setEnabled(False)
            self.ui.btnBack.clicked.connect(self.onBack)
        self.ui.btnReport.clicked.connect(self.onReport)
        self.ui.btnCopy.clicked.connect(self.onCopy)
        self.ui.btnPaste.clicked.connect(self.onPaste)
        #self.ui.btnCurveFit.clicked.connect(self.onCFit)
        self.ui.lblChi.setStyleSheet('color: red')
        self.ui.lblChi.setText("-")
        
    def onSliderQminChange(self,value):
        #get a index value
        print "slider val change.."
        q=self.qbase[value]
        self.ui.editQmin.setText(str(q))
        self.onModelUpdate()
                            
    def onSliderQmaxChange(self,value):
        #get a index value
        q=self.qbase[value]
        self.ui.editQmax.setText(str(q))
        self.onModelUpdate()
    
    def onQminEditChange(self):
        #print "qmin edit"
        if isNumeric(self.ui.editQminVal.text()):
            qmin=float(self.ui.editQminVal.text())
            try:
                self.ui.sliderQmin.setValue(numpy.where((self.qbase>=qmin))[0][0])
            except:
                pass
            '''self.ui.editQmin.setText(str(qmin))
            self.onModelUpdate()
            '''
            
    def onQmaxEditChange(self):
        #print "qmax edit"
        if isNumeric(self.ui.editQmaxVal.text()):
            qmax=float(self.ui.editQmaxVal.text())
            try:
                self.ui.sliderQmax.setValue(numpy.where((self.qbase<=qmax))[0][-1])
            except:
                pass
            '''self.ui.editQmax.setText(str(qmax))
            self.onModelUpdate()'''
            
    
    def getPlotExp(self):
        for i in range(len(self.radioList)):
            if self.ui.radioList[i].isChecked():
                return i
        return 0 #normally impossible
        
    '''def onTextUpdate(self):
        
        minbounds=eval(self.MinText[n].GetValue())
        maxbounds=eval(self.MaxText[n].GetValue())
        if not(isNumeric.isNumeric(self.ParText[n].GetValue())):
            #do nothing
            return
        parValue=eval(self.ParText[n].GetValue())
        if parValue<minbounds:
            self.MinText[event.GetId()].SetValue(str(parValue))
            minbounds=parValue
        if parValue>maxbounds:
            self.MaxText[event.GetId()].SetValue(str(parValue))
            maxbounds=parValue
    '''
    def getValuesForm(self):
        '''
        get the numeric vaules from the widget
        return True if sucess,
        return False if one value is not numeric
        '''
        for i in range(len(self.Model.Arg)):
            if not(isNumeric.isNumeric(str(self.ParText[i].text()))):
                #do nothing
                return
        
             
    
    def onModelUpdate(self,calculate=True):
        '''
        when a parameter is updated
        '''
        if not self.updateFit.isChecked():
            return
        if not(self.parentwindow.data_dict.has_key(self.selectedData)):
            self.parentwindow.printTXT(self.selectedData+" dataset removed ? ")
            return
        self.bounds=[]
        for i in range(len(self.Model.Arg)):
            if not(isNumeric(str(self.ParText[i].text()))):
                #do nothing
                return
            self.par[i]  = float(eval(str(self.ParText[i].text())))
            self.itf[i]=self.CheckFit[i].isChecked()
            bmin=str(self.MinText[i].text())
            bmax=str(self.MaxText[i].text())
            self.bounds.append((bmin,bmax))
        self.Model.setIstofit(self.itf)
        self.Model.setArg(self.par)
        qmin=float(self.ui.editQmin.text())
        qmax=float(self.ui.editQmax.text())
        ''''q=self.qbase
        self.qminIndex=numpy.where((q>=qmin))[0][0]
        self.qmaxIndex=numpy.where((q<=qmax))[0][-1]
        print self.qminIndex,self.qmaxIndex
        '''
        self.qminIndex=self.ui.sliderQmin.value()
        self.qmaxIndex=self.ui.sliderQmax.value()
        #print self.qminIndex,self.qmaxIndex,len(self.qbase)-1
        if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.qbase)-1):
            self.Model.q=self.qbase[self.qminIndex:self.qmaxIndex]
            #compute chicarre
            '''if self.type=="data":
            #compute chi_carre for datas
            #print 'compute chi_carre'
            rawdataset_name = self.parentwindow.data_dict[self.dataset_name].rawdata_ref
            iexp=self.parentwindow.data_dict[rawdataset_name].i[:]
            val=self.Model.chi_carre(self.par,iexp)
            self.chicarre.Clear()
            self.chicarre.AppendText('Chi carre : '+str(val))'''
        if not calculate:
            return
        if self.parentwindow.data_dict[self.selectedData].model<>None:
                #ok model exist
                #self.parentwindow.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                self.parentwindow.data_dict[self.selectedData].model=self.Model
                self.parentwindow.data_dict[self.selectedData].i=self.Model.getIntensity()
                self.parentwindow.data_dict[self.selectedData].q=copy(self.Model.q)
                self.parentwindow.Replot()
                #self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def onFit(self):
        '''
        user want to fit
        '''
        #print 'on fit'
        self.ui.btnBack.setEnabled(True)
        self.backup()
        self.onModelUpdate(calculate=False)
        
        if not self.parentwindow.data_dict.has_key(self.selectedData):
            return
        
        rawdata_name=self.parentwindow.data_dict[self.selectedData].rawdata_ref
        self.parentwindow.printTXT( "fit with raw data from ",rawdata_name)
        if self.parentwindow.data_dict.has_key(rawdata_name) and self.parentwindow.data_dict[self.selectedData].model<>None:
            if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.parentwindow.data_dict[rawdata_name].q)-1):
                #qmin and qmax have changed
                q=self.parentwindow.data_dict[rawdata_name].q[self.qminIndex:self.qmaxIndex]
                i=self.parentwindow.data_dict[rawdata_name].i[self.qminIndex:self.qmaxIndex]
            else :
                #update intensities
                q=self.parentwindow.data_dict[rawdata_name].q
                i=self.parentwindow.data_dict[rawdata_name].i
                self.Model.q=q
            #FIT
            self.fitexp=self.getPlotExp()
            #print "plotexp",self.fitexp
            res=self.Model.fit(i,self.fitexp)
            #fitted parameters -> new parameters
            self.parentwindow.printTXT('fitted parameters : ',res)
            #child.Model.Arg=res
            chi=self.Model.chi_carre(res,i)
            #print chi
            self.ui.lblChi.setText(str(chi))
            self.UpdateAfterFit(res)
            '''self.parentwindow.data_dict[self.selectedData].model=self.Model
            self.parentwindow.data_dict[self.selectedData].i=self.Model.getIntensity()
            self.parentwindow.Replot()'''
    
    def onCFit(self):
        '''
        user want to fit
        '''
        #print 'on fit'
        self.ui.btnBack.setEnabled(True)
        self.backup()
        self.onModelUpdate(calculate=False)
        
        if not self.parentwindow.data_dict.has_key(self.selectedData):
            return
        
        rawdata_name=self.parentwindow.data_dict[self.selectedData].rawdata_ref
        self.parentwindow.printTXT( "fit with raw data from ",rawdata_name)
        if self.parentwindow.data_dict.has_key(rawdata_name) and self.parentwindow.data_dict[self.selectedData].model<>None:
            if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.parentwindow.data_dict[rawdata_name].q)-1):
                #qmin and qmax have changed
                q=self.parentwindow.data_dict[rawdata_name].q[self.qminIndex:self.qmaxIndex]
                i=self.parentwindow.data_dict[rawdata_name].i[self.qminIndex:self.qmaxIndex]
            else :
                #update intensities
                q=self.parentwindow.data_dict[rawdata_name].q
                i=self.parentwindow.data_dict[rawdata_name].i
                self.Model.q=q
            #FIT
            self.fitexp=self.getPlotExp()
            #print "plotexp",self.fitexp
            res=self.Model.cfit(i,self.fitexp)
            #fitted parameters -> new parameters
            self.parentwindow.printTXT('fitted parameters : ',res)
            #child.Model.Arg=res
            self.UpdateAfterFit(res)
            '''self.parentwindow.data_dict[self.selectedData].model=self.Model
            self.parentwindow.data_dict[self.selectedData].i=self.Model.getIntensity()
            self.parentwindow.Replot()'''
        
        
    def onFitBounds(self):
        self.ui.btnBack.setEnabled(True)
        self.backup()
        
        if not self.parentwindow.data_dict.has_key(self.selectedData):
            return
        self.onModelUpdate(calculate=False)
        rawdata_name=self.parentwindow.data_dict[self.selectedData].rawdata_ref
        self.parentwindow.printTXT( "fit with raw data from ",rawdata_name)
        if self.parentwindow.data_dict.has_key(rawdata_name) and self.parentwindow.data_dict[self.selectedData].model<>None:
            if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.parentwindow.data_dict[rawdata_name].q)-1):
                #qmin and qmax have changed
                q=self.parentwindow.data_dict[rawdata_name].q[self.qminIndex:self.qmaxIndex]
                i=self.parentwindow.data_dict[rawdata_name].i[self.qminIndex:self.qmaxIndex]
            else :
                #update intensities
                q=self.parentwindow.data_dict[rawdata_name].q
                i=self.parentwindow.data_dict[rawdata_name].i
                self.Model.q=q
            #FIT
            res=self.Model.fitBounds(i,self.bounds,self.fitexp)
            #fitted parameters -> new parameters
            self.parentwindow.printTXT('fitted parameters : ',res)
            #child.Model.Arg=res
            self.UpdateAfterFit(res)
            
    def onFitLMFIT(self):
        if not self.parentwindow.data_dict.has_key(self.selectedData):
            return
        self.onModelUpdate(calculate=False)
        rawdata_name=self.parentwindow.data_dict[self.selectedData].rawdata_ref
        self.parentwindow.printTXT( "fit with raw data from ",rawdata_name)
        if self.parentwindow.data_dict.has_key(rawdata_name) and self.parentwindow.data_dict[self.selectedData].model<>None:
            if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.parentwindow.data_dict[rawdata_name].q)-1):
                #qmin and qmax have changed
                q=self.parentwindow.data_dict[rawdata_name].q[self.qminIndex:self.qmaxIndex]
                i=self.parentwindow.data_dict[rawdata_name].i[self.qminIndex:self.qmaxIndex]
            else :
                #update intensities
                q=self.parentwindow.data_dict[rawdata_name].q
                i=self.parentwindow.data_dict[rawdata_name].i
                self.Model.q=q
            #FIT
            self.fitexp=self.getPlotExp()
            print self.fitexp
            res,resLMFIT=self.Model.fitLMFIT(i,self.fitexp)
            #fitted parameters -> new parameters
            self.parentwindow.printTXT('fitted parameters : ',res)
            chi=self.Model.chi_carre(res,i)
            self.ui.lblChi.setText(str(chi))
            self.UpdateAfterFit(res,resLMFIT)
    
    
    def UpdateAfterFit(self,result,res_err=None):
        '''
        update all after a fit
        '''
        val=numpy.array(result).copy()
        #print "UPDATE AFTER FIT",val
        for i in range(len(val)):
            #print i,val[i]
            self.ParText[i].setText(self.Model.Format[i] % val[i])
            if res_err is not None:
                if res_err[i] is not None:
                    try:
                        if val[i]!=0:
                            spercent = '({0:.2%})'.format(abs(res_err[i]/val[i]))
                        else:
                            spercent=''
                    except ZeroDivisionError:
                        spercent=''
                    #self.Doc[i]+' %s +/-%6.2f %s' % (pp.value, res_err, spercent)
                    #txterr=self.Model.Format[i] % res_err[i]
                    #print '+/-'+self.Model.Format[i]+' %s'
                    self.ParUncert[i].setText(('+/-'+self.Model.Format[i]+' %s') %(res_err[i],spercent))
                else:
                    self.ParUncert[i].setText('-')
            else:
                self.ParUncert[i].setText('-')
                
        #update plot
        self.parentwindow.data_dict[self.selectedData].model=self.Model
        self.parentwindow.data_dict[self.selectedData].i=self.Model.getIntensity()
        self.parentwindow.Replot()
        self.ui.btnBack.setEnabled(True)
        self.onCopy()
        
        
    def onReport(self):
        '''
        display fit informations on the matplotlib graph
        '''
        #print 'on report'
        self.parentwindow.Replot()
        plotframe=self.parentwindow.plotframe
        
        reporttext='Model : '+self.Model.Description+'\n'
        #reporttext+=self.Model.Author+'\n'
        for i in range(len(self.par)):
            
            if str(self.ParUncert[i].text())!='-':
                reporttext+=self.Model.Doc[i]+' : '+str(self.ParText[i].text())+' '+str(self.ParUncert[i].text())+'\n'
            else:
                reporttext+=self.Model.Doc[i]+' : '+str(self.ParText[i].text())+'\n'
            
        reporttext+='\n'+ctime()
        plotframe.text(0.05,0.05,reporttext)#display text
    
    def onCopy(self):
        '''
        copy parameters to clipboard
        '''
        clipstring=''
        self.clipboard = QtWidgets.QApplication.clipboard()
        for i in range(len(self.Model.Arg)):
            clipstring+= str(self.ParText[i].text())+";"
        clipstring+=str(self.ui.sliderQmin.value())+";"
        clipstring+=str(self.ui.sliderQmax.value())
        self.clipboard.setText(clipstring)
        try:
            self.parentwindow.OnCopyModel(self.Model)
        except AttributeError:
            pass
     
    
    def onPaste(self,clip=None):
        '''
        get parameters to clipboard
        '''
        if clip is None:
            clip=QtWidgets.QApplication.clipboard()
        else:
            print clip
        clipboard = clip
        clipstring=str(clipboard.text())
        print clipstring
        if clipstring!='':
            l=clipstring.split(';')
            for i in range(len(l)):
                if i>=len(self.Model.Arg):
                    break
                if l[i]!='':
                    self.ParText[i].setText(l[i])
            if len(l)>=len(self.Model.Arg)+2:
                if isNumeric.isNumeric(l[i]):
                    self.ui.sliderQmin.setValue(int(l[i]))
                if isNumeric.isNumeric(l[i+1]):
                    self.ui.sliderQmax.setValue(int(l[i+1]))
                
            self.onModelUpdate()
    
    def backup(self):
        self.backupArg=[]
        for a in self.Model.Arg:
            self.backupArg.append(a)
        print self.backupArg
            
    def onBack(self):
        if self.backupArg is not None:
            #print self.backupArg
            for i in range(min([len(self.backupArg),len(self.Model.Arg)])):
                self.Model.Arg[i]=self.backupArg[i]
                self.ParText[i].setText(str(self.Model.Arg[i]))
                #print i
            self.onModelUpdate()
