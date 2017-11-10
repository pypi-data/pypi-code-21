from schematics import types
from schematics.models import BaseType


class CustomDecimalType(types.DecimalType):

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.precision = kwargs.pop('precision', None)
        self.scale = kwargs.pop('scale', None)

        super(CustomDecimalType, self).__init__(min_value=min_value, max_value=max_value, **kwargs)


class NonUnicodeStringType(types.StringType):
    pass


class JSONType(BaseType):
    pass
