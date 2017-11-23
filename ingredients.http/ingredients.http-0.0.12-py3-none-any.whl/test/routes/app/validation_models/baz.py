from schematics import Model
from schematics.types import StringType


class ResponseBaz(Model):
    foo = StringType(required=True)
