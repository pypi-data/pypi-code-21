#!/usr/bin/python

import wx
import numpy
import sys
#import LS.LSsca as LSsca


class LSResolutionDlg(wx.Dialog):
    def __init__(self, parent):
        
        wx.Dialog.__init__(self, parent, 10, "Resolution", size=wx.Size(400,300),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)
        
        
        self.c=0.007
        self.step=0.01
        self.boundary=0.2
        
        
        
        #self.text1 = wx.StaticText(self, 1, "Beam divergence file name", wx.Point(10,10))
        #self.textctrl1 = wx.TextCtrl(self, 2, wx.Point(100, 10), wx.Size(50,20))
        
        self.text2 = wx.StaticText(self, 3, "Vertical Slit Length(SL)", wx.Point(10,30))
        self.textctrl2 = wx.TextCtrl(self, 4, str(self.c), wx.Point(300, 30), wx.Size(50,30))

        self.text3 = wx.StaticText(self, 5, "Step for v(beta)/SL", wx.Point(10,90))
        self.textctrl3 = wx.TextCtrl(self, 6, str(self.step),wx.Point(300, 90), wx.Size(50,30))

        self.text4 = wx.StaticText(self, 7, "R/L boundary for v(beta)", wx.Point(10,150))
        self.textctrl4 = wx.TextCtrl(self, 8, str(self.boundary),wx.Point(300, 150), wx.Size(50,30))
        
        self.QuitButton=wx.Button(self,wx.ID_OK,"OK",wx.Point(100,210),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        
    def OnExitClick(self,event):

        ###More to do for data validation...
        
        self.c  = float(self.textctrl2.GetValue())
        self.step  = float(self.textctrl3.GetValue())
        self.boundary  = float(self.textctrl4.GetValue())
        self.EndModal(wx.ID_OK)
            

        
    #######
##if __name__ == '__main__':
##    app = wx.PySimpleApp()
##    frame = LSResolutionDlg(None)
##    frame.Show(True)
##    app.MainLoop()


