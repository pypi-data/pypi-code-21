'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-03-06
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
from mainwindow_ui import Ui_MainWindow

import strupy.units as u
u.xvalueformat("%5.2f")
from strupy.steel.SteelSection import SteelSection
from strupy.steel. SteelSectionSolver import SteelSectionSolver
from strupy.steel.SteelSectionLoad import SteelSectionLoad
from strupy.x_graphic.PyqtSceneCreator2D import PyqtSceneCreator2D

appname = 'StruthonSteelMonoSection'
version = '0.1.1 (alpha)'

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # QT events
        self.ui.pushButton_apllytosec.clicked.connect(self.pushButton_apllytosec)
        self.ui.pushButton_BrowseSection.clicked.connect(self.pushButton_BrowseSection)
        #---------
        self.ui.pushButton_CheckSection.clicked.connect(self.pushButton_CheckSection)
        self.ui.pushButton_Resistance.clicked.connect(self.pushButton_Resistance)
        self.ui.pushButton_FindSections.clicked.connect(self.pushButton_FindSections)
        self.ui.listWidget_typelist.clicked.connect(self.typeselected)
        self.ui.listWidget_sectnamelist.clicked.connect(self.sectnameselected)
        self.ui.pushButton_ApllySelected.clicked.connect(self.pushButton_ApllySelected)
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
    
    def pushButton_apllytosec(self):
        ui_loadfromdate ()
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_BrowseSection(self):
        ui_loadfromdate ()
        BrowseSection()
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_CheckSection(self):
        HideSectionBrowserList()
        ui_loadfromdate ()
        CheckSection()
        ui_loadtodate()

    def pushButton_Resistance(self):
        HideSectionBrowserList()
        ui_loadfromdate ()
        Resistance()
        ui_loadtodate()
        
    def pushButton_FindSections(self):
        HideSectionBrowserList()
        ui_loadfromdate ()
        FindSections()
        ui_loadtodate()
    
    def typeselected(self):
        ui_typeselected()

    def sectnameselected(self):
        ui_sectnameselected()
        
    def pushButton_ApllySelected(self):
        secnameselected=self.ui.listWidget_sectnamelist.currentItem().text()
        self.ui.lineEdit_SectionFigure.setText(secnameselected)
        ui_loadfromdate ()
        ui_loadtodate ()
        self.pushButton_CheckSection()
        HideSectionBrowserList()
        HideSectionBrowserList()

    def pushButton_loadAllON(self):
        load.caseactiv_all()
        ui_loadtodate()
        HideSectionBrowserList()
        
    def pushButton_loadAllOFF(self):
        load.caseactiv_any()
        ui_loadtodate ()
        HideSectionBrowserList()

    def pushButton_loadAddCase(self):
        ui_loadfromdate ('Add')
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_loadEditSelected(self):
        ui_loadfromdate ('Edit')
        ui_loadtodate ()
        HideSectionBrowserList()

    def pushButton_loadDelAll(self):
        load.clear_loadcase()
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_loadDelSelected(self):
        load.delete_loadcase(loadcaseItemSelected)
        ui_loadtodate () 
        HideSectionBrowserList()    
        
    def pushButton_loadSeletedON(self):
        load.caseactiv_oncase(loadcaseItemSelected)
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_loadSeletedOFF(self):
        load.caseactiv_offcase(loadcaseItemSelected)
        ui_loadtodate ()
        HideSectionBrowserList()
        
    def pushButton_zoom_in(self):
        viev_unit_change(-0.5*u.mm)
        ui_loadtodate ()

    def pushButton_zoom_out(self):
        viev_unit_change(+0.5*u.mm)
        ui_loadtodate ()

