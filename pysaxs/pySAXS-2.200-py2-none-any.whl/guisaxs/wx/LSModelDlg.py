#!/usr/bin/python

import wx
import numpy
import sys
#import pySAXS.LS.LSsca as LSsca
from pySAXS.models import *
from pySAXS.tools import isNumeric

'''
    19-05-2011 OT Remove slider 
    04-08-2010 DC textboxes for parameter values and bounds are now active for typing in
    04-08-2010 DC calculation of chi2 corrected
    03-08-2010 DC typos on the interface corrected
    10-11-2009 print the chi carre
    15-06-2009 now support new model class, use a sizer, fit with or without bounds, remove bugs with slider,...

'''


class LSModelDlg(wx.Frame):
    def __init__(self, parent,dataset_name,type="model",pos=wx.Point(50,50)):
        self.Model=parent.data_dict[dataset_name].model
        wx.Frame.__init__(self, parent, -1, self.Model.name+" model for "+dataset_name, size=wx.Size(700,40+len(self.Model.Arg)*50),pos=pos,style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        wx.Frame.SetIcon(self,parent.favicon)
        # Add a panel so it looks correct on all platforms
        
        self.parentwindow=parent
        self.dataset_name=dataset_name
        self.type=type
        Blig=10
        Bcol=10
        self.par=self.Model.getArg()
        #self.SetBackgroundColour(self.parentwindow.GetBackgroundColour())
        #self.SetBackgroundColour("White")
        self.itf=self.Model.getIstofit()
        self.qbase=copy(self.Model.q)
        self.ParDoc=[]
        self.ParText=[]
        self.MinText=[]
        self.MaxText=[]
        self.SlideMax=1000
        self.CheckFit=[]
        self.slider=[]
        self.fitexp=0
        
        # top sizer
        self.pan=wx.Panel(self, wx.ID_ANY)
        panel = self.pan
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #--- description 
        desc=wx.StaticText(panel,1,"Description : \t"+self.Model.Description,size=wx.Size(400,20))
        desc.SetForegroundColour('red')
        vbox_top.Add(desc,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        author=wx.StaticText(panel,1,"Author : \t"+self.Model.Author,size=wx.Size(400,20))
        author.SetForegroundColour('red')
        vbox_top.Add(author,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #vbox_top.Add(wx.StaticLine(panel),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        '''if self.type=="data":
            #compute chi_carre for datas
            rawdataset_name = self.parentwindow.data_dict[self.dataset_name].rawdata_ref
            #print rawdataset_name,len(self.parentwindow.data_dict[rawdataset_name].q),len(self.parentwindow.data_dict[rawdataset_name].i)
            iexp=numpy.array(self.parentwindow.data_dict[rawdataset_name].i)
            #print len(iexp),len(self.parentwindow.data_dict[rawdataset_name].q)
            val=self.Model.chi_carre(self.par,iexp)
            self.chicarre=wx.TextCtrl(panel,1,"Chi carre : "+str(val),size=wx.Size(400,20))
            self.chicarre.SetForegroundColour('blue')
            vbox_top.Add(self.chicarre,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TE_READONLY)
        '''
        #--- Parameters
        sizer=wx.FlexGridSizer(rows=len(self.par)+1,cols=5,hgap=20,vgap=5)
        sizer.Add(wx.StaticText(panel,1,"Parameter"),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(panel,1,"Value"),flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(panel,1,"Fit ?"),flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(panel,1,"Min"),flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        #sizer.Add(wx.StaticText(panel,1,"Value"),flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(panel,1,"Max"),wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        for i in numpy.arange(len(self.par)):
            #--control par doc
            self.ParDoc.append(wx.StaticText(panel, 5, self.Model.Doc[i]+" : "))
            sizer.Add(self.ParDoc[i],flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            #--control par text
            self.ParText.append(wx.TextCtrl(panel,i,"",size=wx.Size(100,20), style = wx.TE_PROCESS_ENTER))
            self.ParText[i].SetValue(self.Model.Format[i] % self.par[i])
            sizer.Add(self.ParText[i],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            self.ParText[i].Bind(wx.EVT_TEXT,self.textUpdate)
            #--control check fit
            self.CheckFit.append(wx.CheckBox(panel,50+i,label="fit"))
            self.CheckFit[i].SetValue(self.Model.istofit[i])
            sizer.Add(self.CheckFit[i],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            #--control min bounds
            self.MinText.append(wx.TextCtrl(panel,i,"",size=wx.Size(100,20),style = wx.TE_PROCESS_ENTER))
            min=0.0*self.par[i]
            self.MinText[i].SetValue(self.Model.Format[i] % min)
            self.MinText[i].Bind(wx.EVT_TEXT,self.textMinMaxUpdate)
            sizer.Add(self.MinText[i],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            #--control slider            
            '''self.slider.append(wx.Slider(panel,i,self.SlideMax/2.,0,self.SlideMax,style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS,\
                                         size=(200,20)))
            self.slider[i].SetTickFreq(100,1)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.sliderUpdate)
            self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.sliderMove)
            sizer.Add(self.slider[i],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)'''
            #--control max bounds
            max=2.0*self.par[i]
            self.MaxText.append(wx.TextCtrl(panel,i,"",size=wx.Size(100,20),style = wx.TE_PROCESS_ENTER))
            self.MaxText[i].SetValue(self.Model.Format[i] % max)
            self.MaxText[i].Bind(wx.EVT_TEXT,self.textMinMaxUpdate)
            sizer.Add(self.MaxText[i],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            
        box0=wx.StaticBox(panel,-1,"Model parameters :")
        sizerParam=wx.StaticBoxSizer(box0,wx.VERTICAL)    
        sizerParam.Add(sizer)    
        vbox_top.Add(sizerParam)
        #-------- sliders for qrange
        sizerSlide=wx.FlexGridSizer(rows=2,cols=3,hgap=20,vgap=5)
        qmin=0
        self.qminIndex=qmin
        qmax=len(self.qbase)-1
        self.qmaxIndex=qmax
        #qmin
        sizerSlide.Add(wx.StaticText(panel,1,"qmin"),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.qminSlide=wx.Slider(panel, -1, qmin, qmin, qmax, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS ,\
                                         size=(400,20))
        self.qminSlide.SetTickFreq(200,1)
        self.qminSlide.Bind(wx.EVT_SCROLL_THUMBTRACK, self.sliderQminMove)
        sizerSlide.Add(self.qminSlide,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        self.qminTxt=wx.TextCtrl(panel,-1,str(self.qbase[qmin]),size=wx.Size(100,20),style = wx.TE_READONLY)
        sizerSlide.Add(self.qminTxt,flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #qmax
        sizerSlide.Add(wx.StaticText(panel,1,"qmax"),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.qmaxSlide=wx.Slider(panel, -1, qmax, qmin, qmax, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS ,\
                                         size=(400,20))
        self.qmaxSlide.SetTickFreq(200,1)
        self.qmaxSlide.Bind(wx.EVT_SCROLL_THUMBTRACK, self.sliderQmaxMove)
        sizerSlide.Add(self.qmaxSlide,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.qmaxTxt=wx.TextCtrl(panel,-1,str(self.qbase[qmax]),size=wx.Size(100,20),style = wx.TE_READONLY)
        sizerSlide.Add(self.qmaxTxt,flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #qrange
        boxQ=wx.StaticBox(panel,-1,"Q range :")
        sizerQ=wx.StaticBoxSizer(boxQ,wx.VERTICAL)    
        sizerQ.Add(sizerSlide)    
        vbox_top.Add(sizerQ)
        
        #-------- update fit check box
        #vbox_top.Add(wx.StaticLine(panel),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.updateFit=wx.CheckBox(panel,300,label="update model when value are changed")
        self.updateFit.SetValue(True)
        sizer.Add(self.updateFit,flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(wx.StaticLine(panel),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        
        #-- buttons
        sizerButton=wx.FlexGridSizer(rows=1,cols=5,hgap=20,vgap=5)
        if self.type=="data":
            self.Fitbutton=wx.Button(panel,100,"Fit",size=wx.Size(100,30))
            self.Fitbutton.Bind(wx.EVT_BUTTON, self.OnClickFitButton)
            sizerButton.Add(self.Fitbutton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
            self.FitbuttonBounds=wx.Button(panel,100,"Fit with bounds",size=wx.Size(100,30))
            self.FitbuttonBounds.Bind(wx.EVT_BUTTON, self.OnClickFitButtonBounds)
            sizerButton.Add(self.FitbuttonBounds,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
            #choice with iq iq2 iq4...
            choicelist=['normal','iq','iq2','iq3','iq4']
            self.listText=wx.StaticText(panel,-1,"Y type :",size=wx.Size(100,20))
            sizerButton.Add(self.listText,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
            self.ytype=wx.Choice(panel,-1,size=wx.Size(100,20),choices=['normal','iq','iq2','iq3','iq4'])
            self.ytype.Bind(wx.EVT_CHOICE,self.OnClickList)
            self.ytype.SetSelection(0)
            sizerButton.Add(self.ytype,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
            
        self.QuitButton=wx.Button(panel,wx.ID_OK,"CLOSE",size=wx.Size(100,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)
        sizerButton.Add(self.QuitButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(sizerButton)
        panel.SetSizer(vbox_top)
        vbox_top.Fit(self)
        self.parentwindow.OnModelUpdate(self)
        
    def sliderQminMove(self,event):
        val=self.qminSlide.GetValue()
        self.qminTxt.SetValue(str(self.qbase[val]))
        self.qminIndex=val
        if self.updateFit.GetValue():
            self.ModelUpdate()
            self.parentwindow.OnModelUpdate(self)
    
    def sliderQmaxMove(self,event):
        val=self.qmaxSlide.GetValue()
        self.qmaxTxt.SetValue(str(self.qbase[val]))
        self.qmaxIndex=val
        if self.updateFit.GetValue():
            self.ModelUpdate()
            self.parentwindow.OnModelUpdate(self)
    '''def sliderUpdate(self,event):
        #no more used if slider is removed
        b=self.slider[event.GetId()].GetValue()
        c=((eval(self.MaxText[event.GetId()].GetValue())-eval(self.MinText[event.GetId()].GetValue()))/self.SlideMax)*b + eval(self.MinText[event.GetId()].GetValue())
        self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % c)
        self.ModelUpdate()
        self.parentwindow.OnModelUpdate(self)

    def sliderMove(self,event):
        #no more used if slider is removed
        #print "on slider move"
        n=event.GetId()
        b=self.slider[event.GetId()].GetValue()
        #print b
        minbounds=float(eval(self.MinText[n].GetValue()))
        maxbounds=float(eval(self.MaxText[n].GetValue()))
        parValue=float(eval(self.ParText[n].GetValue()))
        range=(maxbounds-minbounds)/self.SlideMax
        newvalue=range*b + minbounds
        #print newvalue
        #self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % c)
        self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % newvalue)
    '''
    def textMinMaxUpdate(self,event):
        #self.parentwindow.printTXT( "min max update")
        #b=self.slider[event.GetId()].GetValue()
        n=event.GetId()
        
        max=self.MaxText[event.GetId()].GetValue()
        min=self.MinText[event.GetId()].GetValue()
        
        if (not(isNumeric.isNumeric(max)))or(not(isNumeric.isNumeric(min))):
            return #not a number : do nothing
        if float(max)<=float(min):
            #do nothing
            return
        val=self.ParText[event.GetId()].GetValue()
        if (not(isNumeric.isNumeric(val))):
            #parameter val is not a number : set as min
            min=float(min)
            self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % min)
        else:
            if float(val)<float(min):
                # val is < than min, set as min
                self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % float(min))
            if float(val)>float(max):
                # val is > than max, set as max
                self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % float(max))
                
        #c=((eval(self.MaxText[event.GetId()].GetValue())-eval(self.MinText[event.GetId()].GetValue()))/self.SlideMax)*b + eval(self.MinText[event.GetId()].GetValue())
        #self.ParText[event.GetId()].SetValue(self.Model.Format[event.GetId()] % c)
        if self.updateFit.GetValue():
            self.ModelUpdate()
            self.parentwindow.OnModelUpdate(self)

    def textUpdate(self,event):
        '''
        parameter value is updated
        '''
        n=event.GetId() #no of text box updated
        #print "text updated",n
        #test if value of text box is coherent with bounds
        minbounds=eval(self.MinText[n].GetValue())
        maxbounds=eval(self.MaxText[n].GetValue())
        if not(isNumeric.isNumeric(self.ParText[n].GetValue())):
            #do nothing
            return
        parValue=eval(self.ParText[n].GetValue())
        if parValue<minbounds:
            self.MinText[event.GetId()].SetValue(str(parValue))
            minbounds=parValue
        if parValue>maxbounds:
            self.MaxText[event.GetId()].SetValue(str(parValue))
            maxbounds=parValue
            
        #update slider
        #b=self.slider[event.GetId()].GetValue()
        #new value of slider in percent
        #range=maxbounds-minbounds
        #newvalue=((parValue-minbounds)/range)*self.SlideMax
        #self.slider[event.GetId()].SetValue(newvalue)  
         
        if self.updateFit.GetValue():
            self.ModelUpdate()
            self.parentwindow.OnModelUpdate(self)
        

    def ModelUpdate(self):
        '''
        when a parameter is updated
        '''
        if not(self.parentwindow.data_dict.has_key(self.dataset_name)):
            self.parentwindow.printTXT(self.dataset_name+" dataset removed ? ")
            return
        self.bounds=[]
        for i in numpy.arange(len(self.Model.Arg)):
            self.par[i]  = float(eval(self.ParText[i].GetValue()))
            self.itf[i]=self.CheckFit[i].GetValue()
            bmin=self.MinText[i].GetValue()
            bmax=self.MaxText[i].GetValue()
            self.bounds.append((bmin,bmax))
        self.Model.setIstofit(self.itf)
        self.Model.setArg(self.par)
        if (self.qminIndex!=0) or (self.qmaxIndex!=len(self.qbase)-1):
            self.Model.q=self.qbase[self.qminIndex:self.qmaxIndex]
            #print self.Model.q
            #print self.Model.q
        #compute chicarre
        '''if self.type=="data":
            #compute chi_carre for datas
            #print 'compute chi_carre'
            rawdataset_name = self.parentwindow.data_dict[self.dataset_name].rawdata_ref
            iexp=self.parentwindow.data_dict[rawdataset_name].i[:]
            val=self.Model.chi_carre(self.par,iexp)
            self.chicarre.Clear()
            self.chicarre.AppendText('Chi carre : '+str(val))'''
            
    def UpdateAfterFit(self,result):
        '''
        update all after a fit
        '''
        val=numpy.array(result).copy()
        #print "UPDATE AFTER FIT",val
        for i in range(len(val)):
            #print i,val[i]
            self.ParText[i].SetValue(str(val[i]))
            
        
    def DlgUpdate(self,event):
        ###More to do for data validation...
        for i in numpy.arange(len(self.Model.Arg)):
            self.ParText[i].SetValue(self.Model.Format[i] % self.par[i])
            self.CheckFit[i].SetValue(self.itf[i])

    def OnExitClick(self,event):
        self.ModelUpdate()
        self.Destroy()

    def OnClickFitButton(self,event):
        self.ModelUpdate()
        self.parentwindow.OnModelFit(self)
        self.Model=self.parentwindow.data_dict[self.dataset_name].model
        self.par=self.Model.getArg()
        self.DlgUpdate(event)
        
    def OnClickFitButtonBounds(self,event):
        self.ModelUpdate()
        self.parentwindow.OnModelFitBounds(self)
        self.Model=self.parentwindow.data_dict[self.dataset_name].model
        self.par=self.Model.getArg()
        self.DlgUpdate(event)

    def OnClickList(self,event):
        choice=self.ytype.GetSelection()
        #print choice
        self.fitexp=choice
