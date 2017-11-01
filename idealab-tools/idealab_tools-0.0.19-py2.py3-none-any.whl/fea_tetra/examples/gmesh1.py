# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

import pygmsh as pg
import numpy as np
import numpy
import matplotlib.cm as cm
import matplotlib.pyplot as plt
plt.ion()
from mpl_toolkits.mplot3d import Axes3D
import shapely
import shapely.geometry as sg

p=  sg.Point(0,0)
circle = p.buffer(1,resolution = 8)
poly2= list(circle.exterior.coords)
poly2 = poly2[:-1]
poly2 = numpy.r_[poly2]
poly2 = numpy.c_[poly2,poly2[:,0]*0]
geom = pg.Geometry()

poly = geom.add_polygon(poly2,lcar=0.05)

axis = [0, 0, 1]
theta = 2.0 / 6.0 * np.pi

geom.extrude(poly,translation_axis=axis,rotation_axis=axis,point_on_axis=[0, 0, 0], angle=theta)

points, cells, point_data, cell_data, field_data = pg.generate_mesh(geom)
triangles_outer = cells['triangle']

tetra = cells['tetra']
ii = numpy.array([[0,1,2],[1,2,3],[2,3,0],[3,0,1]])
triangles = tetra[:,ii].reshape((-1,3))

#f = ((points[triangles,2]<=.55).prod(1)==1)
f = ((points[triangles,0]<=0).prod(1)==1)
g = f
triangles =triangles[g]

xx = points[:,0]
yy = points[:,1]
zz = points[:,2]

cmap = cm.Spectral
c = (xx**2+yy**2)**.5

c_face = (c[triangles]).sum(1)/3

#c_face = c
c_face -= c_face.min()
c_face /= c_face.max()
c_face = [cmap(item) for item in c_face]    
c_face = numpy.array(c_face)
c_face[:,3]=.5

#f = 

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ts = ax.plot_trisurf(xx,yy,zz,triangles = triangles)
ts.set_facecolors(c_face)
#ts.set_edgecolor((0.,0.,0.,1.))
plt.show()

fig.savefig('cylinder.svg')