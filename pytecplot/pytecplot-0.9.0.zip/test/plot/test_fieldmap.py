import os
import sys
import unittest

from unittest.mock import patch, Mock
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.tecutil.util import IndexRange

from ..sample_data import sample_data


class TestFieldmap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = self.dataset.variable('Z').index
        self.fmap = self.plot.fieldmap(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True, False, True]:
            self.fmap.show = val
            self.assertEqual(self.fmap.show, val)

    def test_group(self):
        for i in [0, 1, 100]:
            self.fmap.group = i
            self.assertEqual(self.fmap.group, i)
        with self.assertRaises(TecplotSystemError):
            self.fmap.group = -1
        with self.assertRaises(ValueError):
            self.fmap.group = 'badtype'
        with self.assertRaises(TypeError):
            self.fmap.group = None

    def test_show_volume_objs(self):
        for val in [False, True, False]:
            self.fmap.show_iso_surfaces = val
            self.fmap.show_slices = val
            self.fmap.show_streamtraces = val
            self.assertEqual(self.fmap.show_iso_surfaces, val)
            self.assertEqual(self.fmap.show_slices, val)
            self.assertEqual(self.fmap.show_streamtraces, val)

    def test_toplevel_style_objs(self):
        self.assertIsInstance(self.fmap.contour, tp.plot.FieldmapContour)
        self.assertIsInstance(self.fmap.edge, tp.plot.FieldmapEdge)
        self.assertIsInstance(self.fmap.mesh, tp.plot.FieldmapMesh)
        self.assertIsInstance(self.fmap.scatter, tp.plot.FieldmapScatter)
        self.assertIsInstance(self.fmap.shade, tp.plot.FieldmapShade3D)
        self.assertIsInstance(self.fmap.surfaces, tp.plot.FieldmapSurfaces)
        self.assertIsInstance(self.fmap.points, tp.plot.FieldmapPoints)
        self.assertIsInstance(self.fmap.vector, tp.plot.FieldmapVector)

    def test_zones(self):
        self.assertEqual(list(self.fmap.zones), [self.dataset.zone(0)])

    def test_eq(self):
        fmap0 = self.plot.fieldmap(0)
        self.assertTrue(fmap0 == self.plot.fieldmap(0))
        self.assertTrue(fmap0 != self.plot.fieldmap(1))
        self.assertFalse(fmap0 == self.plot.fieldmap(1))
        self.assertFalse(fmap0 != self.plot.fieldmap(0))