def ui_loadtodate ():
    #section properties
    myapp.ui.lineEdit_SectionFigure.setText(sec.sectname)
    myapp.ui.comboBox_SteelGrade.setCurrentIndex(myapp.ui.comboBox_SteelGrade.findText(sec.steelgrade))
    #section properties
    myapp.ui.textBrowser_SectionProperties.clear()
    myapp.ui.textBrowser_SectionProperties.append(sectpreptext())
    #section drawing
    ui_drawingsection()
    #loadcases list
    myapp.ui.listWidget_loadcases.clear()
    myapp.ui.listWidget_loadcases.addItems (secloadcasaslist())   
    
def ui_loadfromdate (loadcase=0):
    global sec
    #section properties
    sec.set_sectionfrombase(str(myapp.ui.lineEdit_SectionFigure.text()))
    sec.set_steelgrade(myapp.ui.comboBox_SteelGrade.currentText())
    #section loads
    if loadcase is not 0:
        Name=str(myapp.ui.lineEdit_Name.text())
        N_Ed=float((myapp.ui.lineEdit_N_Ed.text()))*u.kN
        M_yEd=float((myapp.ui.lineEdit_M_yEd.text()))*u.kNm
        M_zEd=float((myapp.ui.lineEdit_M_zEd.text()))*u.kNm
        V_yEd=float((myapp.ui.lineEdit_V_yEd.text()))*u.kN
        V_zEd=float((myapp.ui.lineEdit_V_zEd.text()))*u.kN
        T_Ed=float((myapp.ui.lineEdit_T_Ed.text()))*u.kNm
        if loadcase=='Add':
            load.add_loadcase({"Name": Name, "N_Ed": N_Ed, "M_yEd": M_yEd, "M_zEd": M_zEd, "V_yEd": V_yEd, "V_zEd": V_zEd, "T_Ed": T_Ed})
        if loadcase=='Edit':
            load.edit_loadcase(loadcaseItemSelected, {"Name": Name, "N_Ed": N_Ed, "M_yEd": M_yEd, "M_zEd": M_zEd, "V_yEd": V_yEd, "V_zEd": V_zEd, "T_Ed": T_Ed})

def sectpreptext():
    text =  'Section name: ' + str(sec.sectname) + '\n'
    text += 'Section dimension: b=' + str(sec.b) + ' h='+str(sec.h) + '\n'
    text += 'Materials: steel - ' + sec.steelgrade + '  fy=' + str(sec.f_y)  + '\n'
    return text
    
def setLoadCaseItem ():
    global loadcaseItemSelected
    loadcaseItemSelected=int(myapp.ui.listWidget_loadcases.currentItem().text()[0])
    myapp.ui.lineEdit_Name.setText(load.Name[loadcaseItemSelected])
    myapp.ui.lineEdit_N_Ed.setText(str((load.N_Ed[loadcaseItemSelected]/u.kN).asNumber()))
    myapp.ui.lineEdit_M_yEd.setText(str((load.M_yEd[loadcaseItemSelected]/u.kNm).asNumber()))
    myapp.ui.lineEdit_M_zEd.setText(str((load.M_zEd[loadcaseItemSelected]/u.kNm).asNumber()))
    myapp.ui.lineEdit_V_yEd.setText(str((load.V_yEd[loadcaseItemSelected]/u.kN).asNumber()))
    myapp.ui.lineEdit_V_zEd.setText(str((load.V_zEd[loadcaseItemSelected]/u.kN).asNumber()))
    myapp.ui.lineEdit_T_Ed.setText(str((load.T_Ed[loadcaseItemSelected]/u.kN).asNumber()))    

def CheckSection():
    global sec
    result = solv.check_section_for_load(sec, load)
    myapp.ui.textBrowser_Results.clear()
    myapp.ui.textBrowser_Results.append(CheckSectionText(result))

def CheckSectionText(result):
    def true_false_text(i):
        if i==True:
            return 'correct'
        if i==False:
            return 'failure !!!!!!'
        
    text=  '>>>>>>> Section is ' + true_false_text(result[0]) + ' <<<<<<<' + '\n'
    for i in range(len(result[1])):
        text += '------------------------loadcase no. ' + str(result[1][i]) + '  ' +load.Name[result[1][i]] + ' -> ' +  true_false_text(result[2][i]) + '\n' + str(result[3][i] + '\n')
    return text
    
