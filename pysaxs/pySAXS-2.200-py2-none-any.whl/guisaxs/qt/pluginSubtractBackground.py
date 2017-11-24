# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt5 import QtGui, QtCore,QtWidgets
'''import numpy
from scipy import interpolate
from guidata.dataset.datatypes import ActivableDataSet
from guidata.dataset.dataitems import FileOpenItem, BoolItem, ButtonItem
import guidata
import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, ValueProp
from guidata.dataset.dataitems import BoolItem, FloatItem
from pySAXS.guisaxs.qt import plugin
from pySAXS.LS import background
from pySAXS.guisaxs import dataset
prop1 = ValueProp(False)
prop2 = ValueProp(False)

classlist=['SubtractBackground'] #need to be specified

class SubtractBackground(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="SubtractBackground"
    icon="edit_remove.png"
    
    """Calib Start program"""
    
    detector = None
    calibrant = None
    def execute(self):
        datalist=[]
        if self.parent.backgrounddata is not None:
            datalist=[self.parent.backgrounddata]
        datalist+=self.ListOfDatasChecked()
        
        items = {
        "backgroundValue": dataitems.FloatItem("Background : ",0.0,unit='cps/s'),
        "backgroundData":dataitems.ChoiceItem("or Background data : ",datalist),
        }
        clz = type("Background subtraction :", (datatypes.DataSet,), items)
        self.form = clz()
        if self.form.edit():
            #ok
            self.calculate()
            
    def calculate(self):
        datalist=self.ListOfDatasChecked()
        self.backgroundValue=self.form.backgroundValue
        self.backgroundData=datalist[self.form.backgroundData]
        for name in datalist:
            i=self.data_dict[name].i
            q=self.data_dict[name].q
            error=self.data_dict[name].error
            fn=self.data_dict[name].filename
            #subt
            if self.backgroundValue!=0.0:
                nq,ni,nerr=background.subtract1D(q,i,error,self.backgroundValue)
                self.data_dict[name+' -bckgd']=dataset.dataset(name+' -bckgd',nq,ni,filename=fn,\
                                                   parameters=None,error=nerr,\
                                                   type='-backgd',parent=[name],background_value=self.backgroundValue)
            else:
                #subtract a data
                bi=self.data_dict[self.backgroundData].i
                bq=self.data_dict[self.backgroundData].q
                berror=self.data_dict[self.backgroundData].error
                nq,ni,nerr=background.subtract2D(q,i,error,bq,bi,berror)
                self.data_dict[name+' -bckgd']=dataset.dataset(name+' -bckgd',nq,ni,filename=fn,\
                                                   parameters=None,error=nerr,\
                                                   type='-backgd',parent=[name],background_data=self.backgroundData)
                
        self.parent.redrawTheList()
        self.parent.Replot()'''
            