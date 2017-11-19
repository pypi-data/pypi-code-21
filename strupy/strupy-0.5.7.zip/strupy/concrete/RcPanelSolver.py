'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.4 date 2017-03-06

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
- RcPanelSolver class upgraded
File version 0.3 changes:
-reinforce() method upgraded for multi loadcase  calculation
File version 0.4 changes:
-made some tidy
'''
import numpy as np

import strupy.units as u

class RcPanelSolver():

    import fas_pure as fas

    def __init__(self):
        print "RcPanelSolver"
        
    def reinforce(self, panel, load, progress=None):
        b = 1.0 
        ap = panel.ap.asUnit(u.m).asNumber()
        an = panel.an.asUnit(u.m).asNumber()
        fip = panel.fip.asUnit(u.m).asNumber()
        fin = panel.fin.asUnit(u.m).asNumber()
        rysAp = panel.rysAp
        rysAn = panel.rysAn
        wlimp = panel.wlimp.asUnit(u.m).asNumber()
        wlimn = panel.wlimn.asUnit(u.m).asNumber()
        fcd = panel.fcd.asUnit(u.Pa).asNumber()
        fctm = panel.fctm.asUnit(u.Pa).asNumber()
        fyd = panel.fyd.asUnit(u.Pa).asNumber()
        #----
        pointnumber = len(panel.coord_Xp)
        #----
        if len(panel.Anx) == 0:
            panel.Apx = np.zeros(pointnumber)
            panel.Apy = np.zeros(pointnumber)
            panel.Anx = np.zeros(pointnumber)
            panel.Any = np.zeros(pointnumber)
            panel.rysx = np.zeros(pointnumber)
            panel.rysy = np.zeros(pointnumber)
            panel.mimosx = np.zeros(pointnumber)
            panel.mimosy = np.zeros(pointnumber)
            panel.ksieffx = np.zeros(pointnumber)
            panel.ksieffy = np.zeros(pointnumber)
        #----
        local_NX = load.force_equ_NX * (load.force_unit/u.N).asNumber()
        local_MX = load.moment_equ_MX * (load.moment_unit/u.Nm).asNumber()
        local_NY = load.force_equ_NY * (load.force_unit/u.N).asNumber()
        local_MY = load.moment_equ_MY * (load.moment_unit/u.Nm).asNumber()
        local_h = panel.h * (panel.h_unit/u.m).asNumber()
        #----
        A_ratio = (u.m2 / panel.A_unit).asNumber()
        #----
        for i in range(0, pointnumber):
            #----x direction
            tmp=self.fas.calc(local_NX[i], local_MX[i], local_h[i], b, ap, an, fip, fin, rysAp, rysAn, wlimp, wlimn, fcd, fctm, fyd)
            panel.Apx[i] = max(tmp['Ap'] * A_ratio, panel.Apx[i])
            panel.Anx[i] = max(tmp['An'] * A_ratio, panel.Anx[i])
            panel.rysx[i] = max(tmp['rys'], panel.rysx[i])
            panel.mimosx[i] = tmp['mimos']
            panel.ksieffx[i] = max(tmp['ksieff'], panel.ksieffx[i])
            #----y direction
            tmp=self.fas.calc(local_NY[i], local_MY[i], local_h[i], b, ap, an, fip, fin, rysAp, rysAn, wlimp, wlimn, fcd, fctm, fyd)
            panel.Apy[i] = max(tmp['Ap'] * A_ratio, panel.Apy[i])
            panel.Any[i] = max(tmp['An'] * A_ratio, panel.Any[i])
            panel.rysy[i] = max(tmp['rys'], panel.rysy[i])
            panel.mimosy[i] = tmp['mimos']
            panel.ksieffy[i] = max(tmp['ksieff'], panel.ksieffy[i])
            if progress: progress.setValue(100 * i / pointnumber)
        #----
        if progress: progress.setValue(0)
        panel.report += 'An Ap reinforcement calculated.\n'
        return None

# Test if main
if __name__ == '__main__':
    print ('test RcPanelSolver')
