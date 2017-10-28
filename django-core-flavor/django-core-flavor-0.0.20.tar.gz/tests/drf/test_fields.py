import random

from django.test import TestCase
from rest_framework import exceptions
from rest_framework import serializers

from core_flavor.drf import fields


class FiedsTests(TestCase):

    def test_decimal_field(self):
        decimals = random.randint(1, 10)
        field = fields.DecimalField(decimals=decimals)
        decimal_value = random.randint(1, 100)
        value = field.to_internal_value(str(decimal_value))

        self.assertEqual(value, float(decimal_value / 10 ** decimals))
        self.assertEqual(decimal_value, field.to_representation(value))

    def test_decimal_invalid_value(self):
        with self.assertRaises(AssertionError):
            fields.DecimalField(decimals=0)

    def test_decimal_field_to_internal_value_invalid(self):
        decimals = random.randint(1, 10)
        field = fields.DecimalField(decimals=decimals)

        with self.assertRaises(exceptions.ValidationError):
            field.to_internal_value(None)

    def test_decimal_field_to_representation_invalid(self):
        decimals = random.randint(1, 10)
        field = fields.DecimalField(decimals=decimals)

        with self.assertRaises(serializers.ValidationError):
            field.to_representation(None)
