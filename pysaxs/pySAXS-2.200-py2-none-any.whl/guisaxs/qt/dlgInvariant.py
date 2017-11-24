from PyQt5 import QtGui, QtCore, uic,QtWidgets


import pySAXS.LS.SAXSparametersXML as SAXSparameters
import sys

import pySAXS
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
from pySAXS.guisaxs.dataset import *
from pySAXS.LS import  invariant
import os

class dlgInvariant(QtWidgets.QDialog):
    def __init__(self,parent,datasetname="",printout=None):#, referencedata=None,backgrounddata=None,datasetlist=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgInvariant.ui", self)#
        self.datasetname=datasetname
        self.parentwindow=parent
        self.workingdirectory=self.parentwindow.getWorkingDirectory()
        self.parent=parent
        self.data_dict=self.parent.data_dict
        self.printout=parent.printTXT
        #--- invariant
        self.DPQ=self.datasetname+" invariant low q"
        self.data_dict[self.DPQ]=dataset(self.DPQ,\
                                              self.data_dict[self.datasetname].q,\
                                              self.data_dict[self.datasetname].i,\
                                              comment="invariant low q",\
                                              type='calculated',
                                              parent=[self.datasetname])
        
        self.DGQ=self.datasetname+" invariant high q"
        self.data_dict[self.DGQ]=dataset(self.DGQ,\
                                              self.data_dict[self.datasetname].q,\
                                              self.data_dict[self.datasetname].i,\
                                              comment="invariant high q",\
                                              type='calculated',
                                              parent=[self.datasetname])
        
        
        
        self.q=self.data_dict[self.datasetname].q
        self.i=self.data_dict[self.datasetname].i
        self.qmini=self.q[0]
        self.qmaxi=self.q[-1]
        self.radius=300.0
        self.invariant=invariant.invariant(self.q,self.i,radius=self.radius,printout=self.printTXT)
        self.B=self.invariant.B
        #dataset for low q range
        self.data_dict[self.DPQ].q=self.invariant.LowQq
        self.data_dict[self.DPQ].i=self.invariant.LowQi
        #dataset for high q range
        self.data_dict[self.DGQ].q=self.invariant.HighQq
        self.data_dict[self.DGQ].i=self.invariant.HighQi
        self.parent.redrawTheList()
        self.parent.Replot()
        
        
        self.ConstructUI()
        self.calculateAll()
        
        #QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        self.ui.buttonBox.clicked.connect(self.click)
        
    def ConstructUI(self):
        #---- set the text
        self.ui.labelDataset.setText(self.datasetname)
        
        self.UpdateResults()
        self.ui.edtQmin.setText(str(self.qmini))
        self.ui.edtQmin.textChanged.connect(self.onTextEdited)
        self.ui.edtQmin.setValidator(QtGui.QDoubleValidator())
        self.ui.edtQmax.setText(str(self.qmaxi))
        self.ui.edtQmax.textChanged.connect(self.onTextEdited)
        self.ui.edtQmax.setValidator(QtGui.QDoubleValidator())
        self.ui.edtRadius.setText(str(self.radius))
        self.ui.edtRadius.textChanged.connect(self.onTextEdited)
        self.ui.edtRadius.setValidator(QtGui.QDoubleValidator())
        self.ui.edtB.setText(str(self.B))
        self.ui.edtB.textChanged.connect(self.onTextEdited)
        self.ui.edtB.setValidator(QtGui.QDoubleValidator())
        
        self.ui.edtP1.setReadOnly(True)
        self.ui.edtP1.setStyleSheet('color: blue')
        self.ui.edtP2.setReadOnly(True)
        self.ui.edtP2.setStyleSheet('color: blue')
        self.ui.edtP3.setReadOnly(True)
        self.ui.edtP3.setStyleSheet('color: blue')
        self.ui.edtInvariant.setReadOnly(True)
        self.ui.edtInvariant.setStyleSheet('color:red')
        self.ui.edtVolume.setReadOnly(True)
        self.ui.edtVolume.setStyleSheet('color:red')
                
    
    def UpdateResults(self):
        self.ui.edtP1.setText(str(self.invariant.P1))
        self.ui.edtP2.setText(str(self.invariant.P2))
        self.ui.edtP3.setText(str(self.invariant.P3))
        self.ui.edtInvariant.setText(str(self.invariant.invariant))
        self.ui.edtVolume.setText(str(self.invariant.volume))
        
    
    def calculateAll(self):
            #print "Calculating Invariant"
            #"--- Calculating Invariant ---")
            self.invariant.calculate(self.radius, self.qmini, self.qmaxi, self.B)
            
            #update dataset
            #dataset for low q range
            
            self.data_dict[self.DPQ].q=self.invariant.LowQq
            self.data_dict[self.DPQ].i=self.invariant.LowQi
            #dataset for high q range
            self.data_dict[self.DGQ].q=self.invariant.HighQq
            self.data_dict[self.DGQ].i=self.invariant.HighQi
            self.parent.redrawTheList()
            self.parent.Replot()
            self.UpdateResults()
                        
    def onTextEdited(self):
        if isNumeric.isNumeric(self.ui.edtQmin.text()):
            self.qmini=float(self.ui.edtQmin.text())
        else :
            return
        if isNumeric.isNumeric(self.ui.edtQmax.text()):
            self.qmaxi=float(self.ui.edtQmax.text())
        else :
            return
        if isNumeric.isNumeric(self.ui.edtB.text()):
            self.B=float(self.ui.edtB.text())
        else :
            return
        if isNumeric.isNumeric(self.ui.edtRadius.text()):
            self.radius=float(self.ui.edtRadius.text())
        else :
            return
        self.calculateAll()
        
        
        '''
        
        #here we use guidata to generate a dialog box
        items = {"dataname":dataitems.StringItem("Datas :",self.selectedData).set_prop("display", active=False),
                 "bg": datatypes.BeginGroup("Variables :"),
                 "qmin":dataitems.FloatItem("q minimum :",qmini).set_prop("display", callback=self.calculateAll),
                 "radius": dataitems.FloatItem("estimate radius of giration (A)",self.radius).set_prop("display", callback=self.calculateAll),
                 "qmax": dataitems.FloatItem("q maximum :",qmaxi).set_prop("display", callback=self.calculateAll),
                 "B":dataitems.FloatItem("Large angle extrapolation (cm-5): ",self.invariant.B).set_prop("display", callback=self.calculateAll),
                 "eg":datatypes.EndGroup("Variables :"),
                 "bg2":datatypes.BeginGroup("Calculations :"),
                 "P1":dataitems.FloatItem("Small Angle part (cm-4)=",self.invariant.P1).set_prop("display", active=False),
                 "P2":dataitems.FloatItem("Middle Angle part (cm-4)= ",self.invariant.P2).set_prop("display", active=False),
                 "P3":dataitems.FloatItem("Large Angle part (cm-4)= ",self.invariant.P3).set_prop("display", active=False),
                 "Invariant":dataitems.FloatItem("Invariant (cm-4)= ",self.invariant.invariant).set_prop("display", active=False),
                 "volume":dataitems.FloatItem("Particule Volume (cm3) = ",self.invariant.volume).set_prop("display", active=False),
                 "eg2":datatypes.EndGroup("Calculations :"),       
        }
        clz = type("Invariant :", (datatypes.DataSet,), items)
        self.dlg = clz()
        self.dlg.edit() 
        #print "close" 
        '''    
            
    def accepted(self):
        '''
        user click on an accepted button (ok, open,...)
        do nothing
        '''
        print "on accepted"
        pass
    
    
    def click(self,obj=None):
        name=obj.text()
        #print name
        if name=="OK":
            self.close()
        elif name=="Close":
            self.close()
        elif name=="Apply":
            self.onTextEdited()           
        
        
     
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
            
                
