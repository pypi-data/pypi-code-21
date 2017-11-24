#!/usr/bin/python

import wx

class LSGenericParameterDlg(wx.Frame):
    def __init__(self, parent,title="",selectedData=None,parameters=None,callbackFunction=None,comment=''):
        wx.Frame.__init__(self, parent, 10, title, size=wx.Size(400,300),\
                          pos=wx.Point(50,50),\
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parentwindow=parent
        self.SetBackgroundColour("White")
        self.SlideMax=1000
        self.selectedData=selectedData #name of selected datas
        self.parameters=parameters      
        self.controlsDict={}
        self.controlID={}
        self.callbackFunction=callbackFunction
        self.comment=comment
        
        # top sizer
        self.pan=wx.Panel(self, wx.ID_ANY)
        panel = self.pan
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        if comment!='':
            desc=wx.StaticText(panel,1,self.comment,size=wx.Size(400,30))
            desc.SetForegroundColour('red')
            vbox_top.Add(desc,flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        #Parameters sizer
        sizer=wx.FlexGridSizer(rows=4,cols=2,hgap=20,vgap=5) #text , numerical value, slider
        
        nb=len(self.parameters)
        j=0
        self.controlTxt=[]
        for key in sorted(self.parameters.iterkeys()):
            #text
            sizer.Add(wx.StaticText(panel,j, self.parameters[key][0]),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            #control
            self.controlTxt.append(wx.TextCtrl(panel,j,"", style = wx.TE_PROCESS_ENTER))#size=wx.Size(100,20),
            self.controlTxt[-1].SetValue(str(self.parameters[key][1]))
            self.controlTxt[-1].Bind(wx.EVT_TEXT_ENTER,self.textUpdate)
            self.controlTxt[-1].Bind(wx.EVT_TEXT,self.textUpdate)
            sizer.Add(self.controlTxt[-1],flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            self.controlID[j]=key
            j+=1
            
        
        box0=wx.StaticBox(panel,-1,"Parameters :")
        sizerParam=wx.StaticBoxSizer(box0,wx.VERTICAL|wx.EXPAND)    
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
        try:
            self.callbackFunction(self.parentwindow,self.selectedData,self.parameters)
        except:
            pass
        

    def textUpdate(self,event):
        '''
        parameter value is udpated
        '''
        n=event.GetId() #no of text box updated
        try:
            parValue=eval(self.controlTxt[n].GetValue())
            key=self.controlID[n]
            self.parameters[key][4]=parValue
            self.callbackFunction(self.parentwindow,self.selectedData,self.parameters)
        except:
            #not a float
            pass
        
        

  
    def OnExitClick(self,event):
        self.Destroy()
