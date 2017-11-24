#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca


class LSFitGaussianDlg(wx.Dialog):
    def __init__(self, parent, M):
        
        wx.Dialog.__init__(self, parent, -1, "Fit Gaussian", size=wx.Size(400,400),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)
        
        self.wavelength=1.54
        self.n=15
        self.a2=1e-10
        self.a1=10000.
        self.tol=1e-15
        
        self.text1 = wx.StaticText(self, 1, "wave length (A) ", wx.Point(10,10))
        self.textctr1=wx.TextCtrl(self,2,str(self.wavelength),wx.Point(100,10),wx.Size(50,20))

        self.text2 = wx.StaticText(self, 1, "Points", wx.Point(10,40))
        self.textctr2=wx.TextCtrl(self,2,str(self.n),wx.Point(100,40),wx.Size(50,20))   

        self.text3 = wx.StaticText(self, 1, "Centre", wx.Point(10,80))
        self.textctr3=wx.TextCtrl(self,2,str(self.a2),wx.Point(100,80),wx.Size(50,20))

        self.text4 = wx.StaticText(self, 1, "Inv width", wx.Point(10,120))
        self.textctr4=wx.TextCtrl(self,2,str(self.a1),wx.Point(100,120),wx.Size(50,20))

        self.text5 = wx.StaticText(self, 1, "Tol", wx.Point(10,140))
        self.textctr5=wx.TextCtrl(self,2,str(self.a1),wx.Point(100,140),wx.Size(50,20))

                
        self.QuitButton=wx.Button(self,wx.ID_OK,"OK",wx.Point(100,300),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        
    def OnExitClick(self,event):

        ###More to do for data validation...
        self.wavelength  = float(self.textctr1.GetValue())
        self.n  = int(self.textctr2.GetValue())
        self.a2=float(self.textctr3.GetValue())
        self.a1=float(self.textctr4.GetValue())
        
        self.EndModal(wx.ID_OK)
            

        
    #######


