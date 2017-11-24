#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca


class LSBackgroundDlg(wx.Dialog):
    def __init__(self, parent, listofdata):
        self.parentwindow=parent
        self.listofdata=listofdata
        taille=(len(listofdata)+2)*20+80
        wx.Dialog.__init__(self, parent, -1, "Background correction", size=wx.Size(300,taille),pos=wx.Point(50,50),style = wx.DEFAULT_DIALOG_STYLE)

        self.SetBackgroundColour("White")
        spaceBetweenControl=25
        #--- dynamic controls
        self.listCheckBox={}
        self.listTextCtrlback={}
        yposition=10 #begin position for dynamics controls
        print listofdata
        self.DataBackground=0
        self.RockBackground=0
        for var in listofdata:
            self.listCheckBox[var]=wx.CheckBox(self,-1,var,
                                                   wx.Point(10,yposition),
                                                   wx.Size(100,20))
            self.listCheckBox[var].SetValue(True)
            wx.StaticText(self, 1, "background :", wx.Point(120,yposition+3),wx.Size(70,20))
            self.listTextCtrlback[var]=wx.TextCtrl(self,2,"0",
                                                   wx.Point(200,yposition),
                                                   wx.Size(70,20))
            yposition+=spaceBetweenControl
        #--buttons
        yposition+=spaceBetweenControl
        self.QuitButton=wx.Button(self,-1,"Close",wx.Point(20,yposition),wx.Size(75,20))
        wx.EVT_BUTTON(self, self.QuitButton.GetId(), self.OnExitClick)
        self.ApplyButton=wx.Button(self,-1,"Apply",wx.Point(100,yposition),wx.Size(75,20))
        wx.EVT_BUTTON(self, self.ApplyButton.GetId(), self.OnApplyClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)


    def OnApplyClick(self,event):
        for name in self.listofdata:
            if self.listCheckBox[name].IsChecked():
                #print "using ",name
                self.parentwindow.data_dict[name].i-=float(self.listTextCtrlback[name].GetValue())
        self.parentwindow.RePlot()

    def OnExitClick(self,event):
        self.Destroy()


    #######


