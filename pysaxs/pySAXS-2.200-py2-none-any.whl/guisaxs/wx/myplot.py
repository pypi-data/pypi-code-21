from numpy import *
import wx
import matplotlib
from pySAXS.guisaxs.wx import matplotlibwx
from pySAXS.guisaxs.wx import wxmpl




class myplot(matplotlibwx.PlotFrame):
    def __init__(self):
        self.app = wx.App(0)
        self.plotframe= matplotlibwx.PlotFrame(None, 1,"pySAXS datas",size=(700,500))
        self.plotframe.Show(True)
        self.plotframe.xlabel=''
        self.plotframe.ylabel=''
        '''self.plotframe.addData(li, profil, label='profil')
        self.plotframe.addData(li, transmSi, label='Transmission du Si')
        self.plotframe.addData(li, transmGe, label='Transmission du Ge')''' 
        #self.plotframe.replot()
        #self.app.MainLoop()

    def addData(self,x,y,label=''):
        self.plotframe.addData(x, y, label)
        self.plotframe.replot()

    def plot(self):
        self.plotframe.replot()
        self.app.MainLoop()

    def setLabel(self,x='',y=''):
        self.plotframe.xlabel=x
        self.plotframe.ylabel=y
        self.plotframe.replot()
        
