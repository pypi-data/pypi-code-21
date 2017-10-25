'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-02-04

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
import copy

import numpy as np

import strupy.units as u
from BoltClip import BoltClip

class BoltConnection():

    def __init__(self):
        #--Input data
        #self.Clip = BoltClip()
        #----
        self.xi = np.array([20.0 , 20.0, -20.0 , -20.0]) * u.mm
        self.yi = np.array([40.0 , -40.0, 40.0 , -40.0]) * u.mm
        self.boltclipi = [BoltClip(), BoltClip(), BoltClip(), BoltClip()]
        #----
        self.yfip = -80.0 * u.mm
        self.yfin = 80.0 * u.mm
        self.xfip = 50.0 * u.mm
        self.xfin = -50.0 * u.mm
        #----
        self.plate_xpdim =  50.0 * u.mm
        self.plate_xndim = -50.0 * u.mm
        self.plate_ypdim = 80.0 * u.mm
        self.plate_yndim = -80.0 * u.mm
        #----bolt group loads forces and moment
        self.Fx = 0.0 * u.kN
        self.Fy = -60.0 * u.kN
        self.Fz = 60.0 * u.kN
        self.Mx = 0.0 * u.kNm
        self.My = 4.0 * u.kNm
        self.Mz = 3.0 * u.kNm
        self.gamma = 1.2
        #--Output data
        #----coordinate of bolt group center point
        self.O_x = None
        self.O_y = None
        #----each bolt coordinate in O_x / O_y local coordinate system
        self.xoi = np.array([]) * u.mm
        self.yoi = np.array([]) * u.mm  
        #----each bolt forces
        self.fxi = np.array([]) * u.kN # x direction shear force 
        self.fyi = np.array([]) * u.kN # y direction shear force 
        self.fvi = np.array([]) * u.kN # total shear force
        self.fzi = np.array([]) * u.kN # longitudinal force (positive if tension)
        #----bolt group loads forces and moment dreduced to O_x / O_y point
        self.Fox = None
        self.Foy = None
        self.Foz = None
        self.Mox = None
        self.Moy = None
        self.Moz = None
        #---avilable categories
        self.availale_categories = ['A', 'B', 'C', 'D', 'E', 'F', 'A / D', 'B / E', 'C / F']
        self.category = None
        #---check connection results
        self.capacity_global = None
        self.capacity_local_value = []
        self.capacity_local_comment = []
        #---
        self.set_category()
        #--Calulating for init data
        self.calculate()

    def calculate(self):
        self.check_geometry()
        self._calculate_forces_in_bolts()
        self._calculate_clips()
        self._check_bolts()
        
    def check_geometry(self):
        #--If any bolts outside plate then delete them
        to_delete_list = []
        for i in range(len(self.boltclipi)):
            if not ((self.plate_xndim < self.xi[i] < self.plate_xpdim) and (self.plate_yndim < self.yi[i] < self.plate_ypdim)):
                to_delete_list.append(i)
        self.bolts_delete(to_delete_list)
        
    def _calculate_clips(self):
        for nclip, i in zip(self.boltclipi, range(len(self.boltclipi))):
            #---
            a_list = []
            for j in range(len(self.boltclipi)):
                if j != i:
                    ax = abs(self.xi[i] - self.xi[j])
                    ay = abs(self.yi[i] - self.yi[j])
                    a_list.append(max(ax, ay))
            nclip.a = min(a_list)
            #---
            nclip.Si = self.fzi[i]
            #---
            a1_list = []            
            a1_list.append(self.plate_xpdim - self.xi[i])
            a1_list.append(self.xi[i] - self.plate_xndim)
            a1_list.append(self.plate_ypdim - self.yi[i])
            a1_list.append(self.yi[i] - self.plate_yndim)
            nclip.a1 = min(a1_list)
            #---
            nclip.calculate()
        
    def _calculate_forces_in_bolts(self):
        #---bolts quantity
        n = float(len(self.xi))
        #--- bolts center O point
        self.O_x = np.average(u.xunumlistvalue(self.xi / u.mm)) * u.mm
        self.O_y = np.average(u.xunumlistvalue(self.yi  / u.mm)) * u.mm
        #--- coordinates for zero in O point
        self.xoi = self.xi - self.O_x
        self.yoi = self.yi - self.O_y
        #--- forcres reduced to O point
        self.Fox = self.Fx
        self.Foy = self.Fy
        self.Foz = self.Fz
        self.Mox = self.Mx - self.Fz * self.O_y
        self.Moy = self.My + self.Fz * self.O_x
        self.Moz = self.Mz + self.Fx * self.O_y - self.Fy * self.O_x 
        #-Calculating forces in each bolt
        #---initing lists
        self.fxi = np.array([0 for i in xrange(len(self.xi))])*u.kN
        self.fyi = np.array([0 for i in xrange(len(self.xi))])*u.kN
        self.fzi = np.array([0 for i in xrange(len(self.xi))])*u.kN
        #---Fox effect
        self.fxi += self.Fox / n
        #---Foy effect
        self.fyi += self.Foy / n
        #---Foz effect
        self.fzi += self.Foz / n
        #---Mox effect
        if self.Mox > 0*u.kNm:
            ry = self.yi - self.yfip
            ry = ry.clip(min=0*u.mm)
            sumry2 = np.sum(ry**2)
            self.fzi += np.vectorize(lambda y: (abs(self.Mox) * y / sumry2).asUnit(u.kN) )(ry)
        if self.Mox < 0*u.kNm:
            ry = -self.yi + self.yfin
            ry = ry.clip(min=0*u.mm)
            sumry2 = np.sum(ry**2)
            self.fzi += np.vectorize(lambda y: (abs(self.Mox) * y / sumry2).asUnit(u.kN) )(ry)      
        if self.Mox == 0*u.kNm:    
            self.fzi += 0 * u.kN
        #---Moy effect    
        if self.Moy > 0*u.kNm:
            rx = -self.xi + self.xfip
            rx = rx.clip(min=0*u.mm)
            rx = rx.clip(min=0*u.mm)
            sumrx2 = np.sum(rx**2)
            self.fzi += np.vectorize(lambda x: (abs(self.Moy) * x / sumrx2).asUnit(u.kN) )(rx)        
        if self.Moy < 0*u.kNm:
            rx = self.xi - self.xfin
            rx = rx.clip(min=0*u.mm)
            sumrx2 = np.sum(rx**2)
            self.fzi += np.vectorize(lambda x: (abs(self.Moy) * x / sumrx2).asUnit(u.kN) )(rx)         
        if self.Moy == 0*u.kNm:    
            self.fzi += 0 * u.kN        
        #---Moz effect
        r2 = (self.xoi**2 + self.yoi**2)**0.5
        sumr2 = np.sum(r2**2)
        fi = np.vectorize(lambda x: (self.Moz * x / sumr2).asUnit(u.kN) )(r2)
        self.fxi += -fi * self.yoi / (self.xoi**2 + self.yoi**2)**0.5
        self.fyi += fi * self.xoi / (self.xoi**2 + self.yoi**2)**0.5     
        #---
        self.fvi = (self.fxi**2 + self.fyi**2)**0.5
        self.fzi = self.fzi.clip(min=0*u.kN)

    def _check_bolts(self):
        self.capacity_local_value = [None for i in range(len(self.xi))]
        self.capacity_local_comment = [None for i in range(len(self.xi))]
        #---local references
        value = self.capacity_local_value
        comment = self.capacity_local_comment
        #---
        self.capacity_global = True
        #---
        for i in range(len(self.xi)):
            bolt = self.boltclipi[i]
            #----------------- CATEGORIES A, B, C -------------------------
            if self.category == 'A':
                value[i] = self.fvi[i] / min (bolt.SRv, bolt.SRb)
                comment[i] = 'Svd/min(SRv, SRb) = %s/min(%s, %s) = %s { SGN docisk do krawedzi otworow lub sciecie sruby }' % (self.fvi[i], bolt.SRv, bolt.SRb, value[i])
            if self.category == 'B':
                value_1 = self.fvi[i] / min (bolt.SRv, bolt.SRb)
                comment[i] = 'Svd/min(SRv, SRb) = %s/min(%s, %s) = %s { SGN docisk do krawedzi otworow lub sciecie sruby }' % (self.fvi[i], bolt.SRv, bolt.SRb, value_1)
                #---
                value_2 = (self.fvi[i]/self.gamma) / bolt.SRs
                comment[i] += '\n'
                comment[i] += 'Svk/SRs = %s/%s = %s { SGU poslizg styku}' % (self.fvi[i]/self.gamma, bolt.SRs, value_2)
                #---                
                value[i] = max(value_1, value_2)
            if self.category == 'C':
                value[i] = self.fvi[i] / bolt.SRs
                comment[i] = 'Svd/SRs = %s/%s = %s { SGN poslizg styku}' % (self.fvi[i], bolt.SRs, value[i])
            #----------------- CATEGORIES D, E, F -------------------------
            if self.category == 'D':
                value[i] = self.fzi[i] / bolt.SRt
                comment[i] = 'Std/SRt = %s/%s = %s { SGN zerwanie sruby}' % (self.fzi[i], bolt.SRt, value[i])
            if self.category == 'E':
                value_1 = self.fzi[i] / bolt.SRt
                comment[i] = 'Std/SRt = %s/%s = %s { SGN zerwanie sruby}' % (self.fzi[i], bolt.SRt, value_1)
                #---
                value_2 = (self.fzi[i]/self.gamma) / bolt.SRr
                comment[i] += '\n'
                comment[i] += 'Stk/SRr = %s/%s = %s { SGU rozwarcie styku}' % (self.fzi[i]/self.gamma, bolt.SRr, value_2)
                #---                
                value[i] = max(value_1, value_2)
            if self.category == 'F':
                value[i] = self.fzi[i] / bolt.SRr
                comment[i] = 'Stk/SRr = %s/%s = %s { SGN rozwarcie styku}' % (self.fzi[i], bolt.SRr, value[i])
            #----------------- CATEGORIES A / D, B / E, C / F  -------------------------
            if self.category == 'A / D':
                #--SGN
                value_1 = self.fvi[i] / bolt.SRb
                comment[i] = 'Svd/SRb = %s/%s) = %s { SGN docisk do krawedzi otworow }' % (self.fvi[i], bolt.SRb, value_1)
                #---
                value_2 = (self.fvi[i] / bolt.SRv)**2.0 + (self.fzi[i] / bolt.SRt)**2.0 
                comment[i] += '\n'
                comment[i] += '(Svd/SRv)^2 + (Std/SRt)^2 = (%s/%s)^2 + (%s/%s)^2 = %s { SGN nosnosc sruby}' % (self.fvi[i], bolt.SRv, self.fzi[i], bolt.SRt, value_2) 
                #---
                value[i] = max(value_1, value_2)
            #--------------------
            if self.category == 'B / E':
                #--SGN
                value_1 = self.fvi[i] / bolt.SRb
                comment[i] = 'Svd/SRb = %s/%s) = %s { SGN docisk do krawedzi otworow }' % (self.fvi[i], bolt.SRb, value_1)
                #---
                value_2 = (self.fvi[i] / bolt.SRv)**2.0 + (self.fzi[i] / bolt.SRt)**2.0 
                comment[i] += '\n'
                comment[i] += '(Svd/SRv)^2 + (Std/SRt)^2 = (%s/%s)^2 + (%s/%s)^2 = %s { SGN zerwanie sruby}' % (self.fvi[i], bolt.SRv, self.fzi[i], bolt.SRt, value_2)    
                #--SGU  
                if bolt.SRs != 0 * u.kN:
                    value_3 = (self.fvi[i]/self.gamma) / bolt.SRs
                else:
                    value_3 = float('+inf') * (u.kN / u.kN)
                comment[i] += '\n'
                comment[i] += 'Svk/SRs = %s/%s = %s { SGU poslizg styku}' % (self.fvi[i]/self.gamma, bolt.SRs, value_3)
                #---
                value_4 = (self.fzi[i]/self.gamma) / bolt.SRr
                comment[i] += '\n'
                comment[i] += 'Stk/SRr = %s/%s = %s { SGU rozwarcie styku}' % (self.fzi[i]/self.gamma, bolt.SRr, value_4)
                #---
                value[i] = max(value_1, value_2, value_3, value_4)
            #--------------------
            if self.category == 'C / F':
                #--SGN
                value_1 = self.fvi[i] / bolt.SRb
                comment[i] = 'Svd/SRb = %s/%s) = %s { SGN docisk do krawedzi otworow }' % (self.fvi[i], bolt.SRb, value_1)
                #---
                value_2 = (self.fvi[i] / bolt.SRv)**2.0 + (self.fzi[i] / bolt.SRt)**2.0 
                comment[i] += '\n'
                comment[i] += '(Svd/SRv)^2 + (Std/SRt)^2 = (%s/%s)^2 + (%s/%s)^2 = %s { SGN nosnosc sruby}' % (self.fvi[i], bolt.SRv, self.fzi[i], bolt.SRt, value_2)    
                #---
                if bolt.SRs != 0 * u.kN:
                    value_3 = self.fvi[i] / bolt.SRs
                else:
                    value_3 = float('+inf') * (u.kN / u.kN)
                comment[i] += '\n'
                comment[i] += 'Svd/SRs = %s/%s = %s { SGN poslizg styku}' % (self.fvi[i], bolt.SRs, value_3)
                #---
                value_4 = self.fzi[i] / bolt.SRr
                comment[i] += '\n'
                comment[i] += 'Std/SRr = %s/%s = %s { SGN rozwarcie styku}' % (self.fzi[i], bolt.SRr, value_4)
                #---
                value[i] = max(value_1, value_2, value_3, value_4)
            #--------------------
        for i in value:
            if i > 1:
                self.capacity_global = False
        return None
        
    def set_category(self, newcategory='C / F'):
        newcategory = str(newcategory)
        if newcategory in self.availale_categories:
            self.category = newcategory
            if not self.is_loadvector_active_for_category('Fx'):
                self.Fx = 0.0 * u.kN
            if not self.is_loadvector_active_for_category('Fy'):
                self.Fy = 0.0 * u.kN
            if not self.is_loadvector_active_for_category('Fz'):
                self.Fz = 0.0 * u.kN
            if not self.is_loadvector_active_for_category('Mx'):
                self.Mx = 0.0 * u.kNm
            if not self.is_loadvector_active_for_category('My'):
                self.My = 0.0 * u.kNm
            if not self.is_loadvector_active_for_category('Mz'):
                self.Mz = 0.0 * u.kNm
        else:
            print 'Category %s not defined!' %newcategory

    def is_loadvector_active_for_category(self, vector='Fx'):
        active_dir = {}
        active_dir['A'] = { 'Fx':True,   'Fy':True,  'Fz':False,  'Mx':False,  'My':False,   'Mz':True}
        active_dir['B'] = { 'Fx':True,   'Fy':True,  'Fz':False,  'Mx':False,  'My':False,   'Mz':True}
        active_dir['C'] = { 'Fx':True,   'Fy':True,  'Fz':False,  'Mx':False,  'My':False,   'Mz':True}
        active_dir['D'] = { 'Fx':False,   'Fy':False,  'Fz':True,  'Mx':True,  'My':True,  'Mz':False}
        active_dir['E'] = { 'Fx':False,   'Fy':False,  'Fz':True,  'Mx':True,  'My':True,  'Mz':False}
        active_dir['F'] = { 'Fx':False,   'Fy':False,  'Fz':True,  'Mx':True,  'My':True,  'Mz':False}
        
        active_dir['A / D'] = { 'Fx':True,   'Fy':True,  'Fz':True,  'Mx':True,  'My':True,  'Mz':True}
        active_dir['B / E'] = { 'Fx':True,   'Fy':True,  'Fz':True,  'Mx':True,  'My':True,  'Mz':True}
        active_dir['C / F'] = { 'Fx':True,   'Fy':True,  'Fz':True,  'Mx':True,  'My':True,  'Mz':True}
        
        return active_dir[self.category][vector]
        
    def bolts_add(self, p=[10.0*u.mm, 10.0*u.mm]):
        self.xi = np.append(self.xi, [p[0]])
        self.yi = np.append(self.yi, [p[1]])
        self.boltclipi.append(copy.deepcopy(self.boltclipi[0]))

    def bolts_delete(self, indexlist=[0, 1]):
        self.xi = np.delete(self.xi, indexlist)
        self.yi = np.delete(self.yi, indexlist)
        for i in indexlist:
            self.boltclipi[i] = None
        while None in self.boltclipi:
            self.boltclipi.remove(None)

    def bolts_move(self, indexlist=[0, 1], vector=[10*u.mm, 10*u.mm]):
        for i in indexlist:
            self.xi[i] += vector[0]
            self.yi[i] += vector[1]

    def bolts_copy(self, indexlist=[0, 1], vector=[10*u.mm, 10*u.mm]):
        for i in indexlist:
            xcord = self.xi[i] + vector[0]
            ycord = self.yi[i] + vector[1]
            self.bolts_add([xcord, ycord])

    def bolts_projection_x(self, indexlist=[0, 1], xcoord = 10*u.mm):
        for i in indexlist:
            self.xi[i] = xcoord

    def bolts_projection_y(self, indexlist=[0, 1], ycoord = 10*u.mm):
        for i in indexlist:
            self.yi[i] = ycoord

    def set_BoltGrade(self, BoltGrade='3.6'):
        for i in self.boltclipi:
            i.set_BoltGrade(BoltGrade)
        
    def set_BoltDim(self, BoltDim='M12'):
        for i in self.boltclipi:
            i.set_BoltDim(BoltDim)
        
    def set_PlateGrade(self, PlateGrade='S235'):
        for i in self.boltclipi:
            i.set_PlateGrade(PlateGrade)
        
    def set_t1(self, t1=10.0*u.mm):
        for i in self.boltclipi:
            i.t1 = t1
        
    def set_t2(self, t2=10.0*u.mm):
        for i in self.boltclipi:
            i.t2 = t2
        
    def set_m(self, m=2):
        for i in self.boltclipi:
            i.m = m
        
    def set_mi(self, mi=0.3):
        for i in self.boltclipi:
            i.mi = mi

    def draw(self, board, load_p=True, load_o=True, plate=True, bolt_forces=True, bolt_capacity=True,):
        #-- P axis system
        board.addLine([-2*u.cm, 0*u.cm], [2*u.cm, 0*u.cm])
        board.addText(  'x', [2*u.cm, 0*u.cm])
        board.addLine([0*u.cm, -2*u.cm], [0*u.cm, 2*u.cm])
        board.addText(  'y', [0*u.cm, 2*u.cm])
        if load_p:
            board.addVectorForce([0*u.cm, 0*u.cm], [self.Fx, self.Fy, self.Fz])
            board.addVectorMoment([0*u.cm, 0*u.cm], [self.Mx, self.My, self.Mz])
        #-- O axis system
        board.addLine([self.O_x - 1*u.cm, self.O_y], [self.O_x + 1*u.cm, self.O_y])
        board.addText(  'xo', [self.O_x + 1*u.cm, self.O_y])
        board.addLine([self.O_x, self.O_y - 1*u.cm], [self.O_x, self.O_y + 1*u.cm])
        board.addText(  'yo', [self.O_x, self.O_y + 1*u.cm])
        if load_o:
            board.addVectorForce([self.O_x, self.O_y], [self.Fox, self.Foy, self.Foz])
            board.addVectorMoment([self.O_x, self.O_y], [self.Mox, self.Moy, self.Moz])
        #-- plate contour
        if plate:
            board.addPolyline([ [self.plate_xpdim, self.plate_ypdim],
                                [self.plate_xpdim, self.plate_yndim],
                                [self.plate_xndim, self.plate_yndim],
                                [self.plate_xndim, self.plate_ypdim],
                                [self.plate_xpdim, self.plate_ypdim]])
        #-- bending Mx rotate axis 
        board.addArrow([-2*u.cm, self.yfip], [2*u.cm, self.yfip], 'yfip', color='green')
        board.addArrow([2*u.cm, self.yfin], [-2*u.cm, self.yfin], 'yfin', color='green')
        #-- bending My rotate axis
        board.addArrow([self.xfip, -2*u.cm], [self.xfip, 2*u.cm], 'xfip', color='green')
        board.addArrow([self.xfin, 2*u.cm], [self.xfin, -2*u.cm], 'xfin', color='green')   
        #-- bolts
        for i in range(len(self.xi)):
            board.set_origin([self.xi[i],self.yi[i]])
            board.addText(str(i+1), [0*u.cm, 0*u.cm], color='black')
            self.boltclipi[i].draw(board)
            if bolt_forces:
                board.addVectorForce([0*u.cm, 0*u.cm], [self.fxi[i], self.fyi[i], self.fzi[i]])
            if bolt_capacity:
                capacity_text = str(round(self.capacity_local_value[i].asNumber(), 2))
                if self.capacity_local_value[i] > 1:
                    capacity_color = 'red'
                else:
                    capacity_color = 'blue'
                board.addText(capacity_text ,[0*u.cm, self.boltclipi[i].d], color = capacity_color)

    def draw_space_control(self, board, min_bolt_space=True, min_space_to_plate_edge=True, max_space_to_profil_edge=True, min_socket_spanner=True, min_flat_spanner=True):
        for i in range(len(self.xi)):
            board.set_origin([self.xi[i],self.yi[i]])
            if min_bolt_space:
                board.addCircle([0*u.cm,0*u.cm], 2.5*self.boltclipi[i].d, color='green')
                board.addText('min bolt space\nr=2.5*d' ,[0*u.cm, -2.5*self.boltclipi[i].d], color = 'green')
            if min_space_to_plate_edge:
                board.addCircle([0*u.cm,0*u.cm], 1.5*self.boltclipi[i].d, color='blue')
                board.addText('min space to plate edge\n r=1.5*d' ,[0*u.cm, -1.5*self.boltclipi[i].d], color = 'blue')
            if max_space_to_profil_edge:
                board.addCircle([0*u.cm,0*u.cm], 1.5*self.boltclipi[i].d, color='blue')
                board.addText('max space to profil edge\nr=1.5*d' ,[0*u.cm, 1.5*self.boltclipi[i].d], color = 'blue')
            if min_socket_spanner:
                Dz_dict = {'M10': 31.5*u.mm, 'M12': 35.5*u.mm, 'M16': 45.0*u.mm, 'M20': 56.0*u.mm, 'M24': 63.0*u.mm, 'M30': 65.0*u.mm}
                Dz = Dz_dict[self.boltclipi[i].Dim]
                text = 'socket spanner' + self.boltclipi[i].Dim + '\n d=' + str(Dz)
                board.addCircle([0*u.cm,0*u.cm], Dz/2, color='red')
                board.addText(text ,[0*u.cm, 1.5*Dz/2], color = 'red')
            if min_flat_spanner:
                w_dict = {'M10': 22*u.mm, 'M12': 23*u.mm, 'M16': 28*u.mm, 'M120': 33*u.mm, 'M24': 35*u.mm, 'M30': 47*u.mm}
                w = w_dict[self.boltclipi[i].Dim]
                text = 'flat spanner' + self.boltclipi[i].Dim + '\n r=' + str(w)
                board.addCircle([0*u.cm,0*u.cm], w, color='blue')
                board.addText(text ,[0*u.cm, -1.0*w], color = 'blue')

