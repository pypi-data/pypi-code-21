"""
project : pySAXS
description : wxPython Class to plot some data files to gnuplot
authors : Olivier Tache
Last changes :
    13-03-2007 OT
    14-03-2007 get a gnuplot instance from LsScattering
    16-03-2007 change for opening chi files

"""
import wx
from pySAXS.tools.filetools import *
import Gnuplot, Gnuplot.funcutils

class pySaxsPlot(wx.Frame):
    def __init__(self, parent, id, title,plotinstance=None):
        wx.Frame.__init__(self, parent, id, title, (-1, -1), wx.Size(400, 350))
        panel=wx.Panel(self,-1)
        self.selectLabel=wx.StaticText(panel,-1,"Select a folder :",pos=(15,10),size=(100,-1))
        self.selectText=wx.TextCtrl(panel,-1,"",size=(200,-1),pos=(120,10))
        self.selectButton=wx.Button(panel, -1, '...',size=(50,-1),pos=(330,10))
        self.listBox=wx.ListBox(panel,-1,size=(380,200),pos=(10,40),style=wx.LB_ALWAYS_SB+wx.LB_EXTENDED)
        self.Bind(wx.EVT_BUTTON, self.On_selectButton_Click, self.selectButton )
        self.dialog=wx.DirDialog(None,"Choose a directory:")
        self.plotButton=wx.Button(panel,-1,'Plot selected',pos=(10,250),size=(380,-1))
        self.Bind(wx.EVT_BUTTON, self.On_plotButton_Click, self.plotButton )
        self.Centre()
        '''if plotinstance==None:
            self.g = Gnuplot.Gnuplot()
        else:
            self.g=gplotinstance'''
        self.createWxPlot()

        def createWxPlot(self):
            space = 5
            plotposition = self.GetSize()[0] + self.GetScreenPosition()[0] + space, self.GetScreenPosition()[1] - 5
            #print plotposition
            self.plotframe = matplotlibwx.PlotFrame(None, 1, "pySAXS quick view", size=(700, self.GetSize()[1]),\
                                                     pos=plotposition,axetype=1)
            wx.Frame.SetIcon(self.plotframe, self.favicon)
            self.plotframe.Show(True)
            self.plotframe.xlabel = '$q(\AA^{-1})$'
            self.plotframe.ylabel = '$I$'
            self._matplotlib = True

    def On_selectButton_Click(self,event):
        if self.dialog.ShowModal()==wx.ID_OK:
            l=[]
            self.selectText.SetValue(self.dialog.GetPath())
            l=listFiles(self.dialog.GetPath(),"*.*")
            self.listBox.Set(l)

    def On_plotButton_Click(self,event):
        selection=self.listBox.GetSelections()
        #transform index into list of filename
        if len(selection)>0:
            for name in selection:
                datafilename=self.listBox.GetString(name)
                data=numpy.loadtxt(datafilename, comments='#', skiprows=0, usecols=None)# Load data from a text file.
                data=numpy.transpose(numpy.array(data))
                #if len(data)
                self.plotframe.addData(data[0],data[1],self.data_dict[name].name,id=i,error=self.data_dict[name].error)
            
            '''
            to_plot=self.computeCommand(self.listBox.GetString(selection[0]))
            for i in range(1,len(selection)):
                to_plot=to_plot+", "+self.computeCommand(self.listBox.GetString(selection[i]))
            to_plot=to_plot.replace("\\","/")'''
            self.plotframe.replot()

    def computeCommand(self,filename):
        """
        compute and return gnuplot command for filename
        depending of extension file
        if filename is rgr file -> using 2:5
        if filename is other -> using 1:2
        """
        if getExtension(filename)=="rgr":
            return "'"+filename+"' using 2:5 "
        else:
            return "'"+filename+"' using 1:2 "

# ------------------------ Resource data ----------------------

if __name__=='__main__':
    app=wx.PySimpleApp()
    frame = pySaxsPlot(None, -1, 'pySAXS quick plot')
    frame.Show(True)
    app.MainLoop()

