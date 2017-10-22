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
import math

import strupy.units as u
from strupy.steel.MaterialSteel import MaterialSteel

from Bolt import Bolt

class BoltClip (Bolt):
    
    _steel = MaterialSteel()
    
    def __init__(self):
        print "BoltConnect init"
        Bolt.__init__(self)
        self.plate_SteelGrade = 'S235'
        self.t1 = 10.0 * u.mm
        self.t2 = 8.0 * u.mm
        self.mi = 0.30
        #---
        self.fd = 310.0 * u.MPa
        self.a = 40.0 * u.mm
        self.a1 = 40.0 * u.mm
        #---
        self.Si = 0 * u.kN
        #---
        self.SRb = None
        self.SRs = None
        #---
        self.report = 'Boltclip report'
        self.calculate()
        
    def calculate(self):
        self.calculatebolt()
        #---SRb
        alfa = min (self.a1 / self.d, self.a/self.d - 0.75 , 2.5)
        sum_t = min (self.t1, self.t2)
        self.SRb = alfa * self.fd * self.d * sum_t
        self.SRb = self.SRb.asUnit(u.kN)
        #---SRs
        alfa_s = 1
        Si = self.Si
        self.SRs =   alfa_s * self.mi * (self.SRt - Si) * self.m
        if  self.SRs < 0*u.kN:
            self.SRs = 0*u.kN
        self.SRs = self.SRs.asUnit(u.kN)
        #----
        self.report = ''
        self.report += 'a = %s, '% self.a
        self.report += 'a1 = %s, '% self.a1
        self.report += 'sum_t = %s, '% sum_t
        self.report += 'alfa = %s \n'% alfa
        self.report += 'mi = %s, '% self.mi
        self.report += 'm = %s, '% self.m
        self.report += 'Si = %s, '% self.Si
        self.report += 'SRs(Si = %s) = %s, '% (self.Si, self.SRs)
        self.report += 'SRb = %s, '% self.SRb
        self.report += 'SRt = %s, '% self.SRt
        self.report += 'SRv = %s, '% self.SRv
        self.report += 'SRr = %s, '% self.SRr
        self.report += 'SRrdyn = %s'% self.SRrdyn
    
    def set_PlateGrade(self, newgrade):
        if newgrade in BoltClip._steel.get_availablesteelgrade():
            self.fd = BoltClip._steel.f_y(max(self.t1, self.t2))
            self.plate_SteelGrade = newgrade
    
    def draw(self, board, annotation=True, axes=False):
        board.addCircle([0*u.cm,0*u.cm], self.d / 2)
        board.addRegpoly([0*u.mm,0*u.mm], 1.7 * self.d / 2, 6)
        if annotation:
            board.addText(self.Dim + '\n' + self.Grade, [0.7 * self.d, 0.7 * self.d])
        if axes:
            size = 1.0 * self.d
            board.addLine([-size, 0*u.mm], [+size, 0*u.mm])
            board.addLine([0*u.mm, -size], [0*u.mm, +size])
# Test if main
if __name__ == '__main__':
    print ('test BoltClip')
    connect = BoltClip()
    #print vars(connect)
    #print vars(connect)
    connect.set_BoltDim('M20')
    print connect.Dim
    print connect.Grade
    connect.calculate()
    print 'SRt =' + str(connect.SRt)
    print 'SRv =' + str(connect.SRv)
    print 'SRr =' + str(connect.SRr)
    print 'SRrdyn =' + str(connect.SRrdyn)
    print 'SRb =' + str(connect.SRb)
    print 'SRs =' + str(connect.SRs) 