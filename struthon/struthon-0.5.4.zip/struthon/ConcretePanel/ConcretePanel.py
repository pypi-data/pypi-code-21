'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.8 date 2017-10-22
This file is part of Struthon.
Struthon is a range of free open source structural engineering design 
Python applications.
http://struthon.org/

Struthon is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Struthon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.2 changes:
- pushButton_loadROBOTcsv action added
File version 0.3 changes:
- multi loadcase, dxf export, save/open options added
File version 0.4 changes:
- ui upgrade
File version 0.5 changes:
- Mecway output data intergrated
File version 0.6 changes:
- assignScaleValue() argumant name chenged
File version 0.7 changes:
- cut rc peaks and rc smooth features added
File version 0.8 changes:
- Mecway feature upgraded to Mecway7
'''
import sys
import os

from PyQt4 import QtCore, QtGui
from matplotlib.colors import ColorConverter
import numpy as np

import strupy.units as u
u.xvalueformat("%5.2f")
from strupy.concrete.RcPanel import RcPanel
from strupy.concrete.RcPanelLoad import RcPanelLoad
from strupy.concrete.RcPanelDataLoader import RcPanelDataLoader
from strupy.concrete.RcPanelSolver import RcPanelSolver
from strupy.concrete.RcPanelViewer import RcPanelViewer
from strupy.concrete.RcPanelToolbox import RcPanelToolbox 
import strupy.concrete.rcsteel_area as rcsteel_area

from mainwindow_ui import Ui_MainWindow
import saveopen
import infotext

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #toolBox start page
        self.ui.toolBox.setCurrentIndex(0)
        # QT events
        #----load data ui area
        self.ui.pushButton_loadRFEMxls.clicked.connect(self.pushButton_loadRFEMxls)
        self.ui.pushButton_loadMecwaycsv.clicked.connect(self.pushButton_loadMecwaycsv)
        self.ui.pushButton_loadMecwayclipboard.clicked.connect(self.pushButton_loadMecwayclipboard)
        self.ui.pushButton_loadROBOTcsv.clicked.connect(self.pushButton_loadROBOTcsv)
        self.ui.pushButton_clearData.clicked.connect(self.pushButton_clearData)
        #----Geometry and view point set ui area
        self.ui.pushButton_plot3D.clicked.connect(self.pushButton_plot3D)
        self.ui.pushButton_AutoSet.clicked.connect(self.pushButton_AutoSet)
        self.ui.comboBox_SelectViewPoint.currentIndexChanged.connect(self.comboBox_SelectViewPoint)
        self.ui.pushButton_PlotPreview.clicked.connect(self.pushButton_PlotPreview)
        self.ui.pushButton_plotThickness.clicked.connect(self.pushButton_plotThickness)
        #----panel properties ui area
        self.ui.pushButton_Apllytopanel.clicked.connect(self.pushButton_Apllytopanel)
        #----plot internal forces ui area
        self.ui.comboBox_activeloadcase.currentIndexChanged.connect(self.comboBox_activeloadcase)
        self.ui.pushButton_plot_nx.clicked.connect(self.pushButton_plot_nx)
        self.ui.pushButton_plot_ny.clicked.connect(self.pushButton_plot_ny)
        self.ui.pushButton_plot_nxy.clicked.connect(self.pushButton_plot_nxy)
        self.ui.pushButton_plot_mx.clicked.connect(self.pushButton_plot_mx)
        self.ui.pushButton_plot_my.clicked.connect(self.pushButton_plot_my)
        self.ui.pushButton_plot_mxy.clicked.connect(self.pushButton_plot_mxy)
        self.ui.pushButton_plot_equNX.clicked.connect(self.pushButton_plot_equNX)
        self.ui.pushButton_plot_equNY.clicked.connect(self.pushButton_plot_equNY)
        self.ui.pushButton_plot_equMX.clicked.connect(self.pushButton_plot_equMX)
        self.ui.pushButton_plot_equMY.clicked.connect(self.pushButton_plot_equMY)
        #----plot results ui area
        self.ui.pushButton_plotApx.clicked.connect(self.pushButton_plotApx)
        self.ui.pushButton_plotAnx.clicked.connect(self.pushButton_plotAnx)
        self.ui.pushButton_plotApy.clicked.connect(self.pushButton_plotApy)
        self.ui.pushButton_plotAny.clicked.connect(self.pushButton_plotAny)
        self.ui.pushButton_plot_crackx.clicked.connect(self.pushButton_plot_crackx)
        self.ui.pushButton_plot_cracky.clicked.connect(self.pushButton_plot_cracky)
        self.ui.pushButton_plot_ksieffx.clicked.connect(self.pushButton_plot_ksieffx)
        self.ui.pushButton_plot_ksieffy.clicked.connect(self.pushButton_plot_ksieffy)
        self.ui.pushButton_plot_mimosx.clicked.connect(self.pushButton_plot_mimosx)
        self.ui.pushButton_plot_mimosy.clicked.connect(self.pushButton_plot_mimosy)
        #----Reinforcement map ui area
        self.ui.pushButton_mapApx.clicked.connect(self.pushButton_mapApx)
        self.ui.pushButton_mapAnx.clicked.connect(self.pushButton_mapAnx)
        self.ui.pushButton_mapApy.clicked.connect(self.pushButton_mapApy)
        self.ui.pushButton_mapAny.clicked.connect(self.pushButton_mapAny)
        self.ui.pushButton_ApllyToScale.clicked.connect(self.pushButton_Apllytopanel)
        self.ui.pushButton_spaceing.clicked.connect(self.pushButton_spaceing)
        self.ui.comboBox_presetAscale.currentIndexChanged.connect(self.comboBox_presetAscale)
        #----Raport ui area
        self.ui.pushButton_SaveToDXF.clicked.connect(self.pushButton_SaveToDXF)
        #----toolbox
        self.ui.toolBox.currentChanged.connect(self.toolBoxChanged)
        #----MenuBar File
        self.ui.actionSave.triggered.connect(self.actionSave)
        self.ui.actionOpen.triggered.connect(self.actionOpen)
        #----MenuBar Calculate
        self.ui.actionAll_loadcases.triggered.connect(self.calculateAll)
        self.ui.actionActieve_loadcase.triggered.connect(self.calculateActive)
        #---MenuBar Help
        self.ui.actionAbout.triggered.connect(self.actionAbout)

    #----load data ui area
    def pushButton_loadRFEMxls(self):
        panel.clear_arrays_data()
        load.clear_arrays_data()
        myapp.ui.comboBox_activeloadcase.clear()
        loader.RFEMxlsloader(panel, load, self.ui.progressBar)
        panel.calculate_flatten_coordinates()
        autoSetView()
        checkStatus()
        myapp.ui.comboBox_activeloadcase.addItems(load.get_loadcasenamelist())

    def pushButton_loadMecwaycsv(self):
        print 'csv'
        self.loadMecwayc('csv')
    def pushButton_loadMecwayclipboard(self):
        print 'clipboard'
        self.loadMecwayc('clipboard')
    def loadMecwayc(self, mode):
        myapp.ui.comboBox_activeloadcase.clear()
        loader.MECWAYloader(panel, load, self.ui.progressBar, mode)
        panel.calculate_flatten_coordinates()
        autoSetView()
        checkStatus()
        myapp.ui.comboBox_activeloadcase.addItems(load.get_loadcasenamelist())
        
    def pushButton_loadROBOTcsv(self):
        panel.clear_arrays_data()
        load.clear_arrays_data()
        myapp.ui.comboBox_activeloadcase.clear()
        loader.ROBOTcsvloader(panel, load, self.ui.progressBar)
        panel.calculate_flatten_coordinates()
        autoSetView()
        checkStatus()
        myapp.ui.comboBox_activeloadcase.addItems(load.get_loadcasenamelist())

    def pushButton_clearData(self):
        panel.clear_arrays_data()
        load.clear_arrays_data()
        checkStatus()
        myapp.ui.comboBox_activeloadcase.clear()
        
    #----Geometry and view point set ui area
    def pushButton_plot3D(self):
        viewer.plot_coordinates()
        
    def pushButton_AutoSet(self):
        autoSetView()
        
    def comboBox_SelectViewPoint(self):
        userSelectedView = str(myapp.ui.comboBox_SelectViewPoint.currentText())
        panel.set_transf_matrix_for_view(userSelectedView)

    def pushButton_plotThickness(self):
        viewer.plot_thickness()
        
    def pushButton_PlotPreview(self):
        viewer.plot_flatten_shape()
        
    #----panel properties ui area
    def pushButton_Apllytopanel(self):
        ui_loadfromdate ()
        ui_loadtodate ()
        
    #----plot internal forces ui area
    def comboBox_activeloadcase(self):
        if not load.get_loadcasenamelist() == []:
            caseSelected = str(myapp.ui.comboBox_activeloadcase.currentText())
            load.set_activeloadcase(caseSelected)
        
    def pushButton_plot_nx(self):
        viewer.plot_nx()
    def pushButton_plot_ny(self):
        viewer.plot_ny()
    def pushButton_plot_nxy(self):
        viewer.plot_nxy()
    def pushButton_plot_mx(self):
        viewer.plot_mx()
    def pushButton_plot_my(self):
        viewer.plot_my()
    def pushButton_plot_mxy(self):
        viewer.plot_mxy() 
    def pushButton_plot_equNX(self):
        viewer.plot_equ_NX() 
    def pushButton_plot_equNY(self):
        viewer.plot_equ_NY()
    def pushButton_plot_equMX(self):
        viewer.plot_equ_MX()
    def pushButton_plot_equMY(self):
        viewer.plot_equ_MY()

    #----plot results ui area
    def pushButton_plotApx(self):
        viewer.plot_reinforcement_Apx()
    def pushButton_plotAnx(self):
        viewer.plot_reinforcement_Anx()
    def pushButton_plotApy(self):
        viewer.plot_reinforcement_Apy()        
    def pushButton_plotAny(self):
        viewer.plot_reinforcement_Any()
    def pushButton_plot_crackx(self):
        viewer.plot_rysx()       
    def pushButton_plot_cracky(self):
        viewer.plot_rysy()            
    def pushButton_plot_ksieffx(self):
        viewer.plot_ksieffx()
    def pushButton_plot_ksieffy(self):
        viewer.plot_ksieffy()  
    def pushButton_plot_mimosx(self):
        viewer.plot_mimosx()     
    def pushButton_plot_mimosy(self):
        viewer.plot_mimosy() 
    
    #----Reinforcement map ui area
    def pushButton_mapApx(self):
        viewer.map_reinforcement_Apx()
    def pushButton_mapAnx(self):
        viewer.map_reinforcement_Anx()
    def pushButton_mapApy(self):
        viewer.map_reinforcement_Apy()        
    def pushButton_mapAny(self):
        viewer.map_reinforcement_Any()
    def pushButton_mapAxn(self):
        viewer.map_reinforcement_Anx()
    def pushButton_mapAxn(self):
        viewer.map_reinforcement_Anx()

    def pushButton_spaceing(self):
        if myapp.ui.tableWidget_Anscale.currentItem():
            value = float(myapp.ui.tableWidget_Anscale.currentItem().text())
            value += rcsteel_area.ui_area_diameter_spaceing_perdist(perdist=100.0*u.cm)[0].asUnit(panel.A_unit).asNumber()
            myapp.ui.tableWidget_Anscale.currentItem().setText(str(round(value, 2)))
        if myapp.ui.tableWidget_Apscale.currentItem():
            value = float(myapp.ui.tableWidget_Apscale.currentItem().text())
            value += rcsteel_area.ui_area_diameter_spaceing_perdist(perdist=100.0*u.cm)[0].asUnit(panel.A_unit).asNumber()
            myapp.ui.tableWidget_Apscale.currentItem().setText(str(round(value, 2)))  

    def comboBox_presetAscale(self):
        userSelectedScale = str(myapp.ui.comboBox_presetAscale.currentText())
        panel.set_preset_Ascale_value(userSelectedScale)
        ui_loadtodate ()
        
    #----Raport ui area
    def pushButton_SaveToDXF(self):
        viewer.savedxf(self.ui.progressBar)
           
    #----Toolbox       
    def toolBoxChanged(self):
        checkStatus()
        
    #----MenuBar
    def actionSave(self):
        ui_loadfromdate()
        saveopen.saveproject(panel, load, self.ui.progressBar)
        print panel.coord_Xp
        
    def actionOpen(self):
        panel.clear_arrays_data()
        load.clear_arrays_data()
        myapp.ui.comboBox_activeloadcase.clear()        
        saveopen.openproject(panel, load, self.ui.progressBar)
        ui_loadtodate()
        panel.calculate_flatten_coordinates()
        autoSetView()
        checkStatus()
        myapp.ui.comboBox_activeloadcase.addItems(load.get_loadcasenamelist())

    def calculateAll(self):
        ui_loadfromdate ()
        ui_loadtodate ()
        #---
        nowiscase = load.casename
        panel.clear_result()
        for loadcase in load.get_loadcasenamelist():
            print loadcase
            myapp.ui.label_progressText.setText(loadcase + '...')
            load.set_activeloadcase(loadcase)
            solver.reinforce(panel, load, self.ui.progressBar)
            myapp.ui.label_progressText.setText('')
        load.set_activeloadcase(nowiscase)
        self.modif_reinforcement()
        #---
        ui_loadtodate ()
        checkStatus()

    def calculateActive(self):
        ui_loadfromdate ()
        ui_loadtodate ()
        #---
        panel.clear_result()
        myapp.ui.label_progressText.setText(load.casename + '...')
        solver.reinforce(panel, load, self.ui.progressBar)
        myapp.ui.label_progressText.setText('')
        self.modif_reinforcement()
        #---
        ui_loadtodate ()
        checkStatus() 
        
    def modif_reinforcement(self):
        cut_peak=myapp.ui.checkBox_CutPeak.isChecked()
        cut_dist = float((myapp.ui.comboBox_CutPeakSize.currentText()))
        #---
        smooth=myapp.ui.checkBox_Smooth.isChecked()
        smooth_width = float((myapp.ui.comboBox_SmoothWidth.currentText()))
        #---
        anchoring = myapp.ui.checkBox_BarAnchoring.isChecked()
        anchor_filength = float((myapp.ui.comboBox_BarAnchoringLength.currentText()))
        #---
        if len(panel.Apx)>1:
            if cut_peak:
                myapp.ui.label_progressText.setText('cuting peaks...')
                toolbox.cut_peak(cut_dist=cut_dist, progress=self.ui.progressBar)
            if smooth:
                myapp.ui.label_progressText.setText('smoothing...')
                toolbox.smooth_np_reinforcement(smooth_width=smooth_width, progress=self.ui.progressBar)
            if anchoring:
                myapp.ui.label_progressText.setText('anchoring...')
                toolbox.include_anchore(anchor_filength=anchor_filength, progress=self.ui.progressBar)
        myapp.ui.label_progressText.setText('')
    
    def actionAbout(self):
        import Tkinter as tk
        from tkMessageBox import showinfo
        root = tk.Tk()
        root.withdraw()
        text = infotext.version + ' version for testing'
        text += infotext.about
        showinfo('About StruthonConcretePanel', text)
        root.destroy()

class colorscale():
    def __init__(self, parent=None):
        self.TableWiget = None
        self.ScaleColors = []
        self.SclaeValues = []
        #----
        self.converter = ColorConverter()
    
    def assignTablewiget(self, someTableWiget):
        self.TableWiget = someTableWiget
    
    def assignScaleColors(self, someScaleColors):
        self.ScaleColors = someScaleColors

    def assignScaleValue(self, someScaleValues):
        self.SclaeValues = someScaleValues
        
    def updateView(self):
        #----deleting existing table
        for i in reversed(range(self.TableWiget.rowCount())):
            self.TableWiget.removeRow(i)
        for i in reversed(range(self.TableWiget.columnCount())):
            self.TableWiget.removeColumn(i)
        #----creating  table    
        self.TableWiget.insertColumn(0)
        for i in range(len(self.ScaleColors)):
            self.TableWiget.insertRow(i)
            self.TableWiget.setItem(i, 0, QtGui.QTableWidgetItem())
            c = (self.converter.to_rgba_array(self.ScaleColors[i])*255)[0]
            self.TableWiget.item(i, 0).setBackground(QtGui.QColor(c[0],c[1],c[2]))
            self.TableWiget.item(i, 0).setText(str(self.SclaeValues[i]))
        self.TableWiget.verticalHeader().setVisible(False)
        self.TableWiget.horizontalHeader().setVisible(False)
        
    def update_assignedScaleValue(self):
        for i in range(len(self.ScaleColors)):
            self.SclaeValues[i] = float(self.TableWiget.item(i, 0).text())
        self.SclaeValues.sort()

def ui_loadtodate ():
    #----panel properties
    myapp.ui.lineEdit_PanelName.setText(panel.PanelName)
    myapp.ui.lineEdit_an.setText(str((panel.an/u.mm).asNumber()))
    myapp.ui.lineEdit_ap.setText(str((panel.ap/u.mm).asNumber()))
    #---------
    myapp.ui.comboBox_dn.setCurrentIndex(myapp.ui.comboBox_dn.findText(str(round((panel.fin/u.mm).asNumber(), 1))))
    myapp.ui.comboBox_dp.setCurrentIndex(myapp.ui.comboBox_dp.findText(str(round((panel.fip/u.mm).asNumber(), 1))))
    #---------
    myapp.ui.comboBox_cracklimn.setCurrentIndex(myapp.ui.comboBox_cracklimn.findText(str(round((panel.wlimn/u.mm).asNumber(), 1))))
    if panel.rysAn == 0:
        myapp.ui.comboBox_cracklimn.setCurrentIndex(myapp.ui.comboBox_cracklimn.findText('any'))
    myapp.ui.comboBox_cracklimp.setCurrentIndex(myapp.ui.comboBox_cracklimp.findText(str(round((panel.wlimp/u.mm).asNumber(), 1))))
    if panel.rysAp == 0:
        myapp.ui.comboBox_cracklimp.setCurrentIndex(myapp.ui.comboBox_cracklimp.findText('any'))
    #---------
    myapp.ui.comboBox_concreteclass.setCurrentIndex(myapp.ui.comboBox_concreteclass.findText(panel.concretename))
    myapp.ui.comboBox_steelclass.setCurrentIndex(myapp.ui.comboBox_steelclass.findText(panel.rcsteelname))
    #----panel properties text
    myapp.ui.textBrowser_panelprop.clear()
    myapp.ui.textBrowser_panelprop.append(panel.get_panelpreptext())
    #----loadcase list
    #----colorscale
    Anscale.updateView()
    Apscale.updateView()
    myapp.ui.label_scaleUnit.setText('x ' + str(panel.A_unit))
    #----calculation report text
    myapp.ui.textBrowser_report.clear()
    myapp.ui.textBrowser_report.append(panel.report)
    #----data status check and buttons activating
    checkStatus()
    
def ui_loadfromdate (loadcase=0):
    #---------
    panel.PanelName = myapp.ui.lineEdit_PanelName.text()
    panel.an = float((myapp.ui.lineEdit_an.text()))*u.mm
    panel.ap = float((myapp.ui.lineEdit_ap.text()))*u.mm
    #---------
    panel.fin = float((myapp.ui.comboBox_dn.currentText()))*u.mm
    panel.fip = float((myapp.ui.comboBox_dp.currentText()))*u.mm
    #---------
    if not myapp.ui.comboBox_cracklimn.currentText() == 'any':
        panel.wlimn = float((myapp.ui.comboBox_cracklimn.currentText()))*u.mm
        panel.rysAn = 1
    else:
        panel.rysAn = 0
    if not myapp.ui.comboBox_cracklimp.currentText() == 'any':
        panel.wlimp = float((myapp.ui.comboBox_cracklimp.currentText()))*u.mm
        panel.rysAp = 1
    else:
        panel.rysAp = 0
    #---------
    panel.set_concreteclass(myapp.ui.comboBox_concreteclass.currentText())
    panel.set_rcsteelclass(myapp.ui.comboBox_steelclass.currentText())
    #----colorscale
    Anscale.update_assignedScaleValue()
    Apscale.update_assignedScaleValue()
    
def checkStatus():
    #----
    def check (array):
        if len(array) > 1:
            return True
        else :
            return False
    #----
    isPanelData = check(panel.h)
    isLoadData = check(load.moment_mx)
    iseEquLoadCalculated = check(load.moment_equ_MX)
    isCalculated = check(panel.Anx)
    #----Input data data buttons
    myapp.ui.pushButton_plot3D.setEnabled(isPanelData)
    myapp.ui.pushButton_AutoSet.setEnabled(isPanelData)
    myapp.ui.pushButton_PlotPreview.setEnabled(isPanelData)
    myapp.ui.pushButton_plotThickness.setEnabled(isPanelData)
    #----Panel properties buttons
    #----Plot internal forces buttons
    myapp.ui.pushButton_plot_nx.setEnabled(isLoadData)
    myapp.ui.pushButton_plot_ny.setEnabled(isLoadData)    
    myapp.ui.pushButton_plot_nxy.setEnabled(isLoadData)
    myapp.ui.pushButton_plot_mx.setEnabled(isLoadData)
    myapp.ui.pushButton_plot_my.setEnabled(isLoadData)
    myapp.ui.pushButton_plot_mxy.setEnabled(isLoadData)
    #----
    myapp.ui.pushButton_plot_equNX.setEnabled(iseEquLoadCalculated)
    myapp.ui.pushButton_plot_equNY.setEnabled(iseEquLoadCalculated)
    myapp.ui.pushButton_plot_equMX.setEnabled(iseEquLoadCalculated)
    myapp.ui.pushButton_plot_equMY.setEnabled(iseEquLoadCalculated)
    #----Plot results buttons
    myapp.ui.pushButton_plotApx.setEnabled(isCalculated)
    myapp.ui.pushButton_plotApy.setEnabled(isCalculated)
    myapp.ui.pushButton_plotAnx.setEnabled(isCalculated)
    myapp.ui.pushButton_plotAny.setEnabled(isCalculated)
    myapp.ui.pushButton_plot_crackx.setEnabled(isCalculated)
    myapp.ui.pushButton_plot_cracky.setEnabled(isCalculated)
    myapp.ui.pushButton_plot_ksieffx.setEnabled(isCalculated) 
    myapp.ui.pushButton_plot_ksieffy.setEnabled(isCalculated) 
    myapp.ui.pushButton_plot_mimosx.setEnabled(isCalculated) 
    myapp.ui.pushButton_plot_mimosy.setEnabled(isCalculated)     
    #----Reinforcement map buttons
    myapp.ui.pushButton_mapApx.setEnabled(isCalculated)
    myapp.ui.pushButton_mapApy.setEnabled(isCalculated)
    myapp.ui.pushButton_mapAnx.setEnabled(isCalculated)
    myapp.ui.pushButton_mapAny.setEnabled(isCalculated)    
    #----Raport buttons
    myapp.ui.pushButton_SaveToDXF.setEnabled(isCalculated)
    #----MenuBar
    myapp.ui.menuCaltulate.setEnabled(isLoadData)
    myapp.ui.actionAll_loadcases.setEnabled(isLoadData)
    myapp.ui.actionActieve_loadcase.setEnabled(isLoadData)
    #----
    myapp.ui.textBrowser_loaddata.clear()
    myapp.ui.textBrowser_loaddata.setText(status_text())
    
def status_text():
    def array_range_text(array, unit = 1):
        if len(array) > 0:
            text = str(np.min(array) * unit) + ' .. ' + str(np.max(array) * unit) 
            return text
        else:
            return 'No data'
    #----
    def array_size_text(array, unit = 1):
        if len(array) > 0:
            text = str(abs(np.max(array) * unit - np.min(array) * unit))
            return text
        else:
            return 'No data'
    #----
    text = '>>>>Points number:  ' + str(len(panel.coord_Xp)) + '\n'
    text += '>>>>Structure size:\n'
    text += 'in x:  ' + array_size_text(panel.coord_Xp, panel.coord_unit) + '\n'
    text += 'in y:  ' + array_size_text(panel.coord_Yp, panel.coord_unit) + '\n'
    text += 'in z:  ' + array_size_text(panel.coord_Zp, panel.coord_unit) + '\n'   
    text += 'panel thickness:  ' + array_range_text(panel.h, panel.h_unit) + '\n'
    text += '>>>>Load data:\n'
    text += 'loadcases number: ' + str(len(load.loadcasecontainer)) + '\n'
    
    if len(load.loadcasecontainer) > 0:
        text += 'load range (per meter value):\n'
        for case in load.loadcasecontainer:
            text += '  case ' + case['casename'] + '\n'
            text += 'for mx:  ' + array_range_text(case['moment_mx'], load.moment_unit) + '\n'  
            text += 'for my:  ' + array_range_text(case['moment_my'], load.moment_unit) + '\n'    
            text += 'for nx:  ' + array_range_text(case['force_nx'], load.force_unit) + '\n'  
            text += 'for ny:  ' + array_range_text(case['force_ny'], load.force_unit) + '\n'
    return text

def autoSetView():
    size_x = abs(np.max(panel.coord_Xp) - np.min(panel.coord_Xp))
    size_y = abs(np.max(panel.coord_Yp) - np.min(panel.coord_Yp))
    size_z = abs(np.max(panel.coord_Zp) - np.min(panel.coord_Zp))
    viewPoint = 'Top'
    size = size_z
    if size > size_x :
        viewPoint = 'Right'
        size = size_x
    if size > size_y :
        viewPoint = 'Front'
        size = size_y
    myapp.ui.comboBox_SelectViewPoint.setCurrentIndex(myapp.ui.comboBox_SelectViewPoint.findText(viewPoint))
    
if __name__ == "__main__":
    #----needed strupy objects
    panel = RcPanel()
    load = RcPanelLoad()
    loader = RcPanelDataLoader()
    solver = RcPanelSolver()
    viewer = RcPanelViewer()
    toolbox = RcPanelToolbox()
    #----assigning strupy objects
    viewer.assignPanelLoadObiect(load)
    viewer.assignPanelObiect(panel)
    toolbox.assignPanelObiect(panel)
    #----initialdir for data askopenfilename dialog
    loader.initialdir = os.path.dirname(__file__)
    viewer.initialdir = os.path.dirname(__file__)
    #----PyQt objects
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    #----version
    myapp.ui.label_info.setText('www.struthon.org')
    myapp.setWindowTitle(infotext.appname + ' ' + infotext.version)
    #----color scale objects
    Anscale = colorscale()
    Apscale = colorscale()
    Anscale.assignTablewiget(myapp.ui.tableWidget_Anscale)
    Apscale.assignTablewiget(myapp.ui.tableWidget_Apscale)
    Anscale.assignScaleColors(viewer.colorscale)
    Apscale.assignScaleColors(viewer.colorscale)
    Anscale.assignScaleValue(panel.Anscale)
    Apscale.assignScaleValue(panel.Apscale)
    #----
    myapp.ui.comboBox_steelclass.addItems(panel.get_availablercsteelclass())
    myapp.ui.comboBox_concreteclass.addItems(panel.get_availableconcreteclass())
    #----
    myapp.ui.comboBox_dp.addItems([str(round((i/u.mm).asNumber(), 1)) for i in rcsteel_area.default_diameterlist])
    myapp.ui.comboBox_dn.addItems([str(round((i/u.mm).asNumber(), 1)) for i in rcsteel_area.default_diameterlist])
    #----
    myapp.ui.comboBox_cracklimp.addItems(['any', '0.4', '0.3', '0.2', '0.1'])
    myapp.ui.comboBox_cracklimn.addItems(['any', '0.4', '0.3', '0.2', '0.1'])
    #----
    myapp.ui.lineEdit_ap.setText('40')
    myapp.ui.lineEdit_an.setText('40')
    #----
    myapp.ui.comboBox_SelectViewPoint.addItems(panel.named_views().keys())
    #----
    myapp.ui.comboBox_presetAscale.addItems(panel.preset_Ascale_value().keys())
    #----
    myapp.ui.comboBox_activeloadcase.addItems(load.get_loadcasenamelist())
    #----
    myapp.ui.comboBox_CutPeakSize.addItems([ '0.5', '1.0', '1.5'])
    myapp.ui.comboBox_CutPeakSize.setCurrentIndex(myapp.ui.comboBox_CutPeakSize.findText('1.0'))
    myapp.ui.comboBox_SmoothWidth.addItems(['1.5', '2.0', '2.5'])
    myapp.ui.comboBox_SmoothWidth.setCurrentIndex(myapp.ui.comboBox_SmoothWidth.findText('2.0'))
    myapp.ui.comboBox_BarAnchoringLength.addItems(['35', '40', '45', '50'])
    myapp.ui.comboBox_BarAnchoringLength.setCurrentIndex(myapp.ui.comboBox_BarAnchoringLength.findText('40'))
    #---
    ui_loadtodate ()
    ui_loadfromdate ()
    #----
    myapp.show()
    sys.exit(app.exec_())