class TestFieldmapContour(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()

        # we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True
        self.contour = fmap.contour

    def tearDown(self):
        os.remove(self.filename)

    def test_eq(self):
        ctr0 = self.plot.fieldmap(0).contour
        self.assertTrue(ctr0 == self.plot.fieldmap(0).contour)
        self.assertTrue(ctr0 != self.plot.fieldmap(1).contour)
        self.assertFalse(ctr0 == self.plot.fieldmap(1).contour)
        self.assertFalse(ctr0 != self.plot.fieldmap(0).contour)

    def test_show(self):
        self.contour.show = True
        self.assertTrue(self.contour.show)
        self.contour.show = False
        self.assertFalse(self.contour.show)

    def test_contour_type(self):
        contour = self.contour
        for val in [ContourType.Lines, ContourType.Flood]:
            contour.contour_type = val
            self.assertEqual(contour.contour_type, val)
        with self.assertRaises(ValueError):
            contour.contour_type = 0.5

    def test_setting_contour_groups(self):
        contour = self.contour
        for i,j,k in zip([1,2,0],[1,3,4],[1,5,6]):
            ci = self.plot.contour(i)
            cj = self.plot.contour(j)
            ck = self.plot.contour(k)
            contour.flood_contour_group = ci
            contour.line_group = cj
            contour.line_color = ck
            self.assertEqual(contour.flood_contour_group, ci)
            self.assertEqual(contour.line_group, cj)
            self.assertEqual(contour.line_color, ck)

    def test_setting_contour_groups_by_index(self):
        contour = self.contour
        for i,j in [[1,2],[2,3],[3,5]]:
            ci = self.plot.contour(i)
            cj = self.plot.contour(j)
            contour.flood_contour_group_index = i
            contour.line_group_index = j
            self.assertEqual(contour.flood_contour_group_index, i)
            self.assertEqual(contour.line_group_index, j)
            self.assertEqual(contour.flood_contour_group, ci)
            self.assertEqual(contour.line_group, cj)

    def test_line_color(self):
        for c in [Color.Red,Color.Black,self.plot.contour(1)]:
            self.contour.line_color = c
            self.assertEqual(self.contour.line_color, c)
        with self.assertRaises(ValueError):
            self.contour.line_color = 0.5

    def test_line_pattern(self):
        contour = self.contour
        for val in [LinePattern.Solid,LinePattern.Dashed]:
            contour.line_pattern = val
            self.assertEqual(contour.line_pattern, val)
        with self.assertRaises(ValueError):
            contour.line_pattern = 0.5

    def test_line_thickness(self):
        contour = self.contour
        for val in [0.5,1,2]:
            contour.line_thickness = val
            self.assertEqual(contour.line_thickness, val)
        with self.assertRaises(ValueError):
            contour.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            contour.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            contour.pattern_length = -1

    def test_pattern_length(self):
        contour = self.contour
        for val in [0.5,1,2]:
            contour.pattern_length = val
            self.assertEqual(contour.pattern_length, val)
        with self.assertRaises(ValueError):
            contour.pattern_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            contour.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            contour.pattern_length = -1

    def test_use_lighting_effect(self):
        contour = self.contour
        for val in [True,False]:
            contour.use_lighting_effect = val
            self.assertEqual(contour.use_lighting_effect, val)


class TestFieldmapEdge(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True
        self.edge = fmap.edge

    def tearDown(self):
        os.remove(self.filename)

    def test_color(self):
        edge = self.edge
        for val in [Color.Black,Color.Red]:
            edge.color = val
            self.assertEqual(edge.color, val)
        with self.assertRaises(ValueError):
            edge.color = 0.5

    def test_borders(self):
        self.edge.i_border = None
        self.edge.j_border = BorderLocation.Both
        self.edge.k_border = BorderLocation.Max
        self.assertEqual(self.edge.i_border,None)
        self.assertEqual(self.edge.j_border,BorderLocation.Both)
        self.assertEqual(self.edge.k_border,BorderLocation.Max)

    def test_i_border(self):
        edge = self.edge
        for val in [BorderLocation.Both,None,BorderLocation.Min]:
            edge.i_border = val
            self.assertEqual(edge.i_border, val)
        with self.assertRaises(ValueError):
            edge.i_border = 0.5

    def test_j_border(self):
        edge = self.edge
        for val in [BorderLocation.Both,None,BorderLocation.Min]:
            edge.j_border = val
            self.assertEqual(edge.j_border, val)
        with self.assertRaises(ValueError):
            edge.j_border = 0.5

    def test_k_border(self):
        edge = self.edge
        for val in [BorderLocation.Max,None,BorderLocation.Min]:
            edge.k_border = val
            self.assertEqual(edge.k_border, val)
        with self.assertRaises(ValueError):
            edge.k_border = 0.5

    def test_line_thickness(self):
        edge = self.edge
        for val in [0.5,1,2]:
            edge.line_thickness = val
            self.assertEqual(edge.line_thickness, val)
        with self.assertRaises(ValueError):
            edge.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            edge.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            edge.line_thickness = -1

    def test_show(self):
        edge = self.edge
        for val in [True,False,True]:
            edge.show = val
            self.assertEqual(edge.show, val)

    def test_edge_type(self):
        edge = self.edge
        for val in [EdgeType.Borders,EdgeType.Creases]:
            edge.edge_type = val
            self.assertEqual(edge.edge_type, val)
        with self.assertRaises(ValueError):
            edge.edge_type = 0.5

class TestFieldmapEffects(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian2D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.effects = fmap.effects

    def tearDown(self):
        os.remove(self.filename)

    def test_instance(self):
        self.assertIsInstance(self.effects, tp.plot.FieldmapEffects)

    def test_value_blanking(self):
        effects = self.effects
        for val in [True,False]:
            effects.value_blanking = val
            self.assertEqual(effects.value_blanking, val)

    def test_clip_planes(self):
        effects = self.effects
        for val in [None,[],0,1,[1,2],[3,4,5],list(range(6))]:
            effects.clip_planes = val
            if val == []:
                val = None
            elif isinstance(val, int):
                val = [val]
            self.assertEqual(effects.clip_planes, val)

class TestFieldmapEffects3D(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        self.effects = fmap.effects

    def tearDown(self):
        os.remove(self.filename)

    def test_instance(self):
        self.assertIsInstance(self.effects, tp.plot.FieldmapEffects3D)

    def test_use_translucency(self):
        effects = self.effects
        for val in [True, False, True]:
            effects.use_translucency = val
            self.assertEqual(effects.use_translucency, val)

    def test_surface_translucency(self):
        effects = self.effects
        for val in [1,5,99]:
            effects.surface_translucency = val
            self.assertEqual(effects.surface_translucency, val)
        with self.assertRaises(ValueError):
            effects.surface_translucency = 'badtype'
        with self.assertRaises(TecplotSystemError):
            effects.surface_translucency = -1
        with self.assertRaises(TecplotSystemError):
            effects.surface_translucency = 0
        with self.assertRaises(TecplotSystemError):
            effects.surface_translucency = 100

    def test_lighting_effect(self):
        effects = self.effects
        for val in [LightingEffect.Paneled,LightingEffect.Gouraud]:
            effects.lighting_effect = val
            self.assertEqual(effects.lighting_effect, val)
        with self.assertRaises(ValueError):
            effects.lighting_effect = 0.5

class TestFieldmapMesh(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True
        self.mesh = fmap.mesh

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        self.mesh.show = True
        self.assertTrue(self.mesh.show)
        self.mesh.show = False
        self.assertFalse(self.mesh.show)

    def test_mesh_type(self):
        mesh = self.mesh
        for val in [MeshType.Wireframe,MeshType.Overlay]:
            mesh.mesh_type = val
            self.assertEqual(mesh.mesh_type, val)
        with self.assertRaises(ValueError):
            mesh.mesh_type = 0.5

    def test_color(self):
        for c in [Color.Red,Color.Black,self.plot.contour(1)]:
            self.mesh.color = c
            self.assertEqual(self.mesh.color, c)
        with self.assertRaises(ValueError):
            self.mesh.color = 0.5

    def test_line_pattern(self):
        mesh = self.mesh
        for val in [LinePattern.Solid,LinePattern.Dashed]:
            mesh.line_pattern = val
            self.assertEqual(mesh.line_pattern, val)
        with self.assertRaises(ValueError):
            mesh.line_pattern = 0.5

    def test_line_thickness(self):
        mesh = self.mesh
        for val in [0.5,1,2]:
            mesh.line_thickness = val
            self.assertEqual(mesh.line_thickness, val)
        with self.assertRaises(ValueError):
            mesh.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            mesh.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            mesh.line_thickness = -1

    def test_pattern_length(self):
        mesh = self.mesh
        for val in [0.5,1,2]:
            mesh.pattern_length = val
            self.assertEqual(mesh.pattern_length, val)
        with self.assertRaises(ValueError):
            mesh.pattern_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            mesh.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            mesh.pattern_length = -1

class TestFieldmapPoints(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True
        self.pts = fmap.points

    def tearDown(self):
        os.remove(self.filename)

    def test_points_to_plot(self):
        for val in [PointsToPlot.SurfaceNodes,
                    PointsToPlot.SurfaceCellCenters,
                    PointsToPlot.AllConnected]:
            self.pts.points_to_plot = val
            self.assertEqual(self.pts.points_to_plot, val)
        with self.assertRaises(ValueError):
            self.pts.points_to_plot = 0.5

    def test_step(self):
        for val in [None,1,2,(1,),(2,),(2,3),(4,5,6)]:
            self.pts.step = val
            if isinstance(val, tuple):
                step = tp.plot.FieldmapPoints._IJKStep(*val)
            else:
                step = tp.plot.FieldmapPoints._IJKStep(val)
            tup = (step.i or 1, step.j or 1, step.k or 1)
            self.assertEqual(self.pts.step, tup)

class TestFieldmapScatter(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_scatter = True
        self.scatter = fmap.scatter

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True,False]:
            self.scatter.show = val
            self.assertEqual(self.scatter.show, val)

    def test_symbol_type(self):
        for val in [SymbolType.Geometry, SymbolType.Text]:
            self.scatter.symbol_type = val
            self.assertEqual(self.scatter.symbol_type, val)
        with self.assertRaises(ValueError):
            self.scatter.symbol_type = 0.5

    def test_symbol(self):
        self.scatter.symbol_type = SymbolType.Text
        self.assertIsInstance(self.scatter.symbol(), tp.plot.TextSymbol)
        self.scatter.symbol_type = SymbolType.Geometry
        self.assertIsInstance(self.scatter.symbol(), tp.plot.GeometrySymbol)

    def test_fill_mode(self):
        for c in [FillMode.UseSpecificColor, FillMode.UseLineColor,
                  FillMode.UseBackgroundColor]:
            self.scatter.fill_mode = c
            self.assertEqual(self.scatter.fill_mode, c)
        with self.assertRaises(ValueError):
            self.scatter.fill_mode = 0.5

    def test_fill_color(self):
        for c in [Color.Red, Color.Black, self.plot.contour(1)]:
            self.scatter.fill_color = c
            self.assertEqual(self.scatter.fill_color, c)
        with self.assertRaises(ValueError):
            self.scatter.color = 0.5

    def test_color(self):
        for c in [Color.Red,Color.Black,self.plot.contour(1)]:
            self.scatter.color = c
            self.assertEqual(self.scatter.color, c)
        with self.assertRaises(ValueError):
            self.scatter.color = 0.5

    def test_size(self):
        for val in [0,0.5,1,2]:
            self.scatter.size = val
            self.assertEqual(self.scatter.size, val)
        with self.assertRaises(ValueError):
            self.scatter.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.scatter.size = -1

    def test_size_by_variable(self):
        with self.assertRaises((TecplotSystemError, TecplotLogicError)):
            self.scatter.size_by_variable = True
        self.plot.scatter.variable_index = 0
        for c in [True,False,True]:
            self.scatter.size_by_variable = c
            self.assertEqual(self.scatter.size_by_variable, c)

        with patch('tecplot.session.style.set_style', Mock()) as set_style:
            set_style.side_effect = TecplotSystemError('msg')
            with self.assertRaises(TecplotSystemError):
                self.scatter.size_by_variable = True

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.scatter.line_thickness = val
            self.assertEqual(self.scatter.line_thickness, val)
        with self.assertRaises(ValueError):
            self.scatter.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.scatter.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.scatter.line_thickness = -1


class TestFieldmapShade(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian2D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.shade = fmap.shade

    def tearDown(self):
        os.remove(self.filename)

    def test_instance(self):
        self.assertIsInstance(self.shade, tp.plot.FieldmapShade)

    def test_color(self):
        shade = self.shade
        for val in [Color.Black,Color.Red]:
            shade.color = val
            self.assertEqual(shade.color, val)
        with self.assertRaises(ValueError):
            shade.color = 0.5

    def test_show(self):
        shade = self.shade
        for val in [True,False]:
            shade.show = val
            self.assertEqual(shade.show, val)

    def test_no_lighting_effect(self):
        if __debug__:
            with self.assertRaises(AttributeError):
                self.shade.lighting_effect = True
            with self.assertRaises(AttributeError):
                leff = self.shade.lighting_effect

class TestFieldmapShade3D(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.shade = fmap.shade

    def tearDown(self):
        os.remove(self.filename)

    def test_instance(self):
        self.assertIsInstance(self.shade, tp.plot.FieldmapShade3D)

    def test_color(self):
        shade = self.shade
        for val in [Color.Black,Color.Red]:
            shade.color = val
            self.assertEqual(shade.color, val)
        with self.assertRaises(ValueError):
            shade.color = 0.5

    def test_show(self):
        shade = self.shade
        for val in [True,False]:
            shade.show = val
            self.assertEqual(shade.show, val)

    def test_use_lighting_effect(self):
        shade = self.shade
        for val in [True,False]:
            shade.use_lighting_effect = val
            self.assertEqual(shade.use_lighting_effect, val)

class TestFieldmapSurfaces(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True
        self.srf = fmap.surfaces

    def tearDown(self):
        os.remove(self.filename)

    def test_surfaces_to_plot(self):
        for val in [SurfacesToPlot.BoundaryFaces,
                    SurfacesToPlot.ExposedCellFaces,
                    None,
                    SurfacesToPlot.IPlanes]:
            self.srf.surfaces_to_plot = val
            self.assertEqual(self.srf.surfaces_to_plot, val)
        with self.assertRaises(ValueError):
            self.srf.surfaces_to_plot = 0.5

    def test_ranges(self):
        self.srf.i_range = None,None,None
        self.assertEqual(self.srf.i_range, IndexRange(0,-1,1))
        self.srf.i_range = 0,-1,1
        self.assertEqual(self.srf.i_range, IndexRange(0,-1,1))
        self.srf.i_range = -10,-1,1
        self.assertEqual(self.srf.i_range, IndexRange(-10,-1,1))
        self.srf.i_range = None,10,1
        self.assertEqual(self.srf.i_range, IndexRange(0,10,1))
        self.srf.i_range = 0,None,1
        self.assertEqual(self.srf.i_range, IndexRange(0,-1,1))
        self.srf.i_range = 0,10,None
        self.assertEqual(self.srf.i_range, IndexRange(0,10,1))
        self.srf.i_range = 0,10
        self.assertEqual(self.srf.i_range, IndexRange(0,10,1))
        self.srf.i_range = 0,
        self.assertEqual(self.srf.i_range, IndexRange(0,-1,1))

        self.srf.j_range = None,None,None
        self.assertEqual(self.srf.j_range, IndexRange(0,-1,1))
        self.srf.j_range = 0,-1,1
        self.assertEqual(self.srf.j_range, IndexRange(0,-1,1))
        self.srf.j_range = -10,-1,1
        self.assertEqual(self.srf.j_range, IndexRange(-10,-1,1))
        self.srf.j_range = None,10,1
        self.assertEqual(self.srf.j_range, IndexRange(0,10,1))
        self.srf.j_range = 0,None,1
        self.assertEqual(self.srf.j_range, IndexRange(0,-1,1))
        self.srf.j_range = 0,10,None
        self.assertEqual(self.srf.j_range, IndexRange(0,10,1))
        self.srf.j_range = 0,10
        self.assertEqual(self.srf.j_range, IndexRange(0,10,1))
        self.srf.j_range = 0,
        self.assertEqual(self.srf.j_range, IndexRange(0,-1,1))

        self.srf.k_range = None,None,None
        self.assertEqual(self.srf.k_range, IndexRange(0,-1,1))
        self.srf.k_range = 0,-1,1
        self.assertEqual(self.srf.k_range, IndexRange(0,-1,1))
        self.srf.k_range = -10,-1,1
        self.assertEqual(self.srf.k_range, IndexRange(-10,-1,1))
        self.srf.k_range = None,10,1
        self.assertEqual(self.srf.k_range, IndexRange(0,10,1))
        self.srf.k_range = 0,None,1
        self.assertEqual(self.srf.k_range, IndexRange(0,-1,1))
        self.srf.k_range = 0,10,None
        self.assertEqual(self.srf.k_range, IndexRange(0,10,1))
        self.srf.k_range = 0,10
        self.assertEqual(self.srf.k_range, IndexRange(0,10,1))
        self.srf.k_range = 0,
        self.assertEqual(self.srf.k_range, IndexRange(0,-1,1))

    def test_range_limits(self):
        maxint = 2**64 - 1            # maximum of unsigned int64
        minint = -(2**(64-1) - 1) - 1 # minimum of   signed int64
        if __debug__:
            if sys.version_info < (3,):
                exp = OverflowError
            else:
                exp = TecplotOverflowError

            with self.assertRaises(exp):
                self.srf.i_range = maxint + 1,
            with self.assertRaises(exp):
                self.srf.i_range = minint - 1,
            with self.assertRaises(exp):
                self.srf.i_range = 0,maxint + 1
            with self.assertRaises(exp):
                self.srf.i_range = 0,minint - 1
        else:
            if sys.version_info < (3,):
                exp = TecplotSystemError
                with self.assertRaises(exp):
                    self.srf.i_range = minint - 1,
                with self.assertRaises(exp):
                    self.srf.i_range = 0,minint - 1
            else:
                # demonstrating that without __debug__,
                # integer overflows are not caught
                self.srf.i_range = 0, maxint + 1
                self.assertEqual(self.srf.i_range[1], 0)

class TestFieldmapVector(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fmap = self.plot.fieldmap(0)

        self.plot.vector.u_variable = dataset.variable('X')
        self.plot.vector.v_variable = dataset.variable('Y')
        self.plot.vector.w_variable = dataset.variable('Z')
        self.vector = fmap.vector

    def tearDown(self):
        os.remove(self.filename)

    def test_arrowhead_style(self):
        for val in [ArrowheadStyle.Plain,ArrowheadStyle.Filled]:
            self.vector.arrowhead_style = val
            self.assertEqual(self.vector.arrowhead_style, val)
        with self.assertRaises(ValueError):
            self.vector.arrowhead_style = 0.5

    def test_color(self):
        for val in [Color.Black,Color.Red,self.plot.contour(1)]:
            self.vector.color = val
            self.assertEqual(self.vector.color, val)
        with self.assertRaises(ValueError):
            self.vector.color = 0.5

    def test_line_pattern(self):
        for val in [LinePattern.Solid,LinePattern.Dashed]:
            self.vector.line_pattern = val
            self.assertEqual(self.vector.line_pattern, val)
        with self.assertRaises(ValueError):
            self.vector.line_pattern = 0.5

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.vector.line_thickness = val
            self.assertEqual(self.vector.line_thickness, val)
        with self.assertRaises(ValueError):
            self.vector.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.vector.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.vector.line_thickness = -1

    def test_pattern_length(self):
        for val in [0.5,1,2]:
            self.vector.pattern_length = val
            self.assertEqual(self.vector.pattern_length, val)
        with self.assertRaises(ValueError):
            self.vector.pattern_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.vector.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            self.vector.pattern_length = -1

    def test_show(self):
        for val in [True,False,True]:
            self.vector.show = val
            self.assertEqual(self.vector.show, val)

    def test_tangent_only(self):
        for val in [True,False,True]:
            self.vector.tangent_only = val
            self.assertEqual(self.vector.tangent_only, val)

    def test_vector_type(self):
        for val in [VectorType.TailAtPoint,VectorType.HeadAtPoint]:
            self.vector.vector_type = val
            self.assertEqual(self.vector.vector_type, val)
        with self.assertRaises(ValueError):
            self.vector.vector_type = 0.5

if __name__ == '__main__':
    from .. import main
    main()
