'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.4 date 2017-11-17

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

from MaterialSteel import MaterialSteel

from strupy.steel.SectionBase import SectionBase
import strupy.steel.database_sections.sectiontypes as sectiontypes

class SteelSection(MaterialSteel):

    __base = SectionBase()
    import section_resistance as __sectionresistance
    import section_parameters as __section_parameters

    def __init__(self):
        print ('SteelSection init')
        MaterialSteel.__init__(self)
        #---
        self.comment = 'No commenent'
        #---
        #sectionparameters.....
        #---
        self.set_sectionfrombase()
        
    @property
    def _f_thickness(self):
        return max(self.t_w, self.t_f)
    @property
    def f_y(self): # -yield strength
        return MaterialSteel.f_y(self, self._f_thickness)
    @property
    def f_u(self): # -ultimate strength
        return MaterialSteel.f_u(self, self._f_thickness)
        
    @property
    def i_y(self):
        return (self.I_y / self.A)**0.5
    @property
    def i_z(self):
        return (self.I_z / self.A)**0.5
   
    @property
    def _parameters_data(self):
        return self.__section_parameters.get_parameters(self.figuregroup_id, self.f_y, self.h, self.b, self.t_w, self.t_f, self.r_a, self.r_s)
    @property
    def class_comp(self): # -section class for uniform compression
        return self._parameters_data['class_comp']
    @property
    def class_bend_y(self): # -section class for y bending
        return self._parameters_data['class_bend_y']          
    @property
    def class_bend_z(self):# -section class for x bending
        return self._parameters_data['class_bend_z']

    @property
    def chi_wz(self):
        return self._parameters_data['chi_wz'] 
    @property
    def chi_wy(self):
        return self._parameters_data['chi_wy']       

    @property
    def N_tRd(self): # -design tension resistance
        return self.__sectionresistance.N_tRd(self.A, self.f_y)
    @property
    def N_tRk(self): # -characteristic resistance to normal force in tension
        return self.__sectionresistance.N_tRk(self.A, self.f_y)
        
    @property
    def N_cRd(self): # -design compression resistance
        return self.__sectionresistance.N_cRd(self.A, self.f_y, self.class_comp)
    @property
    def N_cRk(self): # -characteristic resistance to normal force in compression
        return self.__sectionresistance.N_cRk(self.A, self.f_y, self.class_comp)
        
    @property
    def M_ycRd(self): # -design resistance for y bending
        return self.__sectionresistance.M_cRd(self.W_ply, self.W_ely, self.f_y, self.class_bend_y)
    @property
    def M_yRk(self): # -characteristic resistance for y bending
        return self.__sectionresistance.M_Rk(self.W_ply, self.W_ely, self.f_y, self.class_bend_y)
        
    @property
    def M_zcRd(self): # -design resistance for z bending
        return self.__sectionresistance.M_cRd(self.W_plz, self.W_elz, self.f_y, self.class_bend_z)
    @property
    def M_zRk(self): # -characteristic resistance for z bending
        return self.__sectionresistance.M_Rk(self.W_plz, self.W_elz, self.f_y, self.class_bend_z)
        
    @property
    def V_ycRd(self): # -design plastic y shear resistance
        return self.__sectionresistance.V_cRd(self.A_yv, self.chi_wy, self.f_y)
    @property
    def V_zcRd(self): # -design plastic z shear resistance
        return self.__sectionresistance.V_cRd(self.A_zv, self.chi_wy, self.f_y)

    def set_sectionfrombase(self, sectname='IPE 270'):
        param = SteelSection.__base.get_sectionparameters(sectname)
        #------------
        self.sectname=param['sectionname']
        self.figure=param['figure']
        self.figuregroup_id  = sectiontypes.FigureGroupId(self.figure)
        self.figuregroup_name  = sectiontypes.FigureGroupName(self.figure)
        self.mass = param['mass']
        self.surf = param['surf']
        self.h = param['h']
        self.b = param['b']
        self.t_w = param['ea']
        self.t_f = param['es']
        self.r_a = param['ra']
        self.r_s = param['rs']
        self.gap = param['gap']
        self.A = param['Ax']
        self.A_yv = param['Ay']
        self.A_zv = param['Az']
        self.I_t = param['Ix']
        self.I_y = param['Iy']
        self.I_z = param['Iz']
        self.I_w = param['Iomega']
        self.v_y = param['vy']
        self.v_py = param['vpy']
        self.v_z = param['vz']
        self.v_pz = param['vpz']
        self.W_ply = param['Wply']
        self.W_plz = param['Wplz']
        self.W_ely = param['Wy']
        self.W_elz = param['Wz']
        self.W_tors = param['Wtors']
        self.gamma = param['gamma']
        #----some sections in sectionbase has W_pl=0 so to solve it:
        self.W_ply = max(self.W_ply, self.W_ely)
        self.W_plz = max(self.W_plz, self.W_elz)       
        #---
        self.sectioncontourpoints = SteelSection.__base.get_sectioncontourpoints(sectname)

    def set_sectionbase_speedmode(self, speedmode=2):
        SteelSection.__base.set_speedmode(speedmode)
        
    def draw_contour(self, SomeGeometryObiect, annotation=1):
        SteelSection.__base.draw_sectiongeometry(SomeGeometryObiect, self.sectname, annotation)
    
    def __str__(self):
        return 'section string .......'
        
# Test if main
if __name__ == '__main__':
    print ('test RcRecSect')
    sec=SteelSection()
    sec.set_sectionfrombase('IPE 100')
    #print sec.M_ycRd
    sec.set_sectionfrombase('TCAR 100x8')
    sec.set_steelgrade('S450')
    print sec.sectname
    print sec.steelgrade
    print sec._parameters_data
    print sec.N_tRd
    print sec.N_tRk
    print sec.N_cRd
    print sec.N_cRk
    print sec.M_ycRd
    print sec.M_yRk
    print sec.M_zcRd
    print sec.M_zRk
    print sec.V_ycRd
    print '-------------------'
    sec.set_sectionbase_speedmode(1)
    sec.set_sectionbase_speedmode(2)