import wx
import numpy
import sys
import os.path, dircache
from pySAXS.tools import FAIsaxs
import pyFAI
from pyFAI import azimuthalIntegrator
from pySAXS.guisaxs.wx import LSGenericParameterDlg
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset
import time
from pyFAI import azimuthalIntegrator


import fabio



class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.AppendItems(filenames)
        
class FAIsaxsDlg(wx.Frame):
    def __init__(self, parent,pos=wx.Point(50,50),withGuisaxs=False):
        
        wx.Frame.__init__(self, parent, -1, "Integration Image Dialog", size=wx.Size(700,400),\
                          pos=pos,style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        self.listFile=[]
        self.workingdirectory = ""
        self.printout=None
        self.withGuisaxs=withGuisaxs
        if parent is not None:
            self.parent=parent
            wx.Frame.SetIcon(self,parent.favicon)
            if withGuisaxs:
                self.withGuisaxs=withGuisaxs
                self.workingdirectory = parent.workingdirectory
                self.printout=parent.printTXT
            
        # Add a panel so it looks correct on all platforms
        # top sizer
        self.pan=wx.Panel(self, wx.ID_ANY)
        panel = self.pan
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        #--- description 
        desc=wx.StaticText(panel,1,"Interface for pyFAI version "+pyFAI.version,size=wx.Size(400,20))
        desc.SetForegroundColour('red')
        vbox_top.Add(desc,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        author=wx.StaticText(panel,1,"pyFAI author : \t"+azimuthalIntegrator.__contact__,size=wx.Size(400,20))
        author.SetForegroundColour('red')
        vbox_top.Add(author,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        vbox_top.Add(wx.StaticLine(panel),0,wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        
        
        #--- Parameters
        box0=wx.StaticBox(panel,-1,"Parameters file :")
        sizerParam=wx.StaticBoxSizer(box0,wx.VERTICAL)
        sizer=wx.FlexGridSizer(rows=1,cols=3,hgap=20,vgap=5)
        self.paramfileCtrl=wx.TextCtrl(panel,3,"",size=wx.Size(350,20), style = wx.TE_PROCESS_ENTER)
        self.paramfileCtrl.SetValue('f:\\test\\paramImageJ.xml')
        sizer.Add(self.paramfileCtrl,flag=wx.EXPAND|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.paramFileButton=wx.Button(panel,-1,"...",size=wx.Size(30,25))
        self.paramFileButton.Bind(wx.EVT_BUTTON, self.OnClickparamFileButton)
        sizer.Add(self.paramFileButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        self.paramViewButton=wx.Button(panel,-1,"View",size=wx.Size(50,25))
        self.paramViewButton.Bind(wx.EVT_BUTTON, self.OnClickViewParamButton)
        sizer.Add(self.paramViewButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        sizerParam.Add(sizer)    
        vbox_top.Add(sizerParam)
        
        # DATAS
        box1=wx.StaticBox(panel,-1,"Data :")
        sizerFileBox=wx.StaticBoxSizer(box1,wx.VERTICAL)
        self.listFile=[]
        #LIST BOX
        self.listBox=wx.ListBox(panel,-1,size=(500,300),choices=self.listFile,style=wx.LB_MULTIPLE)
        #-- file drop
        dt = FileDrop(self.listBox)
        self.listBox.SetDropTarget(dt)
        sizerFileBox.Add(self.listBox)
        sizerFileFlex=wx.FlexGridSizer(rows=1,cols=4,hgap=20,vgap=5)
        #ADD
        self.addFileButton=wx.Button(panel,-1,"Add")#,size=wx.Size(30,25))
        self.addFileButton.Bind(wx.EVT_BUTTON, self.OnClickAddFileButton)
        sizerFileFlex.Add(self.addFileButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        #CLEAR LIST
        self.clearFileButton=wx.Button(panel,-1,"Clear list")#,size=wx.Size(30,25))
        self.clearFileButton.Bind(wx.EVT_BUTTON, self.OnClickClearFileButton)
        sizerFileFlex.Add(self.clearFileButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        #RADIAL AVERAGE
        self.RADButton=wx.Button(panel,-1,"Radial Average")#,size=wx.Size(30,25))
        self.RADButton.Bind(wx.EVT_BUTTON, self.OnClickRADButton)
        sizerFileFlex.Add(self.RADButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        
        #GAUGE
        self.gauge = wx.Gauge(panel, range=100, size=(150, 20))
        sizerFileFlex.Add(self.gauge)
        sizerFileBox.Add(sizerFileFlex)
        vbox_top.Add(sizerFileBox,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP)
        
        box2=wx.StaticBoxSizer(wx.StaticBox(panel,-1,"Output directory :"),wx.VERTICAL)
        #sizerOutDir=wx.StaticBoxSizer(box2,wx.VERTICAL)
        sizerOutDir=wx.FlexGridSizer(rows=1,cols=2,hgap=20,vgap=5)
        self.outdirCtrl=wx.TextCtrl(panel,3,"",size=wx.Size(350,20), style = wx.TE_PROCESS_ENTER)
        self.outdirCtrl.SetValue('f:\\')
        sizerOutDir.Add(self.outdirCtrl,flag=wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.outdirButton=wx.Button(panel,-1,"...",size=wx.Size(30,25))
        self.outdirButton.Bind(wx.EVT_BUTTON, self.OnClickOutDirButton)
        sizerOutDir.Add(self.outdirButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        box2.Add(sizerOutDir)
        vbox_top.Add(box2)
        #QUIT
        self.QuitButton=wx.Button(panel,wx.ID_OK,"CLOSE",size=wx.Size(100,30))
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnExitClick)
        self.Bind(wx.EVT_CLOSE, self.OnExitClick)
        vbox_top.Add(self.QuitButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        panel.SetSizer(vbox_top)
        vbox_top.Fit(self)
        
    def OnExitClick(self,event):
        self.Destroy()
    
    def OnClickAddFileButton(self,event):
        dlg=wx.FileDialog(self, message="Choose files", defaultDir=self.workingdirectory, defaultFile="", wildcard="*.*" \
                           , style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.listBox.AppendItems(dlg.GetPaths())
            
    def OnClickOutDirButton(self,event):
        '''
        choose an output directory
        '''
        dlg=wx.DirDialog(self, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.outdirCtrl.SetValue(dlg.GetPath())
        pass
                
    def OnClickClearFileButton(self,event):
        '''
        user clear the file list
        '''
        self.listBox.Clear()
    
    def OnClickparamFileButton(self,event):
        '''
        user click on ... for opening a parameter file
        '''
        dlg=wx.FileDialog(self, message="Choose parameter file", defaultDir=self.workingdirectory, defaultFile="", wildcard="*.*" \
                           , style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.paramfileCtrl.SetValue(dlg.GetPaths()[0])
            
    def OnClickRADButton(self,event):
        '''
        user click on RAD
        '''
        #get list of files
        l=self.listBox.GetItems()
        #print l
        n=len(l)
        self.gauge.SetRange(n)
        #prepare 
        fai=azimuthalIntegrator.AzimuthalIntegrator()
        filename=self.paramfileCtrl.GetValue()
        if os.path.exists(filename):
            d=FAIsaxs.getIJxml(filename)
        else:
            printTXT(filename+' does not exist')
            return
        FAIsaxs.setGeometry(fai,d)
        if d.has_key('user.qDiv'):
            qDiv=d['user.qDiv']
        else:
            qDiv=1000
        #get the mask defined in parameters
        mad,maskfilename=FAIsaxs.getIJMask(d)
        self.printTXT('Image mask opened in ',maskfilename)
        for i in range(len(l)):
            self.gauge.SetValue(i+1)
            time.sleep(0.1)
            #radial averaging
            #-- opening data
            imageFilename=l[i]
            name=filetools.getFilename(imageFilename)
            outputdir=self.outdirCtrl.GetValue()
            newname=outputdir+os.sep+name+".rgr"
            try:
                im=fabio.open(imageFilename)
            except:
                self.printTXT('error in opening ',imageFilename)
                im=None
            if im is not None:
                t0=time.time()
                #q,i,s=fai.saxs(im.data,qDiv,mask=mad,filename=fn+"test.rgr",correctSolidAngle=False)
                q,i,s=fai.saxs(im.data,qDiv,filename=newname,mask=mad,correctSolidAngle=False)
                #q,i,s=fai.saxs(im.data,1000,mask=mad,correctSolidAngle=False)
                t1=time.time()
                self.printTXT("data averaged in "+str(t1-t0)+" s for "+imageFilename+" and saved as "+newname)
                if self.withGuisaxs:
                    name = filetools.getFilename(imageFilename)
                    self.parent.data_dict[name]=dataset.dataset(name,q,i, imageFilename,type='saxs')
                    self.parent.redrawTheList()
        self.gauge.SetValue(0)
        
            
    def OnClickViewParamButton(self,event):
        #open parameter file
        filename=self.paramfileCtrl.GetValue()
        if os.path.exists(filename):
            d=FAIsaxs.getIJxml(filename)
            d=self.stringinze(d)
            #print d
            pdlg=LSGenericParameterDlg.LSGenericParameterDlg(self,title="Parameters from "+filename,parameters=d,comment='test')
            pdlg.Show()
        else:
            wx.MessageBox("File does not exist")
    
    def stringinze(self,d):
        newd={}
        for key in d:
            newd[str(key)]=[key,str(d[key])]
        return newd
    
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
        
if __name__== '__main__':
    app = wx.App()
    frame = FAIsaxsDlg(None)
    frame.Show()
    app.MainLoop()
