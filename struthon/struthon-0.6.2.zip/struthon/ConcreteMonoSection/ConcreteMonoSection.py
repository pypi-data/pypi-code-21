'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1.2 date 2015-12-15
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
File version 0.1.1 changes:
- ui_loadtodate (), setLoadCaseItem () functions revised
- no feature change in 0.1.1 version
File version 0.1.2 changes:
- ui functionality upgrated
- progress bar added
'''

import sys
import time

import strupy.units as u
u.xvalueformat("%5.2f")

from strupy.concrete.RcRecSect import RcRecSect
from strupy.concrete.RcRecSectSolver import RcRecSectSolver
from strupy.concrete.SectLoad import SectLoad
from strupy.concrete.rcsteel_area import *
from strupy.x_graphic.PyqtSceneCreator2D import PyqtSceneCreator2D

from PyQt4 import QtCore, QtGui

from mainwindow_ui import Ui_MainWindow

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # QT events
        self.ui.pushButton_apllytosec.clicked.connect(self.apllytosec)
        #---------
        self.ui.pushButton_reinforce.clicked.connect(self.reinforcecurrent)
        #---------
        self.ui.pushButton_momentresist.clicked.connect(self.momentresist)
        self.ui.pushButton_forceresist.clicked.connect(self.forceresist)
        self.ui.pushButton_momentforceresist.clicked.connect(self.momentforceresist)
        self.ui.pushButton_Asforcefunction.clicked.connect(self.pushButton_Asforcefunction)
        self.ui.pushButton_Asmomentfunction.clicked.connect(self.pushButton_Asmomentfunction)
        self.ui.pushButton_Asforcemomentfunction.clicked.connect(self.pushButton_Asforcemomentfunction)
        #---------
        self.ui.pushButton_setAndn_nd.clicked.connect(self.pushButton_setAndn_nd)
        self.ui.pushButton_setAndn_ns.clicked.connect(self.pushButton_setAndn_ns)
        #---------
        self.ui.pushButton_setApdp_nd.clicked.connect(self.pushButton_setApdp_nd)
        self.ui.pushButton_setApdp_ns.clicked.connect(self.pushButton_setApdp_ns)
        #---------
        self.ui.pushButton_loadAllON.clicked.connect(self.pushButton_loadAllON)
        self.ui.pushButton_loadAllOFF.clicked.connect(self.pushButton_loadAllOFF)
        self.ui.pushButton_loadAddCase.clicked.connect(self.pushButton_loadAddCase)
        self.ui.pushButton_loadEditSelected.clicked.connect(self.pushButton_loadEditSelected)
        self.ui.pushButton_loadDelAll.clicked.connect(self.pushButton_loadDelAll)
        self.ui.pushButton_loadDelSelected.clicked.connect(self.pushButton_loadDelSelected)
        self.ui.pushButton_loadSeletedON.clicked.connect(self.pushButton_loadSeletedON)
        self.ui.pushButton_loadSeletedOFF.clicked.connect(self.pushButton_loadSeletedOFF)
        #---------
        self.ui.listWidget_loadcases.clicked.connect(self.loadcases_setLoadCaseItem)
        #---------
        self.ui.pushButton_zoom_in.clicked.connect(self.pushButton_zoom_in)
        self.ui.pushButton_zoom_out.clicked.connect(self.pushButton_zoom_out)

    def loadcases_setLoadCaseItem(self):
        setLoadCaseItem ()
  
    def apllytosec(self):
        ui_loadfromdate ()
        ui_loadtodate ()

    def apllytoload(self):
        ui_loadfromdate ()
        ui_loadtodate ()
        
    def reinforcecurrent(self):
        self.apllytosec()
        self.apllytoload()
        reinforce ()
        ui_loadtodate ()

    def momentresist(self):
        self.apllytosec()
        self.apllytoload()
        ui_momentresist ()
        
    def forceresist(self):
        self.apllytosec()
        self.apllytoload()
        ui_forceresist ()
        
    def momentforceresist(self):
        self.apllytosec()
        self.apllytoload()
        ui_momentforceresist ()
        
    def pushButton_Asforcefunction(self):
        self.apllytosec()
        self.apllytoload()
        ui_Asforcefunction ()
        
    def pushButton_Asmomentfunction(self):
        self.apllytosec()
        self.apllytoload()
        ui_Asmomentfunction ()
        
    def pushButton_Asforcemomentfunction(self):
        self.apllytosec()
        self.apllytoload()
        ui_Asforcemomentfunction ()
        
    def pushButton_setAndn_nd(self):
        ui_setAd ('n', 1)
        
    def pushButton_setAndn_ns(self):
        ui_setAd ('n', 2)
        
    def pushButton_setApdp_nd(self):
        ui_setAd ('p', 1)
        
    def pushButton_setApdp_ns(self):
        ui_setAd ('p', 2)

    def pushButton_loadAllON(self):
        load.caseactiv_all()
        ui_loadtodate ()
        
    def pushButton_loadAllOFF(self):
        load.caseactiv_any()
        ui_loadtodate ()

    def pushButton_loadAddCase(self):
        ui_loadfromdate ('Add')
        ui_loadtodate ()
        
    def pushButton_loadEditSelected(self):
        ui_loadfromdate ('Edit')
        ui_loadtodate ()

    def pushButton_loadDelAll(self):
        load.clear_loadcase()
        ui_loadtodate ()
        
    def pushButton_loadDelSelected(self):
        load.delete_loadcase(loadcaseItemSelected)
        ui_loadtodate ()     
        
    def pushButton_loadSeletedON(self):
        load.caseactiv_oncase(loadcaseItemSelected)
        ui_loadtodate ()
        
    def pushButton_loadSeletedOFF(self):
        load.caseactiv_offcase(loadcaseItemSelected)
        ui_loadtodate ()
        
    def pushButton_zoom_in(self):
        viev_unit_change(-0.5*u.mm)
        ui_loadtodate ()

    def pushButton_zoom_out(self):
        viev_unit_change(+0.5*u.mm)
        ui_loadtodate ()

def ui_loadtodate ():
    #section properties
    myapp.ui.lineEdit_b.setText(str((sec.b/u.mm).asNumber()))
    myapp.ui.lineEdit_h.setText(str((sec.h/u.mm).asNumber()))
    #---------
    myapp.ui.lineEdit_an.setText(str((sec.an/u.mm).asNumber()))
    myapp.ui.lineEdit_ap.setText(str((sec.ap/u.mm).asNumber()))
    #---------
    myapp.ui.lineEdit_An.setText(str(round((sec.An/u.cm2).asNumber(),1)))
    myapp.ui.lineEdit_Ap.setText(str(round((sec.Ap/u.cm2).asNumber(),1)))
    #---------
    myapp.ui.comboBox_dn.setCurrentIndex(myapp.ui.comboBox_dn.findText(str(round((sec.fin/u.mm).asNumber(), 1))))
    myapp.ui.comboBox_dp.setCurrentIndex(myapp.ui.comboBox_dp.findText(str(round((sec.fip/u.mm).asNumber(), 1))))
    #---------
    myapp.ui.comboBox_cracklimn.setCurrentIndex(myapp.ui.comboBox_cracklimn.findText(str(round((sec.wlimn/u.mm).asNumber(), 1))))
    if sec.rysAn == 0:
        myapp.ui.comboBox_cracklimn.setCurrentIndex(myapp.ui.comboBox_cracklimn.findText('any'))
    myapp.ui.comboBox_cracklimp.setCurrentIndex(myapp.ui.comboBox_cracklimp.findText(str(round((sec.wlimp/u.mm).asNumber(), 1))))
    if sec.rysAp == 0:
        myapp.ui.comboBox_cracklimp.setCurrentIndex(myapp.ui.comboBox_cracklimp.findText('any'))
    #---------
    myapp.ui.comboBox__concreteclass.setCurrentIndex(myapp.ui.comboBox__concreteclass.findText(sec.concretename))
    myapp.ui.comboBox_steelclass.setCurrentIndex(myapp.ui.comboBox_steelclass.findText(sec.rcsteelname))
    #section properties
    myapp.ui.textBrowser_sectprop.clear()
    myapp.ui.textBrowser_sectprop.append(sectpreptext())
    #section drawing
    ui_drawingsection ()
    #loadcases list
    myapp.ui.listWidget_loadcases.clear()
    myapp.ui.listWidget_loadcases.addItems (secloadcasaslist())   
    
def ui_loadfromdate (loadcase=0):
    global sec, range_Mmin, range_Mmax, range_Nmin, range_Nmax
    #section properties
    sec.b = float((myapp.ui.lineEdit_b.text()))*u.mm
    sec.h = float((myapp.ui.lineEdit_h.text()))*u.mm
    #---------
    sec.an = float((myapp.ui.lineEdit_an.text()))*u.mm
    sec.ap = float((myapp.ui.lineEdit_ap.text()))*u.mm
    #---------
    sec.An = float((myapp.ui.lineEdit_An.text()))*u.cm2
    sec.Ap = float((myapp.ui.lineEdit_Ap.text()))*u.cm2
    #---------
    sec.fin = float((myapp.ui.comboBox_dn.currentText()))*u.mm
    sec.fip = float((myapp.ui.comboBox_dp.currentText()))*u.mm
    #---------
    if not myapp.ui.comboBox_cracklimn.currentText() == 'any':
        sec.wlimn = float((myapp.ui.comboBox_cracklimn.currentText()))*u.mm
        sec.rysAn = 1
    else:
        sec.rysAn = 0
    if not myapp.ui.comboBox_cracklimp.currentText() == 'any':
        sec.wlimp = float((myapp.ui.comboBox_cracklimp.currentText()))*u.mm
        sec.rysAp = 1
    else:
        sec.rysAp = 0
    #---------
    sec.set_concreteclass(myapp.ui.comboBox__concreteclass.currentText())
    sec.set_rcsteelclass(myapp.ui.comboBox_steelclass.currentText())
    #section loads
    if loadcase is not 0:
        Msd=float((myapp.ui.lineEdit_Msd.text()))*u.kNm
        MTsd=float((myapp.ui.lineEdit_Tsd.text()))*u.kNm
        Nsd=float((myapp.ui.lineEdit_Nsd.text()))*u.kN
        Vsd=float((myapp.ui.lineEdit_Vsd.text()))*u.kN
        if loadcase=='Add':
            load.add_loadcase({"Name": 'Noname', "Msd": Msd, "MTsd": MTsd, "Nsd": Nsd, "Vsd": Vsd})
        if loadcase=='Edit':
            load.edit_loadcase(loadcaseItemSelected, {"Name": 'Noname', "Msd": Msd, "MTsd": MTsd, "Nsd": Nsd, "Vsd": Vsd}) 
    #load range for plots
    range_Mmin=float((myapp.ui.lineEdit_Mmin.text()))*u.kNm
    range_Mmax=float((myapp.ui.lineEdit_Mmax.text()))*u.kNm
    range_Nmin=float((myapp.ui.lineEdit_Nmin.text()))*u.kN
    range_Nmax=float((myapp.ui.lineEdit_Nmax.text()))*u.kN
    
def sectpreptext():
    text=  'Section dimension: b=' + str(sec.b) + ' h='+str(sec.h) + '\n'
    text+= 'Materials: concrete - ' + sec.concretename + ' rcsteel - '+sec.rcsteelname + '\n'
    text+= 'Reinforcement area: An - ' + str(sec.An.asUnit(u.cm2)) + ' Ap - '+ str(sec.Ap.asUnit(u.cm2)) + '\n'
    text+= 'Reinforcement: an=' + str(sec.an) + ' ap='+str(sec.ap) + '\n'
    text+= '..................dn=' + str(sec.fin) + ' dp='+str(sec.fip) + '\n'
    text+= 'Crack control: crackcontroln=' + str(sec.rysAn) + ' crackcontrolp='+str(sec.rysAp) + '\n'
    text+= 'Crack limit: cracklimn=' + str(sec.wlimn) + ' cracklimp='+str(sec.wlimp) + '\n'
    return text
    
def sectloadtext():
    text=  'Section loads:' + '\n'
    text+= str(load.get_loadcases())
    return text
    
def setLoadCaseItem ():
    global loadcaseItemSelected
    loadcaseItemSelected=int (myapp.ui.listWidget_loadcases.currentItem().text()[0])
    myapp.ui.lineEdit_Msd.setText(str((load.Msd[loadcaseItemSelected]/u.kNm).asNumber()))
    myapp.ui.lineEdit_Nsd.setText(str((load.Nsd[loadcaseItemSelected]/u.kN).asNumber()))
    myapp.ui.lineEdit_Vsd.setText(str((load.Vsd[loadcaseItemSelected]/u.kN).asNumber()))
    myapp.ui.lineEdit_Tsd.setText(str((load.MTsd[loadcaseItemSelected]/u.kN).asNumber()))    

def reinforce():
    global sec
    solv.reinforce(sec,load)
    myapp.ui.textBrowser_solveresults.clear()
    text=  'Calculated:' + '\n'
    text+= 'Ap=' + str(sec.Ap.asUnit(u.cm2)) + '\n'
    text+= 'An=' + str(sec.An.asUnit(u.cm2)) + '\n'
    text+= str(sec.comment) + '\n'
    myapp.ui.textBrowser_solveresults.append(text)
    
def ui_momentresist ():
    global sec
    solv.resist_moment(sec)    
    myapp.ui.textBrowser_solveresults.clear()
    text=  'Calculated:' + '\n'
    text+= 'Mrdmax=' + str(sec.resist_moment['Mrdmax']) + '\n'
    text+= 'Mrdmin=' + str(sec.resist_moment['Mrdmin']) + '\n'
    text+= 'with Nsd=' + str(0*u.kN) + '\n'
    myapp.ui.textBrowser_solveresults.append(text)
    
def ui_forceresist ():
    global sec
    solv.resist_force(sec)    
    myapp.ui.textBrowser_solveresults.clear()
    text=  'Calculated:' + '\n'
    text+= 'Nrdmax=' + str(sec.resist_force['Nrdmax']) + '\n'
    text+= 'Nrdmin=' + str(sec.resist_force['Nrdmin']) + '\n'
    text+= 'with Msd=' + str(0*u.kNm) + '\n'
    myapp.ui.textBrowser_solveresults.append(text)
    
def ui_momentforceresist ():
    global sec
    solv.resist_forcetomoment(sec,32, myapp.ui.progressBar)
    sec.plot_resist_forcetomoment(load)
    
def ui_Asforcefunction ():
    global sec
    solv.As_as_forcefunction(sec,range_Nmin, range_Nmax, 60)
    sec.plot_As_as_forcefunction()
    
def ui_Asmomentfunction ():
    global sec
    solv.As_as_momentfunction(sec,range_Mmin, range_Mmax, 60)
    sec.plot_As_as_momentfunction()
    
def ui_Asforcemomentfunction ():
    global sec
    solv.As_as_forcetomomentfunction(sec,range_Nmin, range_Nmax, 20, range_Mmin, range_Mmax, 20, myapp.ui.progressBar)
    sec.plot_As_as_forcetomomentfunction()

def viev_unit_change(value=u.mm):
    sectionscene.change_unit(value)
    
def ui_drawingsection ():
    sectionscene.clearScene()
    sec.draw(sectionscene, 1)
    sectionscene.showgrid(50*u.mm, 1.3*sec.b/2, 1.3*sec.h/2)
    sectionscene.ShowOnGraphicsViewObiect()
    
def ui_setAd (side, mode):
    if side =='p':
        if mode == 1:
            tmp=ui_area_diameter_quantity(sec.Ap)
            myapp.ui.lineEdit_Ap.setText(str(round((tmp[0]/u.cm2).asNumber(),2)))
            myapp.ui.comboBox_dp.setCurrentIndex(myapp.ui.comboBox_dp.findText(str(round((tmp[1]/u.mm).asNumber(), 1))))
        if mode == 2:
            tmp=ui_area_diameter_spaceing_perdist(sec.Ap, sec.b)
            myapp.ui.lineEdit_Ap.setText(str(round((tmp[0]/u.cm2).asNumber(),2)))
            myapp.ui.comboBox_dp.setCurrentIndex(myapp.ui.comboBox_dp.findText(str(round((tmp[1]/u.mm).asNumber(), 1))))
    if side == 'n':
        if mode == 1:
            tmp=ui_area_diameter_quantity(sec.An)
            myapp.ui.lineEdit_An.setText(str(round((tmp[0]/u.cm2).asNumber(),2)))
            myapp.ui.comboBox_dn.setCurrentIndex(myapp.ui.comboBox_dn.findText(str(round((tmp[1]/u.mm).asNumber(), 1))))
        if mode == 2:
            tmp=ui_area_diameter_spaceing_perdist(sec.An, sec.b)
            myapp.ui.lineEdit_An.setText(str(round((tmp[0]/u.cm2).asNumber(),2)))
            myapp.ui.comboBox_dn.setCurrentIndex(myapp.ui.comboBox_dn.findText(str(round((tmp[1]/u.mm).asNumber(), 1))))

def secloadcasaslist ():
    u.xvalueformat("%9.2f")
    list=[]
    for i in xrange(len(load.Name)):
        list.append(str(i)+', '+str(load.Name[i])+','+str(load.Msd[i])+','+str(load.Nsd[i])+','+str(load.Vsd[i])+','+str(load.MTsd[i])+' , '+str(load.caseactiv[i]))
    u.xvalueformat("%5.2f")
    return list  

if __name__ == "__main__":
    sec=RcRecSect()
    load=SectLoad()
    solv=RcRecSectSolver()
    #----
    loadcaseItemSelected=0
    #----
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    #----
    sectionscene = PyqtSceneCreator2D()
    sectionscene.set_GraphicsViewObiect(myapp.ui.graphicsView)
    sectionscene.set_unit(0.5*u.cm)
    #----
    myapp.ui.comboBox_steelclass.addItems(sec.get_availablercsteelclass())
    myapp.ui.comboBox__concreteclass.addItems(sec.get_availableconcreteclass())
    myapp.ui.comboBox_dp.addItems([str(round((i/u.mm).asNumber(), 1)) for i in default_diameterlist])
    myapp.ui.comboBox_dn.addItems([str(round((i/u.mm).asNumber(), 1)) for i in default_diameterlist])
    myapp.ui.comboBox_cracklimp.addItems(['any', '0.4', '0.3', '0.2', '0.1'])
    myapp.ui.comboBox_cracklimn.addItems(['any', '0.4', '0.3', '0.2', '0.1'])
    #----
    ui_loadtodate ()
    #----
    myapp.show()
    sys.exit(app.exec_())