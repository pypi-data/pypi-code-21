# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from .class_algebra import ClassAlgebra
from . import geometry
import matplotlib.pyplot as plt
#from .iterable import Iterable
from .layer import Layer
import numpy
from idealab_tools.iterable import Iterable

class WrongNumLayers(Exception):
    pass

class Laminate(Iterable,ClassAlgebra):
    def __init__(self, *layers):
        self.layers = list(layers)
        self.id = id(self)

    def copy(self,identical = True):
        new = type(self)(*[layer.copy(identical) for layer in self.layers])
        if identical:        
            new.id = self.id
        return new

    def export_dict(self):
        d = {}
        d['layers'] = [layer.export_dict() for layer in self.layers]
        d['id'] = self.id
        return d

    @classmethod
    def import_dict(cls,d):
        new = cls(*[Layer.import_dict(item) for item in d['layers']])
        new.id = d['id']
        return new

    def plot(self,new=False):
        import matplotlib.cm
        cm = matplotlib.cm.plasma
        l = len(self.layers)     
        colors = numpy.array([cm(ii/(l-1)) for ii in range(l)])
        colors[:,3] = .25
        colors = [tuple(item) for item in colors]
        if new:
            plt.figure()
        for layer,color in zip(self.layers,colors):
            layer.plot(color = color)

    def plot_layers(self):
        import matplotlib.cm
        cm = matplotlib.cm.plasma
        l = len(self.layers)        
        for ii,geom in enumerate(self.layers):
            plt.figure()
            geom.plot(color = cm((ii)/(l)))
    
    @property
    def list(self):
        return self.layers

    def binary_operation(self,function_name,other,*args,**kwargs):
        if len(self.layers)!=len(other.layers):
            raise(WrongNumLayers())
        else:
            layers = []
            for layer1,layer2 in zip(self.layers,other.layers):
                function = getattr(layer1,function_name)
                layers.append(function(layer2))
            return type(self)(*layers)

    def unary_operation(self,function_name,*args,**kwargs):
            layers = []
            for layer1 in self.layers:
                function = getattr(layer1,function_name)
                layers.append(function(*args,**kwargs))
            return type(self)(*layers)
            
    def union(self,other):
        return self.binary_operation('union',other)

    def difference(self,other):
        return self.binary_operation('difference',other)

    def symmetric_difference(self,other):
        return self.binary_operation('symmetric_difference',other)

    def intersection(self,other):
        return self.binary_operation('intersection',other)
    
    def buffer(self,*args,**kwargs):
        return self.unary_operation('buffer',*args,**kwargs)

    def dilate(self,*args,**kwargs):
        return self.unary_operation('dilate',*args,**kwargs)

    def erode(self,*args,**kwargs):
        return self.unary_operation('erode',*args,**kwargs)

    def translate(self,*args,**kwargs):
        return self.unary_operation('translate',*args,**kwargs)
        
    def rotate(self,*args,**kwargs):
        return self.unary_operation('rotate',*args,**kwargs)

    def scale(self,*args,**kwargs):
        return self.unary_operation('scale',*args,**kwargs)

    def affine_transform(self,*args,**kwargs):
        return self.unary_operation('affine_transform',*args,**kwargs)

    def simplify(self,*args,**kwargs):
        return self.unary_operation('simplify',*args,**kwargs)

    def map_line_stretch(self,*args,**kwargs):
        import foldable_robotics.manufacturing
        return foldable_robotics.manufacturing.map_line_stretch(self,*args,**kwargs)
        
    def export_dxf(self,name):
        for ii,layer in enumerate(self.layers):
            layername = name+str(ii)
            layer.export_dxf(layername)
            
    def mesh_items(self,material_properties):
        import matplotlib.cm as cm
        import pyqtgraph.opengl as gl

        z = 0
        vs = []
        cs = []

        for ii,(layer,mp) in enumerate(zip(self,material_properties)):
            v,c = layer.mesh_items_inner(z+mp.thickness/2,mp.color)
            vs.append(v)
            cs.append(c)
            z+=mp.thickness
            
        verts_outer = numpy.vstack(vs)
        colors_outer = numpy.vstack(cs)

        mi= gl.GLMeshItem(vertexes=verts_outer,vertexColors=colors_outer,smooth=False,shader='balloon',drawEdges=False)

        return mi

    def mass_properties(laminate,material_properties):
        volume = 0
        mass = 0
        z=0
        centroid_x=0
        centroid_y=0
        centroid_z=0
        for ii,layer in enumerate(laminate):
            bottom = z
            top = z+material_properties[ii].thickness
            area=0
    
            area_i,volume_i,mass_i,centroid_i = layer.mass_props(material_properties[ii],bottom,top)

            centroid_x_i,centroid_y_i,centroid_z_i = centroid_i
            area+=area_i
            volume+=volume_i
            mass+=mass_i

            centroid_x += centroid_x_i*mass_i
            centroid_y += centroid_y_i*mass_i
            centroid_z += centroid_z_i*mass_i

            z=top
        
        centroid_x /= mass
        centroid_y /= mass
        centroid_z /= mass
        centroid = (centroid_x,centroid_y,centroid_z)
        
        I=numpy.zeros((3,3))
        bottom = 0
        for ii,layer in enumerate(laminate):
            cn = numpy.array(centroid)                
            I+=layer.inertia(cn,bottom,material_properties[ii])
            bottom += material_properties[ii].thickness
            
        return mass,volume,centroid,I
        
        