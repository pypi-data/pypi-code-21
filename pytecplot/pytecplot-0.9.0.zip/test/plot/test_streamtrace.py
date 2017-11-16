import os
import unittest

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot.plot import ContourGroup
from tecplot.plot.streamtrace import (
    Streamtraces,
    StreamtraceRodRibbon,
    StreamtraceTerminationLine,
    StreamtraceTiming,
    StreamtraceRodRibbonEffects,
    StreamtraceRodRibbonMesh,
    StreamtraceRodRibbonShade,
    StreamtraceRodRibbonContour)
from tecplot.tecutil import Index

from test import patch_tecutil, skip_on

from ..property_test import PropertyTest
from ..sample_data import sample_data


class TestStreamtraces(PropertyTest):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        self.frame = frame

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        self.streamtraces = self.plot.streamtraces

    @skip_on(TecplotOutOfDateEngineError)
    def _add_streamtrace(self, streamtrace_type=Streamtrace.VolumeRibbon):
        self.streamtraces.add_rake(start_position=(0, 0, 0),
                                   end_position=(1, 1, 1),
                                   stream_type=streamtrace_type)

        self.streamtraces.add_on_zone_surface(zones=[0],
                                              stream_type=streamtrace_type)

        self.plot.vector.u_variable_index = 0
        self.plot.vector.v_variable_index = 1
        self.plot.vector.w_variable_index = 2

    def tearDown(self):
        os.remove(self.filename)

    def test_add_on_active_zone_surface(self):
        streamtrace_type = Streamtrace.VolumeRibbon
        self.streamtraces.add_rake(start_position=(0, 0, 0),
                                   end_position=(1, 1, 1),
                                   stream_type=streamtrace_type)
        # Use default zones='None' to force streamtrace seed to be
        # "On surfaces of active zones"
        # Note that this does not require the latest 360, so we
        # don't need to skip on out of date error as above.
        self.streamtraces.add_on_zone_surface(stream_type=streamtrace_type)

        self.plot.vector.u_variable_index = 0
        self.plot.vector.v_variable_index = 1
        self.plot.vector.w_variable_index = 2

    def test_streamtrace_reset_delta(self):
        self._add_streamtrace()
        delta = self.streamtraces.timing.delta
        self.streamtraces.timing.delta = 0.0
        self.streamtraces.timing.reset_delta()
        # We only check to see if the delta has changed, rather than
        # check for a specific value
        self.assertNotAlmostEqual(delta, self.streamtraces.timing.delta)

        with patch_tecutil('StreamtraceResetDelta') as reset_delta:
            reset_delta.return_value = False
            with self.assertRaises(TecplotSystemError):
                self.streamtraces.timing.reset_delta()

    def test_streamtraces_are_active(self):
        self.assertFalse(self.streamtraces.are_active)
        self.plot.vector.u_variable_index = 0
        self.plot.vector.v_variable_index = 1
        self.plot.vector.w_variable_index = 2
        self.plot.show_streamtraces = True
        self._add_streamtrace()
        self.streamtraces.show_paths = True
        self.assertTrue(self.streamtraces.are_active)

    def test_streamtrace_type(self):
        self._add_streamtrace(streamtrace_type=Streamtrace.SurfaceRibbon)
        self.assertEqual(self.streamtraces.streamtrace_type(0),
                         Streamtrace.SurfaceRibbon)

    def test_set_termination_line(self):
        self.assertFalse(self.streamtraces.has_terminating_line)
        self.streamtraces.set_termination_line([[0, 0, 0], [1, 1, 1]])
        self.assertTrue(self.streamtraces.has_terminating_line)

        with patch_tecutil('StreamtraceSetTermLine') as set_term_line:
            set_term_line.return_value = False
            with self.assertRaises(TecplotSystemError):
                self.streamtraces.set_termination_line([[0, 0, 0], [1, 1, 1]])

    def test_delete_all(self):
        self.assertEqual(self.streamtraces.count, 0)
        self._add_streamtrace()
        self.assertGreaterEqual(self.streamtraces.count, 1)
        self.streamtraces.delete_all()
        self.assertEqual(self.streamtraces.count, 0)

        with patch_tecutil('StreamtraceDeleteAll') as delete_all:
            delete_all.return_value = False
            with self.assertRaises(TecplotSystemError):
                self.streamtraces.delete_all()

    def test_delete_range(self):
        self._add_streamtrace()
        num_streamtraces = self.streamtraces.count
        self.streamtraces.delete_range(1, 2)
        self.assertEqual(self.streamtraces.count, num_streamtraces - 2)

        with patch_tecutil('StreamtraceDeleteRange') as delete_range:
            delete_range.return_value = False
            with self.assertRaises(TecplotSystemError):
                self.streamtraces.delete_range(1, 2)

    def test_position(self):
        self._add_streamtrace()
        self.assertTupleEqual(self.streamtraces.position(0), (0.0, 0.0, 0.0))
        self.assertTupleEqual(self.streamtraces.position(9), (1.0, 1.0, 1.0))

    def test_2d_position(self):
        self.frame.plot_type = PlotType.Cartesian2D
        self.streamtraces.add(seed_point=[0, 0],
                              stream_type=Streamtrace.TwoDLine)

    def test_add(self):
        self.assertEqual(self.streamtraces.count, 0)
        self.frame.plot_type = PlotType.Cartesian2D
        self.streamtraces.add(seed_point=[0, 0],
                              stream_type=Streamtrace.TwoDLine)
        self.assertGreaterEqual(self.streamtraces.count, 1)

        with patch_tecutil('StreamtraceAddX') as streamtrace_add:
            streamtrace_add.return_value = False
            self.frame.plot_type = PlotType.Cartesian3D
            with self.assertRaises(TecplotSystemError):
                self._add_streamtrace()

    def test_position_exceptions(self):
        if __debug__:
            for plot_type, seed_point in [
                (PlotType.Cartesian2D, [0, 0, 0]),
                    (PlotType.Cartesian3D, [0, 0])]:
                with self.assertRaises(TecplotTypeError):
                    self.frame.plot_type = plot_type
                    self.streamtraces.add(seed_point=seed_point,
                                          stream_type=Streamtrace.TwoDLine)
            self.frame.plot_type = PlotType.Cartesian2D
            with self.assertRaises(TypeError):
                self.streamtraces.add(seed_point=7,
                                      stream_type=Streamtrace.TwoDLine)

    def test_missing_add_rake(self):
        if __debug__:
            sdk_version = tp.version.sdk_version_info
            try:
                tp.version.sdk_version_info = (0, 0, 0)
                with self.assertRaises(TecplotOutOfDateEngineError):
                    self.streamtraces.add_on_zone_surface(
                        zones=[0],
                        stream_type=Streamtrace.VolumeLine)
            finally:
                tp.version.sdk_version_info = sdk_version

    #  Test type and read-only properties of subtree accessors

    def test_timing(self):
        self.assertIsInstance(self.streamtraces.timing, StreamtraceTiming)
        with self.assertRaises(AttributeError):
            self.streamtraces.timing = None

    def test_termination_line(self):
        self.assertIsInstance(
            self.streamtraces.termination_line, StreamtraceTerminationLine)
        with self.assertRaises(AttributeError):
            self.streamtraces.termination_line = None

    def test_rod_ribbon_mesh(self):
        self.assertIsInstance(
            self.streamtraces.rod_ribbon.mesh, StreamtraceRodRibbonMesh)
        with self.assertRaises(AttributeError):
            self.streamtraces.rod_ribbon.mesh = None

    def test_rod_ribbon_contour(self):
        self.assertIsInstance(
            self.streamtraces.rod_ribbon.contour, StreamtraceRodRibbonContour)
        with self.assertRaises(AttributeError):
            self.streamtraces.rod_ribbon.contour = None

    def test_rod_ribbon_shade(self):
        self.assertIsInstance(
            self.streamtraces.rod_ribbon.shade, StreamtraceRodRibbonShade)
        with self.assertRaises(AttributeError):
            self.streamtraces.rod_ribbon.shade = None

    def test_rod_ribbon_effects(self):
        self.assertIsInstance(
            self.streamtraces.rod_ribbon.effects, StreamtraceRodRibbonEffects)
        with self.assertRaises(AttributeError):
            self.streamtraces.rod_ribbon.effects = None

    def test_rod_ribbon(self):
        self.assertIsInstance(
            self.streamtraces.rod_ribbon, StreamtraceRodRibbon)
        with self.assertRaises(AttributeError):
            self.streamtraces.rod_ribbon = None

    def test_streamtraces_round_trip(self):
        for api, value in (
                ('show_arrows', bool),
                ('arrowhead_size', float),
                ('arrowhead_spacing', float),
                ('color', Color),
                ('dash_skip', int),
                ('line_thickness', float),
                ('marker_color', Color),
                ('marker_size', float),
                ('marker_symbol_type', SymbolType),
                ('max_steps', int),
                ('min_step_size', float),
                ('obey_source_zone_blanking', bool),
                ('show_dashes', bool),
                ('show_markers', bool),
                ('show_paths', bool),
                ('step_size', float),
        ):
            self.internal_test_property_round_trip(
                api, value, Streamtraces, self.streamtraces)

        self.streamtraces.marker_symbol_type = SymbolType.Text
        symbol = self.streamtraces.marker_symbol(SymbolType.Text)
        symbol.text = 'a'
        self.assertEqual(self.streamtraces.marker_symbol(SymbolType.Text).text,
                         'a')

    def test_rod_ribbon_round_trip(self):
        for api, value in (
                ('width', float),
                ('num_rod_points', 3),  # Num rod points must be >= 3
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceRodRibbon, self.streamtraces.rod_ribbon)

    def test_rod_ribbon_mesh_round_trip(self):
        for api, value in (
                ('show', bool),
                ('line_thickness', .5),
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceRodRibbonMesh,
                self.streamtraces.rod_ribbon.mesh)

    def test_rod_ribbon_contour_round_trip(self):
        for api, value in (
                ('flood_contour_group',  ContourGroup(1, self.plot)),
                ('flood_contour_group_index', Index),
                ('show', bool),
                ('use_lighting_effect', bool)
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceRodRibbonContour,
                self.streamtraces.rod_ribbon.contour)

    def test_rod_ribbon_shade_round_trip(self):
        for api, value in (
                ('color', Color),
                ('show', bool),
                ('use_lighting_effect', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceRodRibbonShade,
                self.streamtraces.rod_ribbon.shade)

    def test_rod_ribbon_effects_round_trip(self):
        for api, value in (
                ('lighting_effect', LightingEffect),
                ('surface_translucency', int),
                ('use_translucency', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceRodRibbonEffects,
                self.streamtraces.rod_ribbon.effects)

    def test_streamtrace_timing_round_trip(self):
        for api, value in (
                ('start', float),
                ('end', float),
                ('anchor', float),
                ('delta', float),
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceTiming,
                self.streamtraces.timing)

    def test_streamtrace_termination_line_round_trip(self):
        self._add_streamtrace()
        self.streamtraces.set_termination_line([[0, 0, 0], [1, 1, 1]])
        for api, value in (
                ('color', Color),
                ('is_active', bool),
                ('line_pattern', LinePattern),
                ('line_thickness', float),
                ('pattern_length', float),
                ('show', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, StreamtraceTerminationLine,
                self.streamtraces.termination_line)


if __name__ == '__main__':
    from .. import main
    main()
