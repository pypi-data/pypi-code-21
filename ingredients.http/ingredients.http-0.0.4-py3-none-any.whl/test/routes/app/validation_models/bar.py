from schematics import Model
from schematics.types import StringType


class RequestPostBar(Model):
    foo = StringType(required=True)
