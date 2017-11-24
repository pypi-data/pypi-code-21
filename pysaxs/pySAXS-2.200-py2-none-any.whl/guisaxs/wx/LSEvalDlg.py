#!/usr/bin/python

import wx
import numpy
import sys



class LSEvalDlg(wx.Frame):

    def __init__(self,parent,listofdata,newdatasetname):
        wx.Frame.__init__(self, parent, 10, "pySaxs Calculator", size=wx.Size(350,250),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.listofdata=listofdata
        self.parentwindow=parent
        self.newdatasetname=newdatasetname
        self.SetBackgroundColour("White")
        self.variableDict={}
        variablename='i'

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #--------- dataset name as variable
        box1=wx.StaticBox(self,-1,"Data set :")
        i=0
        stsizer=wx.StaticBoxSizer(box1,wx.VERTICAL)
        stsizer.Add(wx.StaticText(self, 1, "Variables"),flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        for name in self.listofdata:
            self.variableDict[variablename+str(i)]=name
            chaine=variablename+str(i)+'='+name
            stsizer.Add(wx.StaticText(self, 1, chaine),flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            i+=1
        #variableDict={'i0':'data1','i1':'data2',...}
        vbox_top.Add(stsizer, 0, wx.BOTTOM | wx.TOP, 9)
        stsizer.Add(wx.StaticText(self, 1, "IMPORTANT ! : If datas have same abscissa, errors will be added (if present)"),flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #---------- box for formula
        box2=wx.StaticBox(self,-1,"Formula :")
        stsizer2=wx.StaticBoxSizer(box2,wx.VERTICAL)
        self.textFormula=wx.TextCtrl(self,wx.ID_ANY,'i0*1')
        stsizer2.Add(self.textFormula, 0, wx.EXPAND, 9)
        vbox_top.Add(stsizer2, 0, wx.EXPAND, 9)
        
        box3=wx.StaticBox(self,-1,"New data name :")
        stsizer3=wx.StaticBoxSizer(box3,wx.VERTICAL)
        self.textName=wx.TextCtrl(self,wx.ID_ANY,newdatasetname)
        stsizer3.Add(self.textName, 0, wx.EXPAND, 9)
        vbox_top.Add(stsizer3, 0, wx.EXPAND, 9)
        
        self.applyButton=wx.Button(self,wx.ID_ANY,"APPLY")
        vbox_top.Add(self.applyButton, 0, wx.BOTTOM | wx.TOP, 9)
        wx.EVT_BUTTON(self, self.applyButton.GetId(), self.TextUpdate)
        self.CancelButton=wx.Button(self,wx.ID_ANY,"CANCEL")
        vbox_top.Add(self.CancelButton, 0, wx.BOTTOM | wx.TOP, 9)
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnExitClick)

        self.SetSizer(vbox_top)
        vbox_top.Fit(self)
        #self.Centre()


    def TextUpdate(self,event):
        self.parentwindow.OnEvalCalcul(self.textFormula.GetValue(),self.variableDict,self.textName.GetValue(),self.listofdata)

    def OnExitClick(self,event):
        '''
        user click on Cancel
        exit without clipping
        '''
        self.Destroy()
