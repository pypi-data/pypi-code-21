'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2015-11-29

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
- draw() method added
'''

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcRecSect(MaterialConcrete, MaterialRcsteel):

    def __init__(self):
        print "RcRecSect init"
        MaterialConcrete.__init__(self)
        MaterialRcsteel.__init__(self)
        self.name = 'Noname'
        self.b=0.4*u.m
        self.h=0.8*u.m
        self.ap=5.0*u.cm
        self.an=5.0*u.cm
        self.fip=20.0*u.mm
        self.fin=20.0*u.mm
        self.rysAp=1.0
        self.rysAn=1.0
        self.wlimp=0.3*u.mm
        self.wlimn=0.3*u.mm
 
        self.Ap=0*u.cm2
        self.An=0*u.cm2
        self.comment="No comment"

        self.resist_moment=0
        self.resist_force=0
        self.resist_forcetomoment=0
        self.As_as_forcefunction=0
        self.As_as_momentfunction=0
        self.As_as_forcetomomentfunction=0

    def clear_soverresult(self):
        self.resist_moment=0
        self.resist_force=0
        self.resist_forcetomoment=0
        self.resist_forcetomoment_withcrackcontrol=0
        self.As_as_forcefunction=0
        self.As_as_momentfunction=0
        self.As_as_forcetomomentfunction=0

    def get_sectinfo(self):
        i1=self.get_concreteinfo()
        i2=self.get_rcsteelinfo()
        i3={"b":self.b, "h":self.h, "ap":self.ap, "an":self.an, "Ap":self.Ap, "An":self.An, "comment":self.comment}
        i2.update(i1)
        i3.update(i2)
        return i3
        
    def set_b(self, value):
        self.b=value
        self.clear_soverresult()
    def get_b(self):
        return self.b 

    def set_h(self, value):
        self.h=value
        self.clear_soverresult()
    def get_h(self):
        return self.h

    def set_ap(self, value):
        self.ap=value
        self.clear_soverresult()
    def get_ap(self):
        return self.ap

    def set_an(self, value):
        self.an=value
        self.clear_soverresult()
    def get_an(self):
        return self.an

    def clear_comment(self, value):
        self.comment=None        
    def get_comment(self):
        return self.comment
        
    def plot_resist_forcetomoment(self, sectload=None):
        import matplotlib.pyplot as plt1
        Nrdi=self.resist_forcetomoment['Nrdi'][:]
        Mrdi=self.resist_forcetomoment['Mrdi'][:]
        Nrdi=u.xunumlistvalue(Nrdi, u.kN)
        Mrdi=u.xunumlistvalue(Mrdi, u.kNm)
        plt1.plot(Mrdi, Nrdi, 'r', label='resist')
        if self.rysAn or self.rysAp:
            Nrdi=self.resist_forcetomoment_withcrackcontrol['Nrdi'][:]
            Mrdi=self.resist_forcetomoment_withcrackcontrol['Mrdi'][:]
            Nrdi=u.xunumlistvalue(Nrdi, u.kN)
            Mrdi=u.xunumlistvalue(Mrdi, u.kNm)
            plt1.plot(Mrdi, Nrdi, 'm--', label='crack lim')
        if sectload is not None:
            Nrdi=u.xunumlistvalue(sectload.Nsd, u.kN)
            Mrdi=u.xunumlistvalue(sectload.Msd, u.kNm)
            plt1.plot(Mrdi, Nrdi, 'o',  label='load cases')            
        plt1.xlabel('Mrdi[kN]')
        plt1.ylabel('Nrdi[kNm]')
        plt1.title('resist_forcetomoment')
        plt1.legend()
        plt1.grid(True)
        plt1.show()
        
    def plot_As_as_forcefunction(self):
        import matplotlib.pyplot as plt
        Nsd=self.As_as_forcefunction['Nsdrange'][:]
        Ap=self.As_as_forcefunction['Ap'][:]
        An=self.As_as_forcefunction['An'][:]
        Nsd=u.xunumlistvalue(Nsd, u.kN)
        Ap=u.xunumlistvalue(Ap, u.cm2)
        An=u.xunumlistvalue(An, u.cm2)
        plt.plot(Nsd, Ap, 'r', label='Ap')
        plt.plot(Nsd, An, 'b', label='An')
        plt.xlabel('Nsdrange[kN]')
        plt.ylabel('As[cm2]')
        plt.title('As_as_forcefunction')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=1, borderaxespad=0.)
        plt.grid(True)
        plt.show()
        
    def plot_As_as_momentfunction(self):
        import matplotlib.pyplot as plt
        Msd=self.As_as_momentfunction['Msdrange'][:]
        Ap=self.As_as_momentfunction['Ap'][:]
        An=self.As_as_momentfunction['An'][:]
        Msd=u.xunumlistvalue(Msd, u.kNm)
        Ap=u.xunumlistvalue(Ap, u.cm2)
        An=u.xunumlistvalue(An, u.cm2)
        plt.plot(Msd, Ap, 'r', label='Ap')
        plt.plot(Msd, An, 'b', label='An')
        plt.xlabel('Msdrange[kNm]')
        plt.ylabel('As[cm2]')
        plt.title('As_as_momentfunction')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=1, borderaxespad=0.)
        plt.grid(True)
        plt.show()
    
    def plot_As_as_forcetomomentfunction(self):
        Nsd=self.As_as_forcetomomentfunction['Nsd'][:]
        Msd=self.As_as_forcetomomentfunction['Msd'][:]
        Ap=self.As_as_forcetomomentfunction['Ap'][:]
        An=self.As_as_forcetomomentfunction['An'][:]    
        Nsd=u.xunumlistvalue(Nsd, u.kN)
        Msd=u.xunumlistvalue(Msd, u.kNm)
        Ap=u.xunumlistvalue(Ap, u.cm2)
        An=u.xunumlistvalue(An, u.cm2)
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        surf1 = ax.plot_surface(Nsd, Msd, An, rstride=1, cstride=1)
        surf2 = ax.plot_surface(Nsd, Msd, Ap, rstride=1, cstride=1)
        ax.set_xlabel('Nsd [kN]')
        ax.set_ylabel('Msd [kNm]')
        ax.set_zlabel('An [cm2]')
        ax.set_title('As_as_forcetomomentfunction', fontsize=18)
        plt.show()

    def draw(self, SomeGeometryObiect, annotation=1):
        b = self.b
        h = self.h
        ap = self.ap
        an = self.an
        fip = self.fip
        fin = self.fin
        zero = 0*u.cm
        #---section countour
        SomeGeometryObiect.addRect( [-b/2, h/2], [b/2, -h/2])
        #----side p reinforcement
        SomeGeometryObiect.addRect( [-b/2 + ap - fip/2, h/2 - ap + fip/2], [b/2 - ap + fip/2, h/2 - ap - fip/2])
        #----side n reinforcement
        SomeGeometryObiect.addRect( [-b/2 + an - fin/2, -h/2 + an - fin/2], [b/2 - an + fin/2, -h/2 + an + fin/2])    
        if annotation == 1:
            #---y z axis
            SomeGeometryObiect.addLine([zero, 1.2*h/2], [zero, -1.2*h/2])
            SomeGeometryObiect.addLine([-1.2*b/2, zero], [1.2*b/2, zero])
            #---reinforcement
            SomeGeometryObiect.addText('Ap='+str(self.Ap), [-b/2 + ap, h/2 - ap])
            SomeGeometryObiect.addText('An='+str(self.An), [-b/2 + ap, -h/2 + 2.5*ap])
        
# Test if main
if __name__ == '__main__':
    #----
    class ExampleGeometryObiectForTesting():
        def addLine(self, p1, p2):
            print 'line from ' + str(p1) + ' to ' + str(p2)
        def addText(self, text, p):
            print 'text ' + text + ' a t' + str(p)
        def addRect(self, p1, p2):
            print 'Rectangle from ' + str(p1) + ' to ' + str(p2)
    #----
    print ('test RcRecSect')
    sec=RcRecSect()
    print sec.get_sectinfo()
    scene = ExampleGeometryObiectForTesting()
    sec.draw(scene)
    