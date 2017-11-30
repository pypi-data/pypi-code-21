# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import sympy
import pynamics
from pynamics.name_generator import NameGenerator

class Variable(sympy.Symbol,NameGenerator):
    def __new__(self,name=None):
        
        name = name or self.generate_name()
        
        obj = sympy.Symbol.__new__(self,name)
        pynamics.addself(obj,name)
        return obj

class Constant(sympy.Symbol,NameGenerator):
    def __new__(self,value=None,name=None,system = None):

        name = name or self.generate_name()

        system = system or pynamics.get_system()

        obj = sympy.Symbol.__new__(self,name)
        obj.value = value
        system.add_constant(obj)
        if value is not None:
            system.add_constant_value(obj,value)
        pynamics.addself(obj,name)
        return obj

class Differentiable(sympy.Symbol,NameGenerator):
    def __new__(cls,name=None,system = None,limit = 3,ii=0,ini = None):

        system = system or pynamics.get_system()

        name = name or cls.generate_name()

        differentiables = []

        for kk,jj in enumerate(range(ii,limit)):
            

            if kk==0:
                subname = name
                variable = sympy.Symbol.__new__(cls,subname)
            else:
                subname = name+'_'+'d'*kk
                variable = sympy.Symbol.__new__(cls,subname)

            system.add_q(variable,jj)
            differentiables.append(variable)
            pynamics.addself(variable,subname)

        for kk,(a,a_d) in enumerate(zip(differentiables[:-1],differentiables[1:])):
            system.add_derivative(a,a_d)

            if ini is not None:
                system.set_ini(a,ini[kk])
                
        return differentiables 

