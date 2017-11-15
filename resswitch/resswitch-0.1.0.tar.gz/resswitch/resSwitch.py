# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Contains the class for the GUI resswitch.

All the GUI is in this file.
Executing this file will open the GUI

"""

import Tkinter
from setReset import setReset
import types
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfile
import pickle


class ResSwitch(Tkinter.Tk):

    """GUI class for resswitch"""

    def __init__(self):
        """Initializes the object."""

        # Construct the Tk object.
        Tkinter.Tk.__init__(self)
        self.title('resSwitch')

        # Constructs the icon. Comment these lines if running on Windows:
        # img = Tkinter.PhotoImage(file='ico/resSwitch.ico')
        # self.tk.call('wm', 'iconphoto', self._w, img)

        # construct the Left Frame.
        self.labelFrameLeft = Tkinter.LabelFrame(self, text="Data")
        self.labelFrameLeft.pack(fill="both", expand="no", side='left')

        # construct the scollbar.
        self.scrollBar = Tkinter.Scrollbar(self.labelFrameLeft)
        self.scrollBar.pack(side='right', fill='y')

        # construct the listbox of the data
        txt = "cycle       type        tension        resistance      "
        labelHeader = Tkinter.Label(self.labelFrameLeft, text=txt)
        labelHeader.pack(side='top')
        self.listSetReset = Tkinter.Listbox(self.labelFrameLeft, width=35,
                                            yscrollcommand=self.scrollBar.set)
        self.listSetReset.bind('<<ListboxSelect>>', self.chanV)
        self.listSetReset.bind("<Double-Button-1>", self.openWindow)
        self.listSetReset.pack(side='left', fill='both')
        self.scrollBar.config(command=self.listSetReset.yview)

        # constructs the Right Frame
        self.labelFrameRight = Tkinter.LabelFrame(self, text="Plots")
        self.labelFrameRight.pack(fill="both", expand="yes", side='right')

        # initializes matplotlib top plot
        self.plotFrame = Tkinter.LabelFrame(self.labelFrameRight,
                                            text="Cycles")
        self.plotFrame.pack(fill="both", expand="yes", side='top')
        self.figureOne = Figure(figsize=(5, 1), dpi=60)
        self.plotListOne = []
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.canvasOne = FigureCanvasTkAgg(self.figureOne, self.plotFrame)
        self.canvasOne.show()
        self.canvasOne.get_tk_widget().pack(side=Tkinter.TOP,
                                            fill=Tkinter.BOTH, expand=1)
        self.toolbarOne = NavigationToolbar2TkAgg(self.canvasOne,
                                                  self.plotFrame)
        self.toolbarOne.update()
        self.canvasOne._tkcanvas.pack(side=Tkinter.TOP,
                                      fill=Tkinter.BOTH, expand=1)

        # initializes matplotlib bottom plot
        self.analysisFrame = Tkinter.LabelFrame(self.labelFrameRight,
                                                text="Results")
        self.analysisFrame.pack(fill="both", expand="yes",
                                side='bottom')
        self.figureTwo = Figure(figsize=(5, 1),
                                dpi=60)
        self.plotListTwo = []
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.canvasTwo = FigureCanvasTkAgg(self.figureTwo, self.analysisFrame)
        self.canvasTwo.show()
        self.canvasTwo.get_tk_widget().pack(side=Tkinter.TOP,
                                            fill=Tkinter.BOTH, expand=1)
        self.toolbarTwo = NavigationToolbar2TkAgg(self.canvasTwo,
                                                  self.analysisFrame)
        self.toolbarTwo.update()
        self.canvasTwo._tkcanvas.pack(side=Tkinter.TOP,
                                      fill=Tkinter.BOTH, expand=1)

        # Constructs a popup list for top plots
        self.popupPlots = Tkinter.Menu(self, tearoff=0)
        self.popupPlots.add_command(label="Current vs Time",
                                    command=self.chanItime)
        self.popupPlots.add_command(label="Current vs Tension",
                                    command=self.chanIV)
        self.popupPlots.add_command(label="Tension vs Time",
                                    command=self.chanVtime)
        self.popupPlots.add_command(label="Resistance vs Time",
                                    command=self.chanRtime)
        self.popupPlots.add_command(label="Resistance vs Wished tension",
                                    command=self.chanR)
        self.listSetReset.bind("<Button-3>", self.do_popup)

        # Constructs the menu bar
        self.menuBar = Tkinter.Menu(self)

        # create the filemenu, and add it to the menu bar
        self.fileMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open rawdata file",
                                  command=self.opens)
        self.fileMenu.add_command(label="Open RS file",
                                  command=self.openRSFile)
        self.fileMenu.add_command(label="Save",
                                  command=self.file_save)

        self.exportMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.exportMenu.add_command(label="one .txt file",
                                    command=self.export_data)
        self.exportMenu.add_command(label="separate .csv files",
                                    command=self.export_data_2)
        self.fileMenu.add_cascade(label="Export",
                                  menu=self.exportMenu)

        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        # create the analysis menu, and add it to the menu bar
        self.analysisMenu = Tkinter.Menu(self.menuBar, tearoff=0)

        self.treatmentMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.treatmentMenu.add_command(label="No Set",
                                       command=self.noSetWindow)
        self.treatmentMenu.add_command(label="No Reset",
                                       command=self.noResetWindow)
        self.analysisMenu.add_cascade(label="Treatment",
                                      menu=self.treatmentMenu)

        self.histogramMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.histogramMenu.add_command(label="Tension Histogram",
                                       command=self.setTenHist)
        self.histogramMenu.add_command(label="Resistance Histogram",
                                       command=self.setResHist)
        self.histogramMenu.add_command(label="Current Histogram",
                                       command=self.setCurHist)
        self.analysisMenu.add_cascade(label="Histograms",
                                      menu=self.histogramMenu)

        self.cycleMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.cycleMenu.add_command(label="Resistance vs Cycles",
                                   command=self.resPlot)
        self.cycleMenu.add_command(label="Tension vs Cycles",
                                   command=self.tensionPlot)
        self.cycleMenu.add_command(label="Current vs Cycles",
                                   command=self.currentPlot)
        self.analysisMenu.add_cascade(label="Cycle plots",
                                      menu=self.cycleMenu)

        self.scatterPlotMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.scatterPlotMenu.add_command(label="Vset and Vreset vs Roff",
                                         command=self.tensionRoffPlot)
        self.scatterPlotMenu.add_command(label="Vset and Vreset vs Ron",
                                         command=self.tensionRonPlot)
        self.scatterPlotMenu.add_command(label="Ron and Roff vs ion",
                                         command=self.resistanceIonPlot)
        self.scatterPlotMenu.add_command(label="Ron and Roff vs ioff",
                                         command=self.resistanceIoffPlot)
        self.scatterPlotMenu.add_command(label="Vset and Vreset vs ion",
                                         command=self.tensionIonPlot)
        self.scatterPlotMenu.add_command(label="Vset and Vreset vs ioff",
                                         command=self.tensionIoffPlot)
        self.analysisMenu.add_cascade(label="Scatter plots",
                                      menu=self.scatterPlotMenu)
        self.analysisMenu.add_command(label="Results", command=self.result)
        self.menuBar.add_cascade(label="Analysis", menu=self.analysisMenu)

        # create the notemenu, and add it to the menu bar
        self.noteMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.noteMenu.add_command(label="Note", command=self.note)
        self.menuBar.add_cascade(label="Note", menu=self.noteMenu)

        # create the helpmenu, and add it to the menu bar
        self.helpMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="About", command=self.aboutWindow)
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

        # display the menu
        self.config(menu=self.menuBar)

        # other "global variables"
        self.tensionHistoWindow = None
        self.tensionHistoMin = None
        self.tensionHistoMax = None
        self.tensionHistoSteps = None
        self.resistanceHistoWindow = None
        self.resistanceHistoMin = None
        self.resistanceHistoMax = None
        self.resistanceHistoSteps = None
        self.selectedItem = None
        self.cycleWindow = None
        self.entryR = None
        self.entryV = None
        self.entryI = None
        self.filename = None
        self.rawData = None
        self.numberCycles = 0
        self.onResPlot = None
        self.offResPlot = None
        self.bins = None
        self.cuma = None
        self.cumb = None
        self.cumax = None
        self.cumbx = None
        self.cumay = None
        self.cumby = None
        self.cumcax = None
        self.cumcay = None
        self.cumcbx = None
        self.cumcby = None
        self.data = None

    def do_popup(self, event):
        """opens a window by right clicking on the listbox"""

        try:
            self.popupPlots.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popupPlots.grab_release()

    def setTenHist(self):
        """window for defining the tension histogram plot"""

        self.tensionHistoWindow = Tkinter.Toplevel(self)
        f1 = Tkinter.Frame(self.tensionHistoWindow)
        f1.pack()
        f2 = Tkinter.Frame(self.tensionHistoWindow)
        f2.pack(side='bottom')
        f11 = Tkinter.Frame(f1)
        f11.pack(side='top')
        f12 = Tkinter.Frame(f1)
        f12.pack(side='top')
        f13 = Tkinter.Frame(f1)
        f13.pack(side='top')
        L1 = Tkinter.Label(f11, text="min")
        L1.pack(side='left')
        self.tensionHistoMin = Tkinter.Entry(f11, bd=5)
        self.tensionHistoMin.pack(side='right')
        minimum = min([x for x in self.data.onTension if x != 'no set'] +
                      [x for x in self.data.offTension if x != 'no reset'])
        self.tensionHistoMin.insert(0, minimum)
        L2 = Tkinter.Label(f12, text="max")
        L2.pack(side='left')
        self.tensionHistoMax = Tkinter.Entry(f12, bd=5)
        self.tensionHistoMax.pack(side='right')
        maximum = max([x for x in self.data.onTension if x != 'no set'] +
                      [x for x in self.data.offTension if x != 'no reset'])
        self.tensionHistoMax.insert(0, maximum)
        L3 = Tkinter.Label(f13, text="steps")
        L3.pack(side='left')
        self.tensionHistoSteps = Tkinter.Entry(f13, bd=5)
        self.tensionHistoSteps.pack(side='right')
        maximum = max([x for x in self.data.onTension if x != 'no set'] +
                      [x for x in self.data.offTension if x != 'no reset'])
        minimum = min([x for x in self.data.onTension if x != 'no set'] +
                      [x for x in self.data.offTension if x != 'no reset'])
        result = (maximum - minimum) / 0.1
        self.tensionHistoSteps.insert(0, result)
        bu = Tkinter.Button(f2, text='ok', command=self.tenHist)
        bu.pack()

    def tenHist(self):
        """plots the tension histogram on the bottom plot"""

        out = self.data.tensionHistogram(float(self.tensionHistoMin.get()),
                                         float(self.tensionHistoMax.get()),
                                         float(self.tensionHistoSteps.get()),
                                         0)
        self.bins, self.binsa, self.binsb, onT, ofT, self.cuma, self.cumb = out
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].hist(onT, self.bins, color='g', alpha=.5,
                                  label='set')
        self.plotListTwo[-1].hist(ofT, self.bins, color='r', alpha=.5,
                                  label='reset')
        cumValMax = max(self.cuma)
        self.cuma = [100 * cumVal / cumValMax for cumVal in self.cuma]
        cumValMax = max(self.cumb)
        self.cumb = [100 * cumVal / cumValMax for cumVal in self.cumb]
        self.plotListTwo[-1].plot(self.binsa, self.cuma, 'go-')
        self.plotListTwo[-1].plot(self.binsb, self.cumb, 'ro-')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('tension (V)')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()
        self.tensionHistoWindow.destroy()

    def setResHist(self):
        """window for defining the resistance histogram plot"""

        self.resistanceHistoWindow = Tkinter.Toplevel(self)
        f1 = Tkinter.Frame(self.resistanceHistoWindow)
        f1.pack()
        f2 = Tkinter.Frame(self.resistanceHistoWindow)
        f2.pack(side='bottom')
        f11 = Tkinter.Frame(f1)
        f11.pack(side='top')
        f12 = Tkinter.Frame(f1)
        f12.pack(side='top')
        f13 = Tkinter.Frame(f1)
        f13.pack(side='top')
        L1 = Tkinter.Label(f11, text="min")
        L1.pack(side='left')
        self.resistanceHistoMin = Tkinter.Entry(f11, bd=5)
        self.resistanceHistoMin.pack(side='right')
        self.resistanceHistoMin.insert(0, 1)
        L2 = Tkinter.Label(f12, text="max")
        L2.pack(side='left')
        self.resistanceHistoMax = Tkinter.Entry(f12, bd=5)
        self.resistanceHistoMax.pack(side='right')
        m = max([x for x in self.data.onResistance if x != 'no set'] +
                [x for x in self.data.offResistance if x != 'no reset']) * 100
        self.resistanceHistoMax.insert(0, m)
        L3 = Tkinter.Label(f13, text="steps")
        L3.pack(side='left')
        self.resistanceHistoSteps = Tkinter.Entry(f13, bd=5)
        self.resistanceHistoSteps.pack(side='right')
        self.resistanceHistoSteps.insert(0, 100)
        bu = Tkinter.Button(f2, text='ok', command=self.resHist)
        bu.pack()

    def resHist(self):
        """plots the resistance histogram on the bottom plot"""

        out = self.data.ResCum(float(self.resistanceHistoMin.get()),
                               float(self.resistanceHistoMax.get()),
                               float(self.resistanceHistoSteps.get()), 0)
        bins, onR, offR, self.cumax, self.cumay, self.cumbx, self.cumby = out
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].hist(onR, bins, color='g', alpha=.5, label='on')
        self.plotListTwo[-1].hist(offR, bins, color='r', alpha=.5,
                                  label='off')
        cumValMax = max(self.cumay)
        self.cumay = [100 * cumVal / cumValMax for cumVal in self.cumay]
        cumValMax = max(self.cumby)
        self.cumby = [100 * cumVal / cumValMax for cumVal in self.cumby]
        self.plotListTwo[-1].plot(self.cumax, self.cumay, 'go-')
        self.plotListTwo[-1].plot(self.cumbx, self.cumby, 'ro-')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('resistance (ohm)')
        self.plotListTwo[-1].set_xscale('log')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()
        self.resistanceHistoWindow.destroy()

    def setCurHist(self):
        """window for defining the current histogram plot"""

        self.currentHistoWindow = Tkinter.Toplevel(self)
        f1 = Tkinter.Frame(self.currentHistoWindow)
        f1.pack()
        f2 = Tkinter.Frame(self.currentHistoWindow)
        f2.pack(side='bottom')
        f11 = Tkinter.Frame(f1)
        f11.pack(side='top')
        f12 = Tkinter.Frame(f1)
        f12.pack(side='top')
        f13 = Tkinter.Frame(f1)
        f13.pack(side='top')
        L1 = Tkinter.Label(f11, text="min")
        L1.pack(side='left')
        self.currentHistoMin = Tkinter.Entry(f11, bd=5)
        self.currentHistoMin.pack(side='right')
        self.currentHistoMin.insert(0, 0.0000001)
        L2 = Tkinter.Label(f12, text="max")
        L2.pack(side='left')
        self.currentHistoMax = Tkinter.Entry(f12, bd=5)
        self.currentHistoMax.pack(side='right')
        self.currentHistoMax.insert(0, 1)
        L3 = Tkinter.Label(f13, text="steps")
        L3.pack(side='left')
        self.currentHistoSteps = Tkinter.Entry(f13, bd=5)
        self.currentHistoSteps.pack(side='right')
        self.currentHistoSteps.insert(0, 100)
        bu = Tkinter.Button(f2, text='ok', command=self.curHist)
        bu.pack()

    def curHist(self):
        """plots the current histogram on the bottom plot"""

        o = self.data.currentHistogram(float(self.currentHistoMin.get()),
                                       float(self.currentHistoMax.get()),
                                       float(self.currentHistoSteps.get()),
                                       0)
        bins, onC, ofC, self.cumcax, self.cumcay, self.cumcbx, self.cumcby = o
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].hist(onC, bins, color='g', alpha=.5,
                                  label='set')
        self.plotListTwo[-1].hist(ofC, bins, color='r', alpha=.5,
                                  label='reset')
        cumValMax = max(self.cumcay)
        self.cumcay = [100 * cumVal / cumValMax for cumVal in self.cumcay]
        cumValMax = max(self.cumcby)
        self.cumcby = [100 * cumVal / cumValMax for cumVal in self.cumcby]
        self.plotListTwo[-1].plot(self.cumcax, self.cumcay, 'go-')
        self.plotListTwo[-1].plot(self.cumcbx, self.cumcby, 'ro-')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('current (ohm)')
        self.plotListTwo[-1].set_xscale('log')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()
        self.currentHistoWindow.destroy()

    def resPlot(self):
        """plots the on and off resistances with cycles on the bottom plot"""

        self.onResPlot, self.offResPlot = self.data.resistancePlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(range(len(self.onResPlot)), self.onResPlot,
                                  'rs', label='on')
        self.plotListTwo[-1].plot(range(len(self.offResPlot)), self.offResPlot,
                                  'b^', label='off')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('cycle')
        self.plotListTwo[-1].set_ylabel('Resistance (ohm)')
        self.plotListTwo[-1].set_yscale('log')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def tensionPlot(self):
        """plots the set and reset tensions with cycles on the bottom plot"""

        self.onTenPlot, self.offTenPlot = self.data.tensionPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(range(len(self.onTenPlot)),
                                  self.onTenPlot, 'rs', label='set')
        self.plotListTwo[-1].plot(range(len(self.offTenPlot)),
                                  self.offTenPlot, 'b^', label='reset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('cycle')
        self.plotListTwo[-1].set_ylabel('Tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def currentPlot(self):
        """plots the set and reset currents with cycles on the bottom plot"""

        self.onCurPlot, self.offCurPlot = self.data.currentPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(range(len(self.onCurPlot)), self.onCurPlot,
                                  'rs', label='set')
        self.plotListTwo[-1].plot(range(len(self.offCurPlot)),
                                  self.offCurPlot, 'b^', label='reset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('cycle')
        self.plotListTwo[-1].set_ylabel('Tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def tensionRoffPlot(self):
        """Scatter plot set and reset tensions vs off R on bottom plot"""

        self.Roffp, self.Vsetp, self.Vresetp = self.data.tensionRoffPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.Roffp, self.Vsetp, 'rs', label='set')
        self.plotListTwo[-1].plot(self.Roffp, self.Vresetp, 'b^',
                                  label='reset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('Roff')
        self.plotListTwo[-1].set_ylabel('tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def tensionRonPlot(self):
        """Scatter plot set and reset tensions vs on R on the bottom plot"""

        self.Ronp, self.Vsetp, self.Vresetp = self.data.tensionRonPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.Ronp, self.Vsetp, 'rs', label='set')
        self.plotListTwo[-1].plot(self.Ronp, self.Vresetp, 'b^', label='reset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('Ron')
        self.plotListTwo[-1].set_ylabel('tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def resistanceIonPlot(self):
        """Scatter plot on and off R vs set current on the bottom plot"""

        self.ionp, self.Ronp, self.Roffp = self.data.resistanceIonPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.ionp, self.Ronp, 'rs', label='Ron')
        self.plotListTwo[-1].plot(self.ionp, self.Roffp, 'b^', label='Roff')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('ion')
        self.plotListTwo[-1].set_ylabel('resistance')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def resistanceIoffPlot(self):
        """Scatter plot on and off R vs reset current on the bottom plot"""

        self.ioffp, self.Ronp, self.Roffp = self.data.resistanceIoffPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.ioffp, self.Ronp, 'rs', label='Ron')
        self.plotListTwo[-1].plot(self.ioffp, self.Roffp, 'b^', label='Roff')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('ioff')
        self.plotListTwo[-1].set_ylabel('resistance')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def tensionIonPlot(self):
        """Scatter plot set and reset V vs set current on the bottom plot"""

        self.ionp, self.Vsetp, self.Vresetp = self.data.tensionIonPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.ionp, self.Vsetp, 'rs', label='Vset')
        self.plotListTwo[-1].plot(self.ionp, self.Vresetp,
                                  'b^', label='Vreset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('ion')
        self.plotListTwo[-1].set_ylabel('wished tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def tensionIoffPlot(self):
        """Scatter plot set and reset V vs reset current on the bottom plot"""

        self.ioffp, self.Vsetp, self.Vresetp = self.data.tensionIoffPlot()
        self.figureTwo.delaxes(self.plotListTwo[-1])
        self.plotListTwo.append(self.figureTwo.add_subplot(111))
        self.plotListTwo[-1].plot(self.ioffp, self.Vsetp, 'rs', label='Vset')
        self.plotListTwo[-1].plot(self.ioffp,
                                  self.Vresetp, 'b^', label='Vreset')
        self.plotListTwo[-1].legend(loc='upper right')
        self.plotListTwo[-1].set_xlabel('ioff')
        self.plotListTwo[-1].set_ylabel('wished tension (V)')
        self.plotListTwo[-1].set_yscale('linear')
        self.plotListTwo[-1].grid()
        self.canvasTwo.show()

    def chanV(self, event):
        """plots the current vs wished tension on the top plot"""

        if self.listSetReset.curselection() != ():
            self.selectedItem = self.listSetReset.curselection()
        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(0, 1, 'linear', 'set', cy)
        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(0, 1, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('wished tension (V)')
        self.plotListOne[-1].set_ylabel('current')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def chanR(self):
        """plots the resistance vs wished tension on the top plot"""

        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(0, 2, 'linear', 'set', cy)

        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(0, 2, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('wished tension (V)')
        self.plotListOne[-1].set_ylabel('resistance (ohm)')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def chanRtime(self):
        """plots the resistance vs time on the top plot"""

        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 2, 'linear', 'set', cy)
        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 2, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('time (s)')
        self.plotListOne[-1].set_ylabel('resistance (ohm)')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def chanVtime(self):
        """plots the tension vs time on the top plot"""

        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 4, 'linear', 'set', cy)
        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 4, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('time (s)')
        self.plotListOne[-1].set_ylabel('tension (V)')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def chanIV(self):
        """plots the tension vs current on the top plot"""

        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(4, 1, 'linear', 'set', cy)
        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(4, 1, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('tension (V)')
        self.plotListOne[-1].set_ylabel('current (A)')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def chanItime(self):
        """plots the current vs time on the top plot"""

        if int(self.selectedItem[0]) % 2 == 0:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 1, 'linear', 'set', cy)
        else:
            cy = int(self.selectedItem[0])  # /2
            x1, y1 = self.data.cyclePlot(3, 1, 'linear', 'reset', cy)
        self.figureOne.delaxes(self.plotListOne[-1])
        self.plotListOne.append(self.figureOne.add_subplot(111))
        self.plotListOne[-1].plot(x1, y1, 'bo-')
        self.plotListOne[-1].set_xlabel('time (s)')
        self.plotListOne[-1].set_ylabel('current (A)')
        self.plotListOne[-1].grid()
        self.canvasOne.show()

    def openWindow(self, event):
        """opens a window to change the values for the R and the tension"""

        self.cycleWindow = Tkinter.Toplevel(self)
        if int(self.selectedItem[0]) % 2 == 0:
            V = self.data.onTension[int(self.selectedItem[0]) / 2]
            R = self.data.onResistance[int(self.selectedItem[0]) / 2]
            I = self.data.onCurrent[int(self.selectedItem[0]) / 2]

        else:
            V = self.data.offTension[int(self.selectedItem[0]) / 2]
            R = self.data.offResistance[int(self.selectedItem[0]) / 2]
            I = self.data.offCurrent[int(self.selectedItem[0]) / 2]
        f1 = Tkinter.Frame(self.cycleWindow)
        f1.pack(side='top')
        f2 = Tkinter.Frame(self.cycleWindow)
        f2.pack(side='top')
        f3 = Tkinter.Frame(self.cycleWindow)
        f3.pack(side='top')
        f4 = Tkinter.Frame(self.cycleWindow)
        f4.pack(side='top')
        L1 = Tkinter.Label(f1, text="Vset")
        L1.pack(side='left')
        self.entryR = Tkinter.Entry(f1, bd=5)
        self.entryR.pack(side='right')
        self.entryR.insert(0, str(V))
        L2 = Tkinter.Label(f2, text="Ron")
        L2.pack(side='left')
        self.entryV = Tkinter.Entry(f2, bd=5)
        self.entryV.pack(side='right')
        self.entryV.insert(0, str(R))
        L3 = Tkinter.Label(f3, text="Iset")
        L3.pack(side='left')
        self.entryI = Tkinter.Entry(f3, bd=5)
        self.entryI.pack(side='right')
        self.entryI.insert(0, str(I))
        bu = Tkinter.Button(f4, text='ok', command=self.inclu)
        bu.pack()

    def noSetWindow(self):
        """opens a window to force 'no set' values"""

        self.cycleNoSetWindow = Tkinter.Toplevel(self)
        f1 = Tkinter.Frame(self.cycleNoSetWindow)
        f1.pack(side='top')
        f2 = Tkinter.Frame(self.cycleNoSetWindow)
        f2.pack(side='top')
        f3 = Tkinter.Frame(self.cycleNoSetWindow)
        f3.pack(side='top')
        L1 = Tkinter.Label(f1, text="initial")
        L1.pack(side='left')
        self.initialNoSet = Tkinter.Entry(f1, bd=5)
        self.initialNoSet.pack(side='right')
        self.initialNoSet.insert(0, 0)
        L2 = Tkinter.Label(f2, text="final")
        L2.pack(side='left')
        self.finalNoSet = Tkinter.Entry(f2, bd=5)
        self.finalNoSet.pack(side='right')
        self.finalNoSet.insert(0, 0)
        bu = Tkinter.Button(f3, text='ok', command=self.noSetInclu)
        bu.pack()

    def noResetWindow(self):
        """opens a window to force 'no reset' values"""

        self.cycleNoResetWindow = Tkinter.Toplevel(self)
        f1 = Tkinter.Frame(self.cycleNoResetWindow)
        f1.pack(side='top')
        f2 = Tkinter.Frame(self.cycleNoResetWindow)
        f2.pack(side='top')
        f3 = Tkinter.Frame(self.cycleNoResetWindow)
        f3.pack(side='top')
        L1 = Tkinter.Label(f1, text="initial")
        L1.pack(side='left')
        self.initialNoReset = Tkinter.Entry(f1, bd=5)
        self.initialNoReset.pack(side='right')
        self.initialNoReset.insert(0, 0)
        L2 = Tkinter.Label(f2, text="final")
        L2.pack(side='left')
        self.finalNoReset = Tkinter.Entry(f2, bd=5)
        self.finalNoReset.pack(side='right')
        self.finalNoReset.insert(0, 0)
        bu = Tkinter.Button(f3, text='ok', command=self.noResetInclu)
        bu.pack()

    def note(self):
        """opens a window to make comments"""

        self.noteWindow = Tkinter.Toplevel(self)
        self.scrollBarNote = Tkinter.Scrollbar(self.noteWindow)
        self.frameNote1 = Tkinter.Frame(self.noteWindow)
        self.frameNote1.pack(side='top')
        self.frameNote2 = Tkinter.Frame(self.noteWindow)
        self.frameNote2.pack(side='bottom')
        self.scrollBarNote = Tkinter.Scrollbar(self.frameNote1)
        self.scrollBarNote.pack(side='right', fill='y')
        L1 = Tkinter.Label(self.frameNote1, text="note")
        L1.pack(side='top')
        self.commentText = Tkinter.Text(
            self.frameNote1, height=10, bd=2,
            yscrollcommand=self.scrollBarNote.set)
        self.commentText.pack(side='bottom')
        self.commentText.insert('1.0', self.data.comment)
        bu = Tkinter.Button(self.frameNote2, text='ok', command=self.saveNote)
        bu.pack(side='bottom')
        self.scrollBarNote.config(command=self.commentText.yview)

    def saveNote(self):
        """saves content of the notes window"""

        self.data.comment = self.commentText.get('1.0', 'end')
        self.noteWindow.destroy()

    def aboutWindow(self):
        """Shows the version of resSwitch"""

        self.aboutWindow = Tkinter.Toplevel(self)
        self.aboutWindow.minsize(width=200, height=100)
        self.aboutWindow.maxsize(width=200, height=100)
        f1 = Tkinter.Frame(self.aboutWindow)
        f1.pack(side='top')
        about = Tkinter.Label(
            f1, text="\nResSwitch (version 0.01)\n\nauthor: Daniel Silva")
        about.pack()

    def result(self):
        """shows the results in a window"""

        self.resultWindow = Tkinter.Toplevel(self)
        self.resultWindow.minsize(width=350, height=400)
        self.resultWindow.maxsize(width=350, height=400)
        f1 = Tkinter.Frame(self.resultWindow)
        f1.pack(side='top')
        result = Tkinter.Label(f1, text=self.data.results())
        result.pack()

    def inclu(self):
        """updates the listSetReset and the self.data"""

        if int(self.selectedItem[0]) % 2 == 0:
            cond1 = self.entryR.get() != 'no set'
            cond2 = self.entryV.get() != 'no set'
            cond3 = self.entryI.get() != 'no set'
            if cond1 and cond2 and cond3:
                self.data.onTension[int(
                    self.selectedItem[0]) / 2] = float(self.entryR.get())
                self.data.onResistance[int(
                    self.selectedItem[0]) / 2] = float(self.entryV.get())
                self.data.onCurrent[int(
                    self.selectedItem[0]) / 2] = float(self.entryI.get())
                self.colorItem[int(self.selectedItem[0])][1] = 0
            else:
                self.data.onTension[int(self.selectedItem[0]) / 2] = 'no set'
                self.data.onResistance[int(
                    self.selectedItem[0]) / 2] = 'no set'
                self.data.onCurrent[int(self.selectedItem[0]) / 2] = 'no set'
                self.colorItem[int(self.selectedItem[0])][1] = 1
            word1 = ' %02d' % float(int(self.selectedItem[0]) / 2)
            word2 = '          '
            word3 = 'set'
            word4 = '          '
            t = type(self.data.onTension[int(self.selectedItem[0]) / 2])
            if t == types.UnicodeType:
                word5 = 'no set'
                word6 = '          '
                word7 = 'no set'
            else:
                word5 = '%05.2f' % self.data.onTension[int(
                    self.selectedItem[0]) / 2]
                word6 = '          '
                word7 = str(
                    self.data.onResistance[int(self.selectedItem[0]) / 2])
            str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
            self.listSetReset.delete(int(self.selectedItem[0]))
            self.listSetReset.insert(int(self.selectedItem[0]), str1)
        else:
            cond1 = self.entryR.get() != 'no reset'
            cond2 = self.entryV.get() != 'no reset'
            cond3 = self.entryI.get() != 'no reset'
            if cond1 and cond2 and cond3:
                self.data.offTension[int(
                    self.selectedItem[0]) / 2] = float(self.entryR.get())
                self.data.offResistance[int(
                    self.selectedItem[0]) / 2] = float(self.entryV.get())
                self.data.offCurrent[int(
                    self.selectedItem[0]) / 2] = float(self.entryI.get())
                self.colorItem[int(self.selectedItem[0])][1] = 0
            else:
                self.data.offTension[int(
                    self.selectedItem[0]) / 2] = 'no reset'
                self.data.offResistance[int(
                    self.selectedItem[0]) / 2] = 'no reset'
                self.data.offCurrent[int(
                    self.selectedItem[0]) / 2] = 'no reset'
                self.colorItem[int(self.selectedItem[0])][1] = 1
            word1 = ' %02d' % float(int(self.selectedItem[0]) / 2)
            word2 = '          '
            word3 = 'reset'
            word4 = '       '
            t = type(self.data.offTension[int(self.selectedItem[0]) / 2])
            if t == types.UnicodeType:
                word5 = 'no reset'
                word6 = '       '
                word7 = 'no reset'
            else:
                word5 = '%05.2f' % self.data.offTension[int(
                    self.selectedItem[0]) / 2]
                word6 = '          '
                word7 = str(
                    self.data.offResistance[int(self.selectedItem[0]) / 2])
            str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
            self.listSetReset.delete(int(self.selectedItem[0]))
            self.listSetReset.insert(int(self.selectedItem[0]), str1)
        for k in self.colorItem:
            if k[1] == 1:
                self.listSetReset.itemconfig(k[0], bg='red', fg='white')
            if k[1] == 0:
                self.listSetReset.itemconfig(k[0], bg='white', fg='black')
        self.cycleWindow.destroy()

    def noSetInclu(self):
        """updates the listSetReset and the self.data"""

        cond1 = int(self.finalNoSet.get()) < len(self.data.onTension)
        cond2 = int(self.finalNoSet.get()) >= 0
        cond3 = int(self.initialNoSet.get()) < len(self.data.onTension)
        cond4 = int(self.initialNoSet.get()) >= 0
        if cond1 and cond2 and cond3 and cond4:
            int1 = int(self.finalNoSet.get())
            int2 = int(self.initialNoSet.get())
            for i in range(int1 - int2 + 1):
                self.data.onTension[i +
                                    int(self.initialNoSet.get())] = 'no set'
                self.data.onResistance[i +
                                       int(self.initialNoSet.get())] = 'no set'
                self.data.onCurrent[i +
                                    int(self.initialNoSet.get())] = 'no set'
                word1 = ' %02d' % float(int(self.initialNoSet.get()) + i)
                word2 = '          '
                word3 = 'set'
                word4 = '          '
                word5 = 'no set'
                word6 = '          '
                word7 = 'no set'
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.delete(
                    int(self.initialNoSet.get()) * 2 + i * 2)
                self.listSetReset.insert(
                    int(self.initialNoSet.get()) * 2 + i * 2, str1)
                self.listSetReset.itemconfig(
                    int(self.initialNoSet.get()) * 2 + i * 2,
                    bg='red', fg='white')
            self.cycleNoSetWindow.destroy()

    def noResetInclu(self):
        """updates the listSetReset and the self.data"""

        cond1 = int(self.finalNoReset.get()) < len(self.data.onTension)
        cond2 = int(self.finalNoReset.get()) >= 0
        cond3 = int(self.initialNoReset.get()) < len(self.data.onTension)
        cond4 = int(self.initialNoReset.get()) >= 0
        if cond1 and cond2 and cond3 and cond4:
            int1 = int(self.finalNoReset.get())
            int2 = int(self.initialNoReset.get())
            for i in range(int1 - int2 + 1):
                int1 = int(self.initialNoReset.get())
                self.data.offTension[i + int1] = 'no reset'
                self.data.offResistance[i + int1] = 'no reset'
                self.data.offCurrent[i + int1] = 'no reset'
                word1 = ' %02d' % float(int(self.initialNoReset.get()) + i)
                word2 = '          '
                word3 = 'reset'
                word4 = '       '
                word5 = 'no reset'
                word6 = '       '
                word7 = 'no reset'
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.delete(
                    int(self.initialNoReset.get()) * 2 + i * 2 + 1)
                self.listSetReset.insert(
                    int(self.initialNoReset.get()) * 2 + i * 2 + 1, str1)
                self.listSetReset.itemconfig(
                    int(self.initialNoReset.get()) * 2 + i * 2 + 1,
                    bg='red', fg='white')
            self.cycleNoResetWindow.destroy()

    def opens(self):
        """opens a rawdata file"""

        filename = askopenfilename(filetypes=[("Text files", "*.lvm")])
        if filename != () and filename != u'':
            self.onResPlot = None
            self.offResPlot = None
            self.bins = None
            self.cuma = None
            self.cumb = None
            self.cumax = None
            self.cumbx = None
            self.cumay = None
            self.cumby = None
            self.listSetReset.delete(0, 'end')
            file = open(filename, 'r')
            lines = file.readlines()
            file.close()
            temData = [[], [], [], [], []]
            for k in range(len(lines) - 2):
                temData[0].append(float(lines[k + 2].split('\t')[0]))
                temData[1].append(float(lines[k + 2].split('\t')[1]))
                temData[2].append(float(lines[k + 2].split('\t')[2]))
                temData[3].append(float(lines[k + 2].split('\t')[3]))
                temData[4].append(float(lines[k + 2].split('\t')[4]))
            data = []
            indexes = [1]
            flag = 0
            for k in range(len(lines) - 2):
                if flag == 1:
                    if abs(temData[0][k]) < .0000001 or k == len(lines) - 3:
                        indexes.append(k)
                        data.append([])
                        data[-1].append(temData[0][indexes[-2]:indexes[-1]])
                        data[-1].append(temData[1][indexes[-2]:indexes[-1]])
                        data[-1].append(temData[2][indexes[-2]:indexes[-1]])
                        data[-1].append(temData[3][indexes[-2]:indexes[-1]])
                        data[-1].append(temData[4][indexes[-2]:indexes[-1]])
                        flag = 0
                else:
                    flag = 1
            self.numberCycles = len(data)
            self.data = setReset(data, .1, .4)
            self.colorItem = []
            for i in range(len(self.data.onTension)):
                word1 = ' %02d' % (i)
                word2 = '          '
                word3 = 'set'
                word4 = '          '
                if type(self.data.onTension[i]) == types.UnicodeType:
                    word5 = 'no set'
                    word6 = '         '
                    word6 = '          '
                    word7 = str(self.data.onResistance[i])
                    self.colorItem.append([2 * i, 1])
                else:
                    word5 = '%05.2f' % self.data.onTension[i]
                    word6 = '          '
                    word6 = '          '
                    word7 = str(self.data.onResistance[i])
                    self.colorItem.append([2 * i, 0])
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.insert(2 * i + 1, str1)
                word1 = ' %02d' % (i)
                word2 = '          '
                word3 = 'reset'
                word4 = '       '
                if type(self.data.offTension[i]) == types.UnicodeType:
                    word5 = 'no reset'
                    word6 = '       '
                    word7 = str(self.data.offResistance[i])
                    self.colorItem.append([2 * i + 1, 1])
                else:
                    word5 = '%05.2f' % self.data.offTension[i]
                    word6 = '          '
                    word7 = str(self.data.offResistance[i])
                    self.colorItem.append([2 * i + 1, 0])
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.insert(2 * i + 2, str1)
            for i in self.colorItem:
                if i[1] == 1:
                    self.listSetReset.itemconfig(i[0], bg='red', fg='white')

    def openRSFile(self):
        """open saved object setReset()"""

        filename = askopenfilename(filetypes=[("Text files", "*.rs")])
        if filename != () and filename != u'':
            self.onResPlot = None
            self.offResPlot = None
            self.bins = None
            self.cuma = None
            self.cumb = None
            self.cumax = None
            self.cumbx = None
            self.cumay = None
            self.cumby = None
            self.listSetReset.delete(0, 'end')
            file = open(filename, 'rb')
            self.data = pickle.load(file)
            file.close()
            self.colorItem = []
            for i in range(len(self.data.onTension)):
                word1 = ' %02d' % (i)
                word2 = '          '
                word3 = 'set'
                word4 = '          '
                if type(self.data.onTension[i]) == types.UnicodeType:
                    word5 = 'no set'
                    word6 = '         '
                    word6 = '          '
                    word7 = str(self.data.onResistance[i])
                    self.colorItem.append([2 * i, 1])
                else:
                    word5 = '%05.2f' % self.data.onTension[i]
                    word6 = '          '
                    word6 = '          '
                    word7 = str(self.data.onResistance[i])
                    self.colorItem.append([2 * i, 0])
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.insert(2 * i + 1, str1)
                word1 = ' %02d' % (i)
                word2 = '          '
                word3 = 'reset'
                word4 = '       '
                if type(self.data.offTension[i]) == types.UnicodeType:
                    word5 = 'no reset'
                    word6 = '       '
                    word7 = str(self.data.offResistance[i])
                    self.colorItem.append([2 * i + 1, 1])
                else:
                    word5 = '%05.2f' % self.data.offTension[i]
                    word6 = '          '
                    word7 = str(self.data.offResistance[i])
                    self.colorItem.append([2 * i + 1, 0])
                str1 = word1 + word2 + word3 + word4 + word5 + word6 + word7
                self.listSetReset.insert(2 * i + 2, str1)
            for i in self.colorItem:
                if i[1] == 1:
                    self.listSetReset.itemconfig(i[0], bg='red', fg='white')

    def export_data(self):
        """exports the results to a txt file"""

        if self.data is not None:
            self.onResPlot, self.offResPlot = self.data.resistancePlot()
            self.onTenPlot, self.offTenPlot = self.data.tensionPlot()
            self.onCurPlot, self.offCurPlot = self.data.currentPlot()
            name = asksaveasfile(mode='w', defaultextension=".txt")
            text2save = self.data.results()
            text2save += str('\n\nresistance vs cycles (on)\n')
            for i in range(len(self.onResPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.onResPlot[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('resistance vs cycles (off)\n')
            for i in range(len(self.offResPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.offResPlot[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('current vs cycles (set)\n')
            for i in range(len(self.onCurPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.onCurPlot[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('current vs cycles (reset)\n')
            for i in range(len(self.offCurPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.offCurPlot[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('Vset vs cycles\n')
            for i in range(len(self.onTenPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.onTenPlot[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('Vreset vs cycles\n')
            for i in range(len(self.offTenPlot)):
                text2save = text2save + \
                    str(i) + '\t' + str(self.offTenPlot[i]) + '\n'
            text2save = text2save + '\n'
            out = self.data.tensionCumulativeProbability()
            cumon, cumonX, cumoff, cumoffX = out
            text2save = text2save + str('tension histogram (on)\n')
            for i in range(len(cumonX)):
                text2save = text2save + \
                    str(cumonX[i]) + '\t' + str(cumon[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('tension histogram (off)\n')
            for i in range(len(cumoffX)):
                text2save = text2save + \
                    str(cumoffX[i]) + '\t' + str(cumoff[i]) + '\n'
            text2save = text2save + '\n'
            out = self.data.resistanceCumulativeProbability()
            self.cumax, self.cumay, self.cumbx, self.cumby = out
            text2save = text2save + str('resistance histogram (on)\n')
            for i in range(len(self.cumax)):
                text2save = text2save + \
                    str(self.cumax[i]) + '\t' + str(self.cumay[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('resistance histogram (off)\n')
            for i in range(len(self.cumbx)):
                text2save = text2save + \
                    str(self.cumbx[i]) + '\t' + str(self.cumby[i]) + '\n'
            text2save = text2save + '\n'
            out = self.data.currentCumulativeProbability()
            self.cumcax, self.cumcay, self.cumcbx, self.cumcby = out
            text2save = text2save + str('current histogram (set)\n')
            for i in range(len(self.cumcax)):
                text2save = text2save + \
                    str(self.cumcay[i]) + '\t' + str(self.cumcax[i]) + '\n'
            text2save = text2save + '\n'
            text2save = text2save + str('current histogram (reset)\n')
            for i in range(len(self.cumcbx)):
                text2save = text2save + \
                    str(self.cumcby[i]) + '\t' + str(self.cumcbx[i]) + '\n'
            text2save = text2save + '\n'
            name.write(text2save)
            name.close()

    def export_data_2(self):
        """exports the results to several txt files"""

        if self.data is not None:
            self.onResPlot, self.offResPlot = self.data.resistancePlot()
            self.onTenPlot, self.offTenPlot = self.data.tensionPlot()
            self.onCurPlot, self.offCurPlot = self.data.currentPlot()
            name = asksaveasfile(mode='w', defaultextension=".csv")

            text2save2 = self.data.results()
            name.write(text2save2)

            f = open(name.name[:-4] + '_resOn_vs_cycles.csv', 'w')
            text2save = ''
            text2save += str('resistance vs cycles (on)\n')
            for i in range(len(self.onResPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.onResPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_resOFF_vs_cycles.csv', 'w')
            text2save = ''
            text2save = text2save + str('resistance vs cycles (off)\n')
            for i in range(len(self.offResPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.offResPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_setCur_vs_cycles.csv', 'w')
            text2save = ''
            text2save = text2save + str('current vs cycles (set)\n')
            for i in range(len(self.onCurPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.onCurPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_resetCur_vs_cycles.csv', 'w')
            text2save = ''
            text2save = text2save + str('current vs cycles (reset)\n')
            for i in range(len(self.offCurPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.offCurPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_Vset_vs_cycles.csv', 'w')
            text2save = ''
            text2save = text2save + str('Vset vs cycles\n')
            for i in range(len(self.onTenPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.onTenPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_Vreset_vs_cycles.csv', 'w')
            text2save = ''
            text2save = text2save + str('Vreset vs cycles\n')
            for i in range(len(self.offTenPlot)):
                text2save = text2save + \
                    str(i) + ',' + str(self.offTenPlot[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_set_tension_histogram.csv', 'w')
            text2save = ''
            out = self.data.tensionCumulativeProbability()
            cumon, cumonX, cumoff, cumoffX = out
            text2save = text2save + str('tension histogram (on)\n')
            for i in range(len(cumonX)):
                text2save = text2save + \
                    str(cumonX[i]) + ',' + str(cumon[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_reset_tension_histogram.csv', 'w')
            text2save = ''
            text2save = text2save + str('tension histogram (off)\n')
            for i in range(len(cumoffX)):
                text2save = text2save + \
                    str(cumoffX[i]) + ',' + str(cumoff[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_on_resistance_histogram.csv', 'w')
            text2save = ''
            out = self.data.resistanceCumulativeProbability()
            self.cumax, self.cumay, self.cumbx, self.cumby = out
            text2save = text2save + str('resistance histogram (on)\n')
            for i in range(len(self.cumax)):
                text2save = text2save + \
                    str(self.cumax[i]) + ',' + str(self.cumay[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_off_resistance_histogram.csv', 'w')
            text2save = ''
            text2save = text2save + str('resistance histogram (off)\n')
            for i in range(len(self.cumbx)):
                text2save = text2save + \
                    str(self.cumbx[i]) + ',' + str(self.cumby[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_set_current_histogram.csv', 'w')
            text2save = ''
            out = self.data.currentCumulativeProbability()
            self.cumcax, self.cumcay, self.cumcbx, self.cumcby = out
            text2save = text2save + str('current histogram (set)\n')
            for i in range(len(self.cumcax)):
                text2save = text2save + \
                    str(self.cumcay[i]) + ',' + str(self.cumcax[i]) + '\n'
            f.write(text2save)
            f.close()

            f = open(name.name[:-4] + '_reset_current_histogram.csv', 'w')
            text2save = ''
            text2save = text2save + str('current histogram (reset)\n')
            for i in range(len(self.cumcbx)):
                text2save = text2save + \
                    str(self.cumcby[i]) + ',' + str(self.cumcbx[i]) + '\n'
            f.write(text2save)
            f.close()
            name.close()

    def file_save(self):
        """saves the created object setReset()"""

        name = asksaveasfile(mode='wb', defaultextension=".rs")
        pickle.dump(self.data, name)
        name.close()


# Allow the class to run stand-alone.
if __name__ == "__main__":
    ResSwitch().mainloop()
