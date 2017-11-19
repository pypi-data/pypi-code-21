'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2016-08-30
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
- openproject() corrected
'''
import os
import shelve

from Tkinter import Tk
from tkFileDialog import asksaveasfilename
from tkFileDialog import askopenfilename

savedir = os.path.dirname(__file__)#dir path for save and open

def saveproject(panel, load, progress=None):
    #----filename to save tkinter dialog
    global savedir
    root = Tk()
    root.withdraw()
    initName = panel.PanelName + '.scpdata'
    filename = asksaveasfilename(parent=root,title='Save as', filetypes=[('StruthonConcretePanel data', '*.scpdata')], initialdir=savedir, initialfile=initName)
    if not filename == '':
        savedir = os.path.dirname(filename)
    root.destroy()
    #----
    if progress:
        progress.setValue(50)
    #----shelve file open
    db = shelve.open(filename)
    db.clear()
    #----writing panel and load object data to shelve file
    db['rcsteelname'] = panel.rcsteelname
    db['concretename'] = panel.concretename
    db['PanelName'] = panel.PanelName
    db['surfaceID'] = panel.surfaceID
    db['h'] = panel.h
    db['coord_Xp'] = panel.coord_Xp
    db['coord_Yp'] = panel.coord_Yp
    db['coord_Zp'] = panel.coord_Zp
    db['ap'] = panel.ap
    db['an'] = panel.an
    db['fip'] = panel.fip
    db['fin'] = panel.fin
    db['rysAp'] = panel.rysAp
    db['rysAn'] = panel.rysAn
    db['wlimp'] = panel.wlimp
    db['wlimn'] = panel.wlimn
    db['Anscale'] = panel.Anscale
    db['Apscale'] = panel.Apscale
    db['loadcasecontainer'] = load.loadcasecontainer
    #----
    if progress:
        progress.setValue(80)
    #----shelve file close
    db.close()
    #----
    if progress:
        progress.setValue(0)
    
def openproject(panel, load, progress=None):
    #----filename to open tkinter dialog
    global savedir
    root = Tk()
    root.withdraw()
    initName = panel.PanelName
    filename = askopenfilename(parent=root,title='Save as', filetypes=[('StruthonConcretePanel data', '*.scpdata')], initialdir=savedir)
    if not filename == '':
        savedir = os.path.dirname(filename)
    root.destroy()
    #----
    if progress:
        progress.setValue(20)
    #----shelve file open
    db = shelve.open(filename)
    #----claring obiect data
    panel.clear_arrays_data()
    load.clear_arrays_data()
    #----reading data from shelve file and writing to panel and load object
    panel.rcsteelname = db['rcsteelname']
    panel.concretename = db['concretename']
    panel.PanelName = db['PanelName'] 
    panel.surfaceID = db['surfaceID']
    panel.h = db['h']
    panel.coord_Xp = db['coord_Xp']
    panel.coord_Yp = db['coord_Yp']
    panel.coord_Zp = db['coord_Zp']
    panel.ap = db['ap']
    panel.an = db['an']
    panel.fip =db['fip'] 
    panel.fin = db['fin']
    panel.rysAp = db['rysAp']
    panel.rysAn = db['rysAn']
    panel.wlimp = db['wlimp']
    panel.wlimn = db['wlimn']
    panel.Anscale[:] = db['Anscale'][:]
    panel.Apscale[:] = db['Apscale'][:]
    load.loadcasecontainer = db['loadcasecontainer']
    #----
    if progress:
        progress.setValue(80)
    #----shelve file close
    db.close()
    #----
    panel.calculate_flatten_coordinates()
    load.set_activeloadcase(load.get_loadcasenamelist()[0])
    #----
    if progress:
        progress.setValue(0)