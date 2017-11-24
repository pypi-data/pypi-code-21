#!/usr/bin/python

import wx
import numpy
import sys
import pySAXS.LS.SAXSparametersXML as SAXSparameters
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
#import pySAXS.LS.SAXSAbsoluteIntensity as SAXSAbsoluteIntensity 



class SAXSAbsoluteDlg(wx.Frame):
    def __init__(self, parent,params,datasetname=None):
        self.datasetname=datasetname
        self.parentwindow=parent
        self.params=params
        wx.Frame.__init__(self, parent, 10, "-- SAXS SCALING --",style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        wx.Frame.SetIcon(self,parent.favicon)
        self.SetBackgroundColour("White")
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #---------
        if self.datasetname<>None:
            text=wx.StaticText(self,-1,datasetname)
            text.SetForegroundColour('red')
            vbox_top.Add(text)
            vbox_top.Add(wx.StaticLine(self),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        vbox_top.Add(wx.StaticText(self,-1,"PARAMETERS : "))
        vbox_top.Add(wx.StaticLine(self),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        sizer=wx.GridSizer(rows=len(self.params.parameters),cols=2,hgap=10,vgap=3)
        #--- dynamic controls
        self.listStaticText={}
        self.listTextCtrl={}
        #-sorting parameters
        paramslist=self.params.order()
        #- controls
        for name in paramslist:
            par=self.params.parameters[name]
            self.listStaticText[name]=wx.StaticText(self, 1, par.description+" : ")#, wx.Point(10,yposition))
            #formula ?
            if par.formula<>None:
                self.listStaticText[name].SetForegroundColour('blue')
                styleText=wx.TE_READONLY
            else:
                styleText=wx.TE_LEFT
            self.listTextCtrl[name]=wx.TextCtrl(self,2,str(par.value),size=(100,20),style=styleText)
            sizer.Add(self.listStaticText[name],flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(self.listTextCtrl[name],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(sizer)
        #-- check box
        box1=wx.StaticBox(self,-1,"Scaling :")
        stsizer=wx.StaticBoxSizer(box1,wx.VERTICAL)
        self.qrangeChekBox=wx.CheckBox(self,-1,"Scaling Q range")#,pos=wx.Point(10,yposition))
        stsizer.Add(self.qrangeChekBox,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.irangeChekBox=wx.CheckBox(self,-1,"Scaling I range")#,pos=wx.Point(150,yposition))
        stsizer.Add(self.irangeChekBox,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(stsizer, 0, wx.EXPAND, 9)
        #-- select datas
        l=[]
        for name in self.parentwindow.data_dict:
            l.append(name)
        if datasetname<>None:
            box0=wx.StaticBox(self,-1,"Data to apply scaling :")
            stsizer0=wx.StaticBoxSizer(box0,wx.VERTICAL)
            stsizer0.Add(wx.StaticText(self,-1,"Data to apply scaling :")
                  ,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            stsizer0.Add(wx.StaticText(self,-1,self.datasetname)
                  ,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            vbox_top.Add(stsizer0, 0, wx.EXPAND, 9)

        #-- select datas for background
        box2=wx.StaticBox(self,-1,"Select data for background :")
        stsizer2=wx.StaticBoxSizer(box2,wx.VERTICAL)
        stsizer2.Add(wx.StaticText(self,-1,"Select data for background :")
                  ,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.listDataBackground=wx.Choice(self,-1,choices=['none']+l)
        stsizer2.Add(self.listDataBackground,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(stsizer2, 0, wx.EXPAND, 9)
        #-- buttons
        self.computeButton=wx.Button(self,-1,"Compute")
        vbox_top.Add(self.computeButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.computeButton.GetId(), self.Compute)
        if self.datasetname<>None:
            self.ApplyButton=wx.Button(self,-1,"Apply to datas")
            vbox_top.Add(self.ApplyButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
            wx.EVT_BUTTON(self, self.ApplyButton.GetId(), self.OnApplyClick)
        self.SaveButton=wx.Button(self,-1,"Save")
        vbox_top.Add(self.SaveButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.SaveButton.GetId(), self.OnSaveClick)
        self.QuitButton=wx.Button(self,-1,"Close")
        vbox_top.Add(self.QuitButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.QuitButton.GetId(), self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)
        self.SetSizer(vbox_top)
        vbox_top.Fit(self)

        self.Params2Control()

    def Compute(self,event):
        '''
        user modify text
        '''
        self.Control2Params() #entries -> datas
        self.params.calculate_All() #calculate datas
        self.Params2Control() #datas -> entries

    def OnApplyClick(self,event):
        '''
        User click on Apply button
        '''
        self.Compute(event)
        #-- on wich data set ?
        if self.datasetname<>None:
            if self.listDataBackground.GetStringSelection()=='' or self.listDataBackground.GetStringSelection()=='none':
                backgdname=''
            else :
                backgdname=self.listDataBackground.GetStringSelection()
            #-- call  the method in parentwindow
            self.parentwindow.data_dict[self.datasetname].parameters=self.params
            self.parentwindow.OnScalingSAXSApply(self.qrangeChekBox.IsChecked(),
                                              self.irangeChekBox.IsChecked(),
                                              self.datasetname,
                                              backgdname)
    def OnLoadClick(self,event):
        '''
        User click on save button
        '''
        #-- open dialog for parameters
        wc = "SAXS parameters file (*.par)|*.par"
        dlg=wx.FileDialog(self, message="Choose a parameter file", defaultDir=self.parentwindow.workingdirectory, defaultFile="", wildcard=wc, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            print "loading parameters file ",str(dlg.GetPath())
            print self.params.load(str(dlg.GetPath()))
            self.params['filename']=str(dlg.GetPath())
        self.Params2Control()

    def OnSaveClick(self,event):
        '''
        User click on save button
        '''
        self.Control2Params()
        #print self.params.parameters['filename']
        #self.params.save(str(self.params.parameters['filename']))
        #dlg=wx.MessageDialog(self,'Parameters was saved in '+str(self.params.parameters['filename']),'pySAXS info',wx.OK|wx.ICON_INFORMATION)
        #dlg.ShowModal()
        #dlg.Destroy()
        
        
        wc = "Save parameters file(*.xml)|*.xml"
        dlg=wx.FileDialog(self, message="Choose a file", defaultDir=self.parentwindow.workingdirectory, defaultFile="", wildcard=wc, style=wx.SAVE |  wx.CHANGE_DIR)
        returnValue=dlg.ShowModal()
        if  returnValue== wx.ID_OK:
            #check if file exist already
            filename=dlg.GetPath()
            if filetools.fileExist(filename):
                  dlg2=wx.MessageDialog(self, "File exist, replace ?", caption="Question", style=wx.OK | wx.CANCEL)
                  returnValue=dlg2.ShowModal()
                  if returnValue!=wx.ID_OK:
                      self.printTXT("file "+str(filename)+" exist. Datas was NOT replaced")
                      return
        self.params.saveXML(filename)
        if self.params.parameters.has_key('filename'):
            self.params.parameters['filename'].value=filename
        self.parentwindow.printTXT("parameters was saved in "+filename)
        
    def Params2Control(self):
        for key,value in self.params.parameters.items():
            if self.listTextCtrl.has_key(key):
                self.listTextCtrl[key].SetValue(str(self.params.parameters[key].value))


    def Control2Params(self):
        for key,value in self.params.parameters.items():
            if (self.params.parameters[key].datatype=='float') or (self.params.parameters[key].datatype=='int'):
                if isNumeric.isNumeric(self.listTextCtrl[key].GetValue()):
                    self.params.parameters[key].value=float(self.listTextCtrl[key].GetValue())
            else:
                self.params.parameters[key].value=self.listTextCtrl[key].GetValue()
            #print var,self.params.parameters[var]


    def OnExitClick(self,event):
        self.Control2Params()
        self.Destroy()


    #######


