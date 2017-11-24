#!/usr/bin/python

import wx
import numpy
import sys



class LSUSAXSsimuDlg(wx.Frame):
    def __init__(self, parent):
        
        wx.Frame.__init__(self, parent, 100, "USAXSsimu", size=wx.Size(400,300),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parentwindow=parent
        self.SetBackgroundColour("Orange")
        self.mu_p=35.
        self.rho_p=2.
        self.mu_S=1.
        self.rho_S=1.
        self.phim_p=1e-2
        self.rho_soln=1.0
        self.thicks=0.1
        self.backgr=3.0
        self.cb_val=False
        
        self.text1 = wx.StaticText(self, 1, "Particle mu/rho (cm^2/g)", wx.Point(10,40))
        self.textctr1=wx.TextCtrl(self,2,str(self.mu_p),wx.Point(200,40),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr1)

        self.text2 = wx.StaticText(self, 3, "Particle density(g/cc)", wx.Point(10,80))
        self.textctr2=wx.TextCtrl(self,4,str(self.rho_p),wx.Point(200,80),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr2)
        
        self.text3 = wx.StaticText(self, 5, "Solvent mu/rho (cm^2/g)", wx.Point(10,100))
        self.textctr3=wx.TextCtrl(self,6,str(self.mu_S),wx.Point(200,100),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr3)

        self.text4 = wx.StaticText(self, 7, "Solvent density(g/cc)", wx.Point(10,120))
        self.textctr4=wx.TextCtrl(self,8,str(self.rho_S),wx.Point(200,120),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr4)

        self.text5 = wx.StaticText(self, 9, "Particle mass fraction", wx.Point(10,140))
        self.textctr5=wx.TextCtrl(self,10,str(self.phim_p),wx.Point(200,140),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr5)
        
        self.text6 = wx.StaticText(self, 11, "Solution density (g/cc)", wx.Point(16,160))
        self.textctr6=wx.TextCtrl(self,12,str(self.rho_soln),wx.Point(200,160),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr6)

        self.text7 = wx.StaticText(self, 13, "Sample thickness (cm)", wx.Point(10,180))
        self.textctr7=wx.TextCtrl(self,14,str(self.thicks),wx.Point(200,180),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr7)

        self.text8 = wx.StaticText(self, 15, "Background count ", wx.Point(10,200))
        self.textctr8=wx.TextCtrl(self,16,str(self.backgr),wx.Point(200,200),wx.Size(50,20))   
        self.Bind(wx.EVT_TEXT,self.textUpdate,self.textctr8)

        self.cb = wx.CheckBox(self, 17, "Save Data",wx.Point(300, 40), wx.Size(100, 20))
        self.cb.SetValue(0)
        self.Bind(wx.EVT_CHECKBOX, self.textUpdate, self.cb)
        
        self.QuitButton=wx.Button(self,wx.ID_OK,"Close",wx.Point(100,220),wx.Size(75,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        
        
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)
        self.parentwindow.OnUSAXSsimu(self.parentwindow)

        
        
    def textUpdate(self,event):
        
        self.mu_p = float(eval(self.textctr1.GetValue()))
        self.rho_p= float(eval(self.textctr2.GetValue()))
        self.mu_S= float(eval(self.textctr3.GetValue()))
        self.rho_S=float(eval(self.textctr4.GetValue()))
        
        self.phim_p=float(eval(self.textctr5.GetValue()))
        self.rho_soln=float(eval(self.textctr6.GetValue()))
        self.thicks  =float(eval(self.textctr7.GetValue()))
        self.backgr  =float(eval(self.textctr8.GetValue()))
        self.cb_val=self.cb.GetValue()
        
        self.parentwindow.OnUSAXSsimu(self.parentwindow)
        
        
    def OnExitClick(self,event):
        self.Destroy()        

        
    #######
##if __name__ == '__main__':
##    app = wx.PySimpleApp()
##    frame = LSUSAXSsimuDlg(None)
##    frame.Show(True)
##    app.MainLoop()
##
