'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2016-05-20
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
'''

import math

import strupy.units as u
    
class BaseCreator2D():
    def __init__(self):
        self.scene = None
        self.unit = 5.0 * u.mm # pre pixel
        self.unit_force = 1.0 * u.kN # pre pixel
        self.unit_moment = 0.2 * u.kNm # pre pixel
        self.origin = [0*u.mm, 0*u.mm] 
        #---
        self.availablecolors = ['black', 'red', 'blue', 'green', 'yellow']
    #---------------------------------------------
    def set_unit(self, newunit=10*u.mm):
        self.unit = newunit
    
    def set_origin(self, neworigin=[0*u.mm, 0*u.mm]):
        self.origin = neworigin

    def move_origin(self, dx = 0*u.mm, dy = 0*u.mm):
        self.origin = [self.origin[0] + dx, self.origin[1] + dy]
        
    def change_unit(self, value=2*u.mm):
        if not (self.unit + value) <= 0.1*u.mm:
            self.unit += value

    def change_unit_force(self, value=0.01*u.kN):
        if not (self.unit_force + value) <= 0.1*u.kN:
            self.unit_force += value

    def change_unit_moment(self, value=0.3*u.kNm):
        if not (self.unit_moment + value) <= 0.01*u.kNm:
            self.unit_moment += value
    
    def dimtopixels(self, dim):
        if type(dim) is list:
            dim = [dim[0] + self.origin[0], dim[1] + self.origin[1]]
            pixels = []
            for i in dim :
                pixels.append((i / self.unit).asNumber())
        else:
            pixels = (dim / self.unit).asNumber()
        return pixels 
        
    def forcetodim(self, force):
        if type(force) is list:
            dim = []
            for i in force :
                dim.append((i / self.unit_force).asNumber() * self.unit)
        else:
            dim = (force / self.unit_force).asNumber() * self.unit
        return dim

    def momenttodim(self, moment):
        if type(moment) is list:
            dim = []
            for i in moment :
                dim.append((i / self.unit_moment).asNumber() * self.unit)
        else:
            dim = (moment / self.unit_moment).asNumber() * self.unit
        return dim
    #---------------------------------------------
    def addLine(self, p1, p2, color = 'black'):
        print 'addLine base function'
        
    def addText(self, text, p, color = 'black'):
        print 'addText base function'

    def addCircle(self, p, r, color = 'black'):
        print 'addCircle base function'
    #---------------------------------------------
    def addRect(self, p1, p3, color='black'):
        p1 = p1
        p2 = [p3[0], p1[1]]
        p3 = p3
        p4 = [p1[0], p3[1]]
        self.addLine(p1, p2, color=color)
        self.addLine(p2, p3, color=color)
        self.addLine(p3, p4, color=color)
        self.addLine(p4, p1, color=color)
        
    def addPolyline(self, plist, color='black'):
        for i in range(len(plist)-1):
            self.addLine(plist[i], plist[i+1], color=color)
    
    def addRegpoly(self, p, r, side_num, color = 'black'):
        pi = math.pi
        contourpoints = [   [p[0] + r*math.cos(i/float(side_num)*2*pi), 
                            p[1] + r*math.sin(i/float(side_num)*2*pi)] for i in range(0, side_num+1)]
        self.addPolyline(contourpoints, color=color)

    def addArrow(self, p1, p2, text = 'ArrSometext', color = 'black'):
        self.addLine(p1, p2, color=color)
        ptext = [0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1])]
        self.addText(text, ptext, color=color)
        #---drawing arrow
        v = [p2[0] - p1[0], p2[1] - p1[1]]
        len = (v[0]**2 + v[1]**2)**0.5
        v = [self.unit*5.0*v[0]/len, self.unit*5.0*v[1]/len] 
        self.addLine(p2, [p2[0]-v[1]-2.5*v[0], p2[1]+v[0]-2.5*v[1]], color=color)
        self.addLine(p2, [p2[0]+v[1]-2.5*v[0], p2[1]-v[0]-2.5*v[1]], color=color)

    def addVector(self, p, v, text = 'Sometext', color = 'black'):
        p1 = p
        p2 = [p[0] + v[0], p[1] + v[1]]
        self.addArrow(p1, p2, text, color=color)

    def addVectorForce(self, p=[100*u.mm,100*u.mm], F = [150.0*u.kN, 50.0*u.kN, 10.0*u.kN], color='red'): #F - [Fx, Fy, Fz]
        Fz = F.pop()
        v = self.forcetodim(F)
        p1 = p
        Fxy = (F[0]**2 + F[1]**2)**0.5
        if not Fxy == 0*u.kN:
            self.addVector(p1, v, str(Fxy), color=color)
        if not Fz == 0*u.kN:
            self.addCircle(p1, 8.0 * self.unit, color=color)
            self.addText(str(Fz), [p1[0], p1[1]+25.0 * self.unit], color=color)
            if Fz > 0*u.kN:
                self.addCircle(p1, 5.0 * self.unit, color=color)
                self.addCircle(p1, 2.0 * self.unit, color=color)
        
    def addVectorMoment(self, p=[200*u.mm,200*u.mm], M = [-150.0*u.kNm, 50.0*u.kNm, 0.0*u.kNm], color='blue'): #M - [Mx, My, Mz]
        Mz = M.pop()
        v = self.momenttodim(M)
        p1 = p
        Mxy = (M[0]**2 + M[1]**2)**0.5
        if not Mxy == 0*u.kNm:
            self.addVector(p1, v, str(Mxy), color=color)
            self.addVector(p1, [0.8*v[0], 0.8*v[1]], '', color=color)
        if not Mz == 0*u.kNm:
            self.addRegpoly(p1, 9.0 * self.unit, 5, color=color)
            self.addText(str(Mz), p1, color=color)
            if Mz > 0*u.kNm:
                self.addRegpoly(p1, 5.0 * self.unit, 5, color=color)
                self.addRegpoly(p1, 2.0 * self.unit, 5, color=color)

    def showgrid(self, dist=50*u.mm, xrange=300*u.mm, yrange=800*u.mm):
        xnum = int(round(xrange/dist))
        ynum = int(round(yrange/dist))
        for xi in range(-xnum, xnum+1):
            for yi in range(-ynum, ynum+1):
                self.addLine([xi*dist, yi*dist], [xi*dist, yi*dist])
        self.addText(str(dist)+' grid', [-xrange, -0.9*yrange])
        
#----Test if main
if __name__ == "__main__":
    Creator = BaseCreator2D()
    pass