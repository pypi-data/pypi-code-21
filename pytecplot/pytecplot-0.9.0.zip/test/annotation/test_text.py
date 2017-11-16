from __future__ import unicode_literals
from builtins import super

import unittest

from unittest.mock import *

import tecplot
from tecplot.constant import *
from tecplot.annotation.text import Text
from tecplot.annotation.annotation import Annotation
from tecplot.exception import TecplotLogicError, TecplotSystemError

from .. import patch_tecutil
from .test_annotation import AnnotationTestAbstract, AnnotationIteratorTest


class TestAnnoTextIterator(AnnotationIteratorTest):
    def setUp(self):
        super().setUp()

    def test_next(self):
        iterator = Annotation._Iterator(Text, tecplot.active_frame())
        with self.assertRaises(StopIteration):
            iterator.next()
        with self.assertRaises(StopIteration):
            iterator.__next__()

    def test_empty_iterator(self):
        self.run_test_empty_iterator(
            Annotation._Iterator(Text, tecplot.active_frame()))

    def test_non_empty_iterator(self):
        # Add a text, see if we get it back in the iterator
        text = tecplot.active_frame().add_text('testing 1,2,3')
        text_objects = [
            T for T in Annotation._Iterator(Text, tecplot.active_frame())]
        self.assertEqual(1, len(text_objects))
        self.assertTrue(text == text_objects[0])

    def test_frame_switch(self):
        for text_obj in range(3):
            tecplot.active_frame().add_text('testing 1,2,3')

        self.run_test_frame_switch(
            Annotation._Iterator(Text, tecplot.active_frame()))


class TestAnnoTextRoundTrip(AnnotationTestAbstract):
    def setUp(self):
        tecplot.new_layout()
        self.text = tecplot.active_frame().add_text('test_annotation_text')

    def annotation_object(self):
        return self.text

    def annotation_class(self):
        return Text

    def test_round_trip(self):
        for api, value_or_type in [
                ('typeface', 'Times'),
                ('bold', bool),
                ('italic', bool),
                ('size', float),
                ('anchor', TextAnchor),
                ('angle', float),
                ('attached', bool),
                ('line_spacing', float),
                ('text_string', 'abc')]:
            self.internal_test_round_trip(api, value_or_type)


class TestAnnoTextBoxRoundTrip(AnnotationTestAbstract):
    def setUp(self):
        super().setUp()
        tecplot.new_layout()
        self.text = tecplot.active_frame().add_text('abc')

    def annotation_object(self):
        return self.text.text_box

    def annotation_class(self):
        return tecplot.annotation.text.TextBox

    def test_round_trip(self):
        for api, value_or_type in [
                ('margin', float),
                ('text_box_type', tecplot.constant.TextBox),
                ('line_thickness', float)]:
            self.internal_test_round_trip(api, value_or_type)

    def test_textbox_position(self):
        # position is read-only.
        position = self.text.text_box.position
        for value in position:
            self.assertIsInstance(value, float)


class TestAnnoTextBox(unittest.TestCase):
    def setUp(self):
        tecplot.new_layout()
        self.text = tecplot.active_frame().add_text('abc')

    def test_str(self):
        self.text.text_box.text_box_type = TextBox.Filled
        self.assertIn('abc', str(self.text.text_box))

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.text.text_box.color = val
            self.assertEqual(self.text.text_box.color, val)
        with self.assertRaises(ValueError):
            self.text.text_box.color = 'badvalue'
        with self.assertRaises(ValueError):
            self.text.text_box.color = 0.5

    def test_fill_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.text.text_box.fill_color = val
            self.assertEqual(self.text.text_box.fill_color, val)
        with self.assertRaises(ValueError):
            self.text.text_box.fill_color = 'badvalue'
        with self.assertRaises(ValueError):
            self.text.text_box.fill_color = 0.5


class TestAnnoText(unittest.TestCase):
    def setUp(self):
        tecplot.new_layout()
        self.text = tecplot.active_frame().add_text('abc')

    def test_str(self):
        text = tecplot.active_frame().add_text('abc')
        self.assertEqual(str(text), 'abc')

    def test_eq(self):
        text_1 = tecplot.active_frame().add_text('abc')
        text_2 = tecplot.active_frame().add_text('abc')
        self.assertEqual(text_1, text_1)
        self.assertNotEqual(text_1, text_2)

    def test_size_units_and_coord_sys(self):
        self.text.position_coordinate_system = CoordSys.Frame
        self.assertEqual(self.text.position_coordinate_system, CoordSys.Frame)
        self.text.size_units = Units.Point
        self.assertEqual(self.text.size_units, Units.Point)
        self.text.size_units = Units.Grid
        self.assertEqual(self.text.position_coordinate_system, CoordSys.Grid)

        self.text.position_coordinate_system = CoordSys.Frame
        self.assertEqual(self.text.size_units, Units.Frame)

    def test_invalid_text_box_line_thickness(self):
        if __debug__:
            self.text.text_box.text_box_type = TextBox.Filled
            with self.assertRaises(TecplotLogicError):
                self.text.text_box.line_thickness = 0.0

            with self.assertRaises(TecplotLogicError):
                self.text.text_box.line_thickness = -1.0

    def test_invalid_text_box_margin(self):
        if __debug__:
            self.text.text_box.text_box_type = TextBox.Filled
            with self.assertRaises(TecplotLogicError):
                self.text.text_box.margin = -1.0

    def test_engine_failure(self):
        with patch_tecutil('TextGetString') as text_get_string:  # type: Mock
            text_get_string.return_value = (False, '')
            with self.assertRaises(TecplotSystemError):
                s = self.text.text_string
                assert not s

    def test_delete(self):
        fr = tecplot.active_frame()
        txt = fr.add_text('testing')
        self.assertIn(txt, fr.texts())
        fr.delete_text(txt)
        self.assertNotIn(txt, fr.texts())


if __name__ == '__main__':
    from .. import main
    main()
