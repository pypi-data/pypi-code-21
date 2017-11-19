'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-11-15
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

import os
import shelve

from PyQt4 import QtGui

savedir = os.path.dirname(__file__)#dir path for save and open

def saveproject(element, load, progress=None):
    global savedir
    #----asking for filename with default as element.Mark
    filename = QtGui.QFileDialog.getSaveFileName(   caption = 'Save project as',
                                                    directory = os.path.join(savedir,element.Mark),
                                                    filter = "StruthonSteelMember data' (*.ssmdata)")
    filename = str(filename)
    if not filename == '': savedir = os.path.dirname(filename)
    #----
    if progress:
        progress.setValue(50)
    #----shelve file open
    db = shelve.open(filename)
    db.clear()
    #----writing element and load object data to shelve file
    db['Mark'] = element.Mark
    db['sectname'] = element.sectname
    db['steelgrade'] = element.steelgrade
    db['L'] = element.L
    db['k_ycr'] = element.k_ycr
    db['k_zcr'] = element.k_zcr
    db['k_LT'] = element.k_LT
    db['Name'] = load.Name
    db['M_yEd'] = load.M_yEd
    db['M_zEd'] = load.M_zEd
    db['T_Ed'] = load.T_Ed
    db['N_Ed'] = load.N_Ed
    db['V_yEd'] = load.V_yEd
    db['V_zEd'] = load.V_zEd
    db['caseactiv'] = load.caseactiv
    db['stabilitycheck'] = load.stabilitycheck
    #----
    if progress:
        progress.setValue(80)
    #----shelve file close
    db.close()
    #----
    if progress:
        progress.setValue(0)
    
def openproject(element, load, progress=None):
    global savedir
    #----asking for filename
    filename = QtGui.QFileDialog.getOpenFileName(   caption = 'Save project as',
                                                    directory = savedir,
                                                    filter = "StruthonSteelMember data' (*.ssmdata)")
    filename = str(filename)
    if not filename == '': savedir = os.path.dirname(filename)
    #----
    if progress:
        progress.setValue(20)
    #----shelve file open
    db = shelve.open(filename)
    #----claring load object data
    load.clear_loadcase()
    #----reading data from shelve file and writing to element object
    element.Mark = db['Mark']
    element.set_sectionfrombase(db['sectname'])
    element.set_steelgrade(db['steelgrade'])
    element.L = db['L'] 
    element.k_ycr = db['k_ycr']
    element.k_zcr = db['k_zcr'] 
    element.k_LT = db['k_LT']
    #----reading data from shelve file and writing load object
    load.Name = db['Name']
    load.M_yEd = db['M_yEd']
    load.M_zEd = db['M_zEd']
    load.T_Ed = db['T_Ed']
    load.N_Ed = db['N_Ed']
    load.V_yEd = db['V_yEd']
    load.V_zEd = db['V_zEd']
    load.caseactiv = db['caseactiv']
    load.stabilitycheck  = db['stabilitycheck']    
    #----
    if progress:
        progress.setValue(80)
    #----shelve file close
    db.close()
    #----
    if progress:
        progress.setValue(0)