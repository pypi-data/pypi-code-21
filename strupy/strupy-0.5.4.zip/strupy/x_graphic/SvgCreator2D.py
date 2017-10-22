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

import svgwrite
from numpy import array
from PyQt4 import QtGui

import strupy.units as u
from BaseCreator2D import BaseCreator2D
    
class SvgCreator2D(BaseCreator2D):
    def __init__(self):
        BaseCreator2D.__init__(self)
        self.scene = svgwrite.Drawing(size = ('800', '800'))
        
    #---
    def addLine(self, p1, p2, color='black'):
        p1 = self.dimtopixels(p1)
        p2 = self.dimtopixels(p2)
        self.scene.add(self.scene.line( start = (p1[0], -p1[1]), 
                                        end = (p2[0], -p2[1]), 
                                        stroke=color))
        
    def addText(self, text, p, color='black'):
        p = self.dimtopixels(p)
        self.scene.add(self.scene.text( text, 
                                        insert = (p[0], -p[1]), 
                                        fill=color))
        
    def addCircle(self, p, r, color='black'):
        p = self.dimtopixels(p)
        r = self.dimtopixels(r)
        self.scene.add(self.scene.circle(   center = (p[0], -p[1]), 
                                            r = r, fill='none', 
                                            stroke=color))
    #---
    
    def setvievbox(self, center=[0.0*u.mm, 0.0*u.mm], width = 800, high=800, boarder = True):
        center = self.dimtopixels(center)
        self.scene.viewbox(center[0] - width/2, -center[1] - high/2, width, high)
        if boarder:
            self.scene.add(self.scene.rect( insert = (center[0] - width/2, -center[1] - high/2),
                                            size = (width, high),
                                            stroke="black", 
                                            fill = "none"))
        
    def tostring(self):
        return self.scene.tostring()

    def save(self, path):
        svg_file = open(path, "w")
        svg_file.write(self.tostring())
        svg_file.close()

#----Test if main
if __name__ == "__main__":
    SvgBoard = SvgCreator2D()
    path = 'D:\ython.svg'
    
    p1 = [550*u.mm, -100*u.mm]
    p2 = [400*u.mm, -200*u.mm]
    SvgBoard.addLine(p1, p2)
    SvgBoard.addText('Ala ma dfdkotat', p1)
    SvgBoard.addCircle(p1, 40*u.mm)
    SvgBoard.addCircle([0*u.mm, 0*u.mm], 40*u.mm)
    SvgBoard.scene.viewbox()
    SvgBoard.save(path)
    #----------------------------
    import sys
    from PyQt4 import QtGui, QtSvg
    app = QtGui.QApplication(sys.argv) 
    svgWidget = QtSvg.QSvgWidget(path)
    svgWidget.setGeometry(50,50,759,668)
    svgWidget.show()
    sys.exit(app.exec_())
#http://www.perfectxml.com/LearnSVG.asp