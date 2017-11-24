#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca


class LSZeroAdjustDlg(wx.Dialog):
    def __init__(self, parent, M):
        
        wx.Dialog.__init__(self, parent, -1, "Fit Gaussian", size=wx.Size(400,400),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)
        
        self.stepexp=0
        self.steprock=0
        
        self.text1 = wx.StaticText(self, 1, "Shift Data ", wx.Point(10,10))
        self.textctr1=wx.TextCtrl(self,2,str(self.stepexp),wx.Point(100,10),wx.Size(50,20))
        self.text2 = wx.StaticText(self, 1, "Shift Rocking curve ", wx.Point(10,40))
        self.textctr2=wx.TextCtrl(self,2,str(self.steprock),wx.Point(100,40),wx.Size(50,20))
        
                
        self.QuitButton=wx.Button(self,wx.ID_OK,"OK",wx.Point(100,300),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        
    def OnExitClick(self,event):

        ###More to do for data validation...
        self.stepexp  = int(self.textctr1.GetValue())
        self.steprock = int(self.textctr2.GetValue())
        
        
        self.EndModal(wx.ID_OK)
            

        
    #######


