from datetime import datetime

from schematizer.exceptions import SimpleValidationError
from schematizer.nodes.base import BaseCoercibleNode, BaseNode


class DummyNode(BaseNode):
    def to_native(self, obj):
        return obj

    def to_primitive(self, obj):
        return obj


class BoolNode(BaseCoercibleNode):
    TRUE_VALUES = (True, 1, '1', 'true', 't', 'yes', 'y', 'on')
    FALSE_VALUES = (False, 0, '0', 'false', 'f', 'no', 'n', 'off')

    coerce_native = bool

    def to_native(self, obj):
        if obj in self.TRUE_VALUES:
            return True
        if obj in self.FALSE_VALUES:
            return False
        else:
            extra = {'message': f'invalid boolean: {obj!r}'}
            raise SimpleValidationError('INVALID', extra=extra)


class IntNode(BaseCoercibleNode):
    coerce_primitive = int
    coerce_native = int


class FloatNode(BaseCoercibleNode):
    coerce_primitive = float
    coerce_native = float


class StrNode(BaseCoercibleNode):
    coerce_primitive = str
    coerce_native = str


class DateTimeNode(BaseCoercibleNode):
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def coerce_primitive(self, obj):
        return datetime.strptime(obj, self.FORMAT)

    def coerce_native(self, obj):
        return obj.strftime(self.FORMAT)


class DateNode(DateTimeNode):
    FORMAT = '%Y-%m-%d'

    def coerce_primitive(self, obj):
        return super().coerce_primitive(obj).date()


class TimeNode(DateTimeNode):
    FORMAT = '%H:%M:%S'

    def coerce_primitive(self, obj):
        return super().coerce_primitive(obj).time()


Dummy = DummyNode
Bool = BoolNode
Int = IntNode
Float = FloatNode
Str = StrNode
DateTime = DateTimeNode
Date = DateNode
Time = TimeNode
