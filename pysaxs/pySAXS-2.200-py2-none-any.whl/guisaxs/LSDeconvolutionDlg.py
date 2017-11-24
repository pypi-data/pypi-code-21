#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca


class LSDeconvolutionDlg(wx.Dialog):
    def __init__(self, parent):
        
        wx.Dialog.__init__(self, parent, 10, "Deconvolution", size=wx.Size(400,200),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)
        
        
        self.type='Constant background'
        self.typeList=['Constant background','Power law']
        ''' # top sizer
        self.pan=wx.Panel(self, wx.ID_ANY)
        panel = self.pan
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #Parameters sizer
        sizer=wx.FlexGridSizer(rows=4,cols=2,hgap=20,vgap=5) #text , numerical value, slider
        '''
        
        self.text1 = wx.StaticText(self, 1, "Type of extrapollation for high q  ", wx.Point(10,10))
        #self.textctr1=wx.TextCtrl(self,2,str(self.type),wx.Point(100,10),wx.Size(50,20))
        self.ch1 = wx.Choice(self, 2, (50, 50), (200, 30), self.typeList)
        self.ch1.SetSelection(0)

                
        self.QuitButton=wx.Button(self,wx.ID_OK,"OK",wx.Point(100,150),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)

        
    def OnExitClick(self,event):

        ###More to do for data validation...
        
        self.type  = self.typeList[self.ch1.GetCurrentSelection()]         
        self.EndModal(wx.ID_OK)
            

        
    #######


