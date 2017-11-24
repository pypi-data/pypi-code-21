import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca

class LSDataDlg(wx.Dialog):
    def __init__(self, parent, datab,rcb):	
	wx.Dialog.__init__(self, parent, -1, "Data Dlg", size=wx.Size(300,100),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)	