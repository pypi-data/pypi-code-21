# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 08:13:05 2016

@author: daukes
"""

import foldable_robotics
from foldable_robotics.laminate import Laminate
from foldable_robotics.layer import Layer
import shapely.geometry as sg
import shapely.ops as so
import matplotlib.pyplot as plt
plt.ion()


def cleanup(input1,value,res):
    return input1.buffer(value,res).buffer(-2*value,res).buffer(value,res)
    
def cleanup2(a,radius):
    c=(a>>radius)<<2*radius
    e=(a&c)
    bb=(a<<10*radius)
    b=bb-a
    d=(b>>radius)<<2*radius
    
    f=(b&d)
    g=bb-f
    
    h = e^g
    
    i = a^h
    return i

def unary_union(laminate):
    result = Layer()
    for layer in laminate:
        result|=layer
    return result

def keepout_laser(laminate):
    result = unary_union(laminate)
    result = [result]*len(laminate)
    new_lam  = Laminate(*result)
    return new_lam 
#
def keepout_mill_up(laminate):
    result = Layer()
    results = []
    for layer in laminate[::-1]:
        result|=layer
        results.append(result.copy())
    new_lam = Laminate(*results)
    new_lam = new_lam[::-1]
    return new_lam

def keepout_mill_down(laminate):
    return keepout_mill_up(laminate[::-1])[::-1]
#
def keepout_mill_flip(laminate):
    dummy1 = keepout_mill_up(laminate)
    dummy2 = keepout_mill_down(laminate)
    dummy3 = dummy1 & dummy2
    return dummy3
#    
def bounding_box(laminate):
    A = keepout_laser(laminate)
    b = so.unary_union(A[0].geoms)
    c = sg.box(*b.bounds)
    result = Layer(c)
    result = [result]*len(laminate)
    new_lam  = Laminate(*result)
    return new_lam 

def not_removable_up(laminate,is_adhesive):
    result = Layer()
    results = []
    for layer in laminate[::-1]:
        result|=layer
        results.append(result.copy())
    new_lam = Laminate(*results)
    new_lam = new_lam[::-1]
    new_lam = modify_up(new_lam,is_adhesive)    

    return new_lam

def not_removable_down(laminate,is_adhesive):
    return not_removable_up(laminate[::-1],is_adhesive[::-1])[::-1]

def not_removable_both(laminate):
    result = Layer()
    for layer in laminate:
        result|=layer
    result = [result]*len(laminate)
    new_lam  = Laminate(*result)
    return new_lam 
    
def modify_up(laminate,is_adhesive):
    laminate = laminate.copy()
    for ii,(test1,test2) in enumerate(zip(is_adhesive[:-1],is_adhesive[1:])):
        if test1 or test2:
            laminate[ii+1] |= laminate[ii]
    return laminate
    
def zero_test(laminate):
    result = keepout_laser(laminate)
    if not result[0].geoms:
        return True
    else:
        return False
        
def support(laminate,keepout_method,width,invalid_width):
    keepout = keepout_method(laminate)
    all_support = (keepout<<width)-keepout
    not_cuttable = keepout-laminate
    not_cuttable_clean= cleanup(not_cuttable,.001,0)
    valid_support = all_support-(not_cuttable_clean<<invalid_width)
    valid_support <<=.001
    return valid_support

def split_laminate_by_geoms(remain):
    l = len(remain)
    all_laminates = []
    for ii,layerfrom in enumerate(remain):
        for jj,geom in enumerate(layerfrom.geoms):
            split_layers = [Layer()]*ii+[Layer(geom)]+[Layer()]*(l-1-ii)
            split= Laminate(*split_layers)
            all_laminates.append(split)
    return all_laminates

def expand_adhesive(laminate,adhesive):
    l = len(laminate)
    expand_up = Laminate(*([Layer()]*l))
    for ii,(layer,test,test2) in enumerate(zip(laminate[:-1],adhesive[:-1],adhesive[1:])):
        if test or test2:
            expand_up[ii+1] = layer.copy()

    expand_down = Laminate(*([Layer()]*l))
    for ii,(layer,test,test2) in enumerate(zip(laminate[1:],adhesive[1:],adhesive[:-1])):
        if test or test2:
            expand_down[ii+1-1] = layer.copy()
            
    result = laminate|expand_up|expand_down
    return result

def find_connected(laminate,adhesive):
    all_laminates = split_laminate_by_geoms(laminate)
    results = []
    while not not all_laminates:
        result = all_laminates.pop(0)
        expanded_result = expand_adhesive(result,adhesive)
        changed=True
        while changed:
            changed=False
            for item in all_laminates:
                if not zero_test(item&expanded_result):
                    result |= item
                    expanded_result = expand_adhesive(result,adhesive)
                    all_laminates.remove(item)
                    changed = True
        results.append(result)
    return results

def map_line_stretch(self,*args,**kwargs):
    import math
    import numpy
    import foldable_robotics.geometry as geometry
    
    p1 = numpy.array(args[0])
    p2 = numpy.array(args[1])
    p3 = numpy.array(args[2])
    p4 = numpy.array(args[3])

    x_axis = numpy.array([1,0])

    pre_rotate = geometry.planar_angle(x_axis,p2-p1)
    post_rotate = geometry.planar_angle(x_axis,p4-p3)
    scale = geometry.length(p4-p3)/geometry.length(p2-p1)

    laminate = self.translate(*(-p1))
    laminate = laminate.rotate(-pre_rotate*180/math.pi,origin=(0,0))
    laminate = laminate.affine_transform([scale,0,0,1,0,0])
    laminate = laminate.rotate((post_rotate)*180/math.pi,origin=(0,0))
    laminate = laminate.translate(*p3)
    return laminate    
    
def modify_device(device,custom_support_line,support_width,support_gap,hole_buffer):
    custom_support = custom_support_line<<support_width/2
    custom_support_hole = (custom_support & ((device<<support_gap)-device))
    custom_support_hole2 = keepout_laser(custom_support_hole<<hole_buffer) - (custom_support_hole<<2*hole_buffer)
    modified_device = device-custom_support_hole2
    custom_cut = keepout_laser(custom_support_hole)
    return modified_device,custom_support,custom_cut

def lines_to_shapely(hinge_lines):
    hinge_line = sg.LineString([(0,0),(1,0)])
    hinge_layer = Layer(hinge_line)
    all_hinges1 = [hinge_layer.map_line_stretch((0,0),(1,0),*toline) for toline in hinge_lines]
    return all_hinges1

def calc_hole(hinge_lines,width,resolution = None):
    resolution = resolution or foldable_robotics.hole_resolution
    all_hinges1= lines_to_shapely(hinge_lines)
    all_hinges11 = [item.dilate(w/2,resolution = resolution) for item,w in zip(all_hinges1,width)]
    
    plt.figure()
    all_hinges3 = []
    for ii,hinge in enumerate(all_hinges11):
        all_hinges2 = Layer()
        for item in all_hinges11[:ii]+all_hinges11[ii+1:]:
            all_hinges2|=item
        all_hinges3.append(hinge&all_hinges2)
    
    all_hinges4 = Layer()
    for item in all_hinges3:
        all_hinges4|=item
    all_hinges4.plot(new=True)
    
    holes = Laminate(*([all_hinges4]*5))
    
    trimmed_lines = [item-all_hinges4 for item in all_hinges1]
    all_hinges = [tuple(sorted(item.geoms[0].coords)) for item in trimmed_lines]
    return holes,all_hinges

if __name__=='__main__':
    pass