# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

import pygmsh as pg
import numpy
import shapely.geometry as sg
import idealab_tools.fea_tetra.fea as fea
from math import pi
import idealab_tools.fea_tetra.mesh_tools as mesh_tools
lcar = 1e-1

#p=  sg.Point(0,0)
#poly = p.buffer(1,resolution = 8)
#poly3 = p.buffer(.5,resolution = 8)
#poly = poly-poly3
poly = sg.box(1,0,2,1)

def find(points,axis,value,tol):
    d = (points[:,axis]-value)
    r = numpy.abs(d)
    filt = (r-value)<tol
    ii = filt.nonzero()[0]
    return ii

def remove_face(triangle,index):
    kk = (numpy.abs((points[triangle,index])-0)<1e-5)
    ll = ((kk.sum(1))!=3)
    
    triangle = triangle[ll]
    return triangle

geom,poly = mesh_tools.shapely_to_pygmsh(poly,lcar)


axis = [0,1,0]
theta = pi/2
point = [0,0,0]

geom.extrude(poly,rotation_axis=axis,point_on_axis=point, angle=theta)
points, cells, point_data, cell_data, field_data = pg.generate_mesh(geom)
#points, cells, point_data, cell_data, field_data = pg.generate_mesh(geom,num_lloyd_steps=2,num_quad_lloyd_steps=0,optimize = False,prune_vertices=False)

tetra = cells['tetra']
triangle= cells['triangle']

triangle = remove_face(triangle,0)
triangle = remove_face(triangle,2)

points2 = points.copy()
tetra2 = tetra.copy()
triangle2 = triangle.copy()

m = len(points)
tetra2 += m
triangle2 += m
points2[:,2]*=-1

#ii = find(points,0,0,1e-10)
#tetra2[ii,0]-=m

ii = (numpy.abs((points[tetra,2])-0)<1e-5)
jj = ((ii.sum(1))==3).nonzero()[0]

ij = []
for item in jj:
    ij.append((item,ii[item].nonzero()[0]))

for aa,bb in ij:
    tetra2[aa,bb]-=m


points3 = numpy.r_[points,points2]
tetra3 = numpy.r_[tetra,tetra2]
triangle3 = numpy.r_[triangle,triangle2]


tetra4,points4,mapping = fea.reduce_elements(tetra3,points3)
triangle4 = numpy.array([[mapping[key] for key in list1] for list1 in triangle3],dtype = int)

fea.plot_triangles(points4,triangle4)
#fea.plot_triangles(points,triangle)