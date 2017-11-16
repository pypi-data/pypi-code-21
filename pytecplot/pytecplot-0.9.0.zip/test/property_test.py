from __future__ import division
import random
import unittest
from tecplot.constant import *
from tecplot import constant
from tecplot.tecutil import Index
from enum import Enum
from tecplot.plot import ContourGroup
from tecplot.text import TextBox, Font

# TODO: Refactor annotation tests to use this class. 10/26/16, davido


class PropertyTest(unittest.TestCase):
    def _internal_test_property_round_trip_value(self, property_name, value,
                                                 class_type, style_object):
        getter = getattr(class_type, property_name).fget
        setter = getattr(class_type, property_name).fset

        setter(style_object, value)
        getter_value = getter(style_object)

        self.assertAlmostEqual(getter_value, value)

    def internal_test_text_font_round_trip(self, font):
        """@type font: Font"""
        for api, value in (
                ('bold', bool),
                ('italic', bool),
                ('size', float),
                ('size_units', Units.Point),
                ('typeface', 'Arial'),
        ):
            self.internal_test_property_round_trip(
                api, value, Font,
                font)

    def internal_test_text_box_round_trip(self, text_box):
        """@type text_box: TextBox"""
        for api, value in (
                ('box_type', constant.TextBox),
                ('color', Color),
                ('fill_color', Color),
                ('line_thickness', float),
                ('margin', float),
        ):
            self.internal_test_property_round_trip(
                api, value, TextBox,
                text_box)

    def internal_test_property_round_trip(self,
                                          property_name, value_or_type,
                                          class_type, style_object):
        """Test property round trip.

            Given an property name and a value or type, test round trip of
            that property.

        """

        # pytecplot literal object types (such as ContourGroup) must be checked
        # first, but they are processed as if they were primitive literals,
        # so they must support __eq__
        if isinstance(value_or_type, ContourGroup):
            self._internal_test_property_round_trip_value(
                property_name, value_or_type, class_type, style_object)
        else:
            if value_or_type == float:
                self._internal_test_property_round_trip_value(property_name, 1.0,
                                                              class_type,
                                                              style_object)
            elif value_or_type == int or value_or_type == Index:
                self._internal_test_property_round_trip_value(
                    property_name, 1, class_type, style_object)

            # Don't confuse type Enum with a literal int enum
            # Caller may pass the name of the enum or a specific enum value.
            elif (not isinstance(value_or_type, int) and
                  type(value_or_type) == type(Enum)):
                # Enum value:

                # If there are more than 2 enum values,
                # randomly test up to 1/2 of the enum values
                if value_or_type == Color or len(value_or_type) <= 2:
                    sample_size = min(2, len(value_or_type))
                else:
                    sample_size = len(value_or_type) // 2

                enum_values = random.sample(
                    [E for E in value_or_type if E.value >= 0], sample_size)

                for enum_value in enum_values:
                    self._internal_test_property_round_trip_value(
                        property_name, enum_value, class_type, style_object)

            elif value_or_type == bool:
                for val in (True, False, True):
                    self._internal_test_property_round_trip_value(
                        property_name, val, class_type, style_object)
            else:
                # Value is a literal and not a type
                self._internal_test_property_round_trip_value(
                    property_name, value_or_type, class_type, style_object)