def Resistance():
    #global sec
    #solv.calculate_resistance(sec)
    myapp.ui.textBrowser_Results.clear()
    myapp.ui.textBrowser_Results.append(ResistanceText())

def ResistanceText():
    text= '>>>>>>> \n'
    text += 'N_tRd = %s \n' %(sec.N_tRd)
    text += 'N_cRd = %s (class %s)\n ' %(sec.N_cRd, sec.class_comp)
    text += 'M_ycRd = %s (class %s)\n' %(sec.M_ycRd, sec.class_bend_y)
    text += 'M_zcRd = %s (class %s)\n' %(sec.M_zcRd, sec.class_bend_z)
    text += 'V_zcRd = %s \n' %(sec.V_zcRd)
    text += 'V_ycRd = %s \n' %(sec.V_ycRd)
    return text
    
def BrowseSection():
    figure = sec._SteelSection__base.ui_get_sectionparameters()['sectionname']
    sec.set_sectionfrombase(figure)

def FindSections():
    global sectionlist
    global tmpsec
    global tmpload
    global isfrom
    global isto
    global sectiongrouptocalculate
    isfrom_inComboBox = float(myapp.ui.comboBox_Find_from.currentText())
    isto_inComboBox = float(myapp.ui.comboBox_Find_to.currentText())
    if not (tmpsec.steelgrade == sec.steelgrade) & (tmpload.get_loadcases() == load.get_loadcases()) & (isfrom_inComboBox==isfrom) & (isto_inComboBox==isto) & (sectiongrouptocalculate == str(myapp.ui.comboBox_sectiongroups.currentText())):
        ClearFoundSectionList()
        tmpsec = copy.deepcopy(sec)
        tmpload = copy.deepcopy(load)
        #-------
        isfrom = isfrom_inComboBox
        isto = isto_inComboBox
        sectiongrouptocalculate = str(myapp.ui.comboBox_sectiongroups.currentText())
        #-------
        progress=0
        number_of_secion=len(sec._SteelSection__base.get_database_sectionlist())
        #-------
        for i in sec._SteelSection__base.get_database_sectionlist():
            figure = sec._SteelSection__base.get_sectionparameters(i)['figure']
            if sec._SteelSection__base.get_figuregroupname(figure) == sectiongrouptocalculate or sectiongrouptocalculate == 'All' : 
                tmpsec.set_sectionfrombase(i)
                result = solv.check_section_for_load(tmpsec, tmpload)
                if result [0]:
                    if isfrom <= max(result[4]) <= isto :
                        sectionlist.append(i)
            progress += 1
            myapp.ui.progressBar_FindSections.setValue(100 * progress/number_of_secion)
        myapp.ui.progressBar_FindSections.setValue(0)
    ui_reloadlists()

def ui_reloadlists():
    global typelist
    global sectionlist
    sectionlist=sorted(list(set(sectionlist))) 
    typesinsomeseclist=[sec._SteelSection__base.get_sectionparameters(i)['figure'] for i in sectionlist]    
    typelist=sorted(list(set(typesinsomeseclist)))
    myapp.ui.listWidget_sectnamelist.clear()
    myapp.ui.listWidget_sectnamelist.addItems(sectionlist)
    myapp.ui.listWidget_typelist.clear()
    myapp.ui.listWidget_typelist.addItems(typelist)

