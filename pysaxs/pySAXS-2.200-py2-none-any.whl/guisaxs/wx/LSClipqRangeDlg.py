#!/usr/bin/python

import wx
import numpy
import sys



class LSClipqRangeDlg(wx.Frame):

    def __init__(self,parent,dataset_name):
        wx.Frame.__init__(self, parent, 10, "Select q Range", size=wx.Size(250,250),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.dataset_name=dataset_name
        self.parentwindow=parent
        self.SetBackgroundColour("White")
        self.q=self.parentwindow.data_dict[dataset_name].q
        self.qmini=numpy.min(self.q)
        self.qmaxi=numpy.max(self.q)
        self.np=len(self.q)
        sizer=wx.GridSizer(rows=6,cols=2,hgap=10,vgap=10)
        self.text1 = wx.StaticText(self, 1, "q minimum : ")
        sizer.Add(self.text1,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr1=wx.TextCtrl(self,2,str(self.qmini))
        sizer.Add(self.textctr1,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.text2 = wx.StaticText(self, 3, "q maximum : ")
        sizer.Add(self.text2,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr2=wx.TextCtrl(self,wx.ID_ANY,str(self.qmaxi))
        sizer.Add(self.textctr2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.text3 = wx.StaticText(self, 4, "Nb of points : " )
        sizer.Add(self.text3,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr3=wx.TextCtrl(self,5,str(self.np))
        sizer.Add(self.textctr3,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.okButton=wx.Button(self,wx.ID_ANY,"OK")
        sizer.Add(self.okButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.okButton.GetId(), self.TextUpdate)
        self.CancelButton=wx.Button(self,wx.ID_ANY,"CANCEL")
        sizer.Add(self.CancelButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnExitClick)
        sizer.Add(wx.StaticText(self, 1, "WARNING : data will be lost !\n You can duplicate datas before."),flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)
        self.Fit()

    def TextUpdate(self,event):

        self.qmini = float(self.textctr1.GetValue())
        self.qmaxi = float(self.textctr2.GetValue())
        self.np = float(self.textctr3.GetValue())
        #if self.qmini>=numpy.min(self.q) and self.qmaxi<=numpy.max(self.q):
        self.parentwindow.OnClipqRange(self)
        '''else:
           dlg=wx.MessageDialog(self,'Clip Range is out of Data Range','pySAXS alert',wx.OK|wx.ICON_INFORMATION)
           val=dlg.ShowModal()
        '''
        self.Destroy()


    def OnExitClick(self,event):
        '''
        user click on Cancel
        exit without clipping
        '''
        self.Destroy()
