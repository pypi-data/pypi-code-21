from schematics import Model
from schematics.types import IntType


class RequestFooParams(Model):
    foo_id = IntType(required=True)
