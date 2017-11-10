from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import Color
from .forms.fields import ColorField as ColorFormField


def parse_color(color_string):
    try:
        return Color(color_string)
    except ValueError as v:
        raise ValidationError(_('\'%s\' is not recognized as a valid color') % (color_string,))


class ColorField(models.CharField):

    description = "Represent a color using colour.Color"

    def __init__(self, *args, **kwargs):
        defaults = {'max_length': 7}
        defaults.update(kwargs)
        super(ColorField, self).__init__(*args, **defaults)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return parse_color(value)

    def to_python(self, value):
        if isinstance(value, Color):
            return value

        if value is None:
            return value

        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': ColorFormField}
        defaults.update(kwargs)
        return super(ColorField, self).formfield(**defaults)
