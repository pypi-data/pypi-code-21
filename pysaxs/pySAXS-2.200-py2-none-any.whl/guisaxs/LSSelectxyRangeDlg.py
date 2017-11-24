#!/usr/bin/python
"""
project : pySAXS
description : wxPython Class to plot some data files to gnuplot
authors : Antoine Thill, Olivier Spalla, Olivier Tache', Debasis Sen
Last changes :
    16-03-2007 OT : add autoscale buttons, send replot command directly to gnuplot

"""

import wx
import numpy
import sys



class LSSelectqRangeDlg(wx.Frame):
    def __init__(self, parent,qmin,qmax,imin,imax):

        wx.Frame.__init__(self, parent, 10, "Select q Range", size=wx.Size(400,300),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parentwindow=parent
        self.SetBackgroundColour("White")

        self.qmini=qmin
        self.qmaxi=qmax
        self.Imini=imin
        self.Imaxi=imax

        self.text1 = wx.StaticText(self, 1, "q minimum :", wx.Point(10,40))
        self.textctr1=wx.TextCtrl(self,2,str(self.qmini),wx.Point(100,40),wx.Size(90,20))
        self.Bind(wx.EVT_TEXT,self.TextUpdate,self.textctr1)

        self.text2 = wx.StaticText(self, 3, "q maximum :", wx.Point(10,60))
        self.textctr2=wx.TextCtrl(self,100,str(self.qmaxi),wx.Point(100,60),wx.Size(90,20))
        self.Bind(wx.EVT_TEXT,self.TextUpdate,self.textctr2)

        self.qAutoButton=wx.Button(self,wx.ID_OK,"q Autoscale",wx.Point(10,80))#,wx.Size(75,30)
        self.qAutoButton.Bind(wx.EVT_BUTTON,self.on_qAutoButton_Click)


        self.text3 = wx.StaticText(self, 4, "I minimum", wx.Point(10,120))
        self.textctr3=wx.TextCtrl(self,101,str(self.Imini),wx.Point(100,120),wx.Size(90,20))
        self.Bind(wx.EVT_TEXT,self.TextUpdate,self.textctr3)

        self.text4 = wx.StaticText(self, 5, "I maximum", wx.Point(10,140))
        self.textctr4=wx.TextCtrl(self,102,str(self.Imaxi),wx.Point(100,140),wx.Size(90,20))
        self.Bind(wx.EVT_TEXT,self.TextUpdate,self.textctr4)

        self.iAutoButton=wx.Button(self,wx.ID_OK,"I Autoscale",wx.Point(10,160))#,wx.Size(75,30)
        self.iAutoButton.Bind(wx.EVT_BUTTON,self.on_iAutoButton_Click)

        text5 = wx.StaticText(self, 6, "Plot ignores (-)ve values for log scale", wx.Point(10,10))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        text5.SetFont(font)
        self.QuitButton=wx.Button(self,wx.ID_OK,"Close",wx.Point(100,200),wx.Size(75,30))
        self.QuitButton.Bind(wx.EVT_BUTTON,self.on_QuitButton_Click)
        self.Bind(wx.EVT_CLOSE, self.on_QuitButton_Click)

    def on_QuitButton_Click(self,event):
        #print "je destroy"
        self.Destroy()

    def on_qAutoButton_Click(self,event):
        self.parentwindow.xselect='set xrange[:]'
        self.parentwindow.gp('set autoscale x')
        self.parentwindow.gp('replot')

    def on_iAutoButton_Click(self,event):
        self.parentwindow.xselect='set yrange[:]'
        self.parentwindow.gp('set autoscale y')
        self.parentwindow.gp('replot')

    def TextUpdate(self,event):
        try:
            self.qmini = float(eval((self.textctr1.GetValue())))
            self.qmaxi = float(eval((self.textctr2.GetValue())))
            self.Imini = float(eval((self.textctr3.GetValue())))
            self.Imaxi = float(eval((self.textctr4.GetValue())))
            self.parentwindow.OnSelectqRange(self.qmini,self.qmaxi,self.Imini,self.Imaxi)
        except:
            pass


