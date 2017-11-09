# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
#import shapely.geometry as sg
#from .shape import Base
#from . import shape
import shapely.geometry
import shapely.geometry as sg
import shapely.affinity as sa
from .class_algebra import ClassAlgebra
import shapely.ops as so
import shapely.wkt as sw
import matplotlib.pyplot as plt
import numpy
import foldable_robotics

def is_collection(item):
    collections = [
        shapely.geometry.MultiPolygon,
        shapely.geometry.GeometryCollection,
        shapely.geometry.MultiLineString,
        shapely.geometry.MultiPoint]
    iscollection = [isinstance(item, cls) for cls in collections]
    return any(iscollection)

def extract_r(item,list_in = None):
    list_in = list_in or []
    if is_collection(item):
        list_in.extend([item3 for item2 in item.geoms for item3 in extract_r(item2,list_in)])
    else:
        list_in.append(item)
    return list_in
    
def flatten(geoms):
    geom = so.unary_union(geoms)
    entities = extract_r(geom)
#    entities = [item for item in entities if any([isinstance(item,classitem) for classitem in [shapely.geometry.Polygon,shapely.geometry.LineString,shapely.geometry.Point]])]
#    entities = [item for item in entities if not item.is_empty]
    return entities   
    
def from_shapely_to_layer(new_geoms):
    new_geoms = flatten(new_geoms)        
    new_layer = Layer(*new_geoms)
    return new_layer
    
def from_layer_to_shapely(layer):
    geoms = so.unary_union(layer.geoms)
    return geoms

def plot_poly(poly,color = None,edgecolor = None, facecolor =None):
    color = color or (1,0,0,.25)
    
    facecolor = facecolor or color
    edgecolor = edgecolor or tuple(list(color[:3])+[1])
    
    import numpy
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import matplotlib.pyplot as plt
    axes = plt.gca()
    vertices = []
    codes = []
    color = list(color)
    if isinstance(poly,sg.Polygon):
        exterior = list(poly.exterior.coords)
        interiors = [list(interior.coords) for interior in poly.interiors]
        for item in [exterior]+interiors:
            vertices.extend(item+[(0,0)])
            codes.extend([Path.MOVETO]+([Path.LINETO]*(len(item)-1))+[Path.CLOSEPOLY])
        path = Path(vertices,codes)
        patch = PathPatch(path,facecolor=facecolor,edgecolor=edgecolor)        
        axes.add_patch(patch)

    elif isinstance(poly,sg.LineString):
        exterior = numpy.array(poly.coords)
        axes.plot(exterior[:,0],exterior[:,1],color=color[:3]+[.5])
    plt.axis('equal')
    
def check_loop(loop):
    if loop[-1]==loop[0]:
        return loop[:-1]
        
def triangulate_geom(geom):
    import pypoly2tri
    from pypoly2tri.cdt import CDT
    import numpy
    exterior = list(geom.exterior.coords)
    exterior = check_loop(exterior)
    exterior2 = [pypoly2tri.shapes.Point(*item) for item in exterior]
    cdt = CDT(exterior2)
    interiors = []
    for interior in geom.interiors:
        interior= list(interior.coords)
        interior = check_loop(interior)
        interiors.append(interior)
    for interior in interiors:
        interior2 = [pypoly2tri.shapes.Point(*item) for item in interior]
        cdt.AddHole(interior2)
    cdt.Triangulate()
    tris =cdt.GetTriangles()
    points = cdt.GetPoints()
    points2 = numpy.array([item.toTuple() for item in points])
    tris2 = numpy.array([[points.index(point) for point in tri.points_] for tri in tris],dtype = int)
    return points2,tris2

def points_2d_to_3d(points_2d,z_val):
    z = points_2d[:,0:1]*0+z_val
    points3 = numpy.c_[points_2d,z]
    return points3

def extrude(points,tris,z_lower,z_upper):
    from idealab_tools.geometry.triangle import Triangle
    tris3 = [Triangle(*(points[tri])) for tri in tris]
    tets = [tet for tri in tris3 for tet in tri.extrude(z_lower,z_upper)]
    return tets
    
