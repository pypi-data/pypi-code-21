from builtins import super

import unittest

from enum import Enum

import tecplot
from tecplot.constant import *
from tecplot.exception import *
from tecplot.annotation import Annotation


class AnnotationIteratorTest(unittest.TestCase):
    def setUp(self):
        tecplot.layout.new_layout()

    def run_test_empty_iterator(self, annotation_iterator):
        annotation_objects = [
            A for A in annotation_iterator]
        self.assertFalse(annotation_objects)  # No objects to iterate

    def run_test_frame_switch(self, annotation_iterator):
        # annotation_iterator should have at least 2 items
        with self.assertRaises(TecplotError):
            for _ in annotation_iterator:
                tecplot.active_page().add_frame()


class AnnotationTestAbstract(unittest.TestCase):
    def tearDown(self):
        tecplot.layout.new_layout()

    def annotation_object(self):
        raise NotImplementedError

    def annotation_class(self):
        raise NotImplementedError

    def _internal_test_round_trip_value(self, api, value):
        obj = self.annotation_object()
        getter = getattr(self.annotation_class(), api).fget
        setter = getattr(self.annotation_class(), api).fset

        setter(obj, value)
        self.assertEqual(getter(obj), value)

    def internal_test_round_trip(self, api, value_or_type):
        if value_or_type == float:
            self._internal_test_round_trip_value(api, 1.0)
        elif value_or_type == int:
            self._internal_test_round_trip_value(api, 1)

        # Don't confuse type Enum with a literal int enum
        # Caller may pass the name of the enum or a specific enum value.
        elif (not isinstance(value_or_type, int) and
              type(value_or_type) == type(Enum)):

            values_tested = set()
            # Test all enum values for this type of enum
            for enum_value in value_or_type:
                # But skip aliased enum values
                if enum_value.value not in values_tested:
                    values_tested.add(enum_value)
                    if enum_value.value >= 0:
                        self._internal_test_round_trip_value(api, enum_value)
                    else:
                        with self.assertRaises(TecplotLogicError):
                            # Negative enums are not allowed in the
                            # TecUtilAnnotation* API
                            self._internal_test_round_trip_value(
                                api, enum_value)

        elif value_or_type == bool:
            self._internal_test_round_trip_value(api, True)
            self._internal_test_round_trip_value(api, False)
        else:
            # Value is literal
            self._internal_test_round_trip_value(api, value_or_type)


class TestAnnotation(AnnotationTestAbstract):
    def setUp(self):
        super().setUp()
        self.text = tecplot.active_frame().add_text('test_annotation_text')

    def tearDown(self):
        super().tearDown()

    def annotation_object(self):
        return self.text

    def annotation_class(self):
        return Annotation

    def test_round_trip(self):
        for api, value in (('anchor_position', (1.0, 2.0, 0.0)),
                           ('scope', Scope),
                           ('zone_or_map', int),
                           ('attached', bool),
                           ('clipping', Clipping)
                           ):
            self.internal_test_round_trip(api, value)

    def test_bad_id(self):
        with self.assertRaises(TecplotSystemError):
            Annotation(TECUTIL_BAD_ID, None, None)

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.text.color = val
            self.assertEqual(self.text.color, val)
        with self.assertRaises(ValueError):
            self.text.color = 'badvalue'
        with self.assertRaises(ValueError):
            self.text.color = 0.5


if __name__ == '__main__':
    from .. import main
    main()
