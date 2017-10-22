'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-02-04
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

import sys
import math

import numpy as np
from PyQt4 import QtGui, QtCore

import strupy.units as u

from BaseCreator2D import BaseCreator2D
    
class PyqtSceneCreator2D(BaseCreator2D):
    def __init__(self):
        BaseCreator2D.__init__(self)
        self.scene = QtGui.QGraphicsScene()
    #---------------------------------------------
    def addLine(self, p1, p2, color='black'):
        pen = eval('QtCore.Qt.%s' %color)
        p1 = self.dimtopixels(p1)
        p2 = self.dimtopixels(p2)
        self.scene.addLine(p1[0], -p1[1], p2[0], -p2[1], pen)
        
    def addText(self, text, p, color='black'):
        pen = eval('QtCore.Qt.%s' %color)
        p = self.dimtopixels(p)
        item = self.scene.addText(text) # item is QGraphicsTextItem Class
        item.setFont(QtGui.QFont("", 8, 40, True)) # (self, QString family, int pointSize = -1, int weight = -1, bool italic = False)
        item.setPos(p[0], -p[1])
        item.setDefaultTextColor(pen)
        
    def addCircle(self, p, r, color='black'):
        pen = eval('QtCore.Qt.%s' %color)
        p = self.dimtopixels(p)
        r = self.dimtopixels(r)
        self.scene.addEllipse(p[0] - r, -(p[1] + r), 2 * r, 2 * r, pen)
    #---------------------------------------------
    def set_GraphicsViewObiect(self, somegraphicsView):
        self.graphicsView = somegraphicsView
    
    def clearScene(self):
        self.scene.clear()

    def ShowOnGraphicsViewObiect(self):
        self.graphicsView.setScene(self.scene)
        self.graphicsView.show()

#----Test if main
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    grview = QtGui.QGraphicsView()
    #----
    ScienceScene = PyqtSceneCreator2D()
    ScienceScene.set_GraphicsViewObiect(grview)
    ScienceScene.ShowOnGraphicsViewObiect()
    #----
    ScienceScene.set_unit(1*u.mm)
    p1 = [0*u.cm,0*u.mm]
    p2 = [10*u.cm, 10*u.cm]
    #ScienceScene.addLine(p1, p2)
    p3 = [4*u.cm, 4*u.mm]
    p4 = [-10*u.cm, -10*u.mm]
    #ScienceScene.addLine(p3, p4)
    ScienceScene.addText('p1', p1)
    ScienceScene.addText('p2', p2)
    ScienceScene.addRect(p1, p2)
    ScienceScene.addCircle([0*u.cm,0*u.mm], 50*u.mm, 'blue')
    #ScienceScene.set_origin([150*u.mm, 100*u.mm])
    ScienceScene.showgrid()
    #ScienceScene.addCircle(p1, 100*u.mm)
    #ScienceScene.addCircle([0*u.cm,0*u.mm], 100*u.mm)
    #ScienceScene.addArrow([200*u.cm,100*u.cm], [200*u.cm, 200*u.cm])
    #ScienceScene.set_origin([300*u.mm, 150*u.mm])
    #ScienceScene.addVector([110*u.mm,110*u.mm], [100*u.mm,-100*u.mm])
    #ScienceScene.set_origin([150*u.mm, 150*u.mm])
    #ScienceScene.addCircle([0*u.mm,0*u.mm], 100*u.mm)
    ScienceScene.addRegpoly([100*u.mm,100*u.mm], 100*u.mm, 6)
    ScienceScene.addVectorForce()
    ScienceScene.addVectorMoment()
    ScienceScene.addPolyline([p1, p2, p3, p4], 'blue')
    #----
    #from strupy.steel.SectionBase import SectionBase
    #base = SectionBase()
    #for i in base.get_database_sectionlistwithtype('HHEA'):
    #    print i
    #    base.draw_sectiongeometry(ScienceScene, i)
    #---
    sys.exit(app.exec_())