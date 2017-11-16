import tecplot
from tecplot.constant import *
import os
import numpy as np

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
plot = frame.plot()

# Turn on only the periodic slices (start, end and intermeidate) 
# and set them to span the length of the wing
plot.show_slices = True
slices = plot.slice(0)
slices.slice_source = SliceSource.SurfaceZones
slices.orientation = SliceSurface.YPlanes
slices.show_primary_slice = False
slices.show_start_and_end_slices = True
slices.show_intermediate_slices = True
slices.num_intermediate_slices = 5
slices.start_position = (0, 0.02, 0)
slices.end_position = (0,1.19,0)

# Setup First Contour Group to color by the distance along the Y axis (Span)
cont = plot.contour(0)
cont.variable = frame.dataset.variable('y')
cont.levels.reset_levels(np.linspace(0,1.2,13))
cont.legend.show = False

# Color the Surface Slices by the contour, this must be done on the mesh
slices.contour.show = False
slices.mesh.show = True
slices.mesh.color = cont
slices.mesh.line_thickness = 0.6
slices.edge.show = False

# Turn translucency on globally
plot.use_translucency = True

tecplot.export.save_png("wing_slices.png",600, supersample=3)
