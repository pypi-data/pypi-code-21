from builtins import super

import os
import unittest

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot import constant
from tecplot.plot.axis import Axis
from tecplot.plot.view import Cartesian2DView, Cartesian3DView, PolarView
from tecplot.tecutil import sv, ArgList

from ..property_test import PropertyTest
from ..sample_data import sample_data

from test import patch_tecutil, skip_on


class TestView(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        self.frame = tp.active_frame()
        self.frame = self.frame
        self.frame.plot_type = PlotType.Cartesian3D
        self.plot = self.frame.plot()
        self.plot.activate()
        self.view = self.plot.view

    def tearDown(self):
        os.remove(self.filename)


class TestViewActions(TestView, PropertyTest):
    def setUp(self):
        super().setUp()
        self.view.fit()
        self.initial_viewer_position = self.view.position

        self.expected_consider_blanking = None
        self.expected_view_op = None
        self.expected_axis = None
        self.expected_axis_num = None

    def tearDown(self):
        super().tearDown()

    def assertViewPositionAlmostEqual(self, t1, t2):
        for pos in range(3):
            self.assertAlmostEqual(t1[pos], t2[pos])

    def assertViewPositionNotAlmostEqual(self, t1, t2):
        for pos in range(3):
            self.assertNotAlmostEqual(t1[pos], t2[pos])

    def _change_position(self, dx=1.0, dy=2.0, dz=3.0):
        self.view.position = (self.initial_viewer_position.x + dx,
                              self.initial_viewer_position.y + dy,
                              self.initial_viewer_position.z + dz)

        self.assertNotEqual(self.view.position, self.initial_viewer_position)

    def _switch_to_view(self, plot_type):
        self.frame.plot_type = plot_type
        self.view = self.frame.plot().view

    def _check_consider_blanking(self, arg_list):
        if self.expected_consider_blanking:
            self.assertTrue(arg_list[sv.CONSIDERBLANKING])
        else:
            self.assertNotIn(sv.CONSIDERBLANKING, arg_list.keys())

    def _run_view_arg_test(self, obj, test_table_line):
        method = getattr(obj, test_table_line[0])
        view_op = test_table_line[1]
        uses_consider_blanking = test_table_line[2]

        if isinstance(obj, Axis):
            self.expected_axis = ord(obj.name[0])
            self.expected_axis_num = getattr(obj, 'index', 0) + 1

        self.expected_view_op = view_op
        if uses_consider_blanking:
            for value in {True, False}:
                self.expected_consider_blanking = value
                method(value)

        with patch_tecutil('ViewX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                method()

    def test_default_consider_blanking(self):
        for plot_type in (
                PlotType.XYLine,
                PlotType.PolarLine,
                PlotType.Cartesian2D,
                PlotType.Cartesian3D):

            # 'consider_blanking' defaults to True, so if we call
            # the view actions which have a consider_blanking parameter
            # with no arguments then sv.CONSIDERBLANKING=TRUE will be
            # passed to TecUtilViewX.
            # This allows us to test that the correct view action function
            # was called (either the one which has a consider_blanking
            # parameter, or the one that doesn't).
            self._switch_to_view(plot_type)

            self.view.center()
            self.view.fit()
            self.view.fit_data()

            if plot_type != PlotType.Cartesian3D and plot_type != PlotType.PolarLine:
                self.view.fit_to_nice()

            elif plot_type == PlotType.Cartesian3D:
                self.view.fit_surfaces()

    def test_view_axis_arglist_args(self):
        def _fake_view_x(arg_list):
            self.assertEqual(self.expected_view_op.value, arg_list[sv.VIEWOP])
            self._check_consider_blanking(arg_list)
            self.assertEqual(arg_list[sv.AXIS], self.expected_axis)
            self.assertEqual(arg_list[sv.AXISNUM], self.expected_axis_num)

            if not self.expected_consider_blanking:
                self.assertEqual(3, len(arg_list))
            else:
                self.assertEqual(4, len(arg_list))

            return True

        for axis in [self.plot.axes.x_axis, self.plot.axes.y_axis]:
            with patch_tecutil('ViewX', side_effect=_fake_view_x):
                for test_table_line in (
                        ('fit_range', constant.View.AxisFit, True),
                        ('adjust_range_to_nice',
                         constant.View.AxisMakeCurrentValuesNice, None),
                        ('fit_range_to_nice', constant.View.AxisNiceFit, True),
                ):
                    self._run_view_arg_test(axis, test_table_line)

    # Here we are testing that TecUtilViewX is called with the
    # correct arg list parameters for all view ops that we support.
    #
    # We assume that if TecUtilViewX is called correctly,
    # then the pytecplot equivalent method is correct.
    def test_view_arglist_args(self):
        def _fake_view_x(arg_list):
            """@type arg_list: ArgList"""
            self.assertEqual(self.expected_view_op.value, arg_list[sv.VIEWOP])

            if not self.expected_consider_blanking:
                self.assertEqual(1, len(arg_list))
            else:
                self.assertEqual(2, len(arg_list))

            return True

        with patch_tecutil('ViewX', side_effect=_fake_view_x):
            for test_table_line in (
                    # True --> uses consider_blanking
                    ('fit', constant.View.Fit, True),
                    ('center', constant.View.Center, True),
                    ('fit_data', constant.View.DataFit, True),
                           ):
                self._run_view_arg_test(self.view, test_table_line)

            for plot_type in (PlotType.Cartesian2D, PlotType.XYLine):
                self._switch_to_view(plot_type)

                for test_table_line in (
                    ('adjust_to_nice', constant.View.MakeCurrentViewNice, None),
                    ('fit_to_nice', constant.View.NiceFit, None)
                               ):
                    self._run_view_arg_test(self.view, test_table_line)

            self._switch_to_view(PlotType.PolarLine)
            self._run_view_arg_test(self.view, ('reset_to_entire_circle',
                                    constant.View.AxisResetToEntireCircle,
                                    None))

    def test_magnification_property(self):
        self.internal_test_property_round_trip(
            'magnification', 1.0, Cartesian3DView, self.view)

    def test_zoom(self):
        with patch_tecutil('ViewZoom', return_value=True) as tec_util:
            self.view.zoom(xmin=1, xmax=7, ymin=0, ymax=9)
            self.assertEqual(1, tec_util.call_count)
            self.assertEqual(4, len(tec_util.call_args[0]))
            # x1, y1, x2, y1
            for index, value in enumerate((1.0, 0.0, 7.0, 9.0)):
                self.assertEqual(value, tec_util.call_args[0][index])

        with patch_tecutil('ViewZoom', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.zoom(1, 0, 7, 9)

    def test_translate(self):
        with patch_tecutil('ViewTranslate', return_value=True) as tec_util:
            self.view.translate(1.0, 2.0)
            self.assertEqual(1, tec_util.call_count)
            self.assertEqual(2, len(tec_util.call_args[0]))
            self.assertEqual(1.0, tec_util.call_args[0][0])
            self.assertEqual(2.0, tec_util.call_args[0][1])

        with patch_tecutil('ViewTranslate', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.translate(1.0, 2.0)

    # The following tests are not strictly necessary since we've already checked
    # the TecUtil calls, however they do serve as a final sanity check.
    def test_fit(self):
        self._change_position()
        self.view.fit()
        self.assertViewPositionAlmostEqual(self.view.position,
                                           self.initial_viewer_position)

        with patch_tecutil('ViewX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.fit()

    def test_center(self):
        self.view.center()
        centered_position = self.view.position
        self._change_position()
        self.assertViewPositionNotAlmostEqual(centered_position,
                                              self.view.position)
        self.view.fit()
        self.view.center()
        self.assertViewPositionAlmostEqual(self.view.position,
                                           centered_position)

        with patch_tecutil('ViewX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.center()

    def test_data_fit(self):
        self.view.fit_data()
        data_fit_position = self.view.position
        self._change_position()
        self.assertViewPositionNotAlmostEqual(
            data_fit_position, self.view.position)
        self.view.fit_data()
        self.assertViewPositionAlmostEqual(self.view.position,
                                           data_fit_position)

        with patch_tecutil('ViewX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.fit_data()

    def test_fit_surfaces(self):
        self.view.fit_surfaces()
        fit_surfaces_position = self.view.position
        self._change_position()
        self.assertViewPositionNotAlmostEqual(fit_surfaces_position,
                                              self.view.position)
        self.view.fit_surfaces()
        self.assertViewPositionAlmostEqual(self.view.position,
                                           fit_surfaces_position)

        with patch_tecutil('ViewX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.view.fit_surfaces()

    def test_rotate_to_angles(self):
        self.view.rotate_to_angles(20, 40, 60)
        self.assertViewPositionNotAlmostEqual(self.initial_viewer_position,
                                              self.view.position)


class TestPolarView(PropertyTest, TestView):
    def setUp(self):
        super().setUp()
        self.frame.plot_type = PlotType.PolarLine
        self.view = self.frame.plot().view

        self.internal_test_property_round_trip(
            'extents', (1.0, 2.0, 3.0, 4.0), PolarView, self.view)

    def tearDown(self):
        super().tearDown()


class TestView3D(PropertyTest, TestView):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_round_trip(self):
        for api, value in (
                ('alpha', 1.0),
                ('distance', 3.9),
                ('position', (1.0, 2.0, 3.0)),
                ('theta', .5),
                ('psi', 100.0)
        ):
            self.internal_test_property_round_trip(
                api, value, Cartesian3DView,
                self.view)

    @skip_on(TecplotOutOfDateEngineError)
    def test_projection(self):
        self.internal_test_property_round_trip(
            'projection', Projection, Cartesian3DView, self.view)


    @skip_on(TecplotOutOfDateEngineError)
    def test_field_of_view(self):
        self.view.projection = Projection.Perspective
        self.internal_test_property_round_trip(
            'field_of_view', 1.0, Cartesian3DView, self.view)

    @skip_on(TecplotOutOfDateEngineError)
    def test_width(self):
        self.view.projection = Projection.Orthographic
        self.internal_test_property_round_trip(
            'width', 1.0, Cartesian3DView, self.view)

    @skip_on(TecplotOutOfDateEngineError)
    def test_field_of_view_error(self):
        if __debug__:
            self.view.projection = Projection.Orthographic
            with self.assertRaises(TecplotValueError):
                self.view.field_of_view = 1.0

    @skip_on(TecplotOutOfDateEngineError)
    def test_width_error(self):
        if __debug__:
            self.view.projection = Projection.Perspective
            with self.assertRaises(TecplotValueError):
                self.view.width = 1.0

    def test_projection_required_version(self):
        if __debug__:
            save_version_info = tp.version.sdk_version_info
            tp.version.sdk_version_info = (0, 0, 0)

            try:
                with self.assertRaises(TecplotOutOfDateEngineError):
                    self.view.projection = Projection.Perspective
                with self.assertRaises(TecplotOutOfDateEngineError):
                    getattr(Cartesian3DView, 'projection').fget(self.view)
            finally:
                tp.version.sdk_version_info = save_version_info


if __name__ == '__main__':
    from .. import main
    main()
