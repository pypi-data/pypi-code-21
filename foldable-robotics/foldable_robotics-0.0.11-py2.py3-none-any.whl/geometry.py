# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 08:14:35 2016

@author: daukes
"""
import numpy
import math

def length(v1):
    v1 = numpy.array(v1)
    l = (v1.dot(v1))**.5
    return l
    
def planar_angle(v1,v2):
    v1 = numpy.array(v1)
    v2 = numpy.array(v2)
    sint = numpy.cross(v1,v2)
    cost = numpy.dot(v1,v2)
    t = math.atan2(sint,cost)
    return t

def interior_angle(v1,v2):
    v1 = numpy.array(v1)
    v2 = numpy.array(v2)
    sint = numpy.cross(v1,v2)
    sint = length(sint)
    cost = numpy.dot(v1,v2)
    t = math.atan2(sint,cost)
    return t
    
def map_line(p1,p2,p11,p22):
    p1 = numpy.array(p1)
    p2 = numpy.array(p2)
    p11 = numpy.array(p11)
    p22 = numpy.array(p22)
    
    v1 = p2-p1
    v2 = p22-p11
    
    l1=length(v1)
    l2=length(v2)

    scale = l2/l1
    rotate = angle(v1,v2)
    translate = p11-p1
    return translate,rotate,scale