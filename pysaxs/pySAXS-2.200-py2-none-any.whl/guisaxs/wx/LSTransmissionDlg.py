#!/usr/bin/python

import wx



class LSTransmissionDlg(wx.Frame):
    def __init__(self, parent,label):

        wx.Frame.__init__(self, parent, 10, "Data and transmission correction", size=wx.Size(400,300),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parentwindow=parent
        self.SetBackgroundColour("White")
        self.thick=1e-1
        self.stepexp=0
        self.steprock=0
        self.SlideMax=1000
        self.label=label
        
        self.parameter={}
        # text, valeur par defaut, valeur min, valeur max, final value
        self.parameter['thickness']=['Thickness of sample (cm)',1e-1,0,1,0]
        self.parameter['backgroundData']=['Background data(cps/s) ',0,0,100,0]
        self.parameter['backgroundRC']=['Background RC (cps/s) ',0,0,100,0]
        self.parameter['shiftdata']=['Shift Data (steps)',0,0,100,0]
        self.parameter['shiftrock']=['Shift Rocking curve (steps)',0,0,100,0]
        
        self.controlsDict={}
        self.controlID={}
        
        
        # top sizer
        self.pan=wx.Panel(self, wx.ID_ANY)
        panel = self.pan
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #Parameters sizer
        sizer=wx.FlexGridSizer(rows=4,cols=2,hgap=20,vgap=5) #text , numerical value, slider
        
        nb=len(self.parameter)
        j=0
        self.controlTxt=[]
        for key in self.parameter:
            #text
            sizer.Add(wx.StaticText(panel,j, self.parameter[key][0]),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            #control
            self.controlTxt.append(wx.TextCtrl(panel,j,"",size=wx.Size(100,20), style = wx.TE_PROCESS_ENTER))
            self.controlTxt[-1].SetValue(str(self.parameter[key][1]))
            self.controlTxt[-1].Bind(wx.EVT_TEXT_ENTER,self.textUpdate)
            self.controlTxt[-1].Bind(wx.EVT_TEXT,self.textUpdate)
            sizer.Add(self.controlTxt[-1],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            
            #slider
            #self.control.append(wx.Slider(panel,j+3,self.parameter[key][1],self.parameter[key][2],self.parameter[key][3],style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS,\
            #                                 size=(200,20)))
            #self.control[-1].SetTickFreq(100,1)
            #sizer.Add(self.control[-1],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            self.controlID[j]=key
            j+=1
            #self.controlsDict[key]=self.control
            
            
        #self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.SliderUpdate)
        #self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.SliderUpdate)
        #self.Bind(wx.EVT_SLIDER, self.SliderUpdate)
        
        
        box0=wx.StaticBox(panel,-1,"Parameters :")
        sizerParam=wx.StaticBoxSizer(box0,wx.VERTICAL)    
        sizerParam.Add(sizer)    
        vbox_top.Add(sizerParam)
        vbox_top.Add(wx.StaticLine(panel),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        #-- close button
        sizerButton=wx.FlexGridSizer(rows=1,cols=5,hgap=20,vgap=5)
        self.QuitButton=wx.Button(panel,wx.ID_OK,"CLOSE",size=wx.Size(100,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)
        sizerButton.Add(self.QuitButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(sizerButton)
        #-- fit sizers
        panel.SetSizer(vbox_top)
        vbox_top.Fit(self) 
        

    def textUpdate(self,event):
        '''
        parameter value is udpated
        '''
        n=event.GetId() #no of text box updated
        print "text updated"
        parValue=eval(self.controlTxt[n].GetValue())
        key=self.controlID[n]
        self.parameter[key][4]=parValue
        self.parentwindow.OnTransmission(self.parentwindow,self.label)

    def SliderUpdate(self,event):
        for key in self.parameter:
            self.parameter[key][4] = float(self.controlsDict[key][1].GetValue())
        self.parentwindow.OnTransmission(self.parentwindow,self.label)


    def OnExitClick(self,event):
        self.Destroy()
