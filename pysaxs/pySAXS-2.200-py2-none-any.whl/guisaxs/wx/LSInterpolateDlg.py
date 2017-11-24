#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.LSsca as LSsca



class LSInterpolateDlg(wx.Frame):

    def __init__(self,parent,newdatasetname,olddatasetname):
        wx.Frame.__init__(self, parent, 10, "Interpolation", size=wx.Size(350,250),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parentwindow=parent
        self.newdatasetname=newdatasetname
        self.olddatasetname=olddatasetname
        self.SetBackgroundColour("White")
        qminimum=numpy.min(self.parentwindow.data_dict[newdatasetname].q)
        qmaximum=numpy.max(self.parentwindow.data_dict[newdatasetname].q)
        nb=len(self.parentwindow.data_dict[newdatasetname].q)
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #---------
        #box1=wx.StaticBox(self,-1,"q range :")
        #stsizer=wx.StaticBoxSizer(box1,wx.VERTICAL)
        sizer=wx.FlexGridSizer(rows=3,cols=8,hgap=5,vgap=5)
        self.chkb=[]
        self.qmin=[]
        self.qmax=[]
        self.nbpts=[]
        self.qrange_list=['linear','logscale']
        self.qrange_type=[]
        for i in range(3):
            self.chkb.append(wx.CheckBox(self,-1,str(i)+" - q range "))
            sizer.Add(self.chkb[i])
            sizer.Add(wx.StaticText(self,-1," min :"))
            self.qmin.append(wx.TextCtrl(self,-1,value=str(qminimum)))
            sizer.Add(self.qmin[i])
            sizer.Add(wx.StaticText(self,-1," max :"))
            self.qmax.append(wx.TextCtrl(self,-1,value=str(qmaximum)))
            sizer.Add(self.qmax[i])
            sizer.Add(wx.StaticText(self,-1," points :"))
            self.nbpts.append(wx.TextCtrl(self,-1,value=str(nb)))
            sizer.Add(self.nbpts[i])
            self.qrange_type.append(wx.Choice(self,-1,choices=self.qrange_list))
            sizer.Add(self.qrange_type[i])
            self.qrange_type[i].SetSelection(0)
        self.chkb[0].SetValue(True)
        vbox_top.Add(sizer, 0, wx.BOTTOM | wx.TOP, 9)

        self.applyButton=wx.Button(self,wx.ID_ANY,"APPLY")
        vbox_top.Add(self.applyButton, 0, wx.BOTTOM | wx.TOP, 9)
        wx.EVT_BUTTON(self, self.applyButton.GetId(), self.OnApply)
        self.CancelButton=wx.Button(self,wx.ID_ANY,"CANCEL")
        vbox_top.Add(self.CancelButton, 0, wx.BOTTOM | wx.TOP, 9)
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnExitClick)

        self.SetSizer(vbox_top)
        vbox_top.Fit(self)

    def OnApply(self,event):
        '''
        calculate the new qrange
        '''

        # test if q range is selected
        if len(self.giveMeListOfChecked())==0:
            dlg2=wx.MessageDialog(self,
                                      message='No q range are checked !',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
            dlg2.ShowModal()
            dlg2.Destroy()
            return
        # test if q ranges are coherent

        ''' ------ test qmin< qmax '''
        for i in self.giveMeListOfChecked():
            if float(self.qmin[i].GetValue())>float(self.qmax[i].GetValue()):
                dlg2=wx.MessageDialog(self,
                                      message='qmin > qmax in the '+str(i)+'- q range !',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
        '''
        can be optimized in future...
        '''
        '''list of q range ordered by qmin'''
        d={}#a dictionnary of qmin -> qrange are sorted by qmin
        for i in self.giveMeListOfChecked():
            # in d <- qmin and index
            d[float(self.qmin[i].GetValue())]=i
        sorted=self.sortedDictValues(d)
        #d is sorted
        print sorted
        if len(sorted)>1:
            #test si qmax<qmin
            for i in range(1,len(sorted)):
                if float(self.qmax[i-1].GetValue())>float(self.qmin[i].GetValue()):
                    dlg2=wx.MessageDialog(self,
                                      message='qmax in the '+str(i-1)+'- q range > qmin in the '+str(i)+'- q range!',
                                      caption='pySAXS error',
                                      style=wx.OK | wx.ICON_INFORMATION)
                    dlg2.ShowModal()
                    dlg2.Destroy()
                    return
        #creation of qrange
        newqrange=None
        for i in sorted:
            #i is qmin, d[i] is index of qrange
            if newqrange==None:
                newqrange=self.giveMeAQRange(i)
            else:
                newqrange=numpy.concatenate((newqrange,self.giveMeAQRange(i)))
        #c'est fini les amis
        #print newqrange
        self.parentwindow.OnInterpolate(self.newdatasetname,self.olddatasetname,newqrange)


    def giveMeAQRange(self,index):
        '''
        return a q range from the information on the form
        '''
        qmin=float(self.qmin[index].GetValue())
        qmax=float(self.qmax[index].GetValue())
        nbpts=float(self.nbpts[index].GetValue())
        steps=(qmax-qmin)/nbpts
        if self.qrange_type[index].GetStringSelection()=='linear':
            newqrange=numpy.arange(qmin,qmax,steps)
        else:
            newqrange=LSsca.Qlogspace(qmin,qmax,nbpts)
        return newqrange

    def giveMeListOfChecked(self):
        l=[]
        for i in range(3):
            if self.chkb[i].GetValue():
                l.append(i)
        return l

    def sortedDictValues(self,adict):
        '''sort a dictionnary
        '''
        items = adict.items()
        items.sort()
        return [value for key, value in items]

    def OnExitClick(self,event):
        '''
        user click on Cancel
        exit without clipping
        '''
        self.Destroy()
