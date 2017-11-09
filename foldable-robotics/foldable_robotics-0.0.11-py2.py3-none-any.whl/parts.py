# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 10:49:29 2017

@author: daukes
"""

#import modules from shapely and matplotlib
import shapely.geometry as sg
import matplotlib.pyplot as plt

#import classes from my local modules
from foldable_robotics.laminate import Laminate
from foldable_robotics.layer import Layer
from idealab_tools.geometry.tetrahedron import Tetrahedron
from idealab_tools.geometry.triangle import Triangle
import foldable_robotics.manufacturing
from foldable_robotics.dynamics_info import DynamicsInfo,MaterialProperty,JointProps

def make_five_layer_hinge(width = 1, height = 1):
        #create a layer named box
    box = Layer(sg.box(0,0,1,1))
    
    #initialize layer01 as box, and union with the same box translated several times
    layer01 = box
    layer01 = layer01 | box.translate(1,-1)
    layer01 = layer01.translate(.5,0)
    layer01 = layer01 | layer01.affine_transform([-1,0,0,1,0,0])
#    layer01.plot()
    
    layer34 = layer01.affine_transform([1,0,0,-1,0,0])
    
    hinge = Laminate(layer01,layer01,Layer(),layer34,layer34)
    hinge_hole = Layer(sg.box(-.5,-1,.5,1))
    hinge |= Laminate(hinge_hole,hinge_hole,hinge_hole,hinge_hole,hinge_hole)
    hinge = hinge.affine_transform([.2*width,0,0,.5*height,.5*width,0])
    
    return hinge
#    plt.figure()
#    hinge.plot()
def make_text(text):
    import idealab_tools.text_to_polygons
    p = idealab_tools.text_to_polygons.text_to_polygons(text)
    layers = [Layer(sg.Polygon(item)) for item in p]
    l = Layer()
    for item in layers:
        l ^= item
    return l
    

if __name__=='__main__':
    import foldable_robotics
    foldable_robotics.resolution = 2
    h = make_five_layer_hinge(2,.1)
    h.plot()
    
    l = make_text('Monty Python')
    l=l.scale(.2,.2)
    l.plot(new=True)
    
    b = l.bounding_box()<<1
    b.plot()