def inertia_tensor(about_point,density,z_lower,z_upper,points,tris):
    import numpy
    tets = extrude(points,tris,z_lower,z_upper)
    Is = numpy.array([tet.I(density,about_point) for tet in tets])
    I = Is.sum(0)
    return I

class Layer(ClassAlgebra):
    def __init__(self, *geoms):
        geoms = flatten(geoms)
        self.geoms = geoms
        self.id = id(self)

    @classmethod
    def new(cls,*geoms):
        geoms = flatten(geoms)
        new = cls(*geoms)
        return new

    def copy(self,identical = True):
        new = type(self)(*[sw.loads(geom.to_wkt()) for geom in self.geoms])        
        if identical:        
            new.id = self.id
        return new

    def export_dict(self):
        d = {}
        d['geoms'] = [item.to_wkt() for item in self.geoms]
        d['id'] = self.id
        return d

    @classmethod
    def import_dict(cls,d):
        new = cls(*[sw.loads(item) for item in d['geoms']])
        new.id = d['id']
        return new

    def plot(self,*args,**kwargs):
        if 'new' in kwargs:
            new = kwargs.pop('new')
        else:
            new = False
        if new:
            plt.figure()
        for geom in self.geoms:
            plot_poly(geom,*args,**kwargs)

    def binary_operation(self,other,function_name):
        a = from_layer_to_shapely(self)
        b = from_layer_to_shapely(other)
        function = getattr(a,function_name)
        c = function(b)
        return from_shapely_to_layer(c)

    def union(self,other):
        return self.binary_operation(other,'union')

    def difference(self,other):
        return self.binary_operation(other,'difference')

    def symmetric_difference(self,other):
        return self.binary_operation(other,'symmetric_difference')

    def intersection(self,other):
        return self.binary_operation(other,'intersection')
    
    def buffer(self,value,resolution = None):
        resolution = resolution or foldable_robotics.resolution
        return self.dilate(value,resolution)

    def dilate(self,value,resolution = None):
        resolution = resolution or foldable_robotics.resolution
        geoms = from_layer_to_shapely(self)
        new_geoms = (geoms.buffer(value,resolution))
        return from_shapely_to_layer(new_geoms)

    def erode(self,value,resolution = None):
        resolution = resolution or foldable_robotics.resolution
        return self.dilate(-value,resolution)
        
    def translate(self,*args,**kwargs):
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.translate(geoms,*args,**kwargs)
        return from_shapely_to_layer(new_geoms)

    def scale(self,*args,**kwargs):
        try:
            kwargs['origin']
        except KeyError:
            kwargs['origin']=(0,0)
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.scale(geoms,*args,**kwargs)
        return from_shapely_to_layer(new_geoms)

    def rotate(self,*args,**kwargs):
        try:
            kwargs['origin']
        except KeyError:
            kwargs['origin']=(0,0)
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.rotate(geoms,*args,**kwargs)
        return from_shapely_to_layer(new_geoms)

    def affine_transform(self,*args,**kwargs):
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.affine_transform(geoms,*args,**kwargs)
        return from_shapely_to_layer(new_geoms)

    def export_dxf(self,name):
        import ezdxf
        dwg = ezdxf.new('R2010')
        msp = dwg.modelspace()
        for geom in self.geoms:
            segments = self.get_segments(geom)
            for segment in segments:
                for c0,c1 in zip(segment[:-1],segment[1:]):
                    msp.add_line(c0,c1)
        dwg.saveas(name+'.dxf')
        
    def get_segments(self,poly):
        if isinstance(poly,sg.Polygon):
            exterior = list(poly.exterior.coords)
            interiors = [list(interior.coords) for interior in poly.interiors]
            segments = [exterior]+interiors
            segments = [loop+loop[0:1] for loop in segments]
            
        elif isinstance(poly,sg.LineString):
            segments = list(poly.coords)
            
        return segments
        
    def map_line_stretch(self,*args,**kwargs):
        import foldable_robotics.manufacturing
        return foldable_robotics.manufacturing.map_line_stretch(self,*args,**kwargs)
    
    def triangulation(self):
        points = []
        tris = []
        ii = 0
        for geom in self.geoms:
            if isinstance(geom,sg.Polygon):
                points2,tris2 = triangulate_geom(geom)
                points.append(points2)
                tris.append(tris2+ii)
                ii+=len(points2)
        points = numpy.vstack(points)
        tris = numpy.vstack(tris)
        return points,tris
    
    def mesh_items_inner(self,z_offset = 0,color = (1,0,0,1)):

        verts_outer = []
        colors_outer = []
        
        for geom in self.geoms:
            if isinstance(geom,sg.Polygon):
                
                points2,tris2 = triangulate_geom(geom)
                points3 = points_2d_to_3d(points2,z_offset)
                verts =points3[tris2]
                verts_colors = [[color]*3]*len(tris2)
                verts_outer.append(verts)
                colors_outer.append(verts_colors)
        
        verts_outer = numpy.vstack(verts_outer)
        colors_outer = numpy.vstack(colors_outer)
        return verts_outer,colors_outer
    
    def mesh_items(self,z_offset = 0,color = (1,0,0,1)):
        import pyqtgraph.opengl as gl
        verts_outer,colors_outer = self.mesh_items_inner(z_offset,color)
        mi=gl.GLMeshItem(vertexes=verts_outer,vertexColors=colors_outer,smooth=False,shader='balloon',drawEdges=False)
        return mi
    
    def mass_props(self,material_property,bottom,top):
        area_i = 0
        mass_i=0
        volume_i=0
        
        centroid_x_i=0
        centroid_y_i=0
        centroid_z_i=0

        for geom in self.geoms:
            area_i = geom.area
            volume_ii = geom.area*material_property.thickness
            mass_ii  = volume_ii*material_property.density

            volume_i+=volume_ii
            mass_i+=mass_ii
            centroid = list(geom.centroid.coords)[0]
            centroid_x_i += centroid[0]*mass_ii
            centroid_y_i += centroid[1]*mass_ii
            centroid_z_i += (bottom+top)/2*mass_ii

        centroid_i = centroid_x_i/mass_i,centroid_y_i/mass_i,centroid_z_i/mass_i
        
        return area_i,volume_i,mass_i,centroid_i 
    
    def inertia(self,about_point,z_lower,material_property):
        I=numpy.zeros((3,3))
        z_upper = z_lower+material_property.thickness

        for geom in self.geoms:
            points,tris = triangulate_geom(geom)
            I+=inertia_tensor(about_point,material_property.density,z_lower,z_upper,points,tris)
            
        return I
    
    def bounding_box_coords(self):
        a = numpy.array([vertex for geom in self.geoms for vertex in geom.exterior.coords])
        box = [tuple(a.min(0)),tuple(a.max(0))]
        return box

    def bounding_box(self):
        a,b = self.bounding_box_coords()
        p = sg.box(*a,*b)
        l = Layer(p)
        return l
        
    def exteriors(self):
        a = [list(geom.exterior.coords) for geom in self.geoms]
        return a

    def interiors(self):
        a = [list(interior.coords) for geom in self.geoms for interior in geom.interiors]
        return a

    def extrude(self,z_lower,material_property):
        z_upper = z_lower+material_property.thickness
        points, tris =self.triangulation()
        m = points.shape[0]
        n = tris.shape[0]
        points2 = numpy.r_[numpy.c_[points,[z_lower]*len(points)],numpy.c_[points,[z_upper]*len(points)]]
        tris2 = numpy.r_[numpy.c_[tris[:,(0)]+m,tris[:,(1,0,2)]+m],numpy.c_[tris[:,(0,)]+m,tris[:,(1,)],tris[:,(2,)]+m,tris[:,(2,)]],numpy.c_[tris[:,(0,)]+m,tris[:,(1,)],tris[:,(1,2)]+m]]
        return points2,tris2
    
    def simplify(self,tolerance):
        geoms = foldable_robotics.layer.from_layer_to_shapely(self)
        new_geoms = (geoms.simplify(tolerance))
        return foldable_robotics.layer.from_shapely_to_layer(new_geoms)

    
        
def layer_representer(dumper, v):
    d = v.export_dict()
    output = dumper.represent_mapping(u'!Layer',d)
    return output

def layer_constructor(loader, node):
    item = loader.construct_mapping(node)
    new = Layer.import_dict(item)
    return new
    
import yaml        
yaml.add_representer(Layer, layer_representer)
yaml.add_constructor(u'!Layer', layer_constructor)
        