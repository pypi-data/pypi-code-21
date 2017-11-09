# -*- coding: utf-8 -*-
"""
Created on Fri May 26 09:16:38 2017

@author: daukes
"""

class MaterialProperty(object):
    def __init__(self,name,color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive,is_flexible):
        self.name = name
        self.color = color
        self.thickness = thickness
        self.E1 = E1
        self.E2 = E2
        self.density = density
        self.poisson = poisson
        self.is_adhesive = is_adhesive
        self.is_rigid = is_rigid
        self.is_conductive = is_conductive
        self.is_flexible = is_flexible
    def copy(self):
        return MaterialProperty(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive,self.is_flexible)
    @classmethod
    def make_n_blank(cls,n,thickness = 1,E1 = 1,E2 = 1,density = 1, poisson = 1,is_adhesive = False, is_rigid = False, is_conductive = False, is_flexible = False ):
        import numpy
        import matplotlib.cm
        cm = matplotlib.cm.plasma
        colors = numpy.array([cm(ii/(n-1)) for ii in range(n)])
        colors[:,3] = .25
        colors = [tuple(item) for item in colors]   
        materials = []
        for ii,color in enumerate(colors):
            materials.append(cls('layer'+str(ii),color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive,is_flexible))
        return materials
    
class JointProps(object):
    def __init__(self,stiffness,damping,preload,limit_neg,limit_pos,z_pos):
        self.stiffness = stiffness
        self.damping = damping
        self.preload = preload
        self.limit_neg = limit_neg
        self.limit_pos = limit_pos
        self.z_pos = z_pos

class DynamicsInfo(object):
    def __init__(self,connected_items,connections,newtonian_ids,material_properties):
        self.connected_items = connected_items
        self.connections = connections
        self.newtonian_ids = newtonian_ids
        self.material_properties = material_properties
        

if __name__=='__main__':
    import yaml
    d = DynamicsInfo(1,2,3,4)
    with open('asdf.yaml','w') as f:
        yaml.dump(d,f)
    
            