# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""
import numpy
import sympy

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm
from scipy.spatial import Delaunay

def find_edges(triangle_index):
    ti = numpy.array(triangle_index)
    ti2 = numpy.array([ti,ti[:,(1,2,0)]])
    ti2 = ti2.transpose(1,2,0)
    alledges = ti2.reshape(-1,2)
    alledges = sorted(set([tuple(sorted(item)) for item in alledges]))
    low = ((ti2[:,:,0]-ti2[:,:,1])<0)*1
    a = ti2[:,:,0]*low+ti2[:,:,1]*(1-low)
    b = ti2[:,:,0]*(1-low)+ti2[:,:,1]*low
    ti3 = numpy.array([a,b])
    ti3=ti3.transpose(1,2,0)
    edge_index = [[alledges.index(tuple(edge)) for edge in edges] for edges in ti3]
    return edge_index,alledges    

    
def simpsymbolic(A):
    for ii in range(A.shape[0]):
        for jj in range(A.shape[1]):
            A[ii,jj] = A[ii,jj].simplify()
    return A

def symlist(x,num):
    symlist = [sympy.Symbol(x+str(ii)) for ii in range(num)]
    return symlist
    
def plot_xyz(xyz, fig = None,scale_axes = False):
    d = Delaunay(xyz)
    tris = d.simplices

    fig = fig or plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(xyz[:,0],xyz[:,1],xyz[:,2],triangles=tris,cmap=matplotlib.cm.jet,edgecolor = (0,0,0,0))

    ax =  plt.gca()
    
    if scale_axes:
        out = xyz
        out_max = out.max(0)
        out_min = out.min(0)
        out_mid = (out_max+out_min)/2
        max_range = (out_max-out_min).max()/2
        
        ax.set_xlim(out_mid[0] - max_range, out_mid[0] + max_range)
        ax.set_ylim(out_mid[1] - max_range, out_mid[1] + max_range)
        ax.set_zlim(out_mid[2] - max_range, out_mid[2] + max_range)    