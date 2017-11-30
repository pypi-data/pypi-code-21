class Field(object):
    def __init__(self,
               repeated=False,
               default=None):
        self.repeated = repeated
        self.default = default


class IntegerField(Field):
    name = "int64"


class FloatField(Field):
    name = "double"


class BooleanField(Field):
    name = "bool"


class BytesField(Field):
    name = "bytes"


class StringField(Field):
    name = "string"
