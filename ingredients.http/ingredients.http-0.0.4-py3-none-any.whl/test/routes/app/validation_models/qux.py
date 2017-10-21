from schematics import Model
from schematics.types import StringType, IntType


class ResponseQux(Model):
    id = IntType(required=True)
    foo = StringType(required=True)
