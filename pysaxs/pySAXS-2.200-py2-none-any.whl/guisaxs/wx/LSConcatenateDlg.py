#!/usr/bin/python

import wx
import numpy
import sys
from pySAXS.guisaxs.dataset import *

class LSConcatenateDlg(wx.Frame):
    def __init__(self, parent,listofdata,newdatasetname):
        self.parentwindow=parent
        self.data_dict=parent.data_dict
        self.listofdata=listofdata
        self.newdatasetname=newdatasetname
        self.newdataset=self.parentwindow.data_dict[newdatasetname]
        taille=(len(listofdata)+2)*20+50
        wx.Frame.__init__(self, parent, 10, "pySAXS Concatenate different datas", size=wx.Size(400,taille),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetBackgroundColour("White")
        spaceBetweenControl=25
        #--- dynamic controls
        self.listCheckBox={}
        self.listTextCtrlqmin={}
        self.listTextCtrlqmax={}
        yposition=10 #begin position for dynamics controls
        print listofdata
        for var in listofdata:
            self.listCheckBox[var]=wx.CheckBox(self,-1,var,
                                                   wx.Point(10,yposition),
                                                   wx.Size(100,20))
            self.listCheckBox[var].SetValue(True)
            wx.StaticText(self, 1, "qmin :", wx.Point(120,yposition+3),wx.Size(50,20))
            self.listTextCtrlqmin[var]=wx.TextCtrl(self,2,str(numpy.min(self.data_dict[var].q)),
                                                   wx.Point(170,yposition),
                                                   wx.Size(70,20))
            wx.StaticText(self, 1, "qmax :", wx.Point(250,yposition+3),wx.Size(50,20))
            self.listTextCtrlqmax[var]=wx.TextCtrl(self,2,str(numpy.max(self.data_dict[var].q)),
                                                   wx.Point(300,yposition),
                                                   wx.Size(70,20))
            yposition+=spaceBetweenControl
        #-- select datas
        yposition+=spaceBetweenControl
        self.ApplyButton=wx.Button(self,-1,"Apply",wx.Point(20,yposition),wx.Size(75,20))
        wx.EVT_BUTTON(self, self.ApplyButton.GetId(), self.OnApplyClick)
        self.CancelButton=wx.Button(self,-1,"Cancel",wx.Point(100,yposition),wx.Size(75,20))
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnCancelClick)
        self.QuitButton=wx.Button(self,-1,"Close",wx.Point(200,yposition),wx.Size(75,20))
        wx.EVT_BUTTON(self, self.QuitButton.GetId(), self.OnExitClick)

        self.Bind(wx.EVT_CLOSE, self.OnExitClick)


    def OnApplyClick(self,event):
        '''
        User click on Apply button
        '''
        self.createData()
        self.parentwindow.OnConcatenate()

    def OnCancelClick(self,event):
        '''
        User click on Apply button
        '''
        self.parentwindow.OnConcatenateCancel(self.newdatasetname)
        self.Destroy()

    def createData(self):
        #how to know order of data
        d={} #dict with key = qmin val=datasetname
        for name in self.listofdata:
            if self.listCheckBox[name].IsChecked():
                #print "using ",name
                if d.has_key(float(self.listTextCtrlqmin[name].GetValue())):
                    print "Error, can not create datas, different datas have same qmin"
                    return
                d[float(self.listTextCtrlqmin[name].GetValue())]=name
        l=d.keys() #l : list of sorted qmin
        l.sort()
        print l
        dataset=d[l[0]]
        # clip
        self.newdataset.q,self.newdataset.i=self.clipdata(dataset)
        for j in range(1,len(l)):
            dataset=d[l[j]]
            newq,newi=self.clipdata(dataset)
            #concatenate with previous datas
            self.newdataset.q=numpy.concatenate((self.newdataset.q,newq))
            self.newdataset.i=numpy.concatenate((self.newdataset.i,newi))


    def clipdata(self,datasetname):
        q=self.parentwindow.data_dict[datasetname].q
        i=self.parentwindow.data_dict[datasetname].i
        qmini=float(self.listTextCtrlqmin[datasetname].GetValue())
        qmaxi=float(self.listTextCtrlqmax[datasetname].GetValue())
        i=numpy.repeat(i,q>=qmini)
        q=numpy.repeat(q,q>=qmini)
        i=numpy.repeat(i,q<=qmaxi)
        q=numpy.repeat(q,q<=qmaxi)
        return q,i

    def OnExitClick(self,event):
        self.Destroy()


    #######


