#!/usr/bin/python
'''
wx python dialog box for calculation of invariant
'''
import wx
import numpy
import sys
from scipy import integrate
from scipy import interpolate
from scipy import special
from math import  *
#import pySAXS.LS.LSsca as LSsca
from pySAXS.LS import LSsca
from pySAXS.LS import  invariant


class LSInvariantDlg(wx.Frame):

    def __init__(self,parent,dataset_name,DPQ,DGQ):
        wx.Frame.__init__(self, parent, 10, "Invariant", size=wx.Size(250,500),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.DPQ=DPQ
        self.DGQ=DGQ
        self.dataset_name=dataset_name
        self.parentwindow=parent
        self.SetBackgroundColour("lightgrey")
        self.q=self.parentwindow.data_dict[dataset_name].q
        self.i=self.parentwindow.data_dict[dataset_name].i
        qmini=self.q[0]
        qmaxi=self.q[-1]
        self.radius=300.0
        self.invariant=invariant.invariant(self.q,self.i,radius=self.radius,printout=self.parentwindow.printTXT)
        
        #dataset for low q range
        self.parentwindow.data_dict[self.DPQ].q=self.invariant.LowQq
        self.parentwindow.data_dict[self.DPQ].i=self.invariant.LowQi
        #dataset for high q range
        self.parentwindow.data_dict[self.DGQ].q=self.invariant.HighQq
        self.parentwindow.data_dict[self.DGQ].i=self.invariant.HighQi
        
        self.parentwindow.RePlot()
        
        
        #interface
        Dsize=(150,20)
        sizer=wx.GridSizer(rows=11,cols=2,hgap=5,vgap=2)
        self.text1 = wx.StaticText(self, -1, "Data Set : ")
        sizer.Add(self.text1,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.text2 = wx.StaticText(self, -1, dataset_name)
        sizer.Add(self.text2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text3 = wx.StaticText(self, -1, "q minimum : ")
        sizer.Add(self.text3,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr1=wx.TextCtrl(self,-1,str(qmini),size=Dsize)
        sizer.Add(self.textctr1,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.textRadius = wx.StaticText(self, -1, "estimate radius of giration (A) : ")
        sizer.Add(self.textRadius,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctrRadius=wx.TextCtrl(self,-1,str(self.radius),size=Dsize)
        sizer.Add(self.textctrRadius,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text4 = wx.StaticText(self, -1, "q maximum : ")
        sizer.Add(self.text4,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr2=wx.TextCtrl(self,wx.ID_ANY,str(qmaxi),size=Dsize)
        sizer.Add(self.textctr2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text6 = wx.StaticText(self, -1, "Large angle extrapolation (cm-5): " )
        sizer.Add(self.text6,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr4=wx.TextCtrl(self,-1,str(self.invariant.B),size=Dsize)
        sizer.Add(self.textctr4,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 1 result
        self.text7 = wx.StaticText(self, -1, "Small Angle part : ")
        sizer.Add(self.text7,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP1 = wx.StaticText(self, -1, " -- cm-4 ")
        self.textP1.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP1,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 2 result
        self.text8 = wx.StaticText(self, -1, "Middle Angle part : ")
        sizer.Add(self.text8,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP2 = wx.StaticText(self, 1, " -- cm-4 ")
        self.textP2.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 3 result
        self.text9 = wx.StaticText(self, -1, "Large Angle part : ")
        sizer.Add(self.text9,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP3 = wx.StaticText(self, -1, " -- cm-4 ")
        self.textP3.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP3,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #Full result
        self.text10 = wx.StaticText(self, -1, "Invariant = ")
        sizer.Add(self.text10,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textInv = wx.StaticText(self, -1, " -- cm-4 ")
        self.textInv.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textInv,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #Particule volume result
        self.text11 = wx.StaticText(self, -1, "Particule Volume = ")
        sizer.Add(self.text11,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textVolume = wx.StaticText(self, -1, " -- cm3 ")
        self.textVolume.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textVolume,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.okButton=wx.Button(self,wx.ID_ANY,"Compute")
        sizer.Add(self.okButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.okButton.GetId(), self.TextUpdate)
        self.CancelButton=wx.Button(self,wx.ID_ANY,"Close")
        sizer.Add(self.CancelButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnExitClick)
       
        self.SetSizer(sizer)
        self.Fit()
        

    def TextUpdate(self,event):
        '''
        when the user click on Compute
        '''
       #"--- Calculating Invariant ---")
        qmini = float(self.textctr1.GetValue())
        qmaxi = float(self.textctr2.GetValue())
        radius=float(self.textctrRadius.GetValue())
        B = float(self.textctr4.GetValue())
        
        self.invariant.calculate(radius, qmini, qmaxi, B)
        
        #update dataset
        #dataset for low q range
        self.parentwindow.data_dict[self.DPQ].q=self.invariant.LowQq
        self.parentwindow.data_dict[self.DPQ].i=self.invariant.LowQi
        #dataset for high q range
        self.parentwindow.data_dict[self.DGQ].q=self.invariant.HighQq
        self.parentwindow.data_dict[self.DGQ].i=self.invariant.HighQi
        
        #update 
        self.textP1.SetLabel(str(self.invariant.P1) + " cm-4 ")
        self.textP2.SetLabel(str(self.invariant.P2) + " cm-4 ")
        self.textP3.SetLabel(str(self.invariant.P3) + " cm-4 ")
        self.textInv.SetLabel(str(self.invariant.invariant) + " cm-4 ")
        self.textVolume.SetLabel(str(self.invariant.volume) + " cm3 ")
        self.parentwindow.RePlot()
        
        

    def OnExitClick(self,event):
        '''
        user click on Close
        '''
        #remove dataset for low q and high q
        self.parentwindow.data_dict.pop(self.DPQ)
        self.parentwindow.data_dict.pop(self.DGQ)
        self.parentwindow.redrawTheList()
        self.parentwindow.RePlot()
        self.Destroy()
