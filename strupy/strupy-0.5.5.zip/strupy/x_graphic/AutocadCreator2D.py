'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-02-04
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

from pyautocad import Autocad, APoint
import svgwrite
from numpy import array
from PyQt4 import QtGui

import strupy.units as u
from BaseCreator2D import BaseCreator2D
    
class AutocadCreator2D(BaseCreator2D):
    def __init__(self):
        BaseCreator2D.__init__(self)
        self.scene = Autocad(create_if_not_exists=True)
        self.scene.prompt("AutocadCreator2D conected..")
    #---------------------------------------------
    def addLine(self, p1, p2, color='black'):
        p1 = self.dimtopixels(p1)
        p2 = self.dimtopixels(p2)
        p1 = APoint(p1[0], p1[1])
        p2 = APoint(p2[0], p2[1])
        self.scene.model.AddLine(p1, p2)
        
    def addText(self, text, p, color='black'):
        p = self.dimtopixels(p)
        p = APoint(p[0], p[1])       
        self.scene.model.AddText(text, p, 2.5)
        
    def addCircle(self, p, r, color='black'):
        p = self.dimtopixels(p)
        p = APoint(p[0], p[1]) 
        r = self.dimtopixels(r)
        self.scene.model.AddCircle(p, r)
    #---------------------------------------------
#----Test if main
if __name__ == "__main__":
    AcadBoard = AutocadCreator2D()
    p1 = [550*u.mm, -100*u.mm]
    p2 = [400*u.mm, -200*u.mm]
    AcadBoard.addLine(p1, p2)
    AcadBoard.addText('Ala ma dfdkotat', p1)
    AcadBoard.addCircle(p1, 40*u.mm)
    AcadBoard.addCircle([0*u.mm, 0*u.mm], 40*u.mm)
   
'''
http://entercad.ru/acadauto.en/
translacja wspolzendynch
https://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/AutoCAD-ActiveX/files/GUID-95E29CF8-9F69-4600-B8AB-94E121E7E6B6-htm.html
'''