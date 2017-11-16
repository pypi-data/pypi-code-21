import numpy as np
import os
import unittest

from test import patch_tecutil

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.text import Font, LabelFormat
from tecplot.legend import ContourLegend

from ..sample_data import sample_data

class TestContourColormapOverride(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.override = frame.plot().contour(0).colormap_filter.override(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        self.override.show = True
        self.assertTrue(self.override.show)
        self.override.show = False
        self.assertFalse(self.override.show)

    def test_color(self):
        for val in [Color.Black, Color.Red]:
            self.override.color = val
            self.assertEqual(self.override.color, val)
        with self.assertRaises(ValueError):
            self.override.color = 0.5

    def test_start_level(self):
        for val in [0,1]:
            self.override.start_level = val
            self.assertEqual(self.override.start_level, val)
        with self.assertRaises(ValueError):
            self.override.end_level = 'badtype'

    def test_end_level(self):
        for val in [2,3]:
            self.override.end_level = val
            self.assertEqual(self.override.end_level, val)
        with self.assertRaises(ValueError):
            self.override.end_level = 'badtype'

class TestContourColormapZebraShade(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.zebra = frame.plot().contour(0).colormap_filter.zebra_shade

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        self.zebra.show = True
        self.assertTrue(self.zebra.show)
        self.zebra.show = False
        self.assertFalse(self.zebra.show)

    def test_transparent(self):
        for val in [True, False, True]:
            self.zebra.transparent = val
            self.assertEqual(self.zebra.transparent, val)

    def test_color(self):
        for val in [Color.Black,Color.Red]:
            self.zebra.color = val
            self.assertEqual(self.zebra.color, val)
        with self.assertRaises(ValueError):
            self.zebra.color = 0.5
        with self.assertRaises(ValueError):
            self.zebra.color = 'badvalue'

class TestContourColormapFilter(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.filter = frame.plot().contour(0).colormap_filter

    def tearDown(self):
        os.remove(self.filename)

    def test_show_overrides(self):
        for val in [True,False,True]:
            self.filter.show_overrides = val
            self.assertEqual(self.filter.show_overrides, val)

    def test_num_cycles(self):
        colormapfilter = self.filter
        for val in [1,2]:
            colormapfilter.num_cycles = val
            self.assertEqual(colormapfilter.num_cycles, val)
        with self.assertRaises(ValueError):
            colormapfilter.num_cycles = 'badtype'
        with self.assertRaises(TecplotSystemError):
            colormapfilter.num_cycles = 0
        with self.assertRaises(TypeError):
            colormapfilter.num_cycles = None
        with self.assertRaises(TecplotSystemError):
            colormapfilter.num_cycles = 512

    def test_distribution(self):
        colormapfilter = self.filter
        for val in [ColorMapDistribution.Continuous,ColorMapDistribution.Banded]:
            colormapfilter.distribution = val
            self.assertEqual(colormapfilter.distribution, val)
        with self.assertRaises(ValueError):
            colormapfilter.distribution = 'badtype'
        with self.assertRaises(ValueError):
            colormapfilter.distribution = 0.5
        with self.assertRaises(ValueError):
            colormapfilter.distribution = None
        with self.assertRaises(ValueError):
            colormapfilter.distribution = 5

    def test_reversed(self):
        colormapfilter = self.filter
        for val in [True,False,True]:
            colormapfilter.reversed = val
            self.assertEqual(colormapfilter.reversed, val)

    def test_fast_continuous_flood(self):
        colormapfilter = self.filter
        for val in [True,False,True]:
            colormapfilter.fast_continuous_flood = val
            self.assertEqual(colormapfilter.fast_continuous_flood, val)

    def test_continuous_min_max(self):
        colormapfilter = self.filter
        colormapfilter.continuous_min = -1000
        colormapfilter.continuous_max = 1000
        self.assertEqual(colormapfilter.continuous_min, -1000)
        self.assertEqual(colormapfilter.continuous_max, 1000)
        for val in [-1, 0, 0.5, 1, 100, -10]:
            colormapfilter.continuous_min = val
            self.assertEqual(colormapfilter.continuous_min, val)
        for val in [-1, 0, 0.5, 1, 100]:
            colormapfilter.continuous_max = val
            self.assertEqual(colormapfilter.continuous_max, val)

class TestColorCutoff(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.cutoff = frame.plot().contour(0).color_cutoff

    def tearDown(self):
        os.remove(self.filename)

    def test_include_min(self):
        for val in [True, False, True]:
            self.cutoff.include_min = val
            self.assertEqual(self.cutoff.include_min, val)

    def test_include_max(self):
        for val in [True, False, True]:
            self.cutoff.include_max = val
            self.assertEqual(self.cutoff.include_max, val)

    def test_min(self):
        for val in [-2,-1,-0.5,0,0.5,1,2]:
            self.cutoff.min = val
            self.assertEqual(self.cutoff.min, val)
        with self.assertRaises(ValueError):
            self.cutoff.min = 'badtype'

    def test_max(self):
        for val in [-2,-1,-0.5,0,0.5,1,2]:
            self.cutoff.max = val
            self.assertEqual(self.cutoff.max, val)
        with self.assertRaises(ValueError):
            self.cutoff.max = 'badtype'

    def test_inverted(self):
        for val in [True,False,True]:
            self.cutoff.inverted = val
            self.assertEqual(self.cutoff.inverted, val)

class TestContourLabels(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.labels = frame.plot().contour(0).labels

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        contourlabels = self.labels
        for val in [True,False,True]:
            contourlabels.show = val
            self.assertEqual(contourlabels.show, val)

    def test_auto_align(self):
        contourlabels = self.labels
        for val in [True,False]:
            contourlabels.auto_align = val
            self.assertEqual(contourlabels.auto_align, val)

    def test_spacing(self):
        contourlabels = self.labels
        for val in [0,0.5,1,2]:
            contourlabels.spacing = val
            self.assertEqual(contourlabels.spacing, val)
        with self.assertRaises(ValueError):
            contourlabels.spacing = 'badtype'
        with self.assertRaises(TypeError):
            contourlabels.spacing = None
        with self.assertRaises(TecplotSystemError):
            contourlabels.spacing = -1

    def test_step(self):
        contourlabels = self.labels
        for val in [1,2,3.14]:
            contourlabels.step = val
            self.assertEqual(contourlabels.step, int(val))
        with self.assertRaises(ValueError):
            contourlabels.step = 'badtype'
        with self.assertRaises(TypeError):
            contourlabels.step = None
        with self.assertRaises(TecplotSystemError):
            contourlabels.step = -1
        with self.assertRaises(TecplotSystemError):
            contourlabels.step = 0

    def test_color(self):
        contourlabels = self.labels
        for val in [Color.Black,Color.Red]:
            contourlabels.color = val
            self.assertEqual(contourlabels.color, val)
        with self.assertRaises(ValueError):
            contourlabels.color = 0.5

    def test_filled(self):
        contourlabels = self.labels
        for val in [True,False,True]:
            contourlabels.filled = val
            self.assertEqual(contourlabels.filled, val)

    def test_background_color(self):
        contourlabels = self.labels
        for val in [Color.Black,Color.Red,Color.Blue]:
            contourlabels.background_color = val
            self.assertEqual(contourlabels.background_color, val)
        with self.assertRaises(ValueError):
            contourlabels.background_color = 0.5
        with self.assertRaises(ValueError):
            contourlabels.background_color = 'badvalue'

    def test_auto_generate(self):
        contourlabels = self.labels
        for val in [True,False,True]:
            contourlabels.auto_generate = val
            self.assertEqual(contourlabels.auto_generate, val)

    def test_label_by_level(self):
        contourlabels = self.labels
        for val in [True,False,True]:
            contourlabels.label_by_level = val
            self.assertEqual(contourlabels.label_by_level, val)

    def test_margin(self):
        contourlabels = self.labels
        for val in [0,0.5,1,2]:
            contourlabels.margin = val
            self.assertEqual(contourlabels.margin, val)
        with self.assertRaises(ValueError):
            contourlabels.margin = 'badtype'
        with self.assertRaises(TypeError):
            contourlabels.margin = None
        with self.assertRaises(TecplotSystemError):
            contourlabels.margin = -1

    def test_font(self):
        self.assertIsInstance(self.labels.font, Font)

    def test_format(self):
        self.assertIsInstance(self.labels.format, LabelFormat)

class TestContourLevels(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.levels = frame.plot().contour(0).levels

    def tearDown(self):
        os.remove(self.filename)

    def test_list(self):
        self.levels.reset_levels(0,0.5,1)
        self.assertEqual(len(self.levels), 3)
        self.assertEqual(list(self.levels), [0,0.5,1])

    def test_add(self):
        self.levels.reset_levels(0,1)
        self.levels.add(0.5)
        self.assertEqual(len(self.levels), 3)
        self.assertEqual(list(self.levels), [0,0.5,1])

    def test_reset(self):
        self.levels.reset(9)
        self.assertEqual(len(self.levels), 9)
        self.assertTrue(np.allclose(
            list(self.levels), [.1,.2,.3,.4,.5,.6,.7,.8,.9]))

    def test_reset_levels(self):
        self.levels.reset_levels(-1,0,1)
        self.assertEqual(len(self.levels), 3)
        self.assertEqual(list(self.levels), [-1,0,1])
        self.levels.reset_levels(0)
        self.assertEqual(len(self.levels), 1)
        self.assertEqual(list(self.levels), [0])
        with self.assertRaises(IndexError):
            self.levels.reset_levels()

    def test_reset_to_nice(self):
        self.levels.reset_levels(0,1)
        self.levels.reset_to_nice(10)
        self.assertEqual(len(self.levels), 9)
        self.assertTrue(np.allclose(
            list(self.levels), [.1,.2,.3,.4,.5,.6,.7,.8,.9]))

    def test_delete_range(self):
        self.levels.reset_levels(0,0.25,0.5,0.75,1)
        self.levels.delete_range(0,0.5)
        self.assertEqual(len(self.levels), 2)
        self.assertEqual(list(self.levels), [.75,1])

    def test_delete_nearest(self):
        self.levels.reset_levels(0,0.5,1)
        self.levels.delete_nearest(0.51)
        self.assertEqual(len(self.levels), 2)
        self.assertEqual(list(self.levels), [0,1])

    def test_getitem(self):
        self.levels.reset_levels(0,.5,1)
        self.assertEqual(self.levels[0], 0)
        self.assertEqual(self.levels[1], 0.5)
        self.assertEqual(self.levels[2], 1)
        with self.assertRaises(IndexError):
            _=self.levels[3]

    def test_failure(self):
        with patch_tecutil('ContourGetLevels',return_value=(False,None,None)):
            with self.assertRaises(TecplotLogicError):
                _ = list(self.levels)

class TestContourLines(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        ### we need to set up the frame/plot/etc etc manually here
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        contour = plot.contour(0)
        contour.variable_index = dataset.variable('Z').index
        fieldmap = plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        self.lines = frame.plot().contour(0).lines

    def tearDown(self):
        os.remove(self.filename)

    def test_mode(self):
        contourlines = self.lines
        for val in [ContourLineMode.UseZoneLineType,ContourLineMode.SkipToSolid]:
            contourlines.mode = val
            self.assertEqual(contourlines.mode, val)
        with self.assertRaises(ValueError):
            contourlines.mode = 'badtype'
        with self.assertRaises(ValueError):
            contourlines.mode = 0.5
        with self.assertRaises(ValueError):
            contourlines.mode = None
        with self.assertRaises(ValueError):
            contourlines.mode = 5

    def test_step(self):
        lines = self.lines
        for val in [1,2,3.14]:
            lines.step = val
            self.assertEqual(lines.step, int(val))
        with self.assertRaises(ValueError):
            lines.step = 'badtype'
        with self.assertRaises(TypeError):
            lines.step = None
        with self.assertRaises(TecplotSystemError):
            lines.step = -1
        with self.assertRaises(TecplotSystemError):
            lines.step = 0

    def test_pattern_length(self):
        contourlines = self.lines
        for val in [0.5,1,2]:
            contourlines.pattern_length = val
            self.assertEqual(contourlines.pattern_length, val)
        with self.assertRaises(ValueError):
            contourlines.pattern_length = 'badtype'
        with self.assertRaises(TypeError):
            contourlines.pattern_length = None
        with self.assertRaises(TecplotSystemError):
            contourlines.pattern_length = -1
        with self.assertRaises(TecplotSystemError):
            contourlines.pattern_length = 0

class TestContourGroup(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()
        self.dataset = frame.dataset
        self.cgroup = frame.plot().contour(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_set_variable_index(self):
        self.cgroup.variable_index = 1
        self.assertEqual(self.cgroup.variable_index, 1)
        self.cgroup.variable_index = 0
        self.assertEqual(self.cgroup.variable_index, 0)

    def test_colormap_name1(self):
        contourgroup = self.cgroup
        contourgroup.colormap_name = 'Modern'
        name = contourgroup.colormap_name
        self.assertEqual(name, 'Modern')

    def test_colormap_name(self):
        contourgroup = self.cgroup
        for val in ['Modern', 'GrayScale', 'Small Rainbow']:
            contourgroup.colormap_name = val
            self.assertEqual(contourgroup.colormap_name, val)
        with self.assertRaises(TecplotSystemError):
            contourgroup.colormap_name = 0
        with self.assertRaises(TecplotSystemError):
            contourgroup.colormap_name = None
        with self.assertRaises(TecplotSystemError):
            contourgroup.colormap_name = 'typo'
        with self.assertRaises(TecplotSystemError):
            contourgroup.colormap_name = 'oops'

    def test_default_num_levels(self):
        contourgroup = self.cgroup
        for val in [1,2,5,15]:
            contourgroup.default_num_levels = val
            self.assertEqual(contourgroup.default_num_levels, val)
        with self.assertRaises(ValueError):
            contourgroup.default_num_levels = 'badtype'
        with self.assertRaises(TecplotSystemError):
            contourgroup.default_num_levels = 512
        with self.assertRaises(TypeError):
            contourgroup.default_num_levels = None

    def test_eq(self):
        self.assertEqual(self.cgroup, tp.plot.ContourGroup(0,self.cgroup.plot))

        cg1 = self.cgroup.plot.contour(1)
        self.assertNotEqual(self.cgroup, cg1)

        fr = tp.active_frame()
        dummy_frame = tp.layout.frame.Frame(fr.uid+1, fr.page)
        dummy_plot = tp.plot.Cartesian3DFieldPlot(dummy_frame)
        dummy_cg = tp.plot.ContourGroup(0, dummy_plot)
        self.assertNotEqual(self.cgroup, dummy_cg)

    def test_set_variable(self):
        var0 = self.dataset.variable(0)
        var1 = self.dataset.variable(1)
        self.cgroup.variable = var1
        self.assertEqual(self.cgroup.variable, var1)
        self.assertEqual(self.cgroup.variable_index, 1)
        self.cgroup.variable = var0
        self.assertEqual(self.cgroup.variable_index, 0)

        if __debug__:
            fr0 = tp.active_frame()
            ds0 = fr0.dataset
            fr1 = tp.active_page().add_frame()
            ds1 = tp.data.load_tecplot(self.filename)
            with self.assertRaises(TecplotLogicError):
                self.cgroup.variable = ds1.variable(1)
            fr0.activate()

    def test_legend(self):
        self.assertIsInstance(self.cgroup.legend, ContourLegend)

if __name__ == '__main__':
    from .. import main
    main()
