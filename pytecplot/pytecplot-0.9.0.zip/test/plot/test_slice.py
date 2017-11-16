import os
import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.plot.slice import (SliceContour, SliceGroup, SliceEffects,
                                SliceVector, SliceEdge, SliceMesh, SliceShade)

from ..sample_data import sample_data
from tecplot.tecutil import Index
from ..property_test import PropertyTest
from test import patch_tecutil, skip_on
from tecplot.plot import ContourGroup


class TestSlice(PropertyTest):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        self.frame = frame

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        self.slice = self.plot.slice(0)  # type: SliceGroup

    def tearDown(self):
        os.remove(self.filename)

    def test_set_arbitrary(self):
        p1 = (1, 2, 3)
        p2 = (4, 5, 6)
        p3 = (.7, .8, .9)

        self.plot.show_slices = True
        self.slice.orientation = SliceSurface.Arbitrary
        self.slice.set_arbitrary_from_points(p1, p2, p3)

        self.assertAlmostEqual(self.slice.arbitrary_normal[0], -2.7)
        self.assertAlmostEqual(self.slice.arbitrary_normal[1], 5.4)
        self.assertAlmostEqual(self.slice.arbitrary_normal[2], -2.7)
        self.assertEqual(self.slice.origin, (.7, .8, .9))

    def test_set_arbitrary_failure(self):
        with patch_tecutil('SliceSetArbitraryUsingThreePoints') as set_arb:
            set_arb.return_value = False
            with self.assertRaises(TecplotSystemError):
                p1 = (1, 2, 3)
                p2 = (4, 5, 6)
                p3 = (.7, .8, .9)
                self.slice.set_arbitrary_from_points(p1, p2, p3)

    def test_contour(self):
        self.assertIsInstance(self.slice.contour, SliceContour)
        with self.assertRaises(AttributeError):
            self.slice.contour = None

    def test_mesh(self):
        self.assertIsInstance(self.slice.mesh, SliceMesh)
        with self.assertRaises(AttributeError):
            self.slice.mesh = None

    def test_effects(self):
        self.assertIsInstance(self.slice.effects, SliceEffects)
        with self.assertRaises(AttributeError):
            self.slice.effects = None

    def test_edge(self):
        self.assertIsInstance(self.slice.edge, SliceEdge)
        with self.assertRaises(AttributeError):
            self.slice.edge = None

    def test_shade(self):
        self.assertIsInstance(self.slice.shade, SliceShade)
        with self.assertRaises(AttributeError):
            self.slice.shade = None

    def test_vector(self):
        self.assertIsInstance(self.slice.vector, SliceVector)
        with self.assertRaises(AttributeError):
            self.slice.vector = None

    def test_eq(self):
        slice_0 = self.plot.slice(0)
        self.assertTrue(slice_0 == self.plot.slice(0))
        self.assertTrue(slice_0 != self.plot.slice(1))
        self.assertFalse(slice_0 == self.plot.slice(1))
        self.assertFalse(slice_0 != self.plot.slice(0))

    def test_slice_group_round_trip(self):
        for api, value in (
                ('show', bool),
                ('arbitrary_normal', (1.0, 2.0, 3.0)),
                ('show_primary_slice', bool),
                ('slice_source', SliceSource),
                ('show_start_and_end_slices', bool),
                ('obey_source_zone_blanking', bool),
                ('start_position', (1.0, 2.0, 3.0)),
                ('show_intermediate_slices', bool),
                ('end_position', (1.0, 2.0, 3.0)),
                ('num_intermediate_slices', 1)):
            self.internal_test_property_round_trip(
                api, value, SliceGroup, self.slice)

    @skip_on(TecplotOutOfDateEngineError)
    def test_surface_generation_method(self):
        self.internal_test_property_round_trip(
            'surface_generation_method', SurfaceGenerationMethod,
            SliceGroup, self.slice)

    def test_slice_ijk_position(self):
        # Use origin as representative ijk
        for slice_surface in (SliceSurface.IPlanes,
                              SliceSurface.JPlanes,
                              SliceSurface.KPlanes):

            self.slice.orientation = slice_surface
            self.slice.origin = (1, 2, 3)
            self.assertEqual(self.slice.origin.i, 1)
            self.assertEqual(self.slice.origin.j, 2)
            self.assertEqual(self.slice.origin.k, 3)

            if __debug__:
                for bad_attribute in ('x', 'y', 'z'):
                    with self.assertRaises(AttributeError):
                        getattr(self.slice.origin, bad_attribute)

            self.slice.origin += (1, 1, 1)
            self.assertEqual(self.slice.origin, (2, 3, 4))

            self.slice.origin -= (1, 1, 1)
            self.assertEqual(self.slice.origin, (1, 2, 3))

            with self.assertRaises(TecplotSystemError):
                self.slice.origin = -self.slice.origin

            slice_1 = self.plot.slice(1)  # type: SliceGroup
            slice_1.orientation = slice_surface
            slice_1.origin = (1, 2, 3)
            self.slice.origin = slice_1.origin
            self.assertEqual(self.slice.origin.i, 1)
            self.assertEqual(self.slice.origin.j, 2)
            self.assertEqual(self.slice.origin.k, 3)

            self.slice.origin += slice_1.origin
            self.assertEqual(self.slice.origin, (2, 4, 6))

            self.slice.origin -= slice_1.origin
            self.assertEqual(self.slice.origin, (1, 2, 3))

            with self.assertRaises(TypeError):  # read-only
                self.slice.origin[0] = 0

            with self.assertRaises(IndexError):
                self.slice.origin[4]

            self.assertIn('Slice Position', str(self.slice.origin))

            with self.assertRaises(TecplotLogicError):
                self.slice.origin = 1

            with self.assertRaises(TecplotAttributeError):
                self.slice.origin += 2

    def test_slice_xyz_position(self):
        # Use origin as the representative xyz
        for slice_surface in (SliceSurface.XPlanes,
                              SliceSurface.YPlanes,
                              SliceSurface.ZPlanes):

            self.slice.orientation = slice_surface
            self.slice.origin = (1.1, 2, 3)
            self.assertEqual(self.slice.origin.x, 1.1)
            self.assertEqual(self.slice.origin.y, 2.0)
            self.assertEqual(self.slice.origin.z, 3.0)

            if __debug__:
                for bad_attribute in ('i', 'j', 'k'):
                    with self.assertRaises(AttributeError):
                        getattr(self.slice.origin, bad_attribute)

            self.slice.origin += (1, 2, 3)
            self.assertEqual(self.slice.origin, (2.1, 4.0, 6.0))

            self.slice.origin -= (1, 2, 3)
            self.assertEqual(self.slice.origin, (1.1, 2.0, 3.0))

            self.slice.origin = -self.slice.origin
            self.assertEqual(self.slice.origin, (-1.1, -2.0, -3.0))

            slice_1 = self.plot.slice(1)  # type: SliceGroup
            slice_1.orientation = slice_surface
            slice_1.origin = (1.1, 2, 3)
            self.slice.origin = slice_1.origin
            self.assertEqual(self.slice.origin.x, 1.1)
            self.assertEqual(self.slice.origin.y, 2.0)
            self.assertEqual(self.slice.origin.z, 3.0)

            self.slice.origin += slice_1.origin
            self.assertEqual(self.slice.origin, (2.2, 4, 6))

            self.slice.origin -= slice_1.origin
            self.assertEqual(self.slice.origin, (1.1, 2.0, 3.0))

            self.slice.origin = -self.slice.origin
            self.assertEqual(self.slice.origin, (-1.1, -2.0, -3.0))

            with self.assertRaises(TecplotLogicError):
                self.slice.origin = 1

            with self.assertRaises(TecplotAttributeError):
                self.slice.origin += 2

    def test_slice_contour_round_trip(self):
        for api, value in (
                ('show', bool),
                ('line_color', Color),
                ('line_thickness', 0.5),
                ('contour_type', ContourType),
                ('flood_contour_group_index', 1),
                ('flood_contour_group', ContourGroup(1, self.plot)),
                ('use_lighting_effect', bool),
                ('line_contour_group_index', Index),
                ('line_contour_group', ContourGroup(1, self.plot))
                 ):
            self.internal_test_property_round_trip(
                api, value, SliceContour, self.slice.contour)

    def test_slice_effects_round_trip(self):
        for api, value in (
                ('lighting_effect', LightingEffect),
                ('surface_translucency', 1),
                ('use_translucency', bool)
                 ):
            self.internal_test_property_round_trip(
                api, value, SliceEffects, self.slice.effects)

    def test_slice_mesh_round_trip(self):
        for api, value in (
                ('line_thickness', 1.0),
                ('show', bool),
                ('color', Color),
                 ):
            self.internal_test_property_round_trip(
                api, value, SliceMesh, self.slice.mesh)

    def test_slice_shade_round_trip(self):
        for api, value in (
                ('use_lighting_effect', bool),
                ('show', bool),
                ('color', Color),
        ):
            self.internal_test_property_round_trip(
                api, value, SliceShade, self.slice.shade)

    def test_slice_edge_round_trip(self):
        for api, value in (
                ('show', bool),
                ('color', Color),
                ('line_thickness', .01),
                ('edge_type', EdgeType)
                 ):
            self.internal_test_property_round_trip(
                api, value, SliceEdge, self.slice.edge)

    def test_slice_vector_round_trip(self):
        for api, value in (
                ('show', bool),
                ('color', Color),
                ('is_tangent', bool),
                ('line_thickness', .01),
                ('vector_type', VectorType),
                ('is_tangent', bool),
                ('arrowhead_style', ArrowheadStyle)
                 ):
            self.internal_test_property_round_trip(
                api, value, SliceVector, self.slice.vector)

if __name__ == '__main__':
    from .. import main
    main()
