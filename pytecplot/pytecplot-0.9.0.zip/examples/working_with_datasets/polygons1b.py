"""Polygonal Finite-element Data Creation (Part 1b)

This script shows an alternative way to specify the connectivity for the same
polygonal zone from Part 1.

The data created looks like this::

    Node positions (x,y,z):

                   (1,1,1)
                  3
                 / \
                /   \
     (0,1,.5)  2-----1  (1,0,.5)
                \   /
                 \ /
                  0
                   (0,0,0)

The elements are passed in as an "element map" which is a list of elements
which are lists of the nodes that make up the individual elements. This will
look like the following where ``EiNj`` denotes the element index ``i`` and the
node index ``j`` within the element::

    elementmap = [
        [ E0N0, E0N1, E0N2... ],
        [ E1N0, E1N1... ]... ]

"""
import tecplot as tp
from tecplot.constant import *

# Locations (x,y,z) of the nodes
nodes = ((0, 0, 0  ),
         (1, 0, 0.5),
         (0, 1, 0.5),
         (1, 1, 1  ))

# elements (triangles) defined by their nodes
elementmap = ((0, 1, 2),
              (1, 3, 2))

# Scalar value at the nodes
scalar_data = (0, 1, 2, 3)

# Setup dataset and zone
ds = tp.active_frame().create_dataset('Data', ['x', 'y', 'z', 's'])
z = ds.add_poly_zone(ZoneType.FEPolygon, name='FE Polygon Float (4,2,5) Nodal',
                     num_points=len(nodes),
                     num_elements=len(elementmap))

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set facemap
fm = z.facemap
fm.set_elementmap(elementmap)

# Set the scalar data
z.values('s')[:] = scalar_data

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('polygons1b.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous

for ax in plot.axes:
    ax.show = True

plot.show_mesh = False
plot.show_contour = True
plot.show_edge = True
plot.use_translucency = True

fmap = plot.fieldmap(z)
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.All
fmap.effects.surface_translucency = 40

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10
plot.view.width = 2
plot.view.psi = 80
plot.view.theta = 30
plot.view.alpha = 0
plot.view.position = (-4.2, -8.0, 2.3)

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
plot.fieldmap(z).mesh.line_pattern = LinePattern.Dashed

tp.export.save_png('polygons1.png', 600, supersample=3)
