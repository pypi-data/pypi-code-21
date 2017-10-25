'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2016-03-20

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://strupy.org/

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.2 changes:
- RcPanelLoad class upgraded
File version 0.3 changes:
- multi loadcase implemented
'''
import numpy as np

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcPanelLoad(MaterialConcrete, MaterialRcsteel):

    def __init__(self):
        print "RcPanelLoad init"
        #----
        self.casename = 'Noname'
        self.moment_mx= np.array([])
        self.moment_my= np.array([])
        self.moment_mxy= np.array([])
        self.force_nx= np.array([])
        self.force_ny= np.array([])
        self.force_nxy= np.array([])
        self.force_vx= np.array([])
        self.force_vy= np.array([])
        #----
        self.loadcasecontainer = []
        #----
        self.moment_equ_MX= np.array([])
        self.moment_equ_MY= np.array([])
        self.force_equ_NX= np.array([])
        self.force_equ_NY= np.array([])
        #----
        self.force_unit = u.kN
        self.moment_unit = u.kNm

    def calc_equivalent_load(self):
        def equ_M (MN, MT):
            Mp = MN + abs(MT)
            Mn = MN - abs(MT) 
            if abs(Mp) >= abs(Mn):
                return Mp
            if abs(Mn) > abs(Mp):
                return Mn
        def equ_N (NN, NV):
            Nt = NN + abs(NV)
            Nc = NN - abs(NV)
            if Nt > 0:
                return Nt
            else:
                return Nc
        self.moment_equ_MX = np.vectorize(equ_M)(self.moment_mx, self.moment_mxy)
        self.moment_equ_MY = np.vectorize(equ_M)(self.moment_my, self.moment_mxy)
        self.force_equ_NX = np.vectorize(equ_N)(self.force_nx, self.force_nxy)
        self.force_equ_NY = np.vectorize(equ_N)(self.force_ny, self.force_nxy)
        
    def clear_arrays_data(self):
        self.casename = 'Noname'
        self.moment_mx= np.array([])
        self.moment_my= np.array([])
        self.moment_mxy= np.array([])
        self.force_nx= np.array([])
        self.force_ny= np.array([])
        self.force_nxy= np.array([])
        self.force_vx= np.array([])
        self.force_vy= np.array([])
        #----
        self.moment_equ_MX= np.array([])
        self.moment_equ_MY= np.array([])
        self.force_equ_NX= np.array([])
        self.force_equ_NY= np.array([])
        #----
        self.loadcasecontainer = []
        
    def add_loadcase(self):
        casedict = {    'casename' : self.casename,
                        'moment_mx' : self.moment_mx[:],
                        'moment_my' : self.moment_my[:],
                        'moment_mxy' : self.moment_mxy[:],
                        'force_nx' : self.force_nx[:],
                        'force_ny' : self.force_ny[:],
                        'force_nxy' : self.force_nxy[:],
                        'force_vx' : self.force_vx[:],
                        'force_vy' : self.force_vy[:]  }
        self.loadcasecontainer.append(casedict)
    
    def get_loadcasenamelist(self):
        casenamelist = []
        if not self.loadcasecontainer == [] :
            for case in self.loadcasecontainer:
                casenamelist.append(case['casename'])
        return casenamelist
        
    def get_loadcase(self, casename='somename'):
        if casename in self.get_loadcasenamelist():
            for case in self.loadcasecontainer:
                if casename == case['casename']:
                    return case
        else:
            return None
    
    def set_activeloadcase(self, casename='existcasename'):
        if casename in self.get_loadcasenamelist():
            tmpcase = self.get_loadcase(casename)
            self.casename = tmpcase['casename'][:]
            self.moment_mx = tmpcase['moment_mx'][:]
            self.moment_my = tmpcase['moment_my'][:]
            self.moment_mxy = tmpcase['moment_mxy'][:]
            self.force_nx = tmpcase['force_nx'][:]
            self.force_ny = tmpcase['force_ny'][:]
            self.force_nxy = tmpcase['force_nxy'][:]
            self.force_vx = tmpcase['force_vx'][:]
            self.force_vy = tmpcase['force_vy'][:]
        self.calc_equivalent_load()
            
# Test if main
if __name__ == '__main__':
    from RcPanel import RcPanel
    from RcPanelDataLoader import RcPanelDataLoader
    panel = RcPanel()
    load = RcPanelLoad()
    loader = RcPanelDataLoader()
    panel.h_unit = u.mm
    panel.coord_unit = u.m
    load.moment_unit = u.kNm
    load.force_unit = u.kN
    loader.RFEMxlsloader(panel, load)
    #loader.ROBOTcsvloader(panel, load)
    load.casename = 'LoadCase1'
    load.add_loadcase()
    load.casename = 'LoadCase2'
    load.add_loadcase()
    print load.get_loadcasenamelist()
    print load.get_loadcase('LoadCase1')
    print load.casename
    load.set_activeloadcase('LoadCase1')
    print load.casename