from numpy import arange, sin, pi
import matplotlib

# uncomment the following to use wx rather than wxagg
#matplotlib.use('WX')
#from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas

# comment out the following to use wx rather than wxagg
matplotlib.use('WXAgg',warn=False)
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib import colors
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
from pySAXS.guisaxs import pySaxsColors
import wx
from pySAXS.guisaxs.wx import wxmpl
import os
import itertools


class data:
    def __init__(self,x,y,label=None,id=None,error=None,color=None):
        self.x=x
        self.y=y
        self.label=label
        self.id=id #id in the list of datas
        self.error=error
        self.color=color
        
        

class PlotFrame(wx.Frame):
    """
    A matplotlib canvas embedded in a wxPython top-level window.

    @cvar ABOUT_TITLE: Title of the "About" dialog.
    @cvar ABOUT_MESSAGE: Contents of the "About" dialog.
    """

    ABOUT_TITLE = 'About wxmpl.PlotFrame'
    ABOUT_MESSAGE = ('wxmpl.PlotFrame \n'
        + 'Written by Ken McIvor <mcivor@iit.edu>\n'
        + 'Copyright 2005-2009 Illinois Institute of Technology\n'
        + "modified for PySAXS by Olivier Tach'e\n"
        + ' CEA / LIONS 2009')

    

    def __init__(self, parent, id, title, size=(4,4), dpi=96, cursor=True,
     location=True, crosshairs=True, selection=True, zoom=True,
     autoscaleUnzoom=True,axetype=None,**kwds):
        """
        Creates a new PlotFrame top-level window that is the child of the
        wxPython window C{parent} with the wxPython identifier C{id} and the
        title of C{title}.

        All of the named keyword arguments to this constructor have the same
        meaning as those arguments to the constructor of C{PlotPanel}.

        Any additional keyword arguments are passed to the constructor of
        C{wx.Frame}.
        """
        wx.Frame.__init__(self, parent, id, title,size=size, **kwds)
        #convert size (in pixels) into INCH for figure
        sizex=float(size[0])/dpi
        sizey=float(size[1])/dpi
        sizeINCH=(sizex,sizey)
        
        self.panel = wxmpl.PlotPanel(self, -1, sizeINCH, dpi, cursor, location,
            crosshairs, selection, zoom)

        pData = wx.PrintData()
        pData.SetPaperId(wx.PAPER_LETTER)
        if callable(getattr(pData, 'SetPrinterCommand', None)):
            pData.SetPrinterCommand(POSTSCRIPT_PRINTING_COMMAND)
        self.printer = wxmpl.FigurePrinter(self, pData)

        self.datalist=[]
        self.gridON=True
        self.legendON=True
        self.axetype=4 #lin lin
        if axetype!=None:
            self.axetype=axetype
        self.plotexp=0 #x vs y
        self.linetype=1
        self.ylabel=""
        self.xlabel=""
        self.marker_cycle=itertools.cycle(['.','o','^','v','<','>','s','+','x','D','d','1','2','3','4','h','H','p','|','_'])
        self.marker_fixed=['.','-','.-','o',',','x']
        self.colors=pySaxsColors.listOfColors()
        self.errbar=False
        self.markerSize=5
        
        self.create_menus()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Fit()
        
        

    def create_menus(self):
        mainMenu = wx.MenuBar()
        menu = wx.Menu()

        id = wx.NewId()
        menu.Append(id, '&Save As...\tCtrl+S','Save a copy of the current plot')
        wx.EVT_MENU(self, id, self.OnMenuFileSave)

        menu.AppendSeparator()

        if wx.Platform != '__WXMAC__':
            id = wx.NewId()
            menu.Append(id, 'Page Set&up...',
                'Set the size and margins of the printed figure')
            wx.EVT_MENU(self, id, self.OnMenuFilePageSetup)

            id = wx.NewId()
            menu.Append(id, 'Print Pre&view...',
                'Preview the print version of the current plot')
            wx.EVT_MENU(self, id, self.OnMenuFilePrintPreview)

        id = wx.NewId()
        menu.Append(id, '&Print...\tCtrl+P', 'Print the current plot')
        wx.EVT_MENU(self, id, self.OnMenuFilePrint)

        menu.AppendSeparator()

        id = wx.NewId()
        menu.Append(id, '&Close Window\tCtrl+W',
            'Close the current plot window')
        wx.EVT_MENU(self, id, self.OnMenuFileClose)

        mainMenu.Append(menu, '&File')
        #-- grid --
        menu=wx.Menu()
        submenu=wx.Menu()
        item = submenu.Append(30, 'Grid ON', 'Grid On',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnGridOn, item)
        submenu.Check(30, True)
        item = submenu.Append(31, 'Grid OFF', 'Grid Off',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnGridOff, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Grid',submenu)
        #-- legend --
        submenu=wx.Menu()
        item = submenu.Append(20, 'Legend ON', 'Legend On',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLegendOn, item)
        submenu.Check(20, True)
        item = submenu.Append(21, 'Legend OFF', 'Legend Off',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLegendOff, item)
        item = submenu.Append(22, 'x Label', 'x Label')
        self.Bind(wx.EVT_MENU, self.OnLegendXYtitle, item)
        item = submenu.Append(23, 'y Label', 'y Label')
        self.Bind(wx.EVT_MENU, self.OnLegendXYtitle, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Legend and title',submenu)
        #-- line format --
        submenu=wx.Menu()
        item = submenu.Append(11, 'Points', 'With points',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(12, 'Line', 'With lines',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        submenu.Check(12, True)
        item = submenu.Append(13, 'Line and Points', 'With linepoints',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(17, 'Automatic marker with line', 'Automatic marker',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(14, 'Circle', 'With circle',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(15, 'Pixel', 'With pixel marker',kind=wx.wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(16, 'x', 'With x marker',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormat, item)
        item = submenu.Append(17, 'Line With error bar', 'With error bar (if any)',kind=wx.ITEM_RADIO)#kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLineFormatErrorBar, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Line format',submenu)
        
        #-- marker --
        submenu=wx.Menu()
        item = submenu.Append(100, '+', 'marker size +')
        self.Bind(wx.EVT_MENU, self.OnMarkerChange, item)
        item = submenu.Append(101, '-', 'marker size -')
        self.Bind(wx.EVT_MENU, self.OnMarkerChange, item)
        item=menu.AppendMenu(wx.ID_ANY, 'Marker size',submenu)
        #-- axes --
        submenu=wx.Menu()
        self.autoscaleitem = submenu.Append(5, 'Autoscale', 'autoscale',kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnAutoscale, self.autoscaleitem)
        submenu.Check(5, True)
        item = submenu.Append(6, 'Set X range', 'Set X range')
        self.Bind(wx.EVT_MENU, self.OnXYRange, item)
        item = submenu.Append(7, 'Set Y range', 'Set Y range')
        self.Bind(wx.EVT_MENU, self.OnXYRange, item)
        item = submenu.Append(4, '&xLin-xLin', 'Lin-Lin Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(1, '&xLog-yLog', 'Log-Log Plot type',kind=wx.ITEM_RADIO)
        
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(2, '&xLog-yLin', 'Log-Lin Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        item = submenu.Append(3, '&xLin-yLog', 'Lin-Log Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnLogPlotType, item)
        submenu.Check(self.axetype, True)
        item=menu.AppendMenu(wx.ID_ANY, '&Axes',submenu)
        
        #-- type --
        submenu=wx.Menu()
        item = submenu.Append(40, 'x y', 'x vs y type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnPlotXYType, item)
        item = submenu.Append(41, 'x*y', 'x vs x*y Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnPlotXYType, item)
        item = submenu.Append(42, 'x*y2', 'x vs x*y2 Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnPlotXYType, item)
        item = submenu.Append(43, 'x*y3', 'x vs x*y3 Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnPlotXYType, item)
        item = submenu.Append(44, 'x*y4', 'x vs x*y4 Plot type',kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self.OnPlotXYType, item)
        item=menu.AppendMenu(wx.ID_ANY, '&Y Axes',submenu)
        
        mainMenu.Append(menu, '&Plot') # Add the file menu to the menu bar

        menu = wx.Menu()
        id = wx.NewId()
        menu.Append(id, '&About...', 'Display version information')
        wx.EVT_MENU(self, id, self.OnMenuHelpAbout)

        mainMenu.Append(menu, '&Help')
        self.SetMenuBar(mainMenu)

    def OnMenuFileSave(self, evt):
        """
        Handles File->Save menu events.
        """
        fileName = wx.FileSelector('Save Plot', default_extension='png',
            wildcard=('Portable Network Graphics (*.png)|*.png|Scalable Vector Graphics SVG (*.svg)|*.svg|'
                + 'Encapsulated Postscript (*.eps)|*.eps|All files (*.*)|*.*'),
            parent=self, flags=wx.SAVE|wx.OVERWRITE_PROMPT)

        if not fileName:
            return

        path, ext = os.path.splitext(fileName)
        ext = ext[1:].lower()

        if ext != 'png' and ext != 'eps' and ext!='svg':
            error_message = (
                'Only the PNG,SVG and EPS image formats are supported.\n'
                'A file extension of \'png\', \'svg\' or \'eps\' must be used.')
            wx.MessageBox(error_message, 'Error - plotit',
                parent=self, style=wx.OK|wx.ICON_ERROR)
            return

        try:
            self.panel.print_figure(fileName)
        except IOError, e:
            if e.strerror:
                err = e.strerror
            else:
                err = e

            wx.MessageBox('Could not save file: %s' % err, 'Error - plotit',
                parent=self, style=wx.OK|wx.ICON_ERROR)

    def OnMenuFilePageSetup(self, evt):
        """
        Handles File->Page Setup menu events
        """
        self.printer.pageSetup()

    def OnMenuFilePrintPreview(self, evt):
        """
        Handles File->Print Preview menu events
        """
        self.printer.previewFigure(self.get_figure())

    def OnMenuFilePrint(self, evt):
        """
        Handles File->Print menu events
        """
        self.printer.printFigure(self.get_figure())

    def OnMenuFileClose(self, evt):
        """
        Handles File->Close menu events.
        """
        self.Close()
        self=None

    def OnMenuHelpAbout(self, evt):
        """
        Handles Help->About menu events.
        """
        wx.MessageBox(self.ABOUT_MESSAGE, self.ABOUT_TITLE, parent=self,
            style=wx.OK)
        
    def OnGridOn(self,event):
        self.gridON=True
        self.replot()
    
    def OnGridOff(self,event):
        self.gridON=False
        self.replot()
        
    def OnLegendOn(self,event):
        self.legendON=True
        self.replot()
    
    def OnLegendOff(self,event):
        self.legendON=False
        self.replot()
    def OnLineFormat(self,event):
        self.errbar=False
        self.linetype=event.GetId()-11
        self.replot()
        
    def OnLineFormatErrorBar(self,event):
        self.errbar=True
        self.linetype=2 #line and point with error bar
        self.replot()
    
    def OnLogPlotType(self, event):
        self.axetype=event.GetId()
        self.replot()
    
    def OnPlotXYType(self,event):
        self.plotexp=event.GetId()-40
        self.replot()
        
    def OnAutoscale(self,event):
        '''
        if self.autoscaleitem.IsChecked():
        self.statusbar.Show()
        '''
        self.replot()
    def OnMarkerChange(self,event):
        id=event.GetId()
        if id==100:
            self.markerSize+=2
        elif id==101:
            self.markerSize-=2
        #print self.markerSize
        self.replot()
    
    def OnLegendXYtitle(self,event):
        if event.GetId()==22:
            #set x title
            #message box for entry
            dlg=wx.TextEntryDialog(None,
                               "Value for x Label :",
                               "Insert a text for x Label",
                               self.axes.get_xlabel(),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=str(dlg.GetValue())
                self.xlabel=value
                self.replot()
        if event.GetId()==23:
            #set y title
            #message box for entry
            dlg=wx.TextEntryDialog(None,
                               "Value for y Label :",
                               "Insert a text for y Label",
                               self.axes.get_ylabel(),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=str(dlg.GetValue())
                self.ylabel=value
                self.replot()
    
    def OnXYRange(self,event):
        fig = self.get_figure()
        self.axes = fig.gca()
        xlim_min,xlim_max=self.axes.get_xlim()
        ylim_min,ylim_max=self.axes.get_ylim()
        if event.GetId()==6:
            #set x range
            #message box for entry
            dlg=wx.TextEntryDialog(None,
                               "Value for x min :",
                               "Value for x min",
                               defaultValue=str(xlim_min),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=float(dlg.GetValue())
                xlim_min=value
                self.autoscaleitem.Check(False)
            dlg=wx.TextEntryDialog(None,
                               "Value for x max :",
                               "Value for x max",
                               defaultValue=str(xlim_max),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=float(dlg.GetValue())
                xlim_max=value
                self.autoscaleitem.Check(False)
                
        if event.GetId()==7:
            #set y range
            #message box for entry
            dlg=wx.TextEntryDialog(None,
                               "Value for y min :",
                               "Value for y min",
                               defaultValue=str(ylim_min),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=float(dlg.GetValue())
                ylim_min=value
                self.autoscaleitem.Check(False)
            dlg=wx.TextEntryDialog(None,
                               "Value for y max :",
                               "Value for y max",
                               defaultValue=str(ylim_max),
                               style=wx.OK|wx.CANCEL)
            if dlg.ShowModal()==wx.ID_OK:
                value=float(dlg.GetValue())
                ylim_max=value
                self.autoscaleitem.Check(False)
                
        #replot       
        self.axes.set_xlim((xlim_min,xlim_max))
        self.axes.set_ylim((ylim_min,ylim_max))            
        self.replot()
        
    def get_figure(self):
        """
        Returns the figure associated with this canvas.
        """
        return self.panel.figure

    def set_cursor(self, state):
        """
        Enable or disable the changing mouse cursor.  When enabled, the cursor
        changes from the normal arrow to a square cross when the mouse enters a
        matplotlib axes on this canvas.
        """
        self.panel.set_cursor(state)

    def set_location(self, state):
        """
        Enable or disable the display of the matplotlib axes coordinates of the
        mouse in the lower left corner of the canvas.
        """
        self.panel.set_location(state)

    def set_crosshairs(self, state):
        """
        Enable or disable drawing crosshairs through the mouse cursor when it
        is inside a matplotlib axes.
        """
        self.panel.set_crosshairs(state)

    def set_selection(self, state):
        """
        Enable or disable area selections, where user selects a rectangular
        area of the canvas by left-clicking and dragging the mouse.
        """
        self.panel.set_selection(state)

    def set_zoom(self, state):
        """
        Enable or disable zooming in when the user makes an area selection and
        zooming out again when the user right-clicks.
        """
        self.panel.set_zoom(state)

    def set_autoscale_unzoom(self, state):
        """
        Enable or disable automatic view rescaling when the user zooms out to
        the initial figure.
        """
        self.panel.set_autoscale_unzoom(state)

    def draw(self):
        """
        Draw the associated C{Figure} onto the screen.
        """
        self.panel.draw()
    
    def get_marker(self):
        """ Return an infinite, cycling iterator over the available marker symbols.
        or a fixed marker symbol
        """
        #--line style
        if self.linetype<=5:
            #predifined marker
            lstyle=self.marker_fixed[self.linetype]
            #print lstyle
            return lstyle
        else:
            #automatic marker
            return self.marker_cycle.next()+'-'

    def get_color(self,n):
        ''' return a color name from the list of colors
        if n> length of list of colors, return at the beginning
        '''
        if n==None:
            return None
        t=divmod(n,len(self.colors)) #return the no of color in the list
        return self.colors[t[1]]
                
    
        
    
    def replot(self):
        fig = self.get_figure()
        self.axes = fig.gca()
        xlim_min,xlim_max=self.axes.get_xlim()
        ylim_min,ylim_max=self.axes.get_ylim()
        self.axes.cla() #clear
        #-- autoscale
        if self.autoscaleitem.IsChecked():
            #self.axes.autoscale_view(tight=False, scalex=True, scaley=True)
            self.axes.set_autoscale_on(True)
            pass
        else :
            #print "not auto scale", xlim_min,ylim_min, xlim_max,ylim_max
            #self.axes.autoscale_view(tight=False, scalex=False, scaley=False)
            self.axes.set_autoscale_on(False)
            #self.axes.set_autoscalex_on(False)
            #self.axes.set_autoscaley_on(False)
            self.axes.set_xlim((xlim_min,xlim_max))
            self.axes.set_ylim((ylim_min,ylim_max))
        #-- datas
        for d in self.datalist:
            #which color ?
            col=self.get_color(d.id)
            if d.color!=None:
                col=d.color
            #print d.label,d.y,d.color    
            if d.error!=None and self.errbar:
                #print "with errorbar"
                if d.id!=None:
                    self.axes.errorbar(d.x,d.y*(d.x**self.plotexp),yerr=d.error*(d.y**self.plotexp),linestyle='-',marker='.',\
                                       ecolor='b',\
                                       label=d.label,markersize=self.markerSize,color=col)#,label=d.label,markersize=5,fmt=None)
                else:
                    self.axes.errorbar(d.x,d.y*(d.x**self.plotexp),yerr=d.error,\
                                       linestyle='-',marker='.',label=d.label,markersize=self.markerSize)#,label=d.label,markersize=5,fmt=None)
                
            elif col!=None:
                self.axes.plot(d.x,d.y*(d.x**self.plotexp),\
                               self.get_marker(),\
                               label=d.label,\
                               color=col,\
                               markersize=self.markerSize)
            else :
                self.axes.plot(d.x,d.y*(d.x**self.plotexp),self.get_marker(),\
                               label=d.label,markersize=self.markerSize)
        #--grid
        if self.gridON:
            self.axes.get_xaxis().grid(True)
            self.axes.get_yaxis().grid(True)
        else :
            self.axes.get_xaxis().grid(False)
            self.axes.get_yaxis().grid(False)
        
        #--scale
        if self.axetype==1:
            self.axes.set_xscale('log')
            self.axes.set_yscale('log')
        if self.axetype==2:
            self.axes.set_xscale('log')
            self.axes.set_yscale('linear')
        if self.axetype==3:
            self.axes.set_xscale('linear')
            self.axes.set_yscale('log')
        if self.axetype==4:
            self.axes.set_xscale('linear')
            self.axes.set_yscale('linear')
        
        #--legend    
        if self.legendON:
            font=font_manager.FontProperties(style='italic',size='x-small')
            leg=self.axes.legend(loc='upper right',prop=font)
            #leg.get_frame().set_alpha(0.5)
        else:
            self.axes.legend_ = None
        #-- x and y label
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        #self.axes.set_title('Minimum Message Length')
        self.draw()

    def addData(self,x,y,label=None,id=None,error=None,color=None):
        ''' datas to the plot
        x and y are datas
        label : the name of datas
        id : no of datas in a list -> give the colors
        '''
        newdata=data(x,y,label,id,error,color=color)
        #self.datalist.append([x,y,label,id])
        self.datalist.append(newdata)
    
    def clearData(self):
        self.datalist=[]
    

if __name__== '__main__':
    from numpy import *
    app = wx.App()
    frame = PlotFrame(None, 1,"Monocylinder",size=(700,500))
    frame.Show(True)
    from pySAXS.models import MonoCylinder
    modl=MonoCylinder()
    x=modl.q
    y=modl.getIntensity()
    err=ones(shape(x))#random.rand(len(x))/10
    #err=err*y
    #print err
    frame.addData(x, y, label='monocylinder',error=err)
    frame.xlabel="q (A)"
    frame.ylabel="I (cm-1)"
    frame.replot()
    app.MainLoop()
