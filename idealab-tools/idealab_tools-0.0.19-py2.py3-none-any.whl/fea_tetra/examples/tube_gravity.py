# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 15:18:44 2017

@author: danaukes
"""

import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

import sys
import pyqtgraph.opengl as pgo

import pygmsh as pg
import numpy as np
import numpy
#        import matplotlib.cm as cm
#        import matplotlib.pyplot as plt
#        plt.ion()
#        from mpl_toolkits.mplot3d import Axes3D
import shapely
import shapely.geometry as sg

import idealab_tools.fea_tetra.fea as fea
#        import idealab_tools.matplotlib_tools
import idealab_tools.pygmsh_fix

def compute(diameter,length,youngs,poisson,lcar = 1e-1):
    
    
    p=  sg.Point(0,0)
    poly = p.buffer(diameter/2,resolution = 4)
    poly3 = p.buffer(diameter/4,resolution = 4)
    poly2= list(poly.exterior.coords)
    poly2 = poly2[:-1]
    poly4= list(poly3.exterior.coords)
    poly4 = poly4[:-1]
    poly2 = numpy.r_[poly2]
    poly2 = numpy.c_[poly2,poly2[:,0]*0]
    poly4 = numpy.r_[poly4]
    poly4 = numpy.c_[poly4,poly4[:,0]*0]
    
    geom = pg.Geometry()
    hole= geom.add_polygon(poly4, lcar,make_surface=False)
    poly = geom.add_polygon(poly2,lcar,holes=[hole.line_loop])
    
    axis = [0, 0, length]
    theta = 0
    
    geom.extrude(poly,translation_axis=axis,rotation_axis=axis,point_on_axis=[0, 0, 0], angle=theta)
    
    points, cells, point_data, cell_data, field_data = idealab_tools.pygmsh_fix.generate_mesh(geom,num_quad_lloyd_steps=0)
    triangles_outer = cells['triangle']
    
    material = fea.Material(youngs,poisson)
    factor = 1
    f = 1e-2
    
    coordinates = points[:]
    elements = cells['tetra']
    
    elements,coordinates,mapping = fea.reduce_elements(elements,coordinates)
    triangles_outer = numpy.array([[mapping[key] for key in list1] for list1 in triangles_outer],dtype = int)
    del points
    
    a=fea.analyze(coordinates,elements)
    print(a)
    elements[a] = elements[a][:,(0,2,1,3)]
    a=fea.analyze(coordinates,elements)
    print(a)
    
    T = coordinates[elements[:,1:]]-coordinates[elements[:,0:1]]
    dt = numpy.array([numpy.linalg.det(item) for item in T])
    elements = elements[dt!=0]
    
    
    xx = coordinates[:,0]
    yy = coordinates[:,1]
    zz = coordinates[:,2]
    
    z_max = coordinates.max(0)[2]
    z_min = coordinates.min(0)[2]
    x_max = coordinates.max(0)[0]
    x_min = coordinates.min(0)[0]
    
    
    
    ii_bottom = ((coordinates[triangles_outer,2]==z_min).sum(1)==3)
    ii_top = ((coordinates[triangles_outer,2]==z_max).sum(1)==3)
    dirichlet_bottom = triangles_outer[ii_bottom]
    dirichlet_top = triangles_outer[ii_top]
    #dirichlet = numpy.r_[dirichlet_bottom,dirichlet_top]
    dirichlet = dirichlet_bottom
    
    neumann = numpy.zeros((0,3),dtype = int)
    
    dirichlet_nodes = numpy.unique(dirichlet)
    neumann_nodes = numpy.unique(neumann)
    
    #fea.plot_triangles(coordinates,triangles_outer)
    density = 1000
    
    def volume_force(x):
        volforce = numpy.zeros((x.shape[0],3))
        volforce[:,1] = 9.81*density
        return volforce    
    
    def u_d(x):
        mm = x.shape[0]
        M = numpy.zeros((3*mm,3))
        W = numpy.zeros((3*mm,1))
        M[0::3,0] = 1
        M[1::3,1] = 1
        M[2::3,2] = 1
    
    #    ii = (x[:,2]==z_max).nonzero()[0]
    #    W[ii*3+2] = f * x[ii,0:1]+f
        return W,M
    
    u_max = []
    C_max = []
    x,u = fea.compute(material,coordinates,elements,neumann,dirichlet_nodes,volume_force,fea.surface_force_empty,u_d)
    C = fea.max_stress(elements,coordinates, u,material)
    u_max.append([u[0::3].max(),u[2::3].max(),u[2::3].max()])
    C_max.append(C.max())
    
    xyz,triangles_outer,c_face,c_vertex = fea.show23_int(elements,triangles_outer,coordinates,u,material,factor)

    md = pgo.MeshData(vertexes = xyz,faces = triangles_outer,vertexColors = c_vertex)
    mi = pgo.GLMeshItem(meshdata = md,shader='balloon',drawEdges=False,edgeColor = [1,1,1,1],smooth=False,computeNormals = False,glOptions='opaque')
    return mi
#        ax = fea.show3(elements,triangles_outer,coordinates,u,material,factor = factor)

if __name__=='__main__':
    mi = compute(.01,.1,1e5,1e-2)
    import idealab_tools.plot_tris as pt
    pt.plot_mi(mi)