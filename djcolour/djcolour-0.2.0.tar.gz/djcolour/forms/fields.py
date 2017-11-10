from django import forms
from django.forms import widgets

from ..base import Color


class ColorInput(widgets.Input):
    input_type = 'color'

    def format_value(self, value):
        if isinstance(value, Color):
            value = value.get_hex_l()
        return super(ColorInput, self).format_value(value)


class ColorField(forms.Field):
    widget = ColorInput
