'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-03-06
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
File version 0.x changes:
- .....
'''

import sys
import time
import copy

from PyQt4 import QtCore, QtGui

import strupy.units as u
from strupy.steel.SteelSection import SteelSection
from strupy.steel.SteelSectionSolver import SteelSectionSolver
from strupy.steel.BoltConnection import BoltConnection
from strupy.x_graphic.PyqtSceneCreator2D import PyqtSceneCreator2D
try:
    from strupy.x_graphic.AutocadCreator2D import AutocadCreator2D
except:
    pass

from mainwindow_ui import Ui_MainWindow
import infotext

u.xvalueformat("%5.2f")

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #---Bolt area events
        self.ui.pushButton_BoltAddOne.clicked.connect \
        (lambda: dosyntax('Connection.bolts_add()'))
        #--
        self.ui.pushButton_BoltDeleteSelected.clicked.connect \
        (lambda: dosyntax('Connection.bolts_delete(BoltTable_get_selected_index())'))
        #--
        self.ui.pushButton_moveXp.clicked.connect \
        (lambda: dosyntax('Connection.bolts_move(BoltTable_get_selected_index(), [+1.0*u.mm, 0.0*u.mm])'))
        self.ui.pushButton_moveXn.clicked.connect \
        (lambda: dosyntax('Connection.bolts_move(BoltTable_get_selected_index(), [-1.0*u.mm, 0.0*u.mm])'))
        self.ui.pushButton_moveYp.clicked.connect \
        (lambda: dosyntax('Connection.bolts_move(BoltTable_get_selected_index(), [.0*u.mm, +1.0*u.mm])'))
        self.ui.pushButton_moveYn.clicked.connect \
        (lambda: dosyntax('Connection.bolts_move(BoltTable_get_selected_index(), [0.0*u.mm, -1.0*u.mm])'))
        #--
        self.ui.pushButton_projectionX.clicked.connect(lambda: ProjectionSelected('x'))
        self.ui.pushButton_projectionY.clicked.connect(lambda: ProjectionSelected('y'))
        self.ui.pushButton_copyX.clicked.connect(lambda: CopySelected([1.0, 0.0])) #!!!!!!!!!!!!!!
        self.ui.pushButton_copyY.clicked.connect(lambda: CopySelected([0.0, 1.0])) #!!!!!!!!!!!!!!
        self.ui.tableWidget_Bolts.clicked.connect(lambda: highlight_some_bolts(BoltTable_get_selected_index()))
        #---Plate area events
        self.ui.pushButton_xndim_n.clicked.connect(lambda: dosyntax('Connection.plate_xndim += -1.0*u.mm'))
        self.ui.pushButton_xndim_p.clicked.connect(lambda: dosyntax('Connection.plate_xndim += +1.0*u.mm'))
        self.ui.pushButton_xpdim_n.clicked.connect(lambda: dosyntax('Connection.plate_xpdim += -1.0*u.mm'))
        self.ui.pushButton_xpdim_p.clicked.connect(lambda: dosyntax('Connection.plate_xpdim += +1.0*u.mm'))
        self.ui.pushButton_yndim_n.clicked.connect(lambda: dosyntax('Connection.plate_yndim += -1.0*u.mm'))
        self.ui.pushButton_yndim_p.clicked.connect(lambda: dosyntax('Connection.plate_yndim += +1.0*u.mm'))
        self.ui.pushButton_ypdim_n.clicked.connect(lambda: dosyntax('Connection.plate_ypdim += -1.0*u.mm'))
        self.ui.pushButton_ypdim_p.clicked.connect(lambda: dosyntax('Connection.plate_ypdim += +1.0*u.mm'))
        self.ui.pushButton_xfin_n.clicked.connect(lambda: dosyntax('Connection.xfin += -1.0*u.mm'))
        self.ui.pushButton_xfin_p.clicked.connect(lambda: dosyntax('Connection.xfin += +1.0*u.mm'))
        self.ui.pushButton_xfip_n.clicked.connect(lambda: dosyntax('Connection.xfip += -1.0*u.mm'))
        self.ui.pushButton_xfip_p.clicked.connect(lambda: dosyntax('Connection.xfip += +1.0*u.mm'))
        self.ui.pushButton_yfin_n.clicked.connect(lambda: dosyntax('Connection.yfin += -1.0*u.mm'))
        self.ui.pushButton_yfin_p.clicked.connect(lambda: dosyntax('Connection.yfin += +1.0*u.mm'))
        self.ui.pushButton_yfip_n.clicked.connect(lambda: dosyntax('Connection.yfip += -1.0*u.mm'))
        self.ui.pushButton_yfip_p.clicked.connect(lambda: dosyntax('Connection.yfip += +1.0*u.mm'))
        #---Drawing area events
        self.ui.pushButton_zoom_in.clicked.connect(lambda: viev_unit_change(-0.1*u.mm))
        self.ui.pushButton_zoom_out.clicked.connect(lambda: viev_unit_change(+0.1*u.mm))
        self.ui.pushButton_zoom_in_force.clicked.connect(lambda: viev_unit_force_change(-0.1*u.kN))
        self.ui.pushButton_zoom_out_force.clicked.connect(lambda: viev_unit_force_change(+0.1*u.kN))
        self.ui.pushButton_zoom_in_moment.clicked.connect(lambda: viev_unit_moment_change(-0.01*u.kNm))
        self.ui.pushButton_zoom_out_moment.clicked.connect(lambda: viev_unit_moment_change(+0.01*u.kNm))
        #--
        self.ui.checkBox_showBoltForces.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showBoltCapacity.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showLoadO.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showLoadP.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showPlate.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showProfile.clicked.connect(lambda: ui_draw(board))
        #--
        self.ui.checkBox_showMinBoltSpace.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showMinSpaceToPlateEdge.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showMaxSpaceToProfilEdge.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showMinSocketSpanner.clicked.connect(lambda: ui_draw(board))
        self.ui.checkBox_showMinFlatSpanner.clicked.connect(lambda: ui_draw(board))
        #---ReloadApp button event
        self.ui.pushButton_Reload.clicked.connect(ReloadApp)
        #---MenuBar Help
        self.ui.actionAbout.triggered.connect(self.actionAbout)
        
    def actionAbout(self):
        QtGui.QMessageBox.information(None, 'Info', infotext.about)
        
#---Top UI functions
def ReloadApp(): #Reloading application
    ui_loadfromdate()
    Connection.calculate()
    ui_loadtodate ()
    
def ui_draw(board): #Crearing drawing function
    try:
        board.clearScene()
    except:
        pass
    board.set_origin()
    #---drawing Connection
    load_p = myapp.ui.checkBox_showLoadP.isChecked()
    load_o = myapp.ui.checkBox_showLoadO.isChecked()
    plate = myapp.ui.checkBox_showPlate.isChecked()
    bolt_forces = myapp.ui.checkBox_showBoltForces.isChecked()
    bolt_forces = myapp.ui.checkBox_showBoltForces.isChecked()
    bolt_capacity = myapp.ui.checkBox_showBoltCapacity.isChecked()
    Connection.draw(board, load_p=load_p, load_o=load_o, plate=plate, bolt_forces=bolt_forces, bolt_capacity=bolt_capacity)
    #---drawing minimal spaces for bolts
    min_bolt_space = myapp.ui.checkBox_showMinBoltSpace.isChecked()
    min_space_to_plate_edge = myapp.ui.checkBox_showMinSpaceToPlateEdge.isChecked()
    max_space_to_profil_edge = myapp.ui.checkBox_showMaxSpaceToProfilEdge.isChecked()
    min_socket_spanner = myapp.ui.checkBox_showMinSocketSpanner.isChecked()
    min_flat_spanner = myapp.ui.checkBox_showMinFlatSpanner.isChecked()
    Connection.draw_space_control(board, min_bolt_space, min_space_to_plate_edge, max_space_to_profil_edge, min_socket_spanner, min_flat_spanner)
    #---drawing profile
    if myapp.ui.checkBox_showProfile.isChecked():
        board.set_origin()
        Profile.draw_contour(board)
    #---
    try:
        board.ShowOnGraphicsViewObiect()
    except:
        pass

def ui_loadtodate(): #Displaying data on UI functions
    #--Bolt area
    myapp.ui.comboBox_BoltGrade.setCurrentIndex(myapp.ui.comboBox_BoltGrade.findText(Connection.boltclipi[0].Grade))
    myapp.ui.comboBox_BoltDim.setCurrentIndex(myapp.ui.comboBox_BoltDim.findText(Connection.boltclipi[0].Dim))
    BoltTable_pushdata()
    #--Plate area
    myapp.ui.comboBox_PlateGrad.setCurrentIndex(myapp.ui.comboBox_PlateGrad.findText(Connection.boltclipi[0].plate_SteelGrade))
    thickness1_string = str(int(Connection.boltclipi[0].t1.asUnit(u.mm).asNumber()))
    myapp.ui.comboBox_PlateThickness1.setCurrentIndex(myapp.ui.comboBox_PlateThickness1.findText(thickness1_string))
    thickness2_string = str(int(Connection.boltclipi[0].t2.asUnit(u.mm).asNumber()))
    myapp.ui.comboBox_PlateThickness2.setCurrentIndex(myapp.ui.comboBox_PlateThickness2.findText(thickness2_string))
    m_string = str(int(Connection.boltclipi[0].m))
    myapp.ui.comboBox_Plate_m.setCurrentIndex(myapp.ui.comboBox_Plate_m.findText(m_string))
    mi_string = '%2.2f'%round(Connection.boltclipi[0].mi,2)
    myapp.ui.comboBox_Plate_mi.setCurrentIndex(myapp.ui.comboBox_Plate_mi.findText(mi_string))
    #--
    myapp.ui.lineEdit_plate_xndim.setText(str(round(Connection.plate_xndim.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_plate_xpdim.setText(str(round(Connection.plate_xpdim.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_plate_yndim.setText(str(round(Connection.plate_yndim.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_plate_ypdim.setText(str(round(Connection.plate_ypdim.asUnit(u.mm).asNumber(), 2)))
    #---
    myapp.ui.lineEdit_xfin.setText(str(round(Connection.xfin.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_xfip.setText(str(round(Connection.xfip.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_yfin.setText(str(round(Connection.yfin.asUnit(u.mm).asNumber(), 2)))
    myapp.ui.lineEdit_yfip.setText(str(round(Connection.yfip.asUnit(u.mm).asNumber(), 2)))
    #--Profil area
    myapp.ui.comboBox_Profile.setCurrentIndex(myapp.ui.comboBox_Profile.findText(Profile.sectname))
    #--Load area
    myapp.ui.lineEdit_Fx.setText(str(round(Connection.Fx.asUnit(u.kN).asNumber(), 2)))
    myapp.ui.lineEdit_Fy.setText(str(round(Connection.Fy.asUnit(u.kN).asNumber(), 2)))
    myapp.ui.lineEdit_Fz.setText(str(round(Connection.Fz.asUnit(u.kN).asNumber(), 2)))
    myapp.ui.lineEdit_Mx.setText(str(round(Connection.Mx.asUnit(u.kNm).asNumber(), 2)))
    myapp.ui.lineEdit_My.setText(str(round(Connection.My.asUnit(u.kNm).asNumber(), 2)))
    myapp.ui.lineEdit_Mz.setText(str(round(Connection.Mz.asUnit(u.kNm).asNumber(), 2)))
    #---
    myapp.ui.lineEdit_Fx.setEnabled(Connection.is_loadvector_active_for_category('Fx'))
    myapp.ui.lineEdit_Fy.setEnabled(Connection.is_loadvector_active_for_category('Fy'))
    myapp.ui.lineEdit_Fz.setEnabled(Connection.is_loadvector_active_for_category('Fz'))
    myapp.ui.lineEdit_Mx.setEnabled(Connection.is_loadvector_active_for_category('Mx'))
    myapp.ui.lineEdit_My.setEnabled(Connection.is_loadvector_active_for_category('My'))
    myapp.ui.lineEdit_Mz.setEnabled(Connection.is_loadvector_active_for_category('Mz'))
    #--section drawing
    ui_draw(board)
    #--Drawing info
    myapp.ui.label_DrawInfo.clear()
    myapp.ui.label_DrawInfo.setText(draw_info_text())
    #--Creating repport
    myapp.ui.textBrowser_Report.clear()
    myapp.ui.textBrowser_Report.setText(report_text())

def ui_loadfromdate(): #Geting data data from UI function
    global Connection
    global Profile
    #Bolt area
    Connection.set_BoltGrade(myapp.ui.comboBox_BoltGrade.currentText())
    Connection.set_BoltDim(myapp.ui.comboBox_BoltDim.currentText())
    BoltTable_pulldata()
    #--Plate area
    Connection.set_PlateGrade(myapp.ui.comboBox_PlateGrad.currentText())
    Connection.set_t1(float(myapp.ui.comboBox_PlateThickness1.currentText())*u.mm)
    Connection.set_t2(float(myapp.ui.comboBox_PlateThickness2.currentText())*u.mm)
    Connection.set_m(float(myapp.ui.comboBox_Plate_m.currentText()))
    Connection.set_mi(float(myapp.ui.comboBox_Plate_mi.currentText()))
    #---
    Connection.plate_xndim = float(myapp.ui.lineEdit_plate_xndim.text())*u.mm
    Connection.plate_xpdim = float(myapp.ui.lineEdit_plate_xpdim.text())*u.mm
    Connection.plate_yndim = float(myapp.ui.lineEdit_plate_yndim.text())*u.mm
    Connection.plate_ypdim = float(myapp.ui.lineEdit_plate_ypdim.text())*u.mm
    #---
    if myapp.ui.radioButton_RotateAsPlate.isChecked():
        Connection.xfin = Connection.plate_xndim
        Connection.xfip = Connection.plate_xpdim
        Connection.yfin = Connection.plate_ypdim
        Connection.yfip = Connection.plate_yndim
    else:
        Connection.xfin = float(myapp.ui.lineEdit_xfin.text())*u.mm
        Connection.xfip = float(myapp.ui.lineEdit_xfip.text())*u.mm
        Connection.yfin = float(myapp.ui.lineEdit_yfin.text())*u.mm
        Connection.yfip = float(myapp.ui.lineEdit_yfip.text())*u.mm
    #--Profil area
    Profile.set_sectionfrombase(str(myapp.ui.comboBox_Profile.currentText()))
    #--Loads area
    Connection.Fx = float(myapp.ui.lineEdit_Fx.text())*u.kN
    Connection.Fy = float(myapp.ui.lineEdit_Fy.text())*u.kN
    Connection.Fz = float(myapp.ui.lineEdit_Fz.text())*u.kN
    Connection.Mx = float(myapp.ui.lineEdit_Mx.text())*u.kNm
    Connection.My = float(myapp.ui.lineEdit_My.text())*u.kNm
    Connection.Mz = float(myapp.ui.lineEdit_Mz.text())*u.kNm
    Connection.set_category(myapp.ui.comboBox_Category.currentText())
    #--section drawing
    ui_draw(board)
    
def dosyntax(syntax): #Function used as slot for sending simple action
    exec(syntax)
    Connection.calculate()
    ui_loadtodate()
    ReloadApp()

#---Managing functions for tableWidget_Bolts in Bolt UI area
def BoltTable_get_selected_index():
    selected = []
    for i in myapp.ui.tableWidget_Bolts.selectedIndexes():
        selected.append(i.row())
    selected = list(set(selected))
    return selected
    
def BoltTable_pushdata():
        current_selected_rows = BoltTable_get_selected_index()
        #----deleting existing table
        for i in reversed(range(myapp.ui.tableWidget_Bolts.rowCount())):
            myapp.ui.tableWidget_Bolts.removeRow(i)
        #----creating  table   
        for i in range(len(Connection.xi)):
            myapp.ui.tableWidget_Bolts.insertRow(i)
            myapp.ui.tableWidget_Bolts.setItem(i, 0, QtGui.QTableWidgetItem())
            myapp.ui.tableWidget_Bolts.item(i, 0).setText(str(Connection.xi[i].asUnit(u.mm).asNumber()))
            myapp.ui.tableWidget_Bolts.setItem(i, 1, QtGui.QTableWidgetItem())
            myapp.ui.tableWidget_Bolts.item(i, 1).setText(str(Connection.yi[i].asUnit(u.mm).asNumber()))
        #_--
        myapp.ui.tableWidget_Bolts.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        for i in current_selected_rows:
            myapp.ui.tableWidget_Bolts.selectRow(i)
        myapp.ui.tableWidget_Bolts.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

def BoltTable_pulldata():
        for i in range(len(Connection.xi)):
            try:
                Connection.xi[i] = float(myapp.ui.tableWidget_Bolts.item(i, 0).text()) * u.mm
                Connection.yi[i] = float(myapp.ui.tableWidget_Bolts.item(i, 1).text()) * u.mm
            except:
                pass

#---Some function for making opration with Connection object
def ProjectionSelected(direction='x'):
    #---
    title = 'Set new coordinate'
    label = '%s[mm] = '%direction
    text = '0.00'
    try:
        coord_value = QtGui.QInputDialog.getText(None, title, label, text = text)[0]
        coord_value = float(coord_value) * u.mm
    except:
        print 'wrong format'
        return 0
    #---
    selection_list = BoltTable_get_selected_index()
    #---
    if direction == 'x':
        Connection.bolts_projection_x(selection_list, coord_value)
    if direction == 'y':
        Connection.bolts_projection_y(selection_list, coord_value)
    Connection.calculate()
    ui_loadtodate()

def CopySelected(direction=[1.0, 0.0]):
    selection_list = BoltTable_get_selected_index()
    #---
    title = 'Set deplacement '
    label = '%s[mm] x = '%direction
    text = '0.00'
    try:
        deplacement_value = QtGui.QInputDialog.getText(None, title, label, text = text)[0]
        deplacement_value = float(deplacement_value) * u.mm
    except:
        print 'wrong format'
        return 0
    #---
    selection_list = BoltTable_get_selected_index()
    #---
    vector = [direction[0] * deplacement_value, direction[1] * deplacement_value]
    Connection.bolts_copy(selection_list, vector)   
    Connection.calculate()
    ui_loadtodate()

#---Visual effects for drawing UI area 
def viev_unit_change(value=u.mm):
    board.change_unit(value)
    ui_loadtodate()

def viev_unit_force_change(value=u.kN):
    board.change_unit_force(value)
    ui_loadtodate()

def viev_unit_moment_change(value=u.kNm):
    board.change_unit_moment(value)
    ui_loadtodate()

def highlight_some_bolts(boltindex = [0,1]):
    ui_draw(board)
    board.set_origin()
    for i in boltindex:
        boltpoint = [Connection.xi[i], Connection.yi[i]]
        board.addCircle(boltpoint, 30*u.mm, 'blue')
    board.ShowOnGraphicsViewObiect()

#---Report text
def report_text():
    text = 'Connection category: %s \n' %Connection.category
    text += draw_info_text()
    text += '\n---------------\n'
    for i in range(len(Connection.xi)):
        text += 'Bolt %s ' % (i+1)
        if Connection.capacity_local_value[i] > 1:
            text += '(%s)<<<<<<<<<<<<<<<!!!Failure!!!!' % Connection.capacity_local_value[i]
        else:
            text += '(%s)' % Connection.capacity_local_value[i]
        text += '\n' + Connection.boltclipi[i].report + '\n'
        text += 'Warunki nosnosci:\n'
        text += Connection.capacity_local_comment[i]
        text += '\n---------------\n'
    return text

def draw_info_text():
    max_capacity = round(max(Connection.capacity_local_value).asNumber(), 2)
    if Connection.capacity_global:
        return 'OK (%s)' %max_capacity
    else:
        return '!!! Failure !!! (%s)' %max_capacity

def draw_in_Acad():
    try:
        acad_board = AutocadCreator2D()
        acad_board.unit = 1*u.mm
        ui_draw(acad_board)
    except:
        QtGui.QMessageBox.information(None, 'Some problem..', 'AutoCad not respond')
    
if __name__ == "__main__":
    #---
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    #---
    Connection = BoltConnection()
    Connection.set_category('A')
    #---
    Profile = SteelSection()
    Profile.set_sectionfrombase('IPE 120')
    Profile.solver = SteelSectionSolver()
    #---
    board = PyqtSceneCreator2D()
    board.set_GraphicsViewObiect(myapp.ui.graphicsView)
    board.set_unit(0.04*u.cm)
    #---
    myapp.setWindowTitle(infotext.appname + ' ' + infotext.version)
    #---
    myapp.ui.comboBox_BoltDim.addItems(Connection.boltclipi[0].get_AvailableBoltDim())
    myapp.ui.comboBox_BoltGrade.addItems(Connection.boltclipi[0].get_AvailableBoltGrade())
    myapp.ui.comboBox_PlateThickness1.addItems(['5','6', '7', '8', '10', '12', '14', '16', '18', '20', '25', '30', '35', '40'])
    myapp.ui.comboBox_PlateThickness2.addItems(['5','6', '7', '8', '10', '12', '14', '16', '18', '20', '25', '30', '35', '40'])
    myapp.ui.comboBox_Plate_m.addItems(['1', '2', '3', '4', '5'])
    myapp.ui.comboBox_Plate_mi.addItems(['0.10', '0.20', '0.30', '0.40', '0.50'])
    myapp.ui.comboBox_PlateGrad.addItems(Profile.get_availablesteelgrade())
    myapp.ui.comboBox_Profile.addItems(Profile._SteelSection__base.get_database_sectionlist())
    myapp.ui.comboBox_Category.addItems(Connection.availale_categories)
    #---
    ui_loadtodate()
    ReloadApp()
    #---
    myapp.show()
    sys.exit(app.exec_())
    