'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2015-07-01

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

import strupy.units as u

default_diameterlist=[4.5*u.mm,6*u.mm, 10*u.mm, 12*u.mm, 14*u.mm, 16*u.mm, 18*u.mm, 20*u.mm, 25*u.mm, 32*u.mm]
default_quantitylist=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
default_spaceinglist=[50*u.mm, 75*u.mm, 100*u.mm, 150*u.mm, 200*u.mm, 250*u.mm, 250*u.mm, 300*u.mm, 350*u.mm, 400*u.mm]


def area_diameter (diameter=12.0*u.mm):
    return (3.1415*diameter**2/4.0).asUnit(u.cm2)
 

def ui_area_diameter (required_area=0*u.cm2, diameter=default_diameterlist):
    import Tkinter
    def callback(x):
        global area, selected_diameter
        area=area_diameter(diameter[x])
        selected_diameter=diameter[x]
        root.quit()
        root.destroy()
    root = Tkinter.Tk()
    for x in xrange(len(diameter)):
        for y in xrange(1):
            tmp_area=area_diameter(diameter[x])
            Tkinter.Button(root, 
                text= '#'+str(diameter[x])+'\n'+str(area_diameter(diameter[x])),  
                command=lambda x=x : callback(x), bg = bgcolor(required_area,tmp_area), width=18).grid(row=y, column=x)
    root.mainloop()
    return [area, selected_diameter]


def area_diameter_quantity (diameter=12.0*u.mm, quantity=10.0):
    return (area_diameter(diameter)*quantity).asUnit(u.cm2)
 
        
def ui_area_diameter_quantity (required_area=0*u.cm2, diameter=default_diameterlist, quantity=default_quantitylist):
    import Tkinter
    def callback(x, y):
        global area, selected_diameter, selected_quantity
        area=area_diameter_quantity(diameter[x], quantity[y])
        selected_diameter=diameter[x]
        selected_quantity=quantity[y]
        root.quit()
        root.destroy()
    root = Tkinter.Tk()
    for x in xrange(len(diameter)):
        for y in xrange(len(quantity)):
            tmp_area=area_diameter_quantity(diameter[x], quantity[y])
            Tkinter.Button(root, 
                text= str(quantity[y])+'#'+str(diameter[x])+'\n'+str(area_diameter_quantity(diameter[x], quantity[y])),  
                command=lambda x=x, y=y : callback(x, y), bg = bgcolor(required_area,tmp_area), width=18).grid(row=y, column=x)
    root.mainloop()
    return [area, selected_diameter, selected_quantity]
  
    
def area_diameter_spaceing_perdist (diameter=12.0*u.mm, perdist=100.0*u.cm, spaceing=100.0*u.mm):
    return (area_diameter(diameter)*perdist/spaceing).asUnit(u.cm2)

    
def ui_area_diameter_spaceing_perdist (required_area=0*u.cm2, perdist=100.0*u.cm, diameter=default_diameterlist, spaceing=default_spaceinglist):
    import Tkinter
    def callback(x, y):
        global area, selected_diameter, selected_spaceing
        area=area_diameter_spaceing_perdist(diameter[x], perdist, spaceing[y])
        selected_diameter=diameter[x]
        selected_spaceing=spaceing[y]
        root.quit()
        root.destroy()
    root = Tkinter.Tk()
    for x in xrange(len(diameter)):
        for y in xrange(len(spaceing)):
            tmp_area=area_diameter_spaceing_perdist(diameter[x], perdist, spaceing[y])
            Tkinter.Button(root, 
                text= '#'+str(diameter[x])+' every '+str(spaceing[y])+ '\n per ' +str(perdist)+'\n'+str(area_diameter_spaceing_perdist(diameter[x], perdist, spaceing[y])),  
                command=lambda x=x, y=y : callback(x, y), bg = bgcolor(required_area,tmp_area), width=22).grid(row=y, column=x)
    root.mainloop()
    return [area, selected_diameter, selected_spaceing]


def bgcolor(x,y):
    if x>y:
        return 'red'
    else:
        return 'grey'

# Test if main
if __name__ == '__main__':
    print area_diameter()
    print area_diameter_quantity()
    print area_diameter_spaceing_perdist()
    print ui_area_diameter(1*u.cm2)
    print ui_area_diameter_quantity(40*u.cm2)
    print ui_area_diameter_spaceing_perdist(13*u.cm2)
