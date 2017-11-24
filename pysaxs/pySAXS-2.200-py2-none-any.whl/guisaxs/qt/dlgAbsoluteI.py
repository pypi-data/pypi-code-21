from PyQt5 import QtGui, QtCore, QtWidgets,uic

import pySAXS.LS.SAXSparametersXML as SAXSparameters

import sys
import pySAXS
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset
from pySAXS.LS import absolute

import os


class dlgAbsolute(QtWidgets.QDialog):#,dlgAbsoluteIui.Ui_dlgSAXSAbsolute):
    def __init__(self,parent,saxsparameters=None,datasetname=None,printout=None,\
                 referencedata=None,backgrounddata=None,datasetlist=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgAbsoluteI.ui", self)#
        self.datasetname=datasetname
        self.parentwindow=parent
        self.workingdirectory=self.parentwindow.getWorkingDirectory()
        self.params=saxsparameters
        self.datasetlist=datasetlist
        
        self.paramscopy=None
        if self.params is not None:
            self.paramscopy=self.params.copy()
        self.referencedata=referencedata
        self.backgrounddata=backgrounddata
        
        self.printout=parent.printTXT
        
        if self.params is None:
            self.params=SAXSparameters.SAXSparameters(printout=printout)
            if self.referencedata is not None :
                #reference has parameters ?
                #print "reference has parameters ?"
                if self.parentwindow.data_dict.has_key(self.referencedata):
                    #print "yes ", self.referencedata
                    print self.parentwindow.data_dict[self.referencedata].parameters
                    if self.parentwindow.data_dict[self.referencedata].parameters is not None:
                        #print "copy"
                        self.params=self.parentwindow.data_dict[self.referencedata].parameters.copy()
                    else:
                        father=self.parentwindow.data_dict[self.referencedata].parent
                        if father is not None:
                            #try to get parameters from parents
                            if self.parentwindow.data_dict[father[0]].parameters is not None:
                                #print 'Found parameters in father of reference datas : ',father[0]
                                self.params=self.parentwindow.data_dict[father[0]].parameters.copy()
        
            #import parameters from rpt
            #Normally only the first time (updated 7-3-17)
            #get filename
            newfn=filetools.getFilenameOnly(self.parentwindow.data_dict[self.datasetname].filename)
            newfn+='.rpt'
            #print newfn
            if filetools.fileExist(newfn):
                self.params.getfromRPT(newfn)
                #print self.params
            else :
                print "filename rpt ",newfn," not found" 
                newfn=filetools.getFilenameOnly(self.workingdirectory+os.sep+filetools.getFilename(self.parentwindow.data_dict[self.datasetname].filename))
                newdataname=newfn
                newfn+='.rpt'
                print 'trying : ',newfn
                if filetools.fileExist(newfn):
                    print "ici"
                    self.params.getfromRPT(newfn)
                    self.parentwindow.data_dict[self.datasetname].filename=newdataname
                else:
                    print "filename rpt ",newfn," not found"
                    #QtWidgets.QMessageBox.information(self.parent,"pySAXS", "No data are found for "+newfn, buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.NoButton)
                    
                
        self.params.printout=self.printout    
        #setup UI    
        #self.setupUi(self)
        self.ConstructUI()
        #print "constructed"
        self.params.calculate_All() #calculate datas
        self.Params2Control() #datas -> entries
        
        self.ui.buttonBox.clicked.connect(self.click)
        
    def ConstructUI(self):
        #---- set the text
        if self.datasetname is not None:
            self.ui.labelDataset.setText(self.datasetname)
        if self.datasetlist is not None:
            txt=''
            for t in self.datasetlist:
                txt+=str(t)+"\n"
            self.ui.labelDataset.setText(txt)
            
        #--- dynamic controls
        self.listStaticText={}
        self.listTextCtrl={}
        
        #-sorting parameters
        paramslist=self.params.order()
        #- controls
        i=0
        for name in paramslist:
            par=self.params.parameters[name]
            self.listStaticText[name] = QtWidgets.QLabel(par.description+" : ",self.ui.groupBox)
            self.listStaticText[name].setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            self.listStaticText[name].setMinimumHeight(20)
            self.listStaticText[name].setMaximumHeight(20)
            self.ui.formLayout.setWidget(i, QtWidgets.QFormLayout.LabelRole, self.listStaticText[name])
            self.listTextCtrl[name]=QtWidgets.QLineEdit(str(par.value),self.ui.groupBox)
            self.listTextCtrl[name].setMinimumHeight(20)
            self.listTextCtrl[name].setMaximumHeight(20)
            self.ui.formLayout.setWidget(i, QtWidgets.QFormLayout.FieldRole, self.ui.listTextCtrl[name])
            '''if par.datatype=="float":
                self.listTextCtrl[name].setValidator(QtGui.QDoubleValidator())
            elif par.datatype=="int":
                self.listTextCtrl[name].setValidator(QtGui.QIntValidator())
            '''
            if par.formula is not None:
                self.listTextCtrl[name].setReadOnly(True)
                self.listTextCtrl[name].setStyleSheet('color: blue')
                self.listStaticText[name].setStyleSheet('color: blue')          
            else:
                self.listTextCtrl[name].setReadOnly(False)
                self.listTextCtrl[name].textChanged.connect(self.onParamEdited)
            if self.datasetlist is not None :
                if  (name<>'K') and (name<>'thickness'):
                    self.listStaticText[name].setEnabled(False)
                else:
                    self.listTextCtrl[name].setStyleSheet('color: red')
                    self.listStaticText[name].setStyleSheet('color: red')        
                         
            i+=1
    
        self.ui.checkIrange.setChecked(True)
        
        if self.backgrounddata is not None:
            self.ui.groupBoxBack.setEnabled(True)
            self.ui.checkSubtractBack.setChecked(True)
            self.ui.txtBackground.setText(str(self.backgrounddata))
        else:
            self.ui.groupBoxBack.setEnabled(True)
            self.ui.txtBackground.setText("not defined")
        
        if self.referencedata is not None and self.referencedata<>self.datasetname+" scaled" :
            self.ui.groupBoxReference.setEnabled(True)
            self.ui.checkSubstractRef.setChecked(self.parentwindow.referencedataSubtract)
            self.ui.txtReference.setText(str(self.referencedata))
        else :
            self.ui.groupBoxReference.setEnabled(False)
            self.ui.txtReference.setText(str('not defined'))
        if self.datasetlist is not None:
            self.ui.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.YesToAll)
        
    
    def  eraseUI(self):
        '''
        erase the UI
        '''
        for name in self.listStaticText:
            self.ui.formLayout.removeWidget(self.listStaticText[name])
            self.listStaticText[name].deleteLater()
            self.ui.formLayout.removeWidget(self.listTextCtrl[name])
            self.listTextCtrl[name].deleteLater()
        self.listStaticText={}
        self.listTextCtrl={} 
    
    def accepted(self):
        '''
        user click on an accepted button (ok, open,...)
        do nothing
        '''
        print "on accepted"
        pass
    
    def onParamEdited(self):
        #compute
        self.Control2Params() #entries -> datas
        self.params.calculate_All(verbose=False) #calculate datas
        self.ParamsWithFormula2Control() #datas -> entries
    
    def onParamChanged(self):
        #compute
        self.Control2Params() #entries -> datas
        self.params.calculate_All() #calculate datas
        self.Params2Control() #datas -> entries
    
    def click(self,obj=None):
        name=obj.text()        if name=="OK":
            self.close()
        elif name=="Cancel":
            #print 'close'
            if self.paramscopy is not None:
                self.params=self.paramscopy.copy()
            else:
                self.params=None
            #print self.params
            self.parentwindow.data_dict[self.datasetname].parameters=self.params
            self.close()
        elif name=="Close":
            #print 'close'
            #self.params=deepcopy(self.paramscopy)
            #print self.params
            #self.parentwindow.data_dict[self.datasetname].parameters=self.params
            self.close()
        elif name=="Apply":
            self.onParamChanged()
            #apply
            #-- on wich data set ?
            if self.parentwindow is None:
                return #could not apply
            if self.datasetname<>None:
                #-- call  the method in parentwindow
                self.parentwindow.data_dict[self.datasetname].parameters=self.params
                if self.ui.checkSubtractBack.isChecked():
                    self.backgroundname=str(self.ui.txtBackground.text())
                else:
                    self.backgroundname=None
                if self.ui.checkSubstractRef.isChecked():
                    self.referencedata=str(self.ui.txtReference.text())
                    self.parentwindow.referencedataSubtract=True
                else:
                     self.referencedata=None
                     self.parentwindow.referencedataSubtract=False
                OnScalingSAXSApply(self.parentwindow,self.ui.checkQrange.isChecked(),
                                              self.ui.checkIrange.isChecked(),
                                              self.datasetname,\
                                              parameters=self.params.parameters,\
                                              backgroundname=self.backgroundname,\
                                              referencedata=self.referencedata)
                self.parentwindow.redrawTheList()
                self.parentwindow.Replot()
                
        elif name=="Yes to &All":
            print 'applyall'
            self.onParamChanged()
            #-- on wich data set ?
            if self.parentwindow is None:
                return
            if self.ui.checkSubtractBack.isChecked():
                    self.backgroundname=str(self.ui.txtBackground.text())
            else:
                    self.backgroundname=None
            if self.ui.checkSubstractRef.isChecked():
                self.referencedata=str(self.ui.txtReference.text())
            else:
                 self.referencedata=None
            
            thickness=self.params.parameters['thickness']
            k=self.params.parameters['K']
            self.printTXT("Applying for ALL thickness : "+str(thickness) +" and K factor :"+str(k))
            for n in self.datasetlist:
                self.parentwindow.data_dict[n].parameters=self.params.copy()
                newfn=filetools.getFilenameOnly(self.parentwindow.data_dict[n].filename)
                newfn+='.rpt'
                #print newfn
                '''
                if filetools.fileExist(newfn):
                    self.params.getfromRPT(newfn)
                    #self.params.parameters.getfromRPT(newfn)#apply from rpt
                else :
                    print "filename rpt not found" 
                    #will search on current folder
                    newfn=newfn=filetools.getFilenameOnly(self.workingdirectory+os.sep+filetools.getFilename(self.parentwindow.data_dict[self.datasetname].filename))
                    newfn+='.rpt'
                    print newfn
                    if filetools.fileExist(newfn):
                        self.params.getfromRPT(newfn)'''
                #print newfn
                if filetools.fileExist(newfn):
                    self.params.getfromRPT(newfn)
                    #print self.params
                else :
                    print "filename rpt ",newfn," not found" 
                    newfn=filetools.getFilenameOnly(self.workingdirectory+os.sep+filetools.getFilename(self.parentwindow.data_dict[n].filename))
                    newdataname=newfn
                    newfn+='.rpt'
                    print 'trying : ',newfn
                    if filetools.fileExist(newfn):
                        self.params.getfromRPT(newfn)
                        self.parentwindow.data_dict[n].filename=newdataname
                    else:
                        print "filename rpt ",newfn," not found" 
                OnScalingSAXSApply(self.parentwindow,self.ui.checkQrange.isChecked(),
                                              self.ui.checkIrange.isChecked(),
                                              n,\
                                              parameters=self.params.parameters,\
                                              backgroundname=self.backgroundname,\
                                              referencedata=self.referencedata)
            self.parentwindow.redrawTheList()
            self.parentwindow.Replot()
                
        elif name=="Save":
            #save
            self.saveClicked()
        elif name=="Open":
            #open
            self.openClicked()
        
    def openClicked(self):
        #-- open dialog for parameters
        fd = QtGui.QFileDialog(self)
        #get the filenames, and the filter
        filename=fd.getOpenFileName(self, caption="SAXS parameter",filter="*.xml",directory=self.workingdirectory)
        #print "file selected: -",filename,"-"
        filename=str(filename)
        if len(filename)>0:
            self.printTXT("loading parameters file ",str(filename))
            ext=filetools.getExtension(filename)
            self.params=SAXSparameters.SAXSparameters(printout=self.printTXT)
            self.params.openXML(filename)
            self.params.parameters['filename'].value=filename
            self.params.printout=self.printTXT
            
            self.eraseUI()
            self.ConstructUI()
    
    def saveClicked(self):
        '''
        User click on save button
        '''
        self.Control2Params()
        fd = QtGui.QFileDialog(self)
        filename=fd.getSaveFileName(self, caption="SAXS parameter",filter="*.xml")
        wc = "Save parameters file(*.xml)|*.xml"
        filename=str(filename)
        if len(filename)<=0:
            return
        #check if file exist already
        if filetools.fileExist(filename):
                  ret=QtWidgets.QMessageBox.question(self,"pySAXS", "file "+str(filename)+" exist. Replace ?", buttons=QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.Cancel,\
                                                  defaultButton=QtWidgets.QMessageBox.NoButton)
                  if ret==QtGui.QMessageBox.No:
                      self.printTXT("file "+str(filename)+" exist. Datas was NOT replaced")
                      return
                  elif ret==QtGui.QMessageBox.Cancel:
                      return self.saveClicked()
        self.params.saveXML(filename)
        if self.params.parameters.has_key('filename'):
            self.params.parameters['filename'].value=filename
            self.onParamEdited()
        self.printTXT("parameters was saved in "+filename)
        self.parent.setWorkingDirectory(filename) #set working dir
        
    def Params2Control(self):
        for key,value in self.params.parameters.items():
            if self.listTextCtrl.has_key(key):
                self.listTextCtrl[key].setText(str(self.params.parameters[key].value))

    def ParamsWithFormula2Control(self):
        for key,value in self.params.parameters.items():
            if self.listTextCtrl.has_key(key):
                if self.params.parameters[key].formula is not None:
                    #print "----------",key," : ",self.params.parameters[key].value
                    self.listTextCtrl[key].setText(str(self.params.parameters[key].value))

    def Control2Params(self):
        for key,value in self.params.parameters.items():
            #print key,value,self.params.parameters[key].datatype
            if (self.params.parameters[key].datatype=='float') or (self.params.parameters[key].datatype=='int'):
                if isNumeric.isNumeric(self.listTextCtrl[key].text()):
                    self.params.parameters[key].value=float(self.listTextCtrl[key].text())
                    #print "changed", self.params.parameters[key].value
            else:
                if isNumeric.isNumeric(self.listTextCtrl[key].text()):
                    self.params.parameters[key].value=float(self.listTextCtrl[key].text())
                else:
                    self.params.parameters[key].value=str(self.listTextCtrl[key].text())
            #print var,self.params.parameters[var]
     
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
            
                
def OnScalingSAXSApply(parentwindow,applyQ,applyI,dataname,parameters,backgroundname=None,referencedata=None):
        '''
        child dialog box ask to apply parameters
        '''
        workingdirectory=parentwindow.getWorkingDirectory()
        #-- 1 create new datas
        q=parentwindow.data_dict[dataname].q
        i=parentwindow.data_dict[dataname].i
        #saxsparameters=self.parentwindow.data_dict[dataname].parameters
        error=parentwindow.data_dict[dataname].error
        abs=absolute.absolute(q=q,i=i,ierr=error,parameters=parameters) #create new absolute object 2015
        #print self.params.parameters
        #-- 2 apply parameters
        parentwindow.printTXT("------ absolute intensities ------")
        if applyQ:
            parentwindow.printTXT("--set q range --")
            q=saxsparameters.calculate_q(q)
        if applyI:
            if backgroundname is not None:
                #subtract background data BACKGROUND IS DARK
                #self.backgroundname=str(self.txtBackground.text())
                qb=parentwindow.data_dict[backgroundname].q
                ib=parentwindow.data_dict[backgroundname].i
                eb=parentwindow.data_dict[backgroundname].error
                abs.subtractBackground(qb,ib,eb,backgroundname)
            #calculate ABSOLUTE
            if referencedata is None:
                newi,newerr=abs.calculate()
            else:
                thickness=parameters['thickness'].value
                parameters['thickness'].value=1.0
                newi,newerr=abs.calculate()
                #subtract solvent data
                isolv=parentwindow.data_dict[referencedata].i
                qsolv=parentwindow.data_dict[referencedata].q
                esolv=parentwindow.data_dict[referencedata].error
                newi,newerr=abs.subtractSolvent(qsolv,isolv,esolv,referencedata,thickness)
                #i,error=saxsparameters.calculate_i(i,deviation=error,solvent=b)
            '''else :
            i,error=saxsparameters.calculate_i(i,deviation=error)'''
            parentwindow.printTXT("------ absolute intensities END ------")
        #--2 bis save rpt
        #print abs
        try:
            datafile=parentwindow.data_dict[dataname].filename
            #abs.saveRPT(workingdirectory+os.sep+datafile)
            print "datafile:",datafile
            abs.saveRPT(datafile)
            #print abs
        except:
            parentwindow.printTXT('Error when trying to write rpt file for ', dataname)
        #-- 3 replot
        col=parentwindow.data_dict[dataname].color#keep the color from parent
        if parentwindow.data_dict.has_key(dataname+' scaled'):
            col=parentwindow.data_dict[dataname+' scaled'].color#keep the color
        parentwindow.data_dict[dataname+' scaled']=dataset.dataset(dataname+' scaled',q,newi,dataname+' scaled',\
                                                   parameters=None,error=newerr,\
                                                   type='scaled',parent=[dataname],color=col,abs=abs)
        parentwindow.data_dict[dataname].abs=abs
        
        
        