def ui_typeselected():
    selectedtype = myapp.ui.listWidget_typelist.currentItem().text()
    #--------
    myapp.ui.textBrowser_Results.clear()
    myapp.ui.listWidget_sectnamelist.clear()
    basename = sec._SteelSection__base.get_database_name()
    myapp.ui.textBrowser_Results.append(basename)
    selectedtype_description = sec._SteelSection__base.get_database_sectiontypesdescription()[str(selectedtype)]
    myapp.ui.textBrowser_Results.append(selectedtype_description)
    for i in sectionlist:
        if sec._SteelSection__base.get_sectionparameters(i)['figure']==selectedtype:
            myapp.ui.listWidget_sectnamelist.addItem(i)

def ui_sectnameselected():
    global tmpsec
    global tmpload
    selectedsectname = str (myapp.ui.listWidget_sectnamelist.currentItem().text())
    #----------
    myapp.ui.textBrowser_Results.clear()
    selectedtype = sec._SteelSection__base.get_sectionparameters(selectedsectname)['figure']
    basename = sec._SteelSection__base.get_database_name()
    myapp.ui.textBrowser_Results.append(basename)
    selectedtype_description = sec._SteelSection__base.get_database_sectiontypesdescription()[str(selectedtype)]
    myapp.ui.textBrowser_Results.append(selectedtype_description)
    myapp.ui.textBrowser_Results.append(selectedsectname + ' selected')
    #----------
    tmpsec = copy.deepcopy(sec)
    tmpsec.set_sectionfrombase(selectedsectname)
    #----------
    result = solv.check_section_for_load(tmpsec, tmpload)
    myapp.ui.textBrowser_Results.append(CheckSectionText(result))
    
def ClearFoundSectionList():
    global typelist
    global sectionlist
    typelist=[]
    sectionlist=[]
    HideSectionBrowserList()
    
def HideSectionBrowserList():
    myapp.ui.listWidget_sectnamelist.clear()
    myapp.ui.listWidget_typelist.clear()
    myapp.ui.textBrowser_Results.clear()

def ui_drawingsection ():
    sectionscene.clearScene()
    sec.draw_contour(sectionscene, sec.sectname)
    sectionscene.ShowOnGraphicsViewObiect()
    
def viev_unit_change(value=u.mm):
    sectionscene.change_unit(value)

def secloadcasaslist ():
    u.xvalueformat("%9.2f")
    list=[]
    for i in xrange(len(load.Name)):
        list.append(str(i) + ', ' + str(load.Name[i]) + ',' + str(load.N_Ed[i]) + ','+str(load.M_yEd[i]) + ',' + str(load.M_zEd[i]) + ',' + str(load.V_yEd[i]) + ' , ' + str(load.V_zEd[i]) + ',' + str(load.T_Ed[i]) + ',    ' + str(load.caseactiv[i]))
    u.xvalueformat("%5.2f")
    return list 

if __name__ == "__main__":
    sec = SteelSection()
    load = SteelSectionLoad()
    solv = SteelSectionSolver()
    loadcaseItemSelected=0
    #---
    sec.set_sectionbase_speedmode(1)
    #----
    tmpsec = SteelSection()
    tmpsec.steelgrade = None
    tmpload = SteelSectionLoad()
    tmpload.caseactiv_any()
    isfrom = None
    isto = None
    sectiongrouptocalculate = None
    typelist=[]
    sectionlist=[]
    #----
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    sectionscene = PyqtSceneCreator2D()
    sectionscene.set_GraphicsViewObiect(myapp.ui.graphicsView)
    sectionscene.set_unit(0.3*u.cm)
    myapp.ui.comboBox_SteelGrade.addItems(sec.get_availablesteelgrade())
    myapp.ui.comboBox_sectiongroups.addItems(['All'] + [sec._SteelSection__base.get_database_sectiongroups()[i] for i in sorted(sec._SteelSection__base.get_database_sectiongroups().keys())])
    #----
    sec.set_sectionfrombase()
    ui_loadtodate ()
    ui_loadfromdate ()
    #----
    myapp.setWindowTitle(appname + ' ' + version)
    myapp.ui.label_info_2.setText('struthon.org')
    #----
    myapp.show()
    sys.exit(app.exec_())