# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""
import PyQt5.QtGui as qg
import pyqtgraph.opengl as pgo
import sys

def prep():
    app = qg.QApplication(sys.argv)
    w = pgo.GLViewWidget()    
    return app,w

def plot_mi(mi):
    app,w = prep()
    w.addItem(mi)
    w.show()
    sys.exit(app.exec_())

def plot_tris(*args,**kwargs):
    mi = make_mi(*args,**kwargs)
    plot_mi(mi)
    
def make_mi(verts,tris,verts_colors = None,face_colors = None, drawEdges = False, edgeColor = (1,1,1,1)):
    md = pgo.MeshData(vertexes = verts,faces = tris,vertexColors = verts_colors,faceColors = face_colors)
    mi = pgo.GLMeshItem(meshdata = md,shader='balloon',drawEdges=drawEdges,edgeColor = edgeColor,smooth=False,computeNormals = False,glOptions='opaque')
#    mi = pgo.GLMeshItem(meshdata = md,shader='shaded',drawEdges=False,smooth=True,computeNormals = True,glOptions='opaque')
    return mi
    
if __name__=='__main__':
    import numpy
    verts = []
    verts.append([0,0,0])
    verts.append([1,0,0])
    verts.append([0,1,0])
    verts.append([1,1,0])
    verts = numpy.array(verts)
    
    verts_colors = []
    verts_colors.append([1,0,0,1])
    verts_colors.append([0,1,0,1])
    verts_colors.append([0,0,1,1])
    verts_colors.append([1,1,0,1])
    verts_colors = numpy.array(verts_colors)
    
    tris = []
    tris.append([0,1,2])
    tris.append([1,2,3])
    tris = numpy.array(tris)
    
    app,w = prep()
    mi = make_mi(verts,tris,verts_colors,drawEdges = True, edgeColor=(1,1,1,1))
    w.addItem(mi)
    
    
    w.opts['center'] =qg.QVector3D(.5,.5,0)
    w.opts['elevation'] =90
    w.opts['azimuth'] = 0
    w.opts['distance'] = 1
    w.resize(1000,1000)
    w.show()

    w.paintGL()
    w.grabFrameBuffer().save('multimaterial.png')
