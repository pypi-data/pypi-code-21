'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-03-06

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
- section draw function upgraded
- shear resistance formula corrected in ui_find() and ui_loadparamas() 
- checkBox_PropertiesDescription() option in sectpreptext() added
- section family filter added 
'''

import sys
import time
import copy
from PyQt4 import QtCore, QtGui

from strupy.steel.SectionBase import SectionBase
from strupy.steel.MaterialSteel import MaterialSteel
from strupy.x_graphic.PyqtSceneCreator2D import PyqtSceneCreator2D

import strupy.units as u
u.xvalueformat("%5.2f")

from mainwindow_ui import Ui_MainWindow

appname = 'StruthonSteelSectionBrowser'
version = '0.2.1 (beta)'

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # QT events
        self.ui.listWidget_typelist.clicked.connect(self.typeselected)
        self.ui.listWidget_sectnamelist.clicked.connect(self.sectnameselected)
        self.ui.listWidget_sectnamelist.clicked.connect(self.sectnameselected)
        self.ui.pushButton_FIND.clicked.connect(self.find)
        self.ui.pushButton_loadsecnameaslected.clicked.connect(self.loadsecnameaslected)
        self.ui.pushButton_loadparamas.clicked.connect(self.loadparamas)
        #---------
        self.ui.pushButton_zoom_in.clicked.connect(self.pushButton_zoom_in)
        self.ui.pushButton_zoom_out.clicked.connect(self.pushButton_zoom_out)
        #----
        self.ui.comboBox_sectiongroups.currentIndexChanged.connect(self.change_comboBox_sectionfamilie)
  
    def typeselected(self):
        ui_typeselected()

    def sectnameselected(self):
        ui_sectnameselected()

    def find(self):
        ui_find()
        
    def loadsecnameaslected(self):
        secnameselected=self.ui.listWidget_sectnamelist.currentItem().text()
        self.ui.lineEdit_loadparamas.setText(secnameselected)
        
    def loadparamas(self):
        ui_loadparamas()

    def pushButton_zoom_in(self):
        viev_unit_change(-0.5*u.mm)
        ui_drawingsection()
        
    def pushButton_zoom_out(self):
        viev_unit_change(+0.5*u.mm)
        ui_drawingsection()
    
    def change_comboBox_sectionfamilie(self):
        ui_reloadlists(None)
                
def ui_typeselected():
    myapp.ui.textBrowser_sectprep.clear()
    currentpropinrequareaclear()
    sectionscene.clearScene()
    myapp.ui.listWidget_sectnamelist.clear()
    myapp.ui.label_basename.setText(basename)
    selectedtype = myapp.ui.listWidget_typelist.currentItem().text()
    selectedtype_description = base.get_database_sectiontypesdescription()[str(selectedtype)]
    myapp.ui.textBrowser_sectprep.append(selectedtype_description)
    for i in sectionlist:
        if base.get_sectionparameters(i)['figure']==selectedtype:
            myapp.ui.listWidget_sectnamelist.addItem(i)
    sectionscene.flage = 0
    ui_drawingsection()
    
def ui_sectnameselected():
    myapp.ui.textBrowser_sectprep.clear()
    selectedsectname = myapp.ui.listWidget_sectnamelist.currentItem().text()
    myapp.ui.textBrowser_sectprep.append(sectpreptext(selectedsectname))
    currentpropinrequarea(selectedsectname)
    sectionscene.flage = 1
    ui_drawingsection()

def currentpropinrequarea(sectname):
    #----------------
    prep = base.get_sectionparameters(str(sectname))
    currentpropinrequareaclear()
    myapp.ui.label_currentselected.setText(sectname)
    myapp.ui.label_is_h.setText(str(prep['h']))
    myapp.ui.label_is_b.setText(str(prep['b']))
    myapp.ui.label_is_mass.setText(str(prep['mass']))
    myapp.ui.label_is_Ax.setText(str(prep['Ax']))
    myapp.ui.label_is_Iy.setText(str(prep['Iy']))
    myapp.ui.label_is_Iz.setText(str(prep['Iz']))
    myapp.ui.label_is_Wy.setText(str(prep['Wy']))
    myapp.ui.label_is_Wz.setText(str(prep['Wz']))
    #----
    material.set_steelgrade(myapp.ui.comboBox_SteelGrade.currentText())
    fd = material.f_y()
    instability = float(myapp.ui.comboBox_instalility.currentText())
    #----
    Nrd = instability*prep['Ax']*fd
    myapp.ui.label_is_Nrd.setText(str(Nrd.asUnit(u.kN)))
    Mrdy = instability*prep['Wy']*fd
    myapp.ui.label_is_Mrdy.setText(str(Mrdy.asUnit(u.kNm)))
    Mrdz = instability*prep['Wz']*fd
    myapp.ui.label_is_Mrdz.setText(str(Mrdz.asUnit(u.kNm)))
    Vrdy = instability*prep['Ay']*fd / pow(3.0, 0.5)
    myapp.ui.label_is_Vrdy.setText(str(Vrdy.asUnit(u.kN)))
    Vrdz = instability*prep['Az']*fd / pow(3.0, 0.5)
    myapp.ui.label_is_Vrdz.setText(str(Vrdz.asUnit(u.kN)))
    
def currentpropinrequareaclear():
    defult='------------'
    myapp.ui.label_currentselected.setText(defult)
    myapp.ui.label_is_h.setText(defult)
    myapp.ui.label_is_b.setText(defult)
    myapp.ui.label_is_mass.setText(defult)
    myapp.ui.label_is_Ax.setText(defult)
    myapp.ui.label_is_Iy.setText(defult)
    myapp.ui.label_is_Iz.setText(defult)
    myapp.ui.label_is_Wy.setText(defult)
    myapp.ui.label_is_Wz.setText(defult)
    myapp.ui.label_is_Nrd.setText(defult)
    myapp.ui.label_is_Mrdy.setText(defult)
    myapp.ui.label_is_Mrdz.setText(defult)
    myapp.ui.label_is_Vrdy.setText(defult)
    myapp.ui.label_is_Vrdz.setText(defult)
    
def sectpreptext(sectname):
    prep = base.get_sectionparameters(str(sectname))
    prepdescription = base.get_parameters_description()
    selectedtype_description = base.get_database_sectiontypesdescription()[prep['figure']]
    #----------
    text=selectedtype_description + '\n'
    text+=  'Properites of  '+ prep['sectionname'] + '  section: \n'
    preptodisplay=('Ax', 'Ay', 'Az', 'Iomega', 'Ix', 'Iy', 'Iz', 'Wply', 'Wplz', 'Wtors', 
    'b', 'ea', 'es', 'gamma', 'h', 'mass', 'surf', 'Wy', 'Wz', 'vpy', 'vpz', 'vy', 'vz')
    number = 0
    for i in prep :
        if i in preptodisplay:
            if myapp.ui.checkBox_PropertiesDescription.isChecked():
                text += i + '='+ str(prep[i])+' - '+ prepdescription[i] + '\n'
            else:
                text += i + '='+ str(prep[i])
                number += 1 
                if number == 3:
                    text += '\n'
                    number = 0
                else:
                    text += '      '
    #----------
    return text
    
def ui_drawingsection ():
    if sectionscene.flage == 0:
        selectedtype = myapp.ui.listWidget_typelist.currentItem().text()
        sectionscene.clearScene()
        typesectionlist = []
        for i in sectionlist:
            if base.get_sectionparameters(i)['figure']==selectedtype:
                base.draw_sectiongeometry(sectionscene, i, 0)
                typesectionlist.append(i)
        z_min = -max([base.get_sectionparameters(i)['vpz'] for i in typesectionlist])
        sectionscene.addText(selectedtype + ' range', [0*u.mm, z_min])
        sectionscene.ShowOnGraphicsViewObiect()
    if sectionscene.flage == 1:
        try:
            selectedsectname = str(myapp.ui.listWidget_sectnamelist.currentItem().text())
            sectionscene.clearScene()
            base.draw_sectiongeometry(sectionscene, selectedsectname, 1)
            sectionscene.ShowOnGraphicsViewObiect()
        except AttributeError:
            pass
    grid = 20.0 * sectionscene.unit
    sectionscene.addLine([5*grid, -3*grid], [6*grid, -3*grid])
    sectionscene.addLine([5*grid, -2.8*grid], [5*grid, -3.2*grid])
    sectionscene.addLine([6*grid, -2.8*grid], [6*grid, -3.2*grid])      
    sectionscene.addText(str(1*grid), [4.4*grid, -3*grid])
    
def viev_unit_change(value=u.mm):
    sectionscene.change_unit(value)
   
def ui_find():
    myapp.ui.textBrowser_sectprep.clear()
    sectionscene.clearScene()
    queryset=set(base.get_database_sectionlist())
    #h querty
    if myapp.ui.checkBox_h.isChecked():
        delta_n=float(myapp.ui.comboBox_h_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_h_deltap.currentText())
        parameter='h'
        value=float(myapp.ui.lineEdit_req_h.text())*u.cm
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #b querty
    if myapp.ui.checkBox_b.isChecked():
        delta_n=float(myapp.ui.comboBox_b_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_b_deltap.currentText())
        parameter='b'
        value=float(myapp.ui.lineEdit_req_b.text())*u.cm
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))    
    #mass querty
    if myapp.ui.checkBox_mass.isChecked():
        delta_n=float(myapp.ui.comboBox_mass_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_mass_deltap.currentText())
        parameter='mass'
        value=float(myapp.ui.lineEdit_req_mass.text())*u.kg/u.m
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Ax querty
    if myapp.ui.checkBox_Ax.isChecked():
        delta_n=float(myapp.ui.comboBox_Ax_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Ax_deltap.currentText())
        parameter='Ax'
        value=float(myapp.ui.lineEdit_req_Ax.text())*u.cm2
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Iy querty
    if myapp.ui.checkBox_Iy.isChecked():
        delta_n=float(myapp.ui.comboBox_Iy_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Iy_deltap.currentText())
        parameter='Iy'
        value=float(myapp.ui.lineEdit_req_Iy.text())*u.cm4
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Iz querty
    if myapp.ui.checkBox_Iz.isChecked():
        delta_n=float(myapp.ui.comboBox_Iz_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Iz_deltap.currentText())
        parameter='Iz'
        value=float(myapp.ui.lineEdit_req_Iz.text())*u.cm4
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Wy querty
    if myapp.ui.checkBox_Wy.isChecked():
        delta_n=float(myapp.ui.comboBox_Wy_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Wy_deltap.currentText())
        parameter='Wy'
        value=float(myapp.ui.lineEdit_req_Wy.text())*u.cm3
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))        
    #Wz querty
    if myapp.ui.checkBox_Wz.isChecked():
        delta_n=float(myapp.ui.comboBox_Wz_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Wz_deltap.currentText())
        parameter='Wz'
        value=float(myapp.ui.lineEdit_req_Wz.text())*u.cm3
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))       
    #Capacities querty   
    material.set_steelgrade(myapp.ui.comboBox_SteelGrade.currentText())
    fd = material.f_y()
    instability=float(myapp.ui.comboBox_instalility.currentText())
    #Nrd querty
    if myapp.ui.checkBox_Nrd.isChecked():
        delta_n=float(myapp.ui.comboBox_Nrd_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Nrd_deltap.currentText())
        req_Nrd=float(myapp.ui.lineEdit_req_Nrd.text())*u.kN
        req_Ax=req_Nrd/(fd*instability)
        parameter='Ax'
        value=req_Ax.normalize()
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Mrdy querty
    if myapp.ui.checkBox_Mrdy.isChecked():
        delta_n=float(myapp.ui.comboBox_Mrdy_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Mrdy_deltap.currentText())
        req_Mrdy=float(myapp.ui.lineEdit_req_Mrdy.text())*u.kNm
        req_Wy=req_Mrdy/(fd*instability)
        parameter='Wy'
        value=req_Wy.normalize()
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Mrdz querty
    if myapp.ui.checkBox_Mrdz.isChecked():
        delta_n=float(myapp.ui.comboBox_Mrdz_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Mrdz_deltap.currentText())
        req_Mrdz=float(myapp.ui.lineEdit_req_Mrdz.text())*u.kNm
        req_Wz=req_Mrdz/(fd*instability)
        parameter='Wz'
        value=req_Wz.normalize()
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Vrdy querty
    if myapp.ui.checkBox_Vrdy.isChecked():
        delta_n=float(myapp.ui.comboBox_Vrdy_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Vrdy_deltap.currentText())
        req_Vrdy=float(myapp.ui.lineEdit_req_Vrdy.text())*u.kN
        req_Ay=pow(3.0, 0.5)*req_Vrdy/(fd*instability)
        parameter='Ay'
        value=req_Ay.normalize()
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    #Vrdz querty
    if myapp.ui.checkBox_Vrdz.isChecked():
        delta_n=float(myapp.ui.comboBox_Vrdz_deltan.currentText())
        delta_p=float(myapp.ui.comboBox_Vrdz_deltap.currentText())
        req_Vrdz=float(myapp.ui.lineEdit_req_Vrdz.text())*u.kN
        req_Az=pow(3.0, 0.5)*req_Vrdz/(fd*instability)
        parameter='Az'
        value=req_Az.normalize()
        queryset=queryset & set(base.find_withparameter(parameter, value, delta_n, delta_p))
    ui_reloadlists(list(queryset))
    
def ui_reloadlists(someseclist):
    global typelist
    global sectionlist
    myapp.ui.listWidget_typelist.clear()
    myapp.ui.listWidget_sectnamelist.clear()
    myapp.ui.textBrowser_sectprep.clear()
    sectionscene.clearScene()
    #----update global typelist and sectionlist
    if not someseclist == None:
        sectionlist=sorted(list(set(someseclist)))
    typesinsomeseclist=[base.get_sectionparameters(i)['figure'] for i in sectionlist]    
    typelist=sorted(list(set(typesinsomeseclist)))
    #----type filter as group selected in comboBox_sectiongroups 
    groupselected = str(myapp.ui.comboBox_sectiongroups.currentText())
    if groupselected == 'All':
        myapp.ui.listWidget_typelist.addItems(typelist)
        filtertypelist = typelist
    else:
        filtertypelist = []
        for i in typelist:
            if base.get_figuregroupname(i) == groupselected:
                filtertypelist.append(i)
                myapp.ui.listWidget_typelist.addItem(i)
    #----section filter as group selected in comboBox_sectiongroups
    for i in sectionlist:
        if base.get_sectionparameters(i)['figure'] in  filtertypelist:
            myapp.ui.listWidget_sectnamelist.addItem(i)
    #----update group list in comboBox_sectiongroups
    if not someseclist == None:
        groupidlist=[]
        for i in typelist:
            groupidlist.append(base.get_figuregroupid(i))
        groupidlist = sorted(set(groupidlist))
        myapp.ui.comboBox_sectiongroups.clear()
        myapp.ui.comboBox_sectiongroups.addItem('All')
        for i in groupidlist:
            myapp.ui.comboBox_sectiongroups.addItem(base.get_database_sectiongroups()[i])
        
def ui_loadparamas():
    selectname = str(myapp.ui.lineEdit_loadparamas.text())
    prep=base.get_sectionparameters(selectname)
    preciscion=2
    #----------------
    myapp.ui.lineEdit_req_h.setText(str(round(prep['h'].asUnit(u.cm).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_b.setText(str(round(prep['b'].asUnit(u.cm).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_mass.setText(str(round(prep['mass'].asUnit(u.kg/u.m).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_Ax.setText(str(round(prep['Ax'].asUnit(u.cm2).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_Iy.setText(str(round(prep['Iy'].asUnit(u.cm4).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_Iz.setText(str(round(prep['Iz'].asUnit(u.cm4).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_Wy.setText(str(round(prep['Wy'].asUnit(u.cm3).asNumber(), preciscion)))
    myapp.ui.lineEdit_req_Wz.setText(str(round(prep['Wz'].asUnit(u.cm3).asNumber(), preciscion)))
    #----------------    
    material.set_steelgrade(myapp.ui.comboBox_SteelGrade.currentText())
    fd = material.f_y()
    instability=float(myapp.ui.comboBox_instalility.currentText())
    #---------------- 
    Nrd=instability*prep['Ax']*fd
    myapp.ui.lineEdit_req_Nrd.setText(str(round(Nrd.asUnit(u.kN).asNumber(), preciscion)))
    #---------------- 
    Mrdy=instability*prep['Wy']*fd
    myapp.ui.lineEdit_req_Mrdy.setText(str(round(Mrdy.asUnit(u.kNm).asNumber(), preciscion)))
    #---------------- 
    Mrdz=instability*prep['Wz']*fd
    myapp.ui.lineEdit_req_Mrdz.setText(str(round(Mrdz.asUnit(u.kNm).asNumber(), preciscion)))
    #---------------- 
    Vrdy=instability*prep['Ay']*fd / pow(3.0, 0.5) 
    myapp.ui.lineEdit_req_Vrdy.setText(str(round(Vrdy.asUnit(u.kN).asNumber(), preciscion)))
    #---------------- 
    Vrdz=instability*prep['Az']*fd  / pow(3.0, 0.5)
    myapp.ui.lineEdit_req_Vrdz.setText(str(round(Vrdz.asUnit(u.kN).asNumber(), preciscion)))

if __name__ == "__main__":
    #----
    base=SectionBase(1)
    material = MaterialSteel()
    #---
    typelist=base.get_database_sectiontypes()
    sectionlist=base.get_database_sectionlist()
    basename=base.get_database_name()
    #----
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    #----
    sectionscene = PyqtSceneCreator2D()
    sectionscene.set_GraphicsViewObiect(myapp.ui.graphicsView_sectionshape)
    sectionscene.set_unit(0.3*u.cm)
    #----
    myapp.ui.listWidget_typelist.addItems(typelist)
    myapp.ui.comboBox_SteelGrade.addItems(material.get_availablesteelgrade())
    myapp.ui.comboBox_sectiongroups.addItems(['All'] + [base.get_database_sectiongroups()[i] for i in sorted(base.get_database_sectiongroups().keys())])
    #----
    myapp.setWindowTitle(appname + ' ' + version)
    myapp.ui.label_info.setText('struthon.org')
    #----
    myapp.show()
    sys.exit(app.exec_())