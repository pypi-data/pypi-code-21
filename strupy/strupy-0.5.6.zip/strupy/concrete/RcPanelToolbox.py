'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-03-06

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
'''
import itertools

import numpy as np

import strupy.units as u

class RcPanelToolbox():
    
    def __init__(self):
        print "RcPanelToolbox"
        #---
        self.Panel = None
        #----
        self.geogrid = 0.05
        self.geomatrix = np.array([[],[]])

    def assignPanelObiect(self, someRcPanel):
        self.Panel = someRcPanel
    
    #------------------------------------------------------------------------
    #------------------------cut peak mathods--------------------------------
    #------------------------------------------------------------------------ 
    
    def cut_peak(self, cut_dist=1.5, progress=None):
        print 'cut_peak...'
        if progress: progress.setValue(5)
        self._create_geomatrix()
        closepoints_all = self._get_closepoints_relativh(dx=cut_dist, dy=cut_dist)
        if progress: progress.setValue(10)
        closepoints_in = self._get_closepoints_relativh(dx=cut_dist/2.0, dy=cut_dist/2.0)
        closepoints_out = []
        for i in range(len(closepoints_all)):
            closepoints_out.append(None)
            closepoints_out[i] =list(set(closepoints_all[i]).difference(set(closepoints_in[i])))
        if progress: progress.setValue(20)
        self._cut(self.Panel.Apx, closepoints_out, closepoints_in)
        if progress : progress.setValue(40)
        self._cut(self.Panel.Anx, closepoints_out, closepoints_in)
        if progress: progress.setValue(60)
        self._cut(self.Panel.Apy, closepoints_out, closepoints_in)
        if progress: progress.setValue(80)
        self._cut(self.Panel.Any, closepoints_out, closepoints_in)
        if progress: progress.setValue(0)
        print '..done'
        self.Panel.report += 'Peaks cuted with %s*h. \n' %str(cut_dist)

    def _cut(self, rcdata, closepoints_out, closepoints_in):
        data_size = len(rcdata)
        cuted_rcdata = np.zeros(data_size)
        cuted_rcdata[:] = rcdata[:]
        for p in range(data_size):
            if len(closepoints_out[p]) > 4 and len(closepoints_in[p]) > 4:
                rmax = 0
                for n in (closepoints_in[p]+closepoints_out[p]):
                    rmax = max(rmax, rcdata[n])
                if rmax ==  rcdata[p] and rmax != 0:
                    outrmax = 0                 
                    for n in closepoints_out[p]:
                        outrmax = max(outrmax, rcdata[n])
                    for n in closepoints_in[p]:
                        cuted_rcdata[n] = min(outrmax, cuted_rcdata[n])
        rcdata[:] = cuted_rcdata[:]

    #------------------------------------------------------------------------
    #--------------------reinfororcement smooth methods----------------------
    #------------------------------------------------------------------------ 
            
    def smooth_np_reinforcement(self, smooth_width=2.0, progress=None):
        print 'smooth_np_reinforcement...'
        if progress: progress.setValue(5)
        self._create_geomatrix()
        d1 = smooth_width / 2.0
        d2 = 0.25
        #---
        if True:
            xclosepoints = self._get_closepoints_relativh(dx=d1, dy=d2)
            yclosepoints = self._get_closepoints_relativh(dx=d2, dy=d1)
            #---
            if progress: progress.setValue(20)
            self._smooth(self.Panel.Apx, yclosepoints)
            if progress: progress.setValue(40)
            self._smooth(self.Panel.Anx, yclosepoints)
            if progress: progress.setValue(60)
            self._smooth(self.Panel.Apy, xclosepoints)
            if progress: progress.setValue(80)
            self._smooth(self.Panel.Any, xclosepoints)
        if progress: progress.setValue(0)
        print '..done'
        self.Panel.report += 'Smoothed with widht %s*h. \n' %str(smooth_width)

    def _smooth(self, rcdata, closepoints):
        data_size = len(rcdata)
        smoothed_rcdata = np.zeros(data_size)
        for p in range(data_size):
            sum = 0.0
            for n in closepoints[p]:
                sum += rcdata[n]
            pointnumber = float(len(closepoints[p]))
            midvalue =  sum / pointnumber
            smoothed_rcdata[p] = midvalue
        rcdata[:] = smoothed_rcdata[:]

    #------------------------------------------------------------------------
    #------------------------anchoring methods-------------------------------
    #------------------------------------------------------------------------
        
    def include_anchore(self, anchor_filength=45.0, progress=None):
        print 'include_anchore...'
        if progress: progress.setValue(5)
        self._create_geomatrix()
        if progress: progress.setValue(10)
        #---
        if True:
            xclosepoints_Apx = self._get_closepoints_relativfi(self.Panel.Apx, dx = anchor_filength, dy=1.0, side='p')
            if progress: progress.setValue(20)
            xclosepoints_Anx = self._get_closepoints_relativfi(self.Panel.Anx, dx = anchor_filength, dy=1.0, side='n')
            if progress: progress.setValue(30)
            yclosepoints_Apy = self._get_closepoints_relativfi(self.Panel.Apy, dx = 1.0, dy=anchor_filength, side='p')
            if progress: progress.setValue(40)
            yclosepoints_Any = self._get_closepoints_relativfi(self.Panel.Any, dx = 1.0, dy=anchor_filength, side='n')
            #---
            if progress: progress.setValue(60)
            self._ancore(self.Panel.Apx, xclosepoints_Apx)
            self._ancore(self.Panel.Anx, xclosepoints_Anx)
            if progress: progress.setValue(80)
            self._ancore(self.Panel.Apy, yclosepoints_Apy)
            self._ancore(self.Panel.Any, yclosepoints_Any)
            if progress: progress.setValue(0)
        print '..done'

    def _ancore(self, rcdata, closepoints):
        data_size = len(rcdata)
        out_rcdata = np.zeros(data_size)
        out_rcdata[:] = rcdata[:]
        #---
        for p in range(data_size):
            for n in closepoints[p]:
                if out_rcdata[n]<rcdata[p]:
                    out_rcdata[n] = rcdata[p]
        rcdata[:] = out_rcdata[:]

    #------------------------------------------------------------------------
    #------------------------------creating geomatrix------------------------
    #------------------------------------------------------------------------
    
    def _create_geomatrix(self):
        ds = (self.geogrid / self.Panel.coord_unit).asNumber()
        #---
        xmin = min(self.Panel.coord_flatten_x)
        xmax = max(self.Panel.coord_flatten_x)
        ymin = min(self.Panel.coord_flatten_y)
        ymax = max(self.Panel.coord_flatten_y)
        #---
        xsize = int(round(abs((xmax - xmin) / ds))) + 1
        ysize = int(round(abs((ymax - ymin) / ds))) + 1
        #---
        paneldatasize = len(self.Panel.coord_flatten_x)
        #---init empty matrix
        self.geomatrix = np.zeros((xsize, ysize)).tolist()
        for i in range(xsize):
            for j in range(ysize):
                self.geomatrix[i][j] = None
        #---creating data
        for x, y, i in itertools.izip(self.Panel.coord_flatten_x, self.Panel.coord_flatten_y, range(paneldatasize)):
            n = int(round((x-xmin)/ds))
            m = int(round((y-ymin)/ds))
            if self.geomatrix[n][m] == None:
                self.geomatrix[n][m] = []
            self.geomatrix[n][m].append(i)

    #------------------------------------------------------------------------
    #------------------------------closepoints methods-----------------------
    #------------------------------------------------------------------------
    
    def _get_closepoints_totaldist(self, dx = 1.0, dy=0.1):
        paneldatasize = len(self.Panel.coord_flatten_x)
        closepoints = [None] * paneldatasize
        for i in range(len(self.geomatrix)):
            for j in range(len(self.geomatrix[0])):
                if self.geomatrix[i][j]:
                    for p in self.geomatrix[i][j]:
                        dp = self.Panel.h[p]
                        closepoints[p] = self._get_sum(i, j, dx, dy )
        return closepoints

    def _get_closepoints_relativh(self, dx = 1.0, dy=0.1):
        paneldatasize = len(self.Panel.coord_flatten_x)
        closepoints = [None] * paneldatasize
        for i in range(len(self.geomatrix)):
            for j in range(len(self.geomatrix[0])):
                if self.geomatrix[i][j]:
                    for p in self.geomatrix[i][j]:
                        hp = self.Panel.h[p] * (self.Panel.h_unit / self.Panel.coord_unit).asNumber()
                        closepoints[p] = self._get_sum(i, j, dx*hp, dy*hp )
        return closepoints

    def _get_closepoints_relativfi(self, Arequ, dx = 1.0, dy=0.1, side='p'):
        paneldatasize = len(self.Panel.coord_flatten_x)
        closepoints = [None] * paneldatasize
        for i in range(len(self.geomatrix)):
            for j in range(len(self.geomatrix[0])):
                if self.geomatrix[i][j]:
                    for p in self.geomatrix[i][j]:
                        if side == 'p':
                            fi = self.Panel.fi_for_Ap(Arequ[p]) * (self.Panel.fi_unit / self.Panel.coord_unit).asNumber()
                            Aprov = self.Panel.round_to_Apscale(Arequ[p])
                        if side == 'n':
                            fi = self.Panel.fi_for_An(Arequ[p]) * (self.Panel.fi_unit / self.Panel.coord_unit).asNumber()
                            Aprov = self.Panel.round_to_Anscale(Arequ[p])
                        alpha = Arequ[p] / Aprov
                        closepoints[p] = self._get_sum(i, j, dx*fi*alpha, dy*fi*alpha )
        return closepoints        

    def _get_sum(self, i=2,j=2, disti=0.5, distj=0.5):
        di = int(round(disti / self.geogrid))
        dj = int(round(distj / self.geogrid))
        #--
        isize = len(self.geomatrix)
        jsize = len(self.geomatrix[0])
        #--
        imax = min(i + di, isize - 1)
        imin = max(i - di, 0)
        #---
        jmax = min(j + dj, jsize - 1)
        jmin = max(j - dj, 0)
        #---
        sum = []
        for i in range(imin, imax+1):
            for j in range(jmin, jmax+1):
                if self.geomatrix[i][j]:
                    sum += self.geomatrix[i][j]
        return sum
    
# Test if main
if __name__ == '__main__':
    #---
    toolbox = RcPanelToolbox()
    #-----example panel from prepered pickle
    import os
    import pickle
    path = os.path.dirname(os.path.abspath(__file__))
    fileObject = open(os.path.join(path, 'panel.pickled'),'r')
    plyta = pickle.load(fileObject)
    plyta.fi_unit = u.mm
    #---assigning panel to toolbox
    toolbox.assignPanelObiect(plyta)
    #---createing viever
    import RcPanelViewer
    viewer = RcPanelViewer.RcPanelViewer()
    viewer.assignPanelObiect(plyta)
    #viewer.plot_flatten_shape()
    #viewer.plot_reinforcement_Anx()
    #viewer.map_reinforcement_Anx()
    #--
    #print panel.Anx[100]
    toolbox.cut_peak(cut_dist=1.5)
    toolbox.smooth_np_reinforcement(smooth_width=3.0)
    toolbox.include_anchore(50.0)
    #viewer.plot_reinforcement_Anx()
    viewer.map_reinforcement_Anx()
    #print panel.Anx[100]
    #toolbox._get_closepoints_relativfi(plyta.Apx, dx = 45.0, dy=10.0, side='n')
    
    '''
    k = 3600
    toolbox._create_geomatrix()
    #pkts = toolbox._get_closepoints_totaldist(2.0, 0.1)[k]
    #pkts = toolbox._get_closepoints_relativh(0.1, 2.0)[k]
    pkts = toolbox._get_closepoints_relativfi(plyta.Anx, 45.0, 0.1)[k]
    print pkts
    for n in pkts:
        toolbox.Panel.Anx[n] = 200
    toolbox.Panel.Anx[k] = 500
    viewer.plot_reinforcement_Anx()
    '''
    
    '''
    from strupy.concrete.RcPanelToolbox import RcPanelToolbox
    toolbox = RcPanelToolbox() 
    toolbox.assignPanelObiect(panel)
    toolbox.cut_peak_on_panel_np_reinforcement()
    '''
        
    '''
    import pickle
    file_Name = 'C:\Users\lukasz\Documents\panel.pickled'
    fileObject = open(file_Name,'wb')
    pickle.dump(panel,fileObject)
    fileObject.close()
'''
