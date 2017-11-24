#!/usr/bin/python

import wx
import numpy
import sys
from pySAXS.LS import LSneutron as LSneutron

class LSNeutronCon(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,1, "Calculation of Neutron contrasts", size=wx.Size(500,500),pos=wx.Point(100,100),style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour("White")
        self.symbol=[]
        self.Num=[]
        self.chlist=[]
        self.sld=0
        self.nlength=0.
        self.density=1.0
        self.lamda=1.8
        self.Element=False
        self.Number=False
      
        
        b = wx.Button(self, 2, "Reset",wx.Point(100,400),wx.Size(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnResetClick, b)

        c = wx.Button(self, 21, "Calculate",wx.Point(200,400),wx.Size(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnAction, c)

        t0=wx.StaticText(self, 31, "Neutron SLD and Absorption Calculation Applet", (10, 50), (90, 20))
        font1 = wx.Font(15, wx.SWISS, wx.NORMAL, wx.BOLD)
        t0.SetFont(font1)
        t0.SetForegroundColour("Blue")
        t1=wx.StaticText(self, 31, "Add Element", (10, 100), (90, 20))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        t1.SetFont(font)
        
        self.chEle = wx.Choice(self, 3, (150, 100), choices = LSneutron.elements)
        self.Bind(wx.EVT_CHOICE, self.OnAddAtom, self.chEle)
        
        t2=wx.StaticText(self, 41, "Choose Atom Number", (10, 150), (90, 20))
        t2.SetFont(font)
        a=range(1,100)
        for i in range(len(a)):
            self.chlist.append(str(a[i]))
        self.chNum = wx.Choice(self, 4, (150, 150),choices=self.chlist)
        self.Bind(wx.EVT_CHOICE, self.OnAddNum, self.chNum)
        
        #self.Bind(wx.EVT_CHOICE,self.OnAddAtom,self.chNum)
        
        t3=wx.StaticText(self, 31, "Density (gm/c.c)", (10, 200), (50, 20))
        t3.SetFont(font)
        self.textctr=wx.TextCtrl(self,5,str(self.density),wx.Point(150,200),wx.Size(50,20))   

        t4=wx.StaticText(self, 31, "Wavelength (A)", (220, 100), (50, 20))
        t4.SetFont(font)
        self.textctr2=wx.TextCtrl(self,5,str(self.lamda),wx.Point(320,100),wx.Size(50,20))   
        #self.Bind(wx.EVT_TEXT,self.OnAction)

        self.showformula=wx.StaticText(self, 31, "Chemical Formula=  ",pos=wx.Point(220,200))
        #font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.showformula.SetFont(font)
        
        self.show=wx.StaticText(self, 32, "Scattering Length Density= ",pos=wx.Point(10,250))
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.show.SetFont(font)

        self.show2=wx.StaticText(self, 32, "Neuton 1/e Length (cm)= ",pos=wx.Point(10,300))
        self.show2.SetFont(font)
    
    def OnAddAtom(self,event):
        if self.Element==False:
            self.symbol.append(str(event.GetString()))
            
            
            self.showformula.SetLabel(self.showformula.GetLabel()+str(event.GetString()))
            self.Element=True
            self.Number=False
            
        else:
            dlg=wx.MessageDialog(self, "Enter the Number of the Atom already choosen",  style = wx.OK| wx.ICON_INFORMATION)
            dlg.ShowModal()

        
        
    def OnAddNum(self,event):
        if self.Number==False:
            self.Num.append((float(event.GetString())))
            self.showformula.SetLabel(self.showformula.GetLabel()+str(event.GetString()))
            self.Number=True
            self.Element=False
        else:
            dlg=wx.MessageDialog(self, "Enter new Atom for which you have choosen the number",  style = wx.OK| wx.ICON_INFORMATION)
            dlg.ShowModal()
            
            
    def OnAction(self,event):
        
        if ((len(self.symbol)!=len(self.Num)) or  (float(self.textctr.GetValue())==0.)):
            dlg=wx.MessageDialog(self, "Either Atom and/or  number and/or Density is missing",  style = wx.OK| wx.ICON_INFORMATION)
            dlg.ShowModal()
            
        else:
            self.density=float(self.textctr.GetValue())
            self.sld=LSneutron.ScaLengthDensity(self.symbol,self.Num, self.density)
            self.lamda=float(self.textctr2.GetValue())
            self.nlength= LSneutron.PeneDepth(self.symbol,self.Num,self.lamda,self.density)
            self.show.SetLabel("Scattering Length Density (cm-2)= "+("%1.3e"%self.sld))
            self.show2.SetLabel("Neuton 1/e Length (cm)= "+("%f"%self.nlength))
        
    def OnResetClick(self,event):
        self.symbol=[]
        self.Num=[]
        self.show.SetLabel("Scattering Length Density (cm-2)=")
        self.showformula.SetLabel("Chemical Formula= ")
        self.show2.SetLabel("Neuton 1/e Length (cm)= ")
        
##if __name__ == '__main__':
##    app = wx.PySimpleApp()
##    frame = LSNeutronCon(None)
##    frame.Show()
##    app.MainLoop()       