# Test if main
if __name__ == '__main__':
    print ('test BoltConnect')
    connection = BoltConnection()
    connection.calculate()
    print '=================================='
    print connection.capacity_local_value
    print connection.capacity_local_comment
    print connection.capacity_global
    if False:
        from strupy.x_graphic.SvgCreator2D import SvgCreator2D 
        SvgBoard = SvgCreator2D()
        SvgBoard.unit = 0.1*u.mm
        SvgBoard.unit_force = 0.1 * u.kN # pre pixel
        SvgBoard.unit_moment = 1.0 * u.kNm # pre pixel
        SvgBoard.scene.viewbox(-150,-150,300,300)
        #path = '/home/lukaszlab/connectionsvg.svg'
        path = 'D:\ython.svg'
        connection.draw(SvgBoard)
        SvgBoard.save(path)
    if False:
        from strupy.x_graphic.AutocadCreator2D import AutocadCreator2D
        AcadBoard = AutocadCreator2D()
        AcadBoard.unit = 1.0*u.mm
        AcadBoard.unit_force = 0.3 * u.kN # pre pixel
        AcadBoard.unit_moment = 1.0 * u.kNm # pre pixel
        connection.draw(AcadBoard)
    
        from strupy.steel.SteelSection import SteelSection
        section = SteelSection()
        AcadBoard.set_origin()
        section.set_sectionfrombase('IPE 120')
        section.draw_contour(AcadBoard)
    if False:
        import sys
        from PyQt4 import QtGui
        from strupy.x_graphic.PyqtSceneCreator2D import PyqtSceneCreator2D   
        appa = QtGui.QApplication(sys.argv)
        grview = QtGui.QGraphicsView()
        ScienceScene = PyqtSceneCreator2D()
        ScienceScene.set_GraphicsViewObiect(grview)
        ScienceScene.ShowOnGraphicsViewObiect()
        ScienceScene.set_unit(0.3*u.mm)
        ScienceScene.unit_force = 0.1 * u.kN
        ScienceScene.unit_moment = 0.002 * u.kNm
        connection.draw(ScienceScene)
        #---
        ScienceScene.set_origin([0*u.cm, 0*u.cm])
        from strupy.steel.SteelSection import SteelSection
        section = SteelSection()
        section.set_sectionfrombase('IPE 120')
        section.draw_contour(ScienceScene)
        #---
        sys.exit(appa.exec_())