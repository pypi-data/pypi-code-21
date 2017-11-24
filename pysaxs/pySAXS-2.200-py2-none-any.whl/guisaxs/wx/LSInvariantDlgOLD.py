#!/usr/bin/python
'''
wx python dialog box for calculation of invariant
'''
import wx
import numpy
import sys
from scipy import integrate
from scipy import interpolate
from scipy import special
from math import  *
import pySAXS.LS.LSsca as LSsca


class LSInvariantDlg(wx.Frame):

    def __init__(self,parent,dataset_name,DPQ,DGQ):
        wx.Frame.__init__(self, parent, 10, "Invariant", size=wx.Size(250,500),pos=wx.Point(50,50),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.DPQ=DPQ
        self.DGQ=DGQ
        self.dataset_name=dataset_name
        self.parentwindow=parent
        self.SetBackgroundColour("lightgrey")
        self.q=self.parentwindow.data_dict[dataset_name].q
        self.i=self.parentwindow.data_dict[dataset_name].i
        self.qmini=numpy.min(self.q)
        self.qmaxi=numpy.max(self.q)
        self.parentwindow.printTXT('--- Initializing invariant calculation ---')
        self.radius=300.0
        self.A=self.i[0]
        
        #the last nbp points where i>0
        ipositive=self.i[numpy.where(self.i>0)]
        nbp=int(len(ipositive)/3)
        av=numpy.average(ipositive[-nbp:])
        self.B=av*self.qmaxi**4.0*1e32
        self.parentwindow.printTXT('I at qmin : '+str(self.A))
        self.parentwindow.printTXT('Intensity average for last '+str(nbp)+' positive points = '+str(av))
        #dataset for low q range
        self.parentwindow.data_dict[self.DPQ].q=LSsca.Qlogspace(self.qmini/10,self.qmini,100)
        self.parentwindow.data_dict[self.DPQ].i=self.A
        #dataset for high q range
        self.parentwindow.data_dict[self.DGQ].q=LSsca.Qlogspace(self.qmaxi,self.qmaxi*10.0,100)
        self.parentwindow.data_dict[self.DGQ].i=self.parentwindow.data_dict[self.DGQ].q**-4.0*self.B*1e-32
        
        
        #interface
        Dsize=(150,20)
        sizer=wx.GridSizer(rows=10,cols=2,hgap=5,vgap=2)
        self.text1 = wx.StaticText(self, -1, "Data Set : ")
        sizer.Add(self.text1,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.text2 = wx.StaticText(self, -1, dataset_name)
        sizer.Add(self.text2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text3 = wx.StaticText(self, -1, "q minimum : ")
        sizer.Add(self.text3,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr1=wx.TextCtrl(self,-1,str(self.qmini),size=Dsize)
        sizer.Add(self.textctr1,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.textRadius = wx.StaticText(self, -1, "estimate radius of giration (A) : ")
        sizer.Add(self.textRadius,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctrRadius=wx.TextCtrl(self,-1,str(self.radius),size=Dsize)
        sizer.Add(self.textctrRadius,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text4 = wx.StaticText(self, -1, "q maximum : ")
        sizer.Add(self.text4,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr2=wx.TextCtrl(self,wx.ID_ANY,str(self.qmaxi),size=Dsize)
        sizer.Add(self.textctr2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.text6 = wx.StaticText(self, -1, "Large angle extrapolation (cm-5): " )
        sizer.Add(self.text6,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textctr4=wx.TextCtrl(self,-1,str(self.B),size=Dsize)
        sizer.Add(self.textctr4,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 1 result
        self.text7 = wx.StaticText(self, -1, "Small Angle part : ")
        sizer.Add(self.text7,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP1 = wx.StaticText(self, -1, " -- cm-4 ")
        self.textP1.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP1,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 2 result
        self.text8 = wx.StaticText(self, -1, "Middle Angle part : ")
        sizer.Add(self.text8,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP2 = wx.StaticText(self, 1, " -- cm-4 ")
        self.textP2.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP2,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #part 3 result
        self.text9 = wx.StaticText(self, -1, "Large Angle part : ")
        sizer.Add(self.text9,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textP3 = wx.StaticText(self, -1, " -- cm-4 ")
        self.textP3.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textP3,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        #Full result
        self.text10 = wx.StaticText(self, -1, "Invariant = ")
        sizer.Add(self.text10,flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.textInv = wx.StaticText(self, -1, " -- cm-4 ")
        self.textInv.SetForegroundColour(wx.BLUE) # set text color
        sizer.Add(self.textInv,flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        self.okButton=wx.Button(self,wx.ID_ANY,"Compute")
        sizer.Add(self.okButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.okButton.GetId(), self.TextUpdate)
        self.CancelButton=wx.Button(self,wx.ID_ANY,"Close")
        sizer.Add(self.CancelButton,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        wx.EVT_BUTTON(self, self.CancelButton.GetId(), self.OnExitClick)
       
        self.SetSizer(sizer)
        self.Fit()
        

    def TextUpdate(self,event):
        '''
        when the user click on Compute
        '''
        self.parentwindow.printTXT("--- Calculating Invariant ---")
        self.qmini = float(self.textctr1.GetValue())
        self.qmaxi = float(self.textctr2.GetValue())
        self.radius=float(self.textctrRadius.GetValue())
        # calculate I0 with an interpolation 
        f=interpolate.interp1d(self.q,self.i)
        if numpy.min(self.q)<self.qmini:
            Istar=f(self.qmini)
        else:
            Istar=self.i[0]
        I0=Istar*exp(self.qmini**2*self.radius**2/3.0)
        self.parentwindow.printTXT("I*="+str(Istar)+"   I0="+str(I0))
        
        #update q et i inside the qmini, qmaxi range
        imax=int(max(numpy.argwhere(self.q<self.qmaxi)))
        imin=int(min(numpy.argwhere(self.q>self.qmini)))
        qc=self.q[imin:imax]
        ic=self.i[imin:imax]

        #plot a guinier on low q
        self.parentwindow.data_dict[self.DPQ].q=LSsca.Qlogspace(self.qmini/20,self.qmini,100)
        t=numpy.array(LSsca.Guinier(self.parentwindow.data_dict[self.DPQ].q, I0, self.radius))
        self.parentwindow.data_dict[self.DPQ].i=t #now plot a Guinier
        #plot a porod on high q
        self.B = float(self.textctr4.GetValue())
        self.parentwindow.data_dict[self.DGQ].q=LSsca.Qlogspace(self.qmaxi,self.qmaxi*20.0,100)
        self.parentwindow.data_dict[self.DGQ].i=self.parentwindow.data_dict[self.DGQ].q**-4.0*self.B*1e-32
        #calculation
        p1=(3.0*Istar)/(2*self.radius**2)
        p2=exp(self.qmini**2*self.radius**2/3.0)
        p3=((3.*pi)**0.5)/(2*self.radius)
        p4=special.erf(self.qmini*self.radius/(3.0**0.5))
        P1=p1*(-self.qmini+p2*p3*p4)*1e24
        
        #P1= (self.A*1e24*self.qmini**3.0)/3.#
        

        self.textP1.SetLabel(str(P1) + " cm-4 ")

        P2=integrate.trapz(ic*qc*qc*1e16,qc*1e8)

        self.textP2.SetLabel(str(P2) + " cm-4 ")

        P3= self.B/(self.qmaxi*1e8)

        self.textP3.SetLabel(str(P3) + " cm-4 ")

        PF=P1+P2+P3

        self.textInv.SetLabel(str(PF) + " cm-4 ")
        self.parentwindow.printTXT("Invariant = "+str(PF) + " cm-4 ")
        self.parentwindow.RePlot()


    def OnExitClick(self,event):
        '''
        user click on Close
        '''
        #remove dataset for low q and high q
        self.parentwindow.data_dict.pop(self.DPQ)
        self.parentwindow.data_dict.pop(self.DGQ)
        self.parentwindow.redrawTheList()
        self.parentwindow.replot()
        self.Destroy